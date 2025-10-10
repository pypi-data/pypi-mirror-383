"""
Optimized relation fields for bulk operations.

Provides in-memory lookup variants of DRF's relation fields to eliminate
N+1 query problems during bulk validation.
"""

from rest_framework import serializers
from django.utils.encoding import smart_str


class IterableSlugRelatedField(serializers.SlugRelatedField):
    def __init__(self, slug_field=None, records=None, **kwargs):
        kwargs["queryset"] = None
        super().__init__(slug_field=slug_field, **kwargs)
        self.set_records(records)

    def set_records(self, records):
        """Set the records for this field."""
        self._records = records or []
        # Build lookup dictionary immediately
        if self._records:
            self._records_by_slug = {getattr(obj, self.slug_field): obj for obj in self._records}
        else:
            self._records_by_slug = {}

    def to_internal_value(self, data):
        if self._records_by_slug is None:
            self.fail("invalid", value=smart_str(data))

        record = self._records_by_slug.get(data)
        if record is None:
            self.fail("does_not_exist", slug_name=self.slug_field, value=smart_str(data))

        return record

    def get_queryset(self):
        """Return None - we don't use querysets."""
        return None
