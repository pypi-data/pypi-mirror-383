from django.db.models import ForeignKey
from rest_framework import serializers


class BulkModelSerializer(serializers.ModelSerializer):
    """
    Bulk-optimized serializer that accepts standard Django field names.

    Key features:
    - Accepts standard field names (loan_account) in API requests
    - Returns standard field names in responses for consistency
    - Full django-filter compatibility
    - FK field transformation handled in create() for proper SOC
    - DRF's default ListSerializer handles bulk operations when many=True
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._foreign_key_field_mappings = self._build_foreign_key_mappings()

    def create(self, validated_data):
        """
        Create instance with FK field transformation.
        
        Transformation happens here (during create), not during validation.
        This maintains proper SOC:
        - to_internal_value() = validation only
        - create() = prepare data for database operations
        """
        # Transform FK fields before creating the instance
        transformed_data = self._transform_fk_fields(validated_data)
        
        # Create the model instance (not saved to database)
        model_class = self.Meta.model
        instance = model_class(**transformed_data)
        
        return instance
    
    def _transform_fk_fields(self, data):
        """Transform FK fields from logical names to database field names."""
        transformed_data = data.copy()
        
        for fk_name, target_field_name in self._foreign_key_field_mappings.items():
            if fk_name in transformed_data:
                transformed_data[target_field_name] = transformed_data[fk_name]
        
        return transformed_data

    def _build_foreign_key_mappings(self):
        """
        Build mappings from logical field names to their database field names.
        Returns dict mapping logical_field_name -> database_field_name
        """
        foreign_key_mappings = {}

        for model_field in self.Meta.model._meta.get_fields():
            if not isinstance(model_field, ForeignKey):
                continue

            model_field_name = model_field.name
            database_field_name = model_field.attname

            is_slug_field = self._is_slug_field(model_field_name)

            if is_slug_field:
                foreign_key_mappings[model_field_name] = model_field_name  # Use original name for slug fields
            else:
                foreign_key_mappings[model_field_name] = database_field_name  # Use _id name for regular fields

        return foreign_key_mappings

    def _is_slug_field(self, model_field_name):
        """Check if a foreign key field is a SlugRelatedField."""
        if model_field_name not in self.fields:
            return False

        serializer_field = self.fields[model_field_name]
        return isinstance(serializer_field, serializers.SlugRelatedField)
