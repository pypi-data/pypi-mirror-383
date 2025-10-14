"""
Field conversion and M2M handling utilities.

Provides utilities for:
- FK → FK_id field conversion with SlugField support
- M2M relationship extraction and bulk setting
- Batch processing helpers
"""

from django.db import models


class FieldConverter:
    """
    Converts between different field representations.
    Handles FK → FK_id conversion with SlugField support.
    """

    @staticmethod
    def fk_to_id(field_name):
        """
        Convert FK field name to _id field.

        Args:
            field_name: Foreign key field name (e.g., 'user')

        Returns:
            ID field name (e.g., 'user_id')
        """
        return f"{field_name}_id"

    @staticmethod
    def get_model_fk_fields(model):
        """
        Get all ForeignKey field names from model.

        Args:
            model: Django model class

        Returns:
            List of FK field names
        """
        fk_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                fk_fields.append(field.name)
        return fk_fields

    @staticmethod
    def get_fk_field_info(model, fk_field_name):
        """
        Get detailed information about a FK field.

        Args:
            model: Django model class
            fk_field_name: Name of the FK field

        Returns:
            Dict with field info (related_model, to_field, etc.)
        """
        try:
            field = model._meta.get_field(fk_field_name)
            if not isinstance(field, models.ForeignKey):
                return None

            return {
                "field": field,
                "related_model": field.related_model,
                "to_field": field.to_field or "pk",
                "db_column": field.db_column or f"{fk_field_name}_id",
            }
        except Exception:
            return None

    @staticmethod
    def is_slug_backed_fk(model, fk_field_name):
        """
        Return True if the fk_field targets a unique SlugField.

        Args:
            model: Django model class
            fk_field_name: Name of the FK field

        Returns:
            Boolean indicating if FK is slug-backed
        """
        field_info = FieldConverter.get_fk_field_info(model, fk_field_name)
        if not field_info:
            return False

        to_field = field_info["to_field"]
        if to_field == "pk":
            return False

        related_model = field_info["related_model"]
        try:
            related_field = related_model._meta.get_field(to_field)
            return isinstance(related_field, models.SlugField)
        except Exception:
            return False

    @staticmethod
    def collect_fk_identifiers(validated_data, model):
        """
        Scan the batch and collect identifiers for each FK field.

        Args:
            validated_data: List of validated data dicts
            model: Django model class

        Returns:
            Dict mapping fk_field_name to set of identifiers
        """
        fk_fields = FieldConverter.get_model_fk_fields(model)
        identifiers_map = {fk_field: set() for fk_field in fk_fields}

        for data in validated_data:
            for fk_field in fk_fields:
                if fk_field in data and data[fk_field] is not None:
                    identifiers_map[fk_field].add(data[fk_field])

        return {k: v for k, v in identifiers_map.items() if v}

    @staticmethod
    def resolve_fk_ids(model, fk_field_name, identifiers, slug_field=None):
        """
        Resolve identifiers to primary keys in a single query.

        Args:
            model: Django model class
            fk_field_name: Name of the FK field
            identifiers: Set/list of identifiers (ints or strings)
            slug_field: Optional slug field name to use for string identifiers (from serializer)

        Returns:
            Dict mapping identifier to pk
        """
        field_info = FieldConverter.get_fk_field_info(model, fk_field_name)
        if not field_info:
            return {}

        related_model = field_info["related_model"]
        to_field = field_info["to_field"]

        # Check if all identifiers are integers (PKs)
        all_ints = all(isinstance(i, int) for i in identifiers)
        
        # Check if all identifiers are strings (slugs)
        all_strings = all(isinstance(i, str) for i in identifiers)

        if all_ints and to_field == "pk" and not slug_field:
            # Direct PK lookup - no resolution needed
            return {pk: pk for pk in identifiers}

        # Determine which field to use for lookup
        lookup_field = to_field
        if slug_field:
            # Serializer specified a slug field - use that instead of model's to_field
            lookup_field = slug_field
        elif all_strings and to_field == "pk":
            # We have string identifiers but no slug_field specified - can't resolve
            raise ValueError(
                f"Cannot resolve string identifiers for FK field '{fk_field_name}' "
                f"without a slug_field. Please use BulkSlugRelatedField with slug_field parameter, "
                f"or set to_field on the model's ForeignKey."
            )

        # Query for resolution
        if lookup_field == "pk":
            queryset = related_model.objects.filter(pk__in=identifiers)
            return {obj.pk: obj.pk for obj in queryset}
        else:
            # Lookup by slug/to_field
            lookup = {f"{lookup_field}__in": identifiers}
            queryset = related_model.objects.filter(**lookup)
            return {getattr(obj, lookup_field): obj.pk for obj in queryset}

    @staticmethod
    def convert_related_fields_batch(validated_data, model, serializer=None):
        """
        Perform batched FK → _id conversion for the entire payload.
        No per-item database queries.

        Args:
            validated_data: List of validated data dicts
            model: Django model class
            serializer: Optional serializer instance to extract field metadata

        Returns:
            Updated validated_data with FK fields converted to _id fields
        """
        # Extract FK field metadata from serializer
        fk_metadata = {}
        if serializer:
            # Lazy import to avoid circular dependency
            from .serializers import BulkSlugRelatedField
            for field_name, field in serializer.fields.items():
                if isinstance(field, BulkSlugRelatedField):
                    fk_metadata[field_name] = {
                        'slug_field': field.slug_field
                    }
        
        # Collect all FK identifiers
        identifiers_map = FieldConverter.collect_fk_identifiers(validated_data, model)

        # Resolve each FK field in a single query
        resolution_maps = {}
        for fk_field, identifiers in identifiers_map.items():
            if identifiers:
                slug_field = fk_metadata.get(fk_field, {}).get('slug_field')
                resolution_maps[fk_field] = FieldConverter.resolve_fk_ids(
                    model, fk_field, identifiers, slug_field=slug_field
                )

        # Apply conversions to each data item
        for data in validated_data:
            for fk_field, resolution_map in resolution_maps.items():
                if fk_field in data and data[fk_field] is not None:
                    identifier = data[fk_field]
                    if identifier in resolution_map:
                        # Convert to _id field
                        id_field = FieldConverter.fk_to_id(fk_field)
                        data[id_field] = resolution_map[identifier]
                        # Remove original FK field
                        del data[fk_field]

        return validated_data

    @staticmethod
    def get_model_m2m_fields(model):
        """
        Get all ManyToMany field names from model.

        Args:
            model: Django model class

        Returns:
            List of M2M field names
        """
        m2m_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, models.ManyToManyField):
                m2m_fields.append(field.name)
        return m2m_fields


class M2MHandler:
    """
    Handles ManyToMany relationships for bulk operations.
    M2M relations must be set after object creation.
    """

    def __init__(self, model):
        """
        Initialize with model class.

        Args:
            model: Django model class
        """
        self.model = model
        self.m2m_fields = FieldConverter.get_model_m2m_fields(model)

    def extract_m2m_data(self, validated_data):
        """
        Remove M2M fields from validated_data.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Tuple of (cleaned_data, m2m_data_list)
            where m2m_data_list is a list of M2M data per item
        """
        m2m_data_list = []

        for data in validated_data:
            item_m2m = {}
            for field_name in self.m2m_fields:
                if field_name in data:
                    item_m2m[field_name] = data.pop(field_name)
            m2m_data_list.append(item_m2m)

        return validated_data, m2m_data_list

    def set_m2m_relations(self, instances, m2m_data_list):
        """
        Set M2M relations for bulk created/updated instances using batched writes.

        Must be called after objects have IDs.

        Args:
            instances: List of model instances
            m2m_data_list: List of M2M data dicts (one per instance)
        """
        if len(instances) != len(m2m_data_list):
            raise ValueError(f"Mismatch: {len(instances)} instances but {len(m2m_data_list)} M2M data items")

        # Aggregate all through-model rows to insert per field
        field_to_rows = {field_name: [] for field_name in self.m2m_fields}
        field_to_clear = {field_name: [] for field_name in self.m2m_fields}

        # Collect rows
        for instance, m2m_data in zip(instances, m2m_data_list):
            for field_name, values in m2m_data.items():
                if values is None:
                    continue
                # Clear existing relations for updates (replace semantics)
                field_to_clear[field_name].append(instance.pk)

                # Normalize values to list of IDs
                if values and hasattr(values, "__iter__") and not isinstance(values, (str, bytes)):
                    ids = [getattr(v, "pk", v) for v in values]
                else:
                    ids = [getattr(values, "pk", values)] if values is not None else []

                # Prepare through rows later when we have the through model
                field_to_rows[field_name].append((instance.pk, ids))

        # Execute clears and bulk inserts per field
        for field_name in self.m2m_fields:
            pk_list = field_to_clear[field_name]
            if not pk_list and not field_to_rows[field_name]:
                continue

            rel = self.model._meta.get_field(field_name)
            through = rel.remote_field.through
            source_column = rel.m2m_column_name()
            target_column = rel.m2m_reverse_name()

            # Clear existing relations in a single delete per field
            if pk_list:
                through.objects.filter(**{f"{source_column}__in": pk_list}).delete()

            # Build through instances to insert
            to_create = []
            for instance_pk, target_ids in field_to_rows[field_name]:
                for target_pk in target_ids:
                    row = through(**{source_column: instance_pk, target_column: target_pk})
                    to_create.append(row)

            if to_create:
                through.objects.bulk_create(to_create, batch_size=1000)

    def set_m2m_field(self, instance, field_name, values):
        """
        Set M2M field for a single instance.

        Args:
            instance: Model instance
            field_name: Name of M2M field
            values: List of related objects or IDs
        """
        m2m_manager = getattr(instance, field_name)
        m2m_manager.set(values)

    def clear_and_set(self, instance, field_name, values):
        """
        Clear existing M2M relations and set new ones.
        Used for update/upsert operations.

        Args:
            instance: Model instance
            field_name: Name of M2M field
            values: List of related objects or IDs
        """
        m2m_manager = getattr(instance, field_name)
        m2m_manager.clear()
        if values:
            m2m_manager.set(values)


class BatchProcessor:
    """
    Utility for processing large datasets in chunks.
    """

    def __init__(self, batch_size):
        """
        Initialize with batch size.

        Args:
            batch_size: Number of items per batch
        """
        self.batch_size = batch_size

    def process_in_batches(self, items, processor_func):
        """
        Process items in batches.

        Args:
            items: List of items to process
            processor_func: Function called for each batch

        Returns:
            Combined results from all batches
        """
        results = []
        for batch in self.chunk_list(items):
            batch_result = processor_func(batch)
            if batch_result:
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                else:
                    results.append(batch_result)
        return results

    def chunk_list(self, items):
        """
        Split list into chunks of batch_size.
        Generator function for memory efficiency.

        Args:
            items: List of items to chunk

        Yields:
            Chunks of batch_size items
        """
        for i in range(0, len(items), self.batch_size):
            yield items[i : i + self.batch_size]


def build_unique_key(data, unique_fields):
    """
    Build a unique key tuple from data and unique_fields.

    Args:
        data: Dictionary of field values
        unique_fields: List of field names to use for key

    Returns:
        Tuple of values for unique_fields
    """
    return tuple(data.get(field) for field in unique_fields)


def extract_unique_keys(validated_data, unique_fields):
    """
    Extract unique keys from validated data.

    Args:
        validated_data: List of validated data dicts
        unique_fields: List of field names to use for keys

    Returns:
        List of unique key tuples
    """
    return [build_unique_key(data, unique_fields) for data in validated_data]


def build_lookup_dict(instances, unique_fields):
    """
    Build a lookup dictionary mapping unique keys to instances.

    Args:
        instances: List of model instances
        unique_fields: List of field names to use for keys

    Returns:
        Dict mapping unique_key → instance
    """
    lookup = {}
    for instance in instances:
        key = tuple(getattr(instance, field) for field in unique_fields)
        lookup[key] = instance
    return lookup
