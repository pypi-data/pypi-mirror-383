from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class LogEntry(models.Model):
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="visitortracker_log_entries",
    )
    ip = models.CharField(max_length=45, db_index=True)
    status_code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Request log entry"
        verbose_name_plural = "Request log entries"

    def __str__(self):
        return f"{self.path} ({self.ip}) @ {self.timestamp:%Y-%m-%d %H:%M:%S}"
