"""
Granular mixins for bulk operations.

Provides optional mixins for adding specific bulk operations to views.
Can be used independently of BulkModelViewSet.
"""

from rest_framework import status
from rest_framework.response import Response

from .operations import BulkDeleteOperation
from .validators import validate_bulk_request, validate_for_delete
from .settings import bulk_settings
from .transactions import BulkTransactionManager


class BulkCreateMixin:
    """
    Adds bulk create capability to a view.
    Can be used independently of BulkModelViewSet.
    """

    def create(self, request, *args, **kwargs):
        """
        Override create to handle bulk.
        Detects list vs. single object automatically.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        is_bulk = isinstance(request.data, list)

        if not is_bulk:
            # Standard single create
            return super().create(request, *args, **kwargs)

        # Bulk create
        return self._bulk_create(request)

    def _bulk_create(self, request):
        """
        Handle bulk create.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        # Validate batch size
        validate_bulk_request(request.data, getattr(self, "unique_fields", ["id"]), bulk_settings.max_batch_size)

        # Get serializer with many=True
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # Execute with transaction
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            self.perform_create(serializer)

        # Format response
        instances = serializer.instance if isinstance(serializer.instance, list) else [serializer.instance]

        data = {"created": len(instances), "updated": 0, "failed": 0, "data": serializer.data}

        return Response(data, status=status.HTTP_201_CREATED)


class BulkUpdateMixin:
    """
    Adds bulk update capability.
    PUT on collection endpoint.
    """

    def update(self, request, *args, **kwargs):
        """
        Override update to handle bulk.
        Requires unique_fields in each object.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Check if detail endpoint
        if self.kwargs.get(self.lookup_field):
            return super().update(request, *args, **kwargs)

        # Check if bulk request
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk update requires a list of objects")

        return self._bulk_update(request, partial=False)

    def _bulk_update(self, request, partial=False):
        """
        Handle bulk update.

        Args:
            request: HTTP request
            partial: Whether partial update

        Returns:
            Response
        """
        # Get serializer with many=True
        serializer = self.get_serializer(data=request.data, many=True, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Execute update
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            if hasattr(serializer, "update"):
                instances = serializer.update(serializer.validated_data)
            else:
                instances = serializer.save()

        # Format response
        instances = instances if isinstance(instances, list) else [instances]
        response_serializer = self.get_serializer(instances, many=True)

        data = {"created": 0, "updated": len(instances), "failed": 0, "data": response_serializer.data}

        return Response(data, status=status.HTTP_200_OK)


class BulkUpsertMixin:
    """
    Adds bulk upsert capability.
    PATCH on collection endpoint.
    """

    def partial_update(self, request, *args, **kwargs):
        """
        Override partial_update to handle bulk upsert.
        Creates or updates based on unique_fields.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Check if detail endpoint
        if self.kwargs.get(self.lookup_field):
            return super().partial_update(request, *args, **kwargs)

        # Check if bulk request
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk upsert requires a list of objects")

        return self._bulk_upsert(request)

    def _bulk_upsert(self, request):
        """
        Handle bulk upsert.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        # Get serializer with many=True
        serializer = self.get_serializer(data=request.data, many=True, partial=True)
        serializer.is_valid(raise_exception=True)

        # Execute upsert
        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            if hasattr(serializer, "upsert"):
                instances = serializer.upsert(serializer.validated_data)
            else:
                instances = serializer.save()

        # Format response
        instances = instances if isinstance(instances, list) else [instances]
        response_serializer = self.get_serializer(instances, many=True)

        data = {
            "created": 0,  # Would need operation result to separate
            "updated": len(instances),
            "failed": 0,
            "data": response_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)


class BulkDestroyMixin:
    """
    Adds bulk delete capability.
    DELETE on collection endpoint.
    """

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to handle bulk.
        Payload contains unique_field identifiers.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response
        """
        # Check if detail endpoint
        if self.kwargs.get(self.lookup_field):
            return super().destroy(request, *args, **kwargs)

        # Check if bulk request
        if not isinstance(request.data, list):
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Bulk delete requires a list of objects with unique field identifiers")

        return self._bulk_destroy(request)

    def _bulk_destroy(self, request):
        """
        Handle bulk destroy.

        Args:
            request: HTTP request

        Returns:
            Response
        """
        unique_fields = getattr(self, "unique_fields", ["id"])

        # Validate delete request
        validate_for_delete(request.data, unique_fields)

        # Execute delete operation
        model = self.get_queryset().model
        batch_size = getattr(self, "batch_size", bulk_settings.default_batch_size)

        operation = BulkDeleteOperation(
            model=model, unique_fields=unique_fields, batch_size=batch_size, context={"request": request, "view": self}
        )

        transaction_manager = BulkTransactionManager(
            atomic=bulk_settings.atomic_operations, failure_strategy=bulk_settings.partial_failure_strategy
        )

        with transaction_manager.execute():
            result = operation.execute(request.data)

        # Format response
        data = {"deleted": result.deleted}

        return Response(data, status=status.HTTP_200_OK)
