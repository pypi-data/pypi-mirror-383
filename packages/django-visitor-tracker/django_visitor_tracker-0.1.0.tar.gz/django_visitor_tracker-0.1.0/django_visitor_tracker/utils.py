from io import BytesIO
import datetime
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone

import matplotlib

# Use the non-interactive Agg backend so matplotlib can render images
# on servers without a display (headless mode).
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .models import LogEntry


def _choose_trunc(period):
    """
    Return the appropriate Trunc* function depending on the period string.
    This is used to group timestamps by day/week/month/year in the DB query.
    """
    if period == "day":
        return TruncDay
    if period == "week":
        return TruncWeek
    if period == "month":
        return TruncMonth
    if period == "year":
        return TruncYear
    # default fallback: group by day
    return TruncDay


def get_aggregates(period="day", span=30):
    """
    Query the LogEntry table and return aggregated data.

    Args:
      period (str): one of 'day'|'week'|'month'|'year' — determines truncation.
      span (int): number of periods to look back (e.g. 30 days).

    Returns:
      list of dicts, each dict has keys:
        'period' (datetime) - the truncated datetime bucket,
        'unique_ips' (int) - number of distinct IPs in that bucket,
        'visits' (int) - total number of LogEntry rows in that bucket.
    """
    now = timezone.now()

    # Decide the start time according to the period
    if period == "day":
        start = now - datetime.timedelta(days=span - 1)
    elif period == "week":
        start = now - datetime.timedelta(weeks=span - 1)
    # NOTE: below two branches currently ignore `span` and subtract a fixed time.
    elif period == "month":
        start = now - datetime.timedelta(days=30)
    elif period == "year":
        start = now - datetime.timedelta(days=365)
    else:
        start = now - datetime.timedelta(days=span - 1)

    trunc = _choose_trunc(period)

    # Filter rows in the time window
    qs = LogEntry.objects.filter(timestamp__gte=start, timestamp__lte=now)

    # Annotate each row with a truncated 'period', then group by that period
    # and compute:
    #   unique_ips = Count('ip', distinct=True)
    #   visits = Count('id')  (total rows)
    # output will be like below:
    # [
    #     {'day': datetime.date(2025, 10, 1), 'count': 32},
    #     {'day': datetime.date(2025, 10, 2), 'count': 45},
    #     {'day': datetime.date(2025, 10, 3), 'count': 27},
    # ]
    agg_qs = (
        qs.annotate(period=trunc("timestamp"))
        .values("period")
        .annotate(unique_ips=Count("ip", distinct=True), visits=Count("id"))
        .order_by("period")
    )

    # Convert queryset to a list of simple dicts
    return [
        {
            "period": item["period"],
            "unique_ips": item["unique_ips"],
            "visits": item["visits"],
        }
        for item in agg_qs
    ]


def plot_aggregates_to_png(aggregates, title="Visits (unique IPs)"):
    """
    Take the aggregates (from get_aggregates) and draw a line chart,
    returning PNG bytes. to show number of unique IPs that are visted our website

    Args:
      aggregates (list of dicts): output of get_aggregates
      title (str): chart title

    Returns:
      bytes: PNG image bytes
    """
    if not aggregates:
        # Small fallback image if there's no data
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        # Prepare x (period datetimes) and y (unique IP counts)
        x = [a["period"] for a in aggregates]
        y = [a["unique_ips"] for a in aggregates]
        fig, ax = plt.subplots(figsize=(10, 3))
        # Custom line style, color and marker
        ax.plot(x, y, ls=":", color="purple", marker="*")
        ax.set_title(title)
        ax.set_ylabel("Unique IPs")
        # Improve x-axis date label formatting
        fig.autofmt_xdate()

    # Render figure to an in-memory bytes buffer (PNG)
    buf = BytesIO()
    fig.savefig(buf, bbox_inches="tight")
    # Close the figure to release memory
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def plot_bar_chart(labels, values, title="Bar Chart"):
    """
    Create a bar chart from labels and values and return PNG bytes.

    Args:
      labels (list[str]) : category labels (x-axis)
      values (list[int]) : heights of bars
      title (str): chart title

    Returns:
      bytes: PNG image bytes
    """
    if not labels or not values:
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        fig, ax = plt.subplots(figsize=(8, 3))
        # Note: width=0.1 might produce very narrow bars; alpha for transparency
        ax.bar(range(len(values)), values, width=0.1, alpha=0.5, color="hotpink")
        ax.set_xticks(range(len(values)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_title(title)
        ax.set_ylabel("Count")

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def aggregates_to_json_serializable(aggregates):
    """
    Convert aggregates output (with datetime objects) into JSON-friendly
    structures by serializing datetime to ISO strings.

    Args:
      aggregates (list of dict): each dict contains 'period' (datetime), 'unique_ips', 'visits'

    Returns:
      list of dict: same data, but 'period' is an ISO-formatted string
    """
    out = []
    for a in aggregates:
        period = a["period"]
        out.append(
            {
                "period": period.isoformat(),
                "unique_ips": a["unique_ips"],
                "visits": a["visits"],
            }
        )
    return out
