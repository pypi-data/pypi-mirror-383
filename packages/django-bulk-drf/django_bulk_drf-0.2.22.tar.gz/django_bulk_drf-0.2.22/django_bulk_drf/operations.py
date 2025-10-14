"""
Core bulk operation logic.

Provides operation classes for:
- Bulk create
- Bulk update
- Bulk upsert
- Bulk delete

Pure Django ORM, no DRF dependencies.
"""

from .results import BulkOperationResult
from .queries import BulkQueryBuilder, QueryOptimizer
from .utils import BatchProcessor, M2MHandler, build_unique_key
from .exceptions import ObjectNotFoundError
from .monitoring import get_monitor
from .signals import get_dispatcher
from .settings import bulk_settings


class BulkOperation:
    """
    Abstract base for all bulk operations.
    Encapsulates common setup and result handling.
    """

    def __init__(self, model, unique_fields=None, batch_size=None, context=None):
        """
        Initialize operation with configuration.

        Args:
            model: Django model class
            unique_fields: List of fields for matching (upsert/update)
            batch_size: Records per batch
            context: Additional context (user, request, etc.)
        """
        self.model = model
        self.unique_fields = unique_fields or ["id"]
        self.batch_size = batch_size or bulk_settings.default_batch_size
        self.context = context or {}

        self.result = BulkOperationResult()
        self.query_builder = BulkQueryBuilder(model, self.unique_fields)
        self.batch_processor = BatchProcessor(self.batch_size)
        self.m2m_handler = M2MHandler(model)

        # Get monitor and dispatcher from settings
        self.monitor = get_monitor()
        self.dispatcher = get_dispatcher()

    def execute(self, validated_data, m2m_data=None):
        """
        Execute the operation.
        Must be implemented by subclasses.

        Args:
            validated_data: List of validated data dicts
            m2m_data: Optional M2M data list

        Returns:
            BulkOperationResult
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def get_result(self):
        """
        Get operation result object.

        Returns:
            BulkOperationResult instance
        """
        return self.result
    
    def _get_serializer_class(self):
        """
        Extract serializer class from context.
        
        Returns:
            Serializer class or None
        """
        # Try to get from view context
        view = self.context.get('view')
        if view and hasattr(view, 'get_serializer_class'):
            return view.get_serializer_class()
        
        # Try to get directly from context
        return self.context.get('serializer_class')
    
    def _optimize_instances_for_serialization(self, instances):
        """
        Re-fetch instances with select_related/prefetch_related optimizations.
        
        This prevents N+1 queries when serializing the response by pre-loading
        all related objects (ForeignKeys, ManyToMany) in a single query or a few queries.
        
        Args:
            instances: List of model instances to optimize
            
        Returns:
            List of optimized instances with pre-loaded relations
        """
        if not instances:
            return instances
        
        # Get serializer class from context
        serializer_class = self._get_serializer_class()
        if not serializer_class:
            # No serializer, can't optimize - return as-is
            return instances
        
        # Extract PKs from instances
        instance_pks = [instance.pk for instance in instances if instance.pk is not None]
        if not instance_pks:
            return instances
        
        # Build optimized queryset
        queryset = self.model.objects.filter(pk__in=instance_pks)
        
        # Apply optimizations based on serializer
        optimizer = QueryOptimizer(serializer_class)
        queryset = optimizer.apply_optimizations(queryset)
        
        # Fetch all instances with optimizations applied
        optimized_instances = list(queryset)
        
        # Return in same order as original instances (preserve order)
        pk_to_instance = {inst.pk: inst for inst in optimized_instances}
        return [pk_to_instance.get(pk) for pk in instance_pks if pk in pk_to_instance]
    
    def _resolve_foreign_keys(self, validated_data):
        """
        Convert foreign key IDs to model instances efficiently.
        
        For fields that are ForeignKey relations, if the validated_data contains
        integer IDs (from PrimaryKeyRelatedField), we need to convert them to
        actual model instances before creating/updating Django model objects.
        
        This method does this in a single query per FK field (no N+1 queries).
        
        Args:
            validated_data: List of validated data dicts
            
        Returns:
            List of validated data dicts with FK IDs replaced by instances
        """
        if not validated_data:
            return validated_data
        
        # Identify foreign key fields in the model
        fk_fields = {}
        for field in self.model._meta.get_fields():
            if field.many_to_one and field.concrete:  # ForeignKey
                fk_fields[field.name] = field
        
        if not fk_fields:
            # No foreign keys to resolve
            return validated_data
        
        # Collect all FK IDs that need to be fetched (grouped by field)
        fk_ids_to_fetch = {field_name: set() for field_name in fk_fields.keys()}
        
        for data in validated_data:
            for field_name, field in fk_fields.items():
                if field_name in data:
                    value = data[field_name]
                    # Check if it's an integer ID (not already a model instance)
                    if isinstance(value, int):
                        fk_ids_to_fetch[field_name].add(value)
        
        # Fetch all FK instances in a single query per field
        fk_instances = {}
        for field_name, ids in fk_ids_to_fetch.items():
            if ids:
                field = fk_fields[field_name]
                related_model = field.related_model
                # Single query to fetch all instances for this FK field
                instances = related_model.objects.filter(pk__in=ids)
                fk_instances[field_name] = {instance.pk: instance for instance in instances}
        
        # Replace integer IDs with actual instances in validated_data
        resolved_data = []
        for data in validated_data:
            resolved_item = data.copy()
            for field_name, field in fk_fields.items():
                if field_name in resolved_item:
                    value = resolved_item[field_name]
                    # Replace integer ID with instance
                    if isinstance(value, int) and field_name in fk_instances:
                        instance = fk_instances[field_name].get(value)
                        if instance is not None:
                            resolved_item[field_name] = instance
                        # If instance not found, leave the ID as-is and let Django raise error
            resolved_data.append(resolved_item)
        
        return resolved_data


class BulkCreateOperation(BulkOperation):
    """
    Bulk create operation using Model.objects.bulk_create().
    """

    def execute(self, validated_data, m2m_data=None):
        """
        Execute bulk create.

        Args:
            validated_data: List of validated data dicts
            m2m_data: Optional list of M2M data per item

        Returns:
            BulkOperationResult
        """
        if not validated_data:
            return self.result

        with self.monitor.monitor_operation("create", len(validated_data)):
            # Prepare instances
            instances = self._prepare_instances(validated_data)

            # Batch create
            created_instances = self._batch_create(instances)

            # Optimize instances for serialization (prevent N+1 queries)
            # Re-fetch with select_related/prefetch_related
            created_instances = self._optimize_instances_for_serialization(created_instances)

            # Set M2M relations if provided
            if m2m_data and bulk_settings.enable_m2m_handling:
                self.m2m_handler.set_m2m_relations(created_instances, m2m_data)

            # Add to result
            for instance in created_instances:
                self.result.add_created(instance)

            # Dispatch signals
            self.dispatcher.send_post_bulk_create(sender=self.model, instances=created_instances)

        return self.result

    def _prepare_instances(self, validated_data):
        """
        Convert validated dicts to unsaved model instances.

        Args:
            validated_data: List of validated data dicts

        Returns:
            List of unsaved model instances
        """
        # Resolve foreign key IDs to instances (no N+1 queries)
        resolved_data = self._resolve_foreign_keys(validated_data)
        
        instances = []
        for data in resolved_data:
            instance = self.model(**data)
            instances.append(instance)
        return instances

    def _batch_create(self, instances):
        """
        Execute bulk_create in batches.

        Args:
            instances: List of model instances

        Returns:
            List of created instances with IDs
        """
        all_created = []

        for batch in self.batch_processor.chunk_list(instances):
            created = self.model.objects.bulk_create(batch, batch_size=self.batch_size)
            all_created.extend(created)

        return all_created


class BulkUpdateOperation(BulkOperation):
    """
    Bulk update operation using Model.objects.bulk_update().
    Requires all objects to exist.
    """

    def execute(self, validated_data, m2m_data=None):
        """
        Execute bulk update.

        Args:
            validated_data: List of validated data dicts
            m2m_data: Optional list of M2M data per item

        Returns:
            BulkOperationResult
        """
        if not validated_data:
            return self.result

        with self.monitor.monitor_operation("update", len(validated_data)):
            # Fetch existing objects
            existing = self._fetch_existing(validated_data)

            # Validate all exist
            self._validate_all_exist(validated_data, existing)

            # Apply updates
            instances, update_fields = self._apply_updates(existing, validated_data)

            # Batch update
            self._batch_update(instances, update_fields)

            # Optimize instances for serialization (prevent N+1 queries)
            # Re-fetch with select_related/prefetch_related
            instances = self._optimize_instances_for_serialization(instances)

            # Set M2M relations if provided
            if m2m_data and bulk_settings.enable_m2m_handling:
                self.m2m_handler.set_m2m_relations(instances, m2m_data)

            # Add to result
            for instance in instances:
                self.result.add_updated(instance)

            # Dispatch signals
            self.dispatcher.send_post_bulk_update(sender=self.model, instances=instances)

        return self.result

    def _fetch_existing(self, validated_data):
        """
        Single query to fetch all existing objects.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Dict mapping unique_key → instance
        """
        queryset = self.model.objects.all()
        return self.query_builder.fetch_by_unique_fields(queryset, validated_data)

    def _validate_all_exist(self, validated_data, existing):
        """
        Ensure all items in validated_data match existing objects.

        Args:
            validated_data: List of validated data dicts
            existing: Dict of existing instances by unique key

        Raises:
            ObjectNotFoundError: If any objects missing
        """
        missing_keys = []

        for data in validated_data:
            key = build_unique_key(data, self.unique_fields)
            if key not in existing:
                missing_keys.append(dict(zip(self.unique_fields, key)))

        if missing_keys:
            raise ObjectNotFoundError(missing_keys)

    def _apply_updates(self, existing, validated_data):
        """
        Apply validated_data updates to existing instances.

        Args:
            existing: Dict of existing instances by unique key
            validated_data: List of validated data dicts

        Returns:
            Tuple of (instances, update_fields)
        """
        # Resolve foreign key IDs to instances (no N+1 queries)
        resolved_data = self._resolve_foreign_keys(validated_data)
        
        instances = []
        all_fields = set()

        for data in resolved_data:
            key = build_unique_key(data, self.unique_fields)
            instance = existing[key]

            # Apply updates
            for field, value in data.items():
                if field not in self.unique_fields:  # Don't update unique fields
                    setattr(instance, field, value)
                    all_fields.add(field)

            instances.append(instance)

        # Return union of all fields being updated
        update_fields = list(all_fields)
        return instances, update_fields

    def _batch_update(self, instances, update_fields):
        """
        Execute bulk_update in batches.

        Args:
            instances: List of instances to update
            update_fields: List of fields to update
        """
        if not update_fields:
            return

        for batch in self.batch_processor.chunk_list(instances):
            self.model.objects.bulk_update(batch, update_fields, batch_size=self.batch_size)


class BulkUpsertOperation(BulkOperation):
    """
    Bulk upsert (create or update) operation.
    Combines bulk_create and bulk_update.
    """

    def execute(self, validated_data, m2m_data=None):
        """
        Execute bulk upsert.

        Args:
            validated_data: List of validated data dicts
            m2m_data: Optional list of M2M data per item

        Returns:
            BulkOperationResult
        """
        if not validated_data:
            return self.result

        with self.monitor.monitor_operation("upsert", len(validated_data)):
            # Fetch existing objects
            existing = self._fetch_existing(validated_data)

            # Partition data into create vs update
            create_data, update_data, create_m2m, update_m2m = self._partition_data(validated_data, existing, m2m_data)

            # Create new objects
            created_instances = []
            if create_data:
                created_instances = self._create_new(create_data, create_m2m)
                # Optimize created instances for serialization
                created_instances = self._optimize_instances_for_serialization(created_instances)

            # Update existing objects
            updated_instances = []
            if update_data:
                updated_instances = self._update_existing(existing, update_data, update_m2m)
                # Optimize updated instances for serialization
                updated_instances = self._optimize_instances_for_serialization(updated_instances)

            # Add to result
            for instance in created_instances:
                self.result.add_created(instance)
            for instance in updated_instances:
                self.result.add_updated(instance)

            # Dispatch signals
            self.dispatcher.send_post_bulk_upsert(
                sender=self.model, created_instances=created_instances, updated_instances=updated_instances
            )

        return self.result

    def _fetch_existing(self, validated_data):
        """
        Fetch existing objects that match unique_fields.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Dict mapping unique_key → instance
        """
        queryset = self.model.objects.all()
        return self.query_builder.fetch_by_unique_fields(queryset, validated_data)

    def _partition_data(self, validated_data, existing, m2m_data):
        """
        Split validated_data into create vs update.

        Args:
            validated_data: List of validated data dicts
            existing: Dict of existing instances by unique key
            m2m_data: Optional list of M2M data per item

        Returns:
            Tuple of (create_data, update_data, create_m2m, update_m2m)
        """
        create_data = []
        update_data = []
        create_m2m = []
        update_m2m = []

        for idx, data in enumerate(validated_data):
            key = build_unique_key(data, self.unique_fields)

            if key in existing:
                # Update existing
                update_data.append(data)
                if m2m_data:
                    update_m2m.append(m2m_data[idx])
            else:
                # Create new
                create_data.append(data)
                if m2m_data:
                    create_m2m.append(m2m_data[idx])

        return create_data, update_data, create_m2m, update_m2m

    def _create_new(self, create_data, create_m2m):
        """
        Use BulkCreateOperation to create new objects.

        Args:
            create_data: List of data for new objects
            create_m2m: List of M2M data for new objects

        Returns:
            List of created instances
        """
        create_op = BulkCreateOperation(self.model, self.unique_fields, self.batch_size, self.context)
        result = create_op.execute(create_data, create_m2m)
        return result.created

    def _update_existing(self, existing, update_data, update_m2m):
        """
        Update existing objects using partial update logic.

        Args:
            existing: Dict of existing instances by unique key
            update_data: List of data for updates
            update_m2m: List of M2M data for updates

        Returns:
            List of updated instances
        """
        # Resolve foreign key IDs to instances (no N+1 queries)
        resolved_data = self._resolve_foreign_keys(update_data)
        
        instances = []
        all_fields = set()

        for data in resolved_data:
            key = build_unique_key(data, self.unique_fields)
            instance = existing[key]

            # Apply partial updates (only provided fields)
            for field, value in data.items():
                if field not in self.unique_fields:
                    setattr(instance, field, value)
                    all_fields.add(field)

            instances.append(instance)

        # Batch update
        if instances and all_fields:
            update_fields = list(all_fields)
            for batch in self.batch_processor.chunk_list(instances):
                self.model.objects.bulk_update(batch, update_fields, batch_size=self.batch_size)

        # Set M2M relations
        if update_m2m and bulk_settings.enable_m2m_handling:
            self.m2m_handler.set_m2m_relations(instances, update_m2m)

        return instances


class BulkDeleteOperation(BulkOperation):
    """
    Bulk delete operation using QuerySet.delete().
    """

    def execute(self, validated_data, m2m_data=None):
        """
        Execute bulk delete.

        Args:
            validated_data: List of validated data dicts with unique field values
            m2m_data: Not used for delete operations

        Returns:
            BulkOperationResult
        """
        if not validated_data:
            return self.result

        with self.monitor.monitor_operation("delete", len(validated_data)):
            # Build queryset
            queryset = self._build_queryset(validated_data)

            # Execute delete
            count = self._batch_delete(queryset)

            # Set result
            self.result.set_deleted_count(count)

            # Dispatch signals
            self.dispatcher.send_post_bulk_delete(sender=self.model, count=count, filters={"unique_fields": self.unique_fields})

        return self.result

    def _build_queryset(self, validated_data):
        """
        Build queryset matching unique_fields in validated_data.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Filtered queryset
        """
        q_filter = self.query_builder.build_lookup_filter(validated_data)
        return self.model.objects.filter(q_filter)

    def _batch_delete(self, queryset):
        """
        Execute delete.

        Args:
            queryset: Queryset to delete

        Returns:
            Total deleted count
        """
        deleted_count, _ = queryset.delete()
        return deleted_count
