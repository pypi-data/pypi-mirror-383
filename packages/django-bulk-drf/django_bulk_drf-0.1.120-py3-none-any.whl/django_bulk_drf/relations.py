"""
Optimized relation fields for bulk operations.

Provides in-memory lookup variants of DRF's relation fields to eliminate
N+1 query problems during bulk validation.
"""

from rest_framework import serializers
from django.utils.encoding import smart_str
import sys


class IterableSlugRelatedField(serializers.SlugRelatedField):
    def __init__(self, slug_field=None, records=None, **kwargs):
        kwargs["queryset"] = None
        super().__init__(slug_field=slug_field, **kwargs)
        self.set_records(records)

    def set_records(self, records):
        """Set the records for this field."""
        self._records = records or []
        self._records_by_slug = None

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if self._records and self._records_by_slug is None:
            self._records_by_slug = {getattr(obj, self.slug_field): obj for obj in self._records}

    def to_internal_value(self, data):
        print(f"DEBUG: _records_by_slug = {self._records_by_slug}", file=sys.stderr)
        print(f"DEBUG: data = {data}", file=sys.stderr)
        print(f"DEBUG: slug_field = {self.slug_field}", file=sys.stderr)

        if self._records_by_slug is None:
            print("ERROR: _records_by_slug is None - records not set!", file=sys.stderr)
            self.fail("invalid", value=smart_str(data))

        record = self._records_by_slug.get(data)
        if record is None:
            print(f"ERROR: No record found for slug '{data}'", file=sys.stderr)
            print(f"Available slugs: {list(self._records_by_slug.keys())}", file=sys.stderr)
            self.fail("does_not_exist", slug_name=self.slug_field, value=smart_str(data))

        return record

    def get_queryset(self):
        """Return None - we don't use querysets."""
        return None
