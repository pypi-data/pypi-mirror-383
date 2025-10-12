import os

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from django_visitor_tracker.middleware import RequestLoggingMiddleware
from django_visitor_tracker.models import LogEntry


class MiddlewareLoggingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass")

    def test_middleware_records_request_unauthenticated(self):
        def get_response(req):
            class R:
                status_code = 200

            return R()

        mw = RequestLoggingMiddleware(get_response)
        request = self.factory.get("/some/path")
        mw(request)

        self.assertTrue(LogEntry.objects.exists())
        entry = LogEntry.objects.first()
        self.assertEqual(entry.path, "/some/path")

    def test_middleware_records_user_and_ua(self):
        def get_response(req):
            class R:
                status_code = 200

            return R()

        mw = RequestLoggingMiddleware(get_response)
        request = self.factory.get(
            "/u/path", HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        request.user = self.user
        mw(request)

        entry = LogEntry.objects.filter(path="/u/path").first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.user.username, "tester")
        self.assertTrue(entry.os is not None)
        self.assertTrue(entry.browser is not None)


class ViewsTests(TestCase):
    def test_counts_view_empty(self):
        url = "/django-visitor-tracker/counts/"
        # call view directly
        from django.test import RequestFactory

        from django_visitor_tracker.views import summary_counts

        rf = RequestFactory()
        request = rf.get("/dummy")
        response = summary_counts(request)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
