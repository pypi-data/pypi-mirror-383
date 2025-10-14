"""
Query building and optimization for bulk operations.

Provides utilities for:
- Building efficient OR queries with Q objects
- Single-query fetches for bulk lookups
- Automatic select_related/prefetch_related optimization
"""

from django.db.models import Q


class BulkQueryBuilder:
    """
    Builds optimized queries for bulk operations.
    """

    def __init__(self, model, unique_fields):
        """
        Initialize with model and unique field configuration.

        Args:
            model: Django model class
            unique_fields: Fields used for object matching
        """
        self.model = model
        self.unique_fields = unique_fields if isinstance(unique_fields, (list, tuple)) else [unique_fields]

    def build_lookup_filter(self, lookup_values):
        """
        Build Q objects for complex lookups.

        Args:
            lookup_values: List of dicts with unique field values

        Returns:
            Q object for filtering

        Example:
            unique_fields = ['sku', 'warehouse']
            lookup_values = [
                {'sku': 'A', 'warehouse': 1},
                {'sku': 'B', 'warehouse': 2}
            ]
            Returns: Q(sku='A', warehouse=1) | Q(sku='B', warehouse=2)
        """
        if not lookup_values:
            return Q(pk__in=[])  # Empty queryset

        # Optimize for single field lookups
        if len(self.unique_fields) == 1:
            field = self.unique_fields[0]
            values = [item.get(field) for item in lookup_values if field in item]
            return self.build_in_filter(field, values)

        # Multi-field lookups require OR conditions
        return self.build_or_conditions(lookup_values)

    def build_or_conditions(self, lookup_values):
        """
        Build OR conditions for multiple objects.

        Args:
            lookup_values: List of dicts with unique field values

        Returns:
            Q object with OR conditions
        """
        q_objects = []

        for item in lookup_values:
            # Build AND condition for this item's unique fields
            q_kwargs = {}
            for field in self.unique_fields:
                if field in item:
                    q_kwargs[field] = item[field]

            if q_kwargs:
                q_objects.append(Q(**q_kwargs))

        if not q_objects:
            return Q(pk__in=[])  # Empty queryset

        # Combine with OR
        combined_q = q_objects[0]
        for q in q_objects[1:]:
            combined_q |= q

        return combined_q

    def build_in_filter(self, field, values):
        """
        Build __in filter for single field.

        Args:
            field: Field name
            values: List of values

        Returns:
            Q object with __in filter
        """
        if not values:
            return Q(pk__in=[])  # Empty queryset

        return Q(**{f"{field}__in": values})

    def fetch_by_unique_fields(self, queryset, validated_data):
        """
        Single query to fetch all matching objects.

        Args:
            queryset: Base queryset to filter
            validated_data: List of data dicts with unique field values

        Returns:
            Dict mapping unique_key → instance
        """
        # Build lookup filter
        q_filter = self.build_lookup_filter(validated_data)

        # Execute single query
        instances = queryset.filter(q_filter)

        # Build lookup dict
        lookup = {}
        for instance in instances:
            key = self._get_instance_key(instance)
            lookup[key] = instance

        return lookup

    def _get_instance_key(self, instance):
        """
        Get unique key tuple for an instance.

        Args:
            instance: Model instance

        Returns:
            Tuple of unique field values
        """
        return tuple(getattr(instance, field) for field in self.unique_fields)

    def _get_data_key(self, data):
        """
        Get unique key tuple from data dict.

        Args:
            data: Dictionary of field values

        Returns:
            Tuple of unique field values
        """
        return tuple(data.get(field) for field in self.unique_fields)

    def optimize_queryset(self, queryset, serializer_class):
        """
        Apply select_related/prefetch_related based on serializer.

        Args:
            queryset: Queryset to optimize
            serializer_class: Serializer class to analyze

        Returns:
            Optimized queryset
        """
        optimizer = QueryOptimizer(serializer_class)
        return optimizer.apply_optimizations(queryset)


class QueryOptimizer:
    """
    Analyzes serializers to optimize queries.
    """

    def __init__(self, serializer_class):
        """
        Initialize with serializer to analyze.

        Args:
            serializer_class: DRF serializer class
        """
        self.serializer_class = serializer_class
        self._select_related = []
        self._prefetch_related = []
        self._analyzed = False

    def analyze(self):
        """
        Analyze serializer fields to determine optimizations.
        """
        if self._analyzed:
            return

        if not self.serializer_class:
            self._analyzed = True
            return

        # Get serializer fields
        try:
            serializer = self.serializer_class()
            fields = serializer.get_fields()
        except Exception:
            self._analyzed = True
            return

        # Analyze each field
        for field_name, field in fields.items():
            self._analyze_field(field_name, field)

        self._analyzed = True

    def _analyze_field(self, field_name, field):
        """
        Analyze a single field for optimization opportunities.

        Args:
            field_name: Name of the field
            field: Field instance
        """
        from rest_framework import serializers

        # Check for nested serializers (FK fields)
        if isinstance(field, serializers.Serializer):
            # Nested serializer indicates FK or M2M
            if isinstance(field, serializers.ListSerializer):
                # Many=True indicates M2M or reverse FK
                self._prefetch_related.append(field_name)
            else:
                # Single nested serializer indicates FK
                self._select_related.append(field_name)

        # Check for PrimaryKeyRelatedField, SlugRelatedField, etc.
        elif isinstance(field, (serializers.PrimaryKeyRelatedField, serializers.SlugRelatedField)):
            if getattr(field, "many", False):
                # Many=True indicates M2M
                self._prefetch_related.append(field_name)
            else:
                # Single FK
                self._select_related.append(field_name)

    def get_select_related_fields(self):
        """
        Extract ForeignKey fields that should use select_related.

        Returns:
            List of field names
        """
        if not self._analyzed:
            self.analyze()
        return self._select_related

    def get_prefetch_related_fields(self):
        """
        Extract M2M/reverse FK fields for prefetch_related.

        Returns:
            List of field names
        """
        if not self._analyzed:
            self.analyze()
        return self._prefetch_related

    def apply_optimizations(self, queryset):
        """
        Apply all optimizations to queryset.

        Args:
            queryset: Queryset to optimize

        Returns:
            Optimized queryset
        """
        if not self._analyzed:
            self.analyze()

        # Apply select_related
        if self._select_related:
            queryset = queryset.select_related(*self._select_related)

        # Apply prefetch_related
        if self._prefetch_related:
            queryset = queryset.prefetch_related(*self._prefetch_related)

        return queryset


def build_filter_for_delete(model, unique_fields, data_list):
    """
    Build filter for bulk delete operation.

    Args:
        model: Django model class
        unique_fields: List of unique field names
        data_list: List of dicts with unique field values

    Returns:
        Q object for filtering records to delete
    """
    builder = BulkQueryBuilder(model, unique_fields)
    return builder.build_lookup_filter(data_list)


def fetch_existing_objects(model, unique_fields, validated_data):
    """
    Fetch existing objects matching validated_data.

    Args:
        model: Django model class
        unique_fields: List of unique field names
        validated_data: List of data dicts

    Returns:
        Dict mapping unique_key → instance
    """
    builder = BulkQueryBuilder(model, unique_fields)
    queryset = model.objects.all()
    return builder.fetch_by_unique_fields(queryset, validated_data)
