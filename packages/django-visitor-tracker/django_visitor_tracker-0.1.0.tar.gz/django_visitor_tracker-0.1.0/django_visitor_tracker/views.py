from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
import datetime

from .utils import get_aggregates, aggregates_to_json_serializable
from .models import LogEntry


@require_GET
def stats_view(request):
    period = request.GET.get('period', 'day')
    try:
        span = int(request.GET.get('span', '30'))
    except ValueError:
        span = 30

    aggregates = get_aggregates(period=period, span=span)
    data = aggregates_to_json_serializable(aggregates)
    return JsonResponse({'period': period, 'data': data})


@require_GET
def summary_counts(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - datetime.timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)

    def unique_ips(start, end):
        return LogEntry.objects.filter(timestamp__gte=start, timestamp__lt=end).values('ip').distinct().count()

    data = {
        'today': unique_ips(today_start, now),
        'week': unique_ips(week_start, now),
        'month': unique_ips(month_start, now),
        'year': unique_ips(year_start, now),
    }
    return JsonResponse({'summary': data})
