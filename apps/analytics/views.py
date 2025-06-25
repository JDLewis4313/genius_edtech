from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Event
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
