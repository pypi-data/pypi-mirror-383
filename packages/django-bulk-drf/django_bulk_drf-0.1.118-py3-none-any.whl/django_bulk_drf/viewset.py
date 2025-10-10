"""
Operation mixins for DRF ViewSets.

Provides a unified mixin that enhances standard ViewSet endpoints with efficient
synchronous bulk operations using query parameters.
"""

import sys
import time

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from django_bulk_drf.config import get_bulk_drf_settings


class BulkModelViewSet:
    """
    Enhanced ViewSet mixin providing efficient bulk operations.

    Provides optimized bulk database operations for arrays while maintaining
    standard behavior for single instances.

    Simple routing strategy:
    - Single instances (dict): Direct database operations
    - Arrays (list): Optimized bulk database operations

    Enhanced endpoints:
    - GET    /api/model/?ids=1                    # Direct single get
    - GET    /api/model/?ids=1,2,3               # Bulk multi-get
    - POST   /api/model/?unique_fields=...       # Smart upsert routing
    - PATCH  /api/model/?unique_fields=...      # Smart upsert routing
    - PUT    /api/model/?unique_fields=...      # Smart upsert routing

    Relies on DRF's built-in payload size limits for request validation.
    Optimizes database operations for maximum performance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        """Handle array data for serializers with upsert context."""
        try:
            data = kwargs.get("data", None)
            if data is not None and isinstance(data, list):
                kwargs["many"] = True

            serializer = super().get_serializer(*args, **kwargs)

            return serializer
        except Exception:
            raise

    # =============================================================================
    # Enhanced Standard ViewSet Methods (Sync Operations)
    # =============================================================================

    def list(self, request, *args, **kwargs):
        """
        Enhanced list endpoint that supports multi-get via ?ids= parameter.

        - GET /api/model/                    # Standard list
        - GET /api/model/?ids=1,2,3          # Sync multi-get (small datasets)
        """
        ids_param = request.query_params.get("ids")
        if ids_param:
            return self._sync_multi_get(request, ids_param)

        # Standard list behavior
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Enhanced create endpoint that supports bulk operations.

        - POST /api/model/                                    # Standard single create (dict data)
        - POST /api/model/                                    # Bulk create (array data)
        - POST /api/model/?unique_fields=field1,field2       # Bulk upsert (array data)
        """
        unique_fields_param = request.query_params.get("unique_fields")

        if isinstance(request.data, list):
            # Array data - route based on unique_fields presence
            if unique_fields_param:
                unique_fields = self._parse_upsert_params(request)
                update_fields = self._get_payload_fields(request.data, unique_fields)
                return self._partial_upsert(unique_fields, update_fields, request.data)
            else:
                return self._handle_bulk_create(request)
        # Standard single create behavior
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Enhanced update endpoint that supports sync upsert via query params.

        - PUT /api/model/{id}/                               # Standard single update
        - PUT /api/model/?unique_fields=field1,field2       # Full replacement upsert
        """
        if request.query_params.get("unique_fields"):
            unique_fields = self._parse_upsert_params(request)
            update_fields = self._get_all_model_fields(unique_fields)
            return self._full_replace(unique_fields, update_fields, request.data)

        # Standard single update behavior
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Enhanced partial update endpoint that supports sync upsert via query params.

        - PATCH /api/model/{id}/                             # Standard single partial update
        - PATCH /api/model/?unique_fields=field1,field2     # Partial upsert (only provided fields)
        """
        if request.query_params.get("unique_fields"):
            unique_fields = self._parse_upsert_params(request)
            update_fields = self._get_payload_fields(request.data, unique_fields)
            return self._partial_upsert(unique_fields, update_fields, request.data)

        # Standard single partial update behavior
        return super().partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests on the base endpoint for upsert operations.

        DRF doesn't handle PATCH on base endpoints by default, so we add this method
        to support: PATCH /api/model/?unique_fields=field1,field2

        Requires:
        - unique_fields query parameter
        - Array or object data in request body
        - Performs partial upsert: creates new records or updates only provided fields
        """
        unique_fields = self._parse_upsert_params(request)
        update_fields = self._get_payload_fields(request.data, unique_fields)
        return self._partial_upsert(unique_fields, update_fields, request.data)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests on list endpoint for sync upsert.

        DRF doesn't handle PUT on list endpoints by default, so we add this method
        to support: PUT /api/model/?unique_fields=field1,field2

        Performs full replacement upsert: updates all fields (missing fields become null).
        """
        unique_fields = self._parse_upsert_params(request)
        update_fields = self._get_all_model_fields(unique_fields)
        return self._full_replace(unique_fields, update_fields, request.data)

    # =============================================================================
    # Sync Operation Implementations
    # =============================================================================

    def _parse_upsert_params(self, request):
        """
        Parse and validate upsert query parameters from request.

        Returns:
            list: unique_fields (the only param users should provide)
        """
        unique_fields_param = request.query_params.get("unique_fields")
        if not unique_fields_param:
            raise ValidationError("Missing required parameter: unique_fields")

        unique_fields = [f.strip() for f in unique_fields_param.split(",") if f.strip()]

        return unique_fields

    def _get_payload_fields(self, data, unique_fields):
        """
        Get fields to update from payload (PATCH behavior).
        Only update fields that are present in the data.
        """
        if isinstance(data, dict):
            payload_fields = set(data.keys())
        elif isinstance(data, list) and data:
            # For arrays, get union of all fields across all items
            payload_fields = set()
            for item in data:
                if isinstance(item, dict):
                    payload_fields.update(item.keys())
        else:
            return []

        # Remove unique_fields from update_fields (they're used for matching, not updating)
        unique_fields_set = set(unique_fields)
        return list(payload_fields - unique_fields_set)

    def _get_all_model_fields(self, unique_fields):
        """
        Get all model fields for full replacement (PUT behavior).
        Update all fields except unique_fields and auto-generated fields.
        """
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        # Get all model fields except unique_fields and auto fields
        model_fields = [f.name for f in model_class._meta.fields]
        auto_fields = {"id", "created_at", "updated_at"}
        unique_fields_set = set(unique_fields)

        return [field for field in model_fields if field not in unique_fields_set and field not in auto_fields]

    def _sync_multi_get(self, request, ids_param):
        """Handle multi-get for one or more items."""
        try:
            ids_list = [int(id_str.strip()) for id_str in ids_param.split(",")]
        except ValueError:
            raise ValidationError("Invalid ID format. Use comma-separated integers.")

        # Direct database query for all items
        queryset = self.get_queryset().filter(id__in=ids_list)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
                "operation_type": "multi_get",
            }
        )

    def _partial_upsert(self, unique_fields, update_fields, data):
        """
        Partial upsert: Update only specified fields, leave others untouched.
        PATCH semantics.
        """
        if isinstance(data, dict):
            return self._handle_single_upsert(data, update_fields, unique_fields)
        elif isinstance(data, list):
            return self._handle_array_upsert(data, update_fields, unique_fields)
        else:
            raise ValidationError("Expected dict or array data for upsert operations.")

    def _full_replace(self, unique_fields, update_fields, data):
        """
        Full replacement: Update all fields, missing fields → None/default.
        PUT semantics.
        """
        if isinstance(data, dict):
            return self._handle_single_upsert(data, update_fields, unique_fields)
        elif isinstance(data, list):
            return self._handle_array_upsert(data, update_fields, unique_fields)
        else:
            raise ValidationError("Expected dict or array data for upsert operations.")

    def _handle_single_upsert(self, payload, update_fields, unique_fields):
        """Handle single instance upsert using direct database operations."""
        if not unique_fields:
            raise ValidationError("unique_fields parameter is required for upsert operations")

        # Use direct database operations for single instance
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        try:
            # Try to find existing instance
            unique_filter = {}
            for field in unique_fields:
                if field in payload:
                    unique_filter[field] = payload[field]

            existing_instance = None
            if unique_filter:
                existing_instance = model_class.objects.filter(**unique_filter).first()

            if existing_instance:
                # Update existing instance
                if update_fields:
                    update_data = {k: v for k, v in payload.items() if k in update_fields}
                else:
                    update_data = {k: v for k, v in payload.items() if k not in unique_fields}

                for field, value in update_data.items():
                    setattr(existing_instance, field, value)
                existing_instance.save()

                serializer = serializer_class(existing_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Create new instance
                serializer = serializer_class(data=payload)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError(
                        {
                            "errors": [
                                {
                                    "index": 0,
                                    "error": str(serializer.errors),
                                    "data": payload,
                                }
                            ],
                        }
                    )

        except Exception as e:
            raise ValidationError(f"Direct upsert failed: {str(e)}")

    def _handle_bulk_create(self, request):
        """Handle bulk create operations using DRF's ListSerializer."""
        data = request.data
        serializer_class = self.get_serializer_class()
        model_class = serializer_class.Meta.model

        # Use DRF's ListSerializer for bulk validation and FK transformation
        list_serializer = serializer_class(data=data, many=True)

        if list_serializer.is_valid():
            # Get transformed instances (no DML - serializer only validates/transforms)
            instances = list_serializer.save()

            # ViewSet handles DML operations
            settings = get_bulk_drf_settings()
            batch_size = settings.get("optimized_batch_size", 2000)
            created_instances = model_class.objects.bulk_create(instances, batch_size=batch_size)

            # Serialize response
            response_serializer = serializer_class(created_instances, many=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Convert DRF's error format to our expected format
            errors = self._format_validation_errors(list_serializer.errors, data)
            raise ValidationError({"errors": errors, "error_count": len(errors)})

    def _handle_array_upsert(self, payload, update_fields, unique_fields):
        """
        Optimized bulk upsert with efficient batch processing.
        """

        # Step 1: Validate and prepare instances
        records, errors = self._validate_and_prepare_instances(payload)

        if errors:
            raise ValidationError({"errors": errors, "error_count": len(errors)})

        if not records:
            return Response([], status=status.HTTP_200_OK)

        # Step 2: Infer update fields if not provided
        if not update_fields:
            update_fields = self._get_update_fields(payload, unique_fields)

        # Step 3: Perform bulk upsert
        try:
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model
            upserted_instances = self._perform_bulk_upsert(records, unique_fields, update_fields, model_class)
            response = self._build_upsert_response(upserted_instances, serializer_class)
            return response

        except Exception as e:
            raise ValidationError(self._build_upsert_error_message(e, unique_fields, update_fields))

    def _format_validation_errors(self, serializer_errors, payload):
        """
        Format DRF validation errors into our expected format.

        Returns:
            list: Formatted error list
        """
        errors = []
        for index, item_errors in enumerate(serializer_errors):
            if item_errors:  # Only add if there are actual errors
                errors.append(
                    {
                        "index": index,
                        "error": item_errors,
                        "data": payload[index] if index < len(payload) else None,
                    }
                )
        return errors

    def _validate_and_prepare_instances(self, payload):
        """
        Orchestrate validation and instance preparation for upsert operations.

        Uses DRF's optimized bulk validation. FK transformation is delegated
        to the serializer where it belongs.

        Returns:
            tuple: (records, errors)
        """
        serializer_class = self.get_serializer_class()
        list_serializer = serializer_class(data=payload, many=True)

        start_time = time.perf_counter()

        is_valid = list_serializer.is_valid()

        elapsed = time.perf_counter() - start_time
        print(f"[TIMING] is_valid = list_serializer.is_valid(): {elapsed:.4f}s", file=sys.stderr)

        if is_valid:
            records = list_serializer.save()
            return records, []
        else:
            errors = self._format_validation_errors(list_serializer.errors, payload)
            return [], errors

    def _get_update_fields(self, payload, unique_fields):
        """Get update fields, auto-inferring if necessary."""
        update_fields = self._infer_update_fields(payload, unique_fields)
        if not update_fields:
            # Get all model fields except unique_fields and auto fields
            serializer_class = self.get_serializer_class()
            model_class = serializer_class.Meta.model
            model_fields = [f.name for f in model_class._meta.fields]
            auto_fields = ["id", "created_at", "updated_at"]
            unique_fields_set = set(unique_fields)
            update_fields = [field for field in model_fields if field not in unique_fields_set and field not in auto_fields]
        return update_fields

    def _perform_bulk_upsert(self, records, unique_fields, update_fields, model_class):
        """
        Perform the actual bulk upsert operation.

        Tries optimized bulk_create with update_conflicts first,
        falls back to separate create/update if needed.
        """
        settings = get_bulk_drf_settings()
        batch_size = settings.get("batch_size", 1000)

        try:
            result = model_class.objects.bulk_create(
                records,
                update_conflicts=True,
                update_fields=update_fields,
                unique_fields=unique_fields,
                batch_size=batch_size,
            )
            return result
        except Exception as e:
            raise ValidationError(f"Bulk upsert failed: {str(e)}")

    def _build_upsert_response(self, upserted_instances, serializer_class):
        """Build the response for a successful upsert operation."""
        if not upserted_instances:
            return Response([], status=status.HTTP_200_OK)

        serializer = serializer_class(upserted_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _build_upsert_error_message(self, exception, unique_fields, update_fields):
        """Build detailed error message for upsert failures."""
        error_message = str(exception).lower()

        if "unique constraint" in error_message or "unique_fields" in error_message:
            detailed_error = (
                "Unique constraint error during upsert. "
                f"Ensure that fields {unique_fields} form a unique constraint in your database. "
                "If you're using a multi-column unique constraint, make sure it's properly defined."
            )
        elif "cannot force an update" in error_message or "no primary key" in error_message:
            detailed_error = (
                "Upsert operation failed due to primary key conflicts. "
                "This usually occurs when trying to update existing records without proper primary key handling."
            )
        else:
            detailed_error = f"Bulk upsert failed: {str(exception)}"

        return {
            "error": "Bulk upsert failed",
            "details": detailed_error,
            "unique_fields": unique_fields,
            "update_fields": update_fields,
        }

    def _infer_update_fields(self, payload, unique_fields):
        """Auto-infer update fields from data payload."""
        if not payload:
            return []

        all_fields = set()
        for item in payload:
            if isinstance(item, dict):
                all_fields.update(item.keys())

        unique_fields_set = set(unique_fields)
        return list(all_fields - unique_fields_set)
