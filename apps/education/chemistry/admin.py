from django.contrib import admin
from .models import Element

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = (
        'atomic_number', 'symbol', 'name', 'category', 'group', 'period', 'phase', 'radioactive', 'natural'
    )
    search_fields = ('name', 'symbol', 'category')
    list_filter = ('category', 'group', 'period', 'phase', 'radioactive', 'natural')