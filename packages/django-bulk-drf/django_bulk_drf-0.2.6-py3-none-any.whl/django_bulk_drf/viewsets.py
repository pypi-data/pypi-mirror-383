"""
ViewSet layer for bulk operations.

Provides:
- BulkOperationMixin: Configuration and context injection
- BulkModelViewSet: Complete viewset with bulk operations
"""

import time
import logging
from django.db import connection, reset_queries
from rest_framework import status, viewsets
from rest_framework.response import Response

from .operations import BulkDeleteOperation
from .queries import build_filter_for_delete
from .results import BulkResponseFormatter
from .settings import bulk_settings
from .transactions import BulkTransactionManager
from .validators import validate_bulk_request, validate_for_delete

logger = logging.getLogger(__name__)


class QueryMonitoringMixin:
    def _monitor_queries(self, operation_name, func, *args, **kwargs):
        """Monitor database queries for a specific operation."""
        reset_queries()
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        query_count = len(connection.queries)
        duration = end_time - start_time

        logger.info(f"\n=== {operation_name} Performance ===")
        logger.info(f"Duration: {duration:.3f} seconds")
        logger.info(f"Query Count: {query_count}")
        logger.info(f"Queries per second: {query_count / duration:.1f}")

        # Log slow queries
        for query in connection.queries:
            if float(query["time"]) > 0.1:  # Queries taking more than 100ms
                logger.info(f"SLOW QUERY ({query['time']}s): {query['sql'][:100]}...")

        return result


class BulkOperationMixin:
    """
    Configuration and context injection for bulk operations.
    """

    # Class attributes (can be overridden)
    unique_fields = ["id"]  # Fields for upsert matching
    batch_size = None  # Records per database batch (uses settings default if None)
    allow_singular = None  # Allow single-object requests (uses settings default if None)

    def get_unique_fields(self):
        """
        Get unique fields for this request.
        Can be overridden to support per-request configuration.

        Returns:
            List of unique field names
        """
        return self.unique_fields

    def get_batch_size(self):
        """
        Get batch size for this request.
        Respects MAX_BATCH_SIZE setting.

        Returns:
            Batch size integer
        """
        batch_size = self.batch_size
        if batch_size is None:
            batch_size = bulk_settings.default_batch_size

        # Ensure doesn't exceed max
        max_batch_size = bulk_settings.max_batch_size
        return min(batch_size, max_batch_size)

    def get_allow_singular(self):
        """
        Get whether singular requests are allowed.

        Returns:
            Boolean
        """
        if self.allow_singular is not None:
            return self.allow_singular
        return bulk_settings.allow_singular

    def get_serializer_context(self):
        """
        Inject bulk configuration into serializer context.

        Returns:
            Dict with context
        """
        context = super().get_serializer_context()

        # Add bulk-specific context
        context.update(
            {
                "unique_fields": self.get_unique_fields(),
                "batch_size": self.get_batch_size(),
                "operation": self._detect_operation(),
                "prefer_minimal": self._get_prefer_minimal(),
            }
        )

        return context

    def _detect_operation(self):
        """
        Map HTTP method to operation type.

        Returns:
            Operation type string
        """
        method = self.request.method if hasattr(self, "request") else None

        mapping = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "upsert",
            "DELETE": "delete",
        }

        return mapping.get(method, "unknown")

    def _get_prefer_minimal(self):
        """
        Check if minimal response is preferred.
        Checks Prefer header and settings.

        Returns:
            Boolean
        """
        if not hasattr(self, "request"):
            return bulk_settings.prefer_minimal_response

        # Check Prefer header
        prefer_header = self.request.headers.get("Prefer", "")
        if "minimal" in prefer_header.lower():
            return True

        return bulk_settings.prefer_minimal_response

    def _is_bulk_request(self):
        """
        Determine if request is bulk or single.

        Returns:
            Boolean
        """
        # Check if detail endpoint (has lookup field in kwargs)
        if self.kwargs.get(self.lookup_field):
            return False

        # Check if data is a list
        if hasattr(self, "request") and isinstance(self.request.data, list):
            return True

        return False

    def _check_bulk_or_single(self, request):
        """
        Enforce request shape based on configuration.

        Args:
            request: HTTP request

        Raises:
            ValidationError: If request shape not allowed
        """
        is_list = isinstance(request.data, list)
        allow_singular = self.get_allow_singular()

        if is_list and not allow_singular:
            # List provided but only singular allowed
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk operations not allowed on this endpoint")

    def _build_delete_queryset(self, data):
        """
        Build queryset for bulk delete from request data.

        Args:
            data: List of dicts with unique field values

        Returns:
            Filtered queryset
        """
        model = self.get_queryset().model
        unique_fields = self.get_unique_fields()

        q_filter = build_filter_for_delete(model, unique_fields, data)
        return self.get_queryset().filter(q_filter)


class BulkModelViewSet(BulkOperationMixin, QueryMonitoringMixin, viewsets.ModelViewSet):
    """
    Complete viewset with bulk operations on collection endpoints.
    Detail endpoints remain standard DRF behavior.
    """

    def get_serializer(self, *args, **kwargs):
        """
        Auto-detect many=True from request data structure.
        Injects serializer context with bulk configuration.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Serializer instance
        """
        # Auto-detect many=True for bulk operations
        if self._is_bulk_request() and "many" not in kwargs:
            kwargs["many"] = True

        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        POST /items/

        Handles both:
        - Single: {"name": "Item"}
        - Bulk: [{"name": "Item 1"}, {"name": "Item 2"}]

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        is_bulk = self._is_bulk_request()

        if is_bulk:
            return self._handle_bulk_create(request)
        else:
            # Standard DRF single create
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        PUT /items/ or PUT /items/{id}/

        Collection (no lookup): Bulk update
        Detail (with lookup): Standard single update

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        if self.kwargs.get(self.lookup_field):
            # Detail endpoint - standard update
            return super().update(request, *args, **kwargs)

        # Collection endpoint - bulk update
        return self._handle_bulk_update(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /items/ or PATCH /items/{id}/

        Collection (no pk): Bulk upsert
        Detail (with pk): Standard single partial update

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        if self.kwargs.get(self.lookup_field):
            # Detail endpoint - standard partial update
            return super().partial_update(request, *args, **kwargs)

        # Collection endpoint - bulk upsert
        return self._handle_bulk_upsert(request)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /items/ or DELETE /items/{id}/

        Collection: Bulk delete by unique_fields
        Detail: Standard single delete

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        if self.kwargs.get(self.lookup_field):
            # Detail endpoint - standard delete
            return super().destroy(request, *args, **kwargs)

        # Collection endpoint - bulk delete
        return self._handle_bulk_destroy(request)

    def perform_create(self, serializer):
        """
        Hook for custom create logic.
        Called after validation, before save.

        Args:
            serializer: Serializer instance
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Hook for custom update logic.

        Args:
            serializer: Serializer instance
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Hook for custom delete logic.

        Args:
            instance: Instance to delete (or queryset for bulk)
        """
        if hasattr(instance, "delete"):
            instance.delete()

    def _handle_bulk_create(self, request):
        """
        Internal handler for bulk create operations.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        # Validate batch size
        validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

        # Get serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Execute with transaction
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            self.perform_create(serializer)

        # Format response using BulkOperationResult if available
        result = getattr(serializer, "bulk_result", None)
        prefer_minimal = self._get_prefer_minimal()
        if result is not None:
            data = BulkResponseFormatter.format_success(result, serializer=self.get_serializer, prefer_minimal=prefer_minimal)
            return Response(data, status=status.HTTP_201_CREATED)

        # Fallback to counts from serializer
        instances = serializer.instance if isinstance(serializer.instance, list) else [serializer.instance]
        data = {"created": len(instances), "updated": 0, "failed": 0, "data": serializer.data if not prefer_minimal else None}
        if prefer_minimal and "data" in data:
            del data["data"]
        return Response(data, status=status.HTTP_201_CREATED)

    def _handle_bulk_update(self, request, partial=False):
        """
        Internal handler for bulk update operations.

        Args:
            request: HTTP request
            partial: Whether this is a partial update

        Returns:
            Response
        """
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk update requires a list of objects")

        # Validate bulk request
        validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

        # Get serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Execute update
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            # Call serializer's update method (for bulk)
            if hasattr(serializer, "update"):
                instances = serializer.update(serializer.validated_data)
            else:
                instances = serializer.save()

        # Format response using BulkOperationResult if available
        result = getattr(serializer, "bulk_result", None)
        prefer_minimal = self._get_prefer_minimal()
        if result is not None:
            if result.has_errors() and result.has_successes():
                data = BulkResponseFormatter.format_partial_success(result, serializer=self.get_serializer, prefer_minimal=prefer_minimal)
                return Response(data, status=status.HTTP_207_MULTI_STATUS)
            elif result.has_errors() and not result.has_successes():
                data = BulkResponseFormatter.format_error(result.errors)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = BulkResponseFormatter.format_success(result, serializer=self.get_serializer, prefer_minimal=prefer_minimal)
                return Response(data, status=status.HTTP_200_OK)

        # Fallback to instance counts
        instances = instances if isinstance(instances, list) else [instances]
        if prefer_minimal:
            data = {"created": 0, "updated": len(instances), "failed": 0}
            return Response(data, status=status.HTTP_200_OK)
        response_serializer = self.get_serializer(instances, many=True)
        data = {"created": 0, "updated": len(instances), "failed": 0, "data": response_serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def _handle_bulk_upsert(self, request):
        """
        Internal handler for bulk upsert.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk upsert requires a list of objects")

        # Validate bulk request
        validate_bulk_request(request.data, self.get_unique_fields(), bulk_settings.max_batch_size)

        # Get serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Execute upsert
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            # Call serializer's upsert method
            if hasattr(serializer, "upsert"):
                instances = serializer.upsert(serializer.validated_data)
            else:
                instances = serializer.save()

        # Format response using BulkOperationResult if available
        result = getattr(serializer, "bulk_result", None)
        prefer_minimal = self._get_prefer_minimal()
        if result is not None:
            if result.has_errors() and result.has_successes():
                data = BulkResponseFormatter.format_partial_success(result, serializer=self.get_serializer, prefer_minimal=prefer_minimal)
                return Response(data, status=status.HTTP_207_MULTI_STATUS)
            elif result.has_errors() and not result.has_successes():
                data = BulkResponseFormatter.format_error(result.errors)
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = BulkResponseFormatter.format_success(result, serializer=self.get_serializer, prefer_minimal=prefer_minimal)
                return Response(data, status=status.HTTP_200_OK)

        # Fallback to instance counts
        instances = instances if isinstance(instances, list) else [instances]
        if prefer_minimal:
            data = {"created": 0, "updated": len(instances), "failed": 0}
            return Response(data, status=status.HTTP_200_OK)
        response_serializer = self.get_serializer(instances, many=True)
        data = {"created": 0, "updated": len(instances), "failed": 0, "data": response_serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def _handle_bulk_destroy(self, request):
        """
        Internal handler for bulk delete.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk delete requires a list of objects with unique field identifiers")

        # Validate delete request
        validate_for_delete(request.data, self.get_unique_fields())

        # Execute delete operation
        model = self.get_queryset().model
        operation = BulkDeleteOperation(
            model=model,
            unique_fields=self.get_unique_fields(),
            batch_size=self.get_batch_size(),
            context={"request": request, "view": self},
        )

        # Validate data (simple structure validation)
        validated_data = request.data

        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            result = operation.execute(validated_data)

        # Format response
        data = {"deleted": result.deleted}

        return Response(data, status=status.HTTP_200_OK)
