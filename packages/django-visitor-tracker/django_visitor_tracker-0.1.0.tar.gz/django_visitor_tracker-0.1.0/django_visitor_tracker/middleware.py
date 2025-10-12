import logging
from .models import LogEntry
from user_agents import parse as parse_ua

# Initialize a logger for this module
logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Extract the client's IP address from the request.
    Checks the X-Forwarded-For header first (used with proxies),
    otherwise falls back to REMOTE_ADDR.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def parse_ua_info(user_agent):
    """
    Parse the user-agent string using the 'user_agents' library.
    Returns (os_name, browser_name).
    """
    if not user_agent:
        return "", ""
    try:
        ua = parse_ua(user_agent)
        print("ua =========== >>>> ", ua)
        os = ua.os.family or ""
        browser = ua.browser.family or ""
        return os, browser
    except Exception:
        # Return empty strings if parsing fails
        return "", ""


class RequestLoggingMiddleware:
    """
    Custom Django middleware that logs every HTTP request to the database.

    ⚠️ Note: Writing to the DB for every request can be expensive.
    In production, consider batching, sampling, or asynchronous logging.
    """

    def __init__(self, get_response):
        # Django passes get_response so middleware can call the next step
        self.get_response = get_response

    def __call__(self, request):
        """
        Called for each request.
        - Calls the next middleware/view
        - Then logs the request/response details to LogEntry table.
        """
        response = self.get_response(request)

        try:
            # Identify user if logged in
            user = None
            if (
                hasattr(request, "user")
                and request.user
                and request.user.is_authenticated
            ):
                user = request.user

            # Extract and parse the user-agent
            ua_string = request.META.get("HTTP_USER_AGENT", "")
            print("ua_string ============ >>>>  ", ua_string)
            os, browser = parse_ua_info(ua_string)

            # Save request info in the LogEntry model
            LogEntry.objects.create(
                path=request.path[:500],
                method=request.method,
                user=user,
                ip=get_client_ip(request) or "",
                status_code=getattr(response, "status_code", None),
                user_agent=ua_string[:1000],
                os=os,
                browser=browser,
            )
        except Exception:
            # If logging fails, log it to server logs but do not break the request
            logger.exception("RequestLogger: failed to record request")

        return response
