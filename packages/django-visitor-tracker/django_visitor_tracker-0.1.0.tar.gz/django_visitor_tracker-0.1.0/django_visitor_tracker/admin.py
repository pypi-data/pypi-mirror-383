from django.contrib import admin
from django.template.response import TemplateResponse
import base64
from django.db.models import Count

from .models import LogEntry
from . import utils


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "path", "ip", "user", "status_code", "os", "browser")
    list_filter = ("status_code", "os", "browser")
    search_fields = ("path", "ip", "user__username")

    # Use a custom admin template for the LogEntry changelist
    change_list_template = "admin/django_visitor_tracker/logentry/change_list.html"

    def changelist_view(self, request, extra_context=None):
        """
        Customizes the changelist view to include charts and analytics.
        This method prepares data and passes it to the admin template.
        """

        # Get aggregated visitor data for the last 30 days
        aggregates = utils.get_aggregates(period="day", span=30)

        # Generate a line chart (as PNG bytes) and encode it in base64 for HTML embedding
        img = utils.plot_aggregates_to_png(
            aggregates, title="Unique IPs — last 30 days"
        )
        img_b64 = base64.b64encode(img).decode("ascii")

        # Calculate OS distribution among visitors (top 20)
        os_data = (
            LogEntry.objects.values("os")
            .annotate(count=Count("id"))
            .order_by("-count")[:20]
        )
        os_labels = [
            item["os"] or "Unknown" for item in os_data
        ]  # Replace None with 'Unknown'
        os_counts = [item["count"] for item in os_data]

        # Generate a bar chart for OS usage and encode it as base64
        os_chart = utils.plot_bar_chart(os_labels, os_counts, title="Operating Systems")
        os_chart_b64 = base64.b64encode(os_chart).decode("ascii")

        # Prepare extra context for the template
        if extra_context is None:
            extra_context = {}
        extra_context["chart_base64"] = img_b64  # Line chart (unique IPs)
        extra_context["os_chart_base64"] = os_chart_b64  # Bar chart (OS distribution)
        extra_context["aggregates_table"] = utils.aggregates_to_json_serializable(
            aggregates
        )  # Data table

        # Render the changelist view with custom context
        return super().changelist_view(request, extra_context=extra_context)
