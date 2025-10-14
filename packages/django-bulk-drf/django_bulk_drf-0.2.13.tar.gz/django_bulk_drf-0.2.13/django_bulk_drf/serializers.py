"""
Serializer layer for bulk operations.

Provides:
- BulkSerializerMixin: Preprocessing utilities
- BulkListSerializer: Coordination and delegation
- BulkModelSerializer: Main serializer class
"""

from rest_framework import serializers
from .operations import BulkCreateOperation, BulkUpdateOperation, BulkUpsertOperation
from .utils import FieldConverter, M2MHandler
from .settings import bulk_settings


class BulkSerializerMixin:
    """
    Preprocessing utilities for bulk serialization.
    Handles FK → FK_id conversion and M2M extraction.
    """

    def to_internal_value(self, data):
        """
        Override to handle bulk-specific field transformations.

        Args:
            data: Input data dict

        Returns:
            Validated internal data
        """
        # Call parent to_internal_value first
        validated_data = super().to_internal_value(data)

        # Note: FK conversion and M2M extraction are now done in bulk
        # by the ListSerializer, not per-item

        return validated_data

    def _convert_fk_to_id_fields(self, data):
        """
        Transform foreign key references to database-friendly format.

        Note: This is now a no-op as conversion happens in bulk.
        Kept for compatibility.

        Args:
            data: Data dict

        Returns:
            Transformed data
        """
        return data

    def _extract_m2m_fields(self, validated_data):
        """
        Separate M2M fields from main data.
        M2M relations must be set after object creation.

        Args:
            validated_data: Validated data dict

        Returns:
            Tuple of (cleaned_data, m2m_data)
        """
        if not hasattr(self.Meta, "model"):
            return validated_data, {}

        model = self.Meta.model
        m2m_fields = FieldConverter.get_model_m2m_fields(model)

        m2m_data = {}
        for field_name in m2m_fields:
            if field_name in validated_data:
                m2m_data[field_name] = validated_data.pop(field_name)

        return validated_data, m2m_data


class BulkListSerializer(serializers.ListSerializer):
    """
    Coordinator for bulk operations.
    Delegates to operation classes, handles result formatting.
    
    CRITICAL: Overrides is_valid() to prevent N+1 queries during validation.
    """

    def is_valid(self, raise_exception=False):
        """
        Override DRF's default validation to avoid N+1 queries.
        
        CRITICAL PERFORMANCE ISSUE:
            DRF's default ListSerializer.is_valid() calls child.to_internal_value() for each item,
            which triggers individual database queries per record:
            - UniqueValidator: SELECT 1 FROM table WHERE unique_field = ? LIMIT 1
            - FK field validation: SELECT * FROM related_table WHERE id = ? LIMIT 21
            - UniqueTogetherValidator: Complex queries for composite unique constraints
            
            With 10K records, this becomes 20K+ queries (2+ per record).
            Real-world example: 10,000 records = 20,741 queries in debug log.
        
        SOLUTION - Validator Disabling Pattern:
            1. Temporarily disable database-hitting validators before validation
            2. Run field-level validation (types, required fields) without DB queries
            3. Restore validators after validation
            4. Defer database validation to operations layer (bulk queries)
        
        Validators to disable:
            - UniqueValidator
            - UniqueTogetherValidator  
            - UniqueForDateValidator, UniqueForMonthValidator, UniqueForYearValidator
            - FK field querysets (set to .none() to skip existence checks)
        
        Performance Impact:
            - Before: O(n) queries - 20,000+ queries for 10K records
            - After: O(1) queries - <5 queries total during validation
            - Speed improvement: 10x+ faster validation
        
        Returns:
            Boolean indicating if data is valid
        """
        if not hasattr(self, '_validated_data'):
            try:
                # Disable database-hitting validators
                disabled_validators = self._disable_db_validators()
                
                try:
                    # Run validation without DB queries
                    self._validated_data = self._run_validation(self.initial_data)
                    self._errors = []
                finally:
                    # Restore validators for single-object operations
                    self._restore_db_validators(disabled_validators)
                    
            except serializers.ValidationError as exc:
                self._validated_data = []
                self._errors = exc.detail
        
        if self._errors and raise_exception:
            raise serializers.ValidationError(self._errors)
        
        return not bool(self._errors)
    
    def _disable_db_validators(self):
        """
        Temporarily remove database-hitting validators from child serializer fields.
        
        CRITICAL: This method prevents N+1 queries by disabling validators that
        would otherwise query the database for each record during validation.
        
        IMPORTANT: Only disables validators that make database queries.
        
        Disables:
        - UniqueValidator: Checks uniqueness per record
        - UniqueTogetherValidator: Checks composite unique constraints
        - UniqueForDateValidator, UniqueForMonthValidator, UniqueForYearValidator
        - FK field querysets (existence checks)
        
        Preserves:
        - Field-level type validation (CharField, IntegerField, etc.)
        - validate_<field> methods (unless they query DB)
        - Custom validators without DB access
        - required/allow_blank/allow_null checks
        - Field-level constraints (min_value, max_length, etc.)
        
        These will be validated in bulk by the operation layer instead.
        
        Returns:
            Dict mapping field names to their disabled validators for restoration
        """
        from rest_framework.validators import (
            UniqueValidator, 
            UniqueTogetherValidator,
            UniqueForDateValidator,
            UniqueForMonthValidator,
            UniqueForYearValidator,
        )
        from rest_framework.relations import (
            PrimaryKeyRelatedField, 
            SlugRelatedField,
            StringRelatedField,
            HyperlinkedRelatedField,
            HyperlinkedIdentityField,
        )
        
        disabled_validators = {
            'field_validators': {},  # field_name -> list of disabled validators
            'serializer_validators': [],  # serializer-level validators
            'field_querysets': {},  # field_name -> original queryset
            'replaced_fields': {},  # field_name -> original field (for FK fields)
        }
        
        # Disable field-level validators
        for field_name, field in self.child.fields.items():
            if hasattr(field, 'validators'):
                # Find and disable database-hitting validators
                db_validators = []
                remaining_validators = []
                
                for validator in field.validators:
                    if isinstance(validator, (
                        UniqueValidator,
                        UniqueForDateValidator,
                        UniqueForMonthValidator,
                        UniqueForYearValidator,
                    )):
                        db_validators.append(validator)
                    else:
                        remaining_validators.append(validator)
                
                if db_validators:
                    disabled_validators['field_validators'][field_name] = db_validators
                    field.validators = remaining_validators
            
            # Replace FK fields with pass-through fields to skip DB validation
            # PrimaryKeyRelatedField queries the database to check if the PK exists
            # We replace it temporarily with an IntegerField that just validates the type
            if isinstance(field, PrimaryKeyRelatedField):
                disabled_validators['replaced_fields'][field_name] = field
                
                # Handle many=True edge case (list of FKs)
                if getattr(field, 'many', False):
                    # Replace with ListField of integers
                    kwargs = {
                        'child': serializers.IntegerField(),
                        'required': field.required,
                        'allow_null': field.allow_null,
                        'allow_empty': getattr(field, 'allow_empty', True),
                    }
                    # Only include source if it differs from field_name (DRF doesn't allow redundant source)
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.ListField(**kwargs)
                else:
                    # Single FK - replace with IntegerField
                    kwargs = {
                        'required': field.required,
                        'allow_null': field.allow_null,
                    }
                    # Only include source if it differs from field_name (DRF doesn't allow redundant source)
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.IntegerField(**kwargs)
                
                # CRITICAL: Bind the replacement field to the serializer
                replacement.bind(field_name, self.child)
                self.child.fields[field_name] = replacement
            
            # Similarly handle SlugRelatedField - replace with CharField
            elif isinstance(field, SlugRelatedField):
                disabled_validators['replaced_fields'][field_name] = field
                
                # Handle many=True edge case (list of slugs)
                if getattr(field, 'many', False):
                    # Replace with ListField of strings
                    kwargs = {
                        'child': serializers.CharField(),
                        'required': field.required,
                        'allow_null': field.allow_null,
                        'allow_empty': getattr(field, 'allow_empty', True),
                    }
                    # Only include source if it differs from field_name (DRF doesn't allow redundant source)
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.ListField(**kwargs)
                else:
                    # Single slug - replace with CharField
                    kwargs = {
                        'required': field.required,
                        'allow_null': field.allow_null,
                        'allow_blank': getattr(field, 'allow_blank', False),
                    }
                    # Only include source if it differs from field_name (DRF doesn't allow redundant source)
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.CharField(**kwargs)
                
                # CRITICAL: Bind the replacement field to the serializer
                replacement.bind(field_name, self.child)
                self.child.fields[field_name] = replacement
            
            # For other relational fields with querysets, disable the queryset
            elif hasattr(field, 'queryset') and field.queryset is not None:
                disabled_validators['field_querysets'][field_name] = field.queryset
                # Set to all() instead of none() to allow validation to pass
                # We'll handle actual FK validation in the operation layer
                field.queryset = field.queryset.model.objects.all()
            
            # Handle other relational field types that make database queries
            elif isinstance(field, (StringRelatedField, HyperlinkedRelatedField, HyperlinkedIdentityField)):
                disabled_validators['replaced_fields'][field_name] = field
                
                # Replace with appropriate pass-through field
                if isinstance(field, StringRelatedField):
                    # StringRelatedField displays __str__ of related object
                    # Replace with CharField to just validate it's a string
                    kwargs = {
                        'required': field.required,
                        'allow_null': field.allow_null,
                        'allow_blank': getattr(field, 'allow_blank', False),
                    }
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.CharField(**kwargs)
                elif isinstance(field, (HyperlinkedRelatedField, HyperlinkedIdentityField)):
                    # Hyperlinked fields expect URLs
                    # Replace with URLField to just validate URL format
                    kwargs = {
                        'required': field.required,
                        'allow_null': field.allow_null,
                        'allow_blank': getattr(field, 'allow_blank', False),
                    }
                    if field.source != field_name:
                        kwargs['source'] = field.source
                    replacement = serializers.URLField(**kwargs)
                
                # CRITICAL: Bind the replacement field to the serializer
                replacement.bind(field_name, self.child)
                self.child.fields[field_name] = replacement
        
        # Disable serializer-level validators (UniqueTogetherValidator, etc.)
        if hasattr(self.child, 'validators'):
            db_validators = []
            remaining_validators = []
            
            for validator in self.child.validators:
                if isinstance(validator, UniqueTogetherValidator):
                    db_validators.append(validator)
                else:
                    remaining_validators.append(validator)
            
            if db_validators:
                disabled_validators['serializer_validators'] = db_validators
                self.child.validators = remaining_validators
        
        return disabled_validators
    
    def _restore_db_validators(self, disabled_validators):
        """
        Restore validators and fields that were temporarily disabled/replaced.
        
        This ensures that single-object operations still work correctly
        with full validation.
        
        Restoration includes:
        - Re-adding disabled validators to fields
        - Restoring original querysets on relational fields
        - Replacing temporary fields (IntegerField, CharField) with original
          FK fields (PrimaryKeyRelatedField, SlugRelatedField)
        - Re-adding disabled serializer-level validators
        
        Args:
            disabled_validators: Dict returned by _disable_db_validators() containing:
                - field_validators: Field-level validators to restore
                - serializer_validators: Serializer-level validators to restore
                - field_querysets: Original querysets to restore
                - replaced_fields: Original FK fields to restore
        
        Returns:
            None
        """
        # Restore replaced FK fields first (IntegerField -> PrimaryKeyRelatedField, etc.)
        for field_name, original_field in disabled_validators['replaced_fields'].items():
            # CRITICAL: Re-bind the original field to the serializer
            # DRF doesn't allow redundant source (source='field_name' when field_name matches)
            # Clear the source if it matches the field name to avoid AssertionError on re-bind
            if hasattr(original_field, 'source') and original_field.source == field_name:
                original_field.source = None
            original_field.bind(field_name, self.child)
            self.child.fields[field_name] = original_field
        
        # Restore field-level validators
        for field_name, validators in disabled_validators['field_validators'].items():
            if field_name in self.child.fields:
                field = self.child.fields[field_name]
                field.validators.extend(validators)
        
        # Restore field querysets
        for field_name, queryset in disabled_validators['field_querysets'].items():
            if field_name in self.child.fields:
                self.child.fields[field_name].queryset = queryset
        
        # Restore serializer-level validators
        if disabled_validators['serializer_validators']:
            if hasattr(self.child, 'validators'):
                self.child.validators.extend(disabled_validators['serializer_validators'])
            else:
                self.child.validators = disabled_validators['serializer_validators']
    
    def _run_validation(self, data):
        """
        Perform validation without database hits.
        
        This method validates structure and field types without querying the database.
        Database validation (existence checks, FK validation) is deferred to the
        operation layer where it can be done in bulk.
        
        Args:
            data: List of data dicts
            
        Returns:
            List of validated data dicts
            
        Raises:
            ValidationError: If validation fails
        """
        # Ensure data is a list
        if not isinstance(data, list):
            raise serializers.ValidationError({
                'non_field_errors': ['Expected a list of items but got type "{0}".'.format(type(data).__name__)]
            })
        
        if not self.allow_empty and len(data) == 0:
            raise serializers.ValidationError({
                'non_field_errors': ['This list may not be empty.']
            })
        
        # Validate each item
        ret = []
        errors = []
        
        for item in data:
            try:
                # Validate individual item using child serializer
                # This performs field-level validation without DB queries
                validated = self._validate_item(item)
                ret.append(validated)
                errors.append({})
            except serializers.ValidationError as exc:
                ret.append({})
                errors.append(exc.detail)
        
        # Check if any errors occurred
        if any(errors):
            raise serializers.ValidationError(errors)
        
        return ret
    
    def _validate_item(self, item):
        """
        Validate a single item without database queries.
        
        Uses the child serializer's to_internal_value for field validation,
        but skips unique validators and FK existence checks.
        
        Args:
            item: Data dict for single item
            
        Returns:
            Validated data dict
            
        Raises:
            ValidationError: If field validation fails
        """
        # Use child serializer for field-level validation
        # This validates data types, required fields, etc. without DB queries
        # The validators have been disabled, so this should not hit the database
        
        # CRITICAL: Add additional safety by temporarily disabling all querysets
        # This ensures no database queries can happen during validation
        original_querysets = {}
        for field_name, field in self.child.fields.items():
            if hasattr(field, 'queryset') and field.queryset is not None:
                original_querysets[field_name] = field.queryset
                # Temporarily set to empty queryset to prevent any DB access
                field.queryset = field.queryset.model.objects.none()
        
        try:
            return self.child.to_internal_value(item)
        finally:
            # Restore original querysets
            for field_name, queryset in original_querysets.items():
                if field_name in self.child.fields:
                    self.child.fields[field_name].queryset = queryset

    def create(self, validated_data):
        """
        Delegate to BulkCreateOperation.

        Args:
            validated_data: List of validated data dicts

        Returns:
            List of created instances
        """
        # Extract M2M data
        validated_data, m2m_data_list = self._extract_m2m_data(validated_data)

        # Convert FK fields in batch
        validated_data = self._convert_fk_fields_batch(validated_data)

        # Get operation context
        context = self._prepare_operation_context()

        # Execute operation
        operation = BulkCreateOperation(
            model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
        )

        result = operation.execute(validated_data, m2m_data_list)

        # Expose operation result for viewset response formatting
        self.bulk_result = result

        return result.get_all_instances()

    def update(self, validated_data):
        """
        Delegate to BulkUpdateOperation.
        Requires all objects exist and unique fields are present.

        Args:
            validated_data: List of validated data dicts

        Returns:
            List of updated instances
        """
        # Extract M2M data
        validated_data, m2m_data_list = self._extract_m2m_data(validated_data)

        # Convert FK fields in batch
        validated_data = self._convert_fk_fields_batch(validated_data)

        # Get operation context
        context = self._prepare_operation_context()

        # Execute operation
        operation = BulkUpdateOperation(
            model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
        )

        result = operation.execute(validated_data, m2m_data_list)

        # Expose operation result for viewset response formatting
        self.bulk_result = result

        return result.get_all_instances()

    def upsert(self, validated_data):
        """
        Delegate to BulkUpsertOperation.
        Creates new or updates existing based on unique_fields.

        Args:
            validated_data: List of validated data dicts

        Returns:
            List of instances (created + updated)
        """
        # Extract M2M data
        validated_data, m2m_data_list = self._extract_m2m_data(validated_data)

        # Convert FK fields in batch
        validated_data = self._convert_fk_fields_batch(validated_data)

        # Get operation context
        context = self._prepare_operation_context()

        # Execute operation
        operation = BulkUpsertOperation(
            model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
        )

        result = operation.execute(validated_data, m2m_data_list)

        # Expose operation result for viewset response formatting
        self.bulk_result = result

        return result.get_all_instances()

    def _extract_m2m_data(self, validated_data):
        """
        Extract M2M fields from validated data.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Tuple of (cleaned_data, m2m_data_list)
        """
        if not bulk_settings.enable_m2m_handling:
            return validated_data, []

        model = self._get_model()
        if not model:
            return validated_data, []

        m2m_handler = M2MHandler(model)
        return m2m_handler.extract_m2m_data(validated_data)

    def _convert_fk_fields_batch(self, validated_data):
        """
        Convert FK fields to _id fields for entire batch.
        Single query per FK field.

        Args:
            validated_data: List of validated data dicts

        Returns:
            Updated validated_data
        """
        model = self._get_model()
        if not model:
            return validated_data

        return FieldConverter.convert_related_fields_batch(validated_data, model)

    def _get_model(self):
        """
        Get model class from child serializer.

        Returns:
            Model class or None
        """
        if hasattr(self.child, "Meta") and hasattr(self.child.Meta, "model"):
            return self.child.Meta.model
        return None

    def _prepare_operation_context(self):
        """
        Extract context needed by operations.

        Returns:
            Dict with operation context
        """
        context = {
            "model": self._get_model(),
            "unique_fields": self.context.get("unique_fields", ["id"]),
            "batch_size": self.context.get("batch_size", bulk_settings.default_batch_size),
            "user": self.context.get("request").user if self.context.get("request") else None,
            "request": self.context.get("request"),
            "view": self.context.get("view"),
        }
        return context

    def _get_operation(self, operation_type):
        """
        Factory method to instantiate correct operation class.

        Args:
            operation_type: 'create', 'update', or 'upsert'

        Returns:
            Operation instance
        """
        context = self._prepare_operation_context()

        if operation_type == "create":
            return BulkCreateOperation(
                model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
            )
        elif operation_type == "update":
            return BulkUpdateOperation(
                model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
            )
        elif operation_type == "upsert":
            return BulkUpsertOperation(
                model=context["model"], unique_fields=context.get("unique_fields"), batch_size=context.get("batch_size"), context=context
            )
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")

    def _format_operation_result(self, result):
        """
        Convert BulkOperationResult to serializer output.

        Args:
            result: BulkOperationResult instance

        Returns:
            List of serialized instances
        """
        instances = result.get_all_instances()
        return self.child.serialize(instances, many=True)


class BulkModelSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    """
    Main serializer users inherit from.
    Auto-uses BulkListSerializer when many=True.
    """

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        DRF hook called when instantiated with many=True.
        Returns BulkListSerializer instead of default ListSerializer.

        Args:
            *args: Positional arguments (instance for reading)
            **kwargs: Keyword arguments (data for writing)

        Returns:
            BulkListSerializer instance
        """
        # Allow overriding list_serializer_class
        list_serializer_class = kwargs.pop("list_serializer_class", None)
        if list_serializer_class is None:
            list_serializer_class = BulkListSerializer

        # Extract data and instance - these belong to the ListSerializer, not the child
        # The child is just a template for validating individual items
        data = kwargs.pop("data", None)
        instance = args[0] if args else kwargs.pop("instance", None)

        # Create child serializer WITHOUT data/instance
        # The child is a template; it doesn't process the actual data
        child_serializer = cls(**kwargs)

        # Build list serializer kwargs
        list_kwargs = {
            "child": child_serializer,
        }

        # Pass data/instance to the ListSerializer
        if data is not None:
            list_kwargs["data"] = data
        if instance is not None:
            list_kwargs["instance"] = instance

        # Copy context (required for operations)
        if "context" in kwargs:
            list_kwargs["context"] = kwargs["context"]

        # Copy other relevant kwargs
        for key in ["allow_empty", "max_length", "min_length"]:
            if key in kwargs:
                list_kwargs[key] = kwargs[key]

        return list_serializer_class(**list_kwargs)

    def create(self, validated_data):
        """
        Create a single instance.
        Standard DRF behavior.

        Args:
            validated_data: Validated data dict

        Returns:
            Created instance
        """
        # Extract M2M data
        validated_data, m2m_data = self._extract_m2m_fields(validated_data)

        # Create instance
        instance = super().create(validated_data)

        # Set M2M fields
        if m2m_data and bulk_settings.enable_m2m_handling:
            for field_name, value in m2m_data.items():
                setattr(instance, field_name, value)

        return instance

    def update(self, instance, validated_data):
        """
        Update a single instance.
        Standard DRF behavior.

        Args:
            instance: Instance to update
            validated_data: Validated data dict

        Returns:
            Updated instance
        """
        # Extract M2M data
        validated_data, m2m_data = self._extract_m2m_fields(validated_data)

        # Update instance
        instance = super().update(instance, validated_data)

        # Set M2M fields
        if m2m_data and bulk_settings.enable_m2m_handling:
            for field_name, value in m2m_data.items():
                getattr(instance, field_name).set(value)

        return instance
