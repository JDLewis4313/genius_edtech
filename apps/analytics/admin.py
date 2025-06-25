from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin  # ✅ This is the missing piece
from .models import Event
from django.db.models import Count
from collections import defaultdict

@staff_member_required
def analytics_overview(request):
    chart_data = defaultdict(int)

    recent = Event.objects.filter(event_type__in=['tool_open', 'tool_use']).order_by('-timestamp')[:200]
    for e in recent:
        tool = e.meta.get('tool', 'Other')
        chart_data[tool] += 1

    labels = list(chart_data.keys())
    values = list(chart_data.values())

    return render(request, 'analytics/overview.html', {
        'labels': labels,
        'values': values
    })

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'path', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'path')
