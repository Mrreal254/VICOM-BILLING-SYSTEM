from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Lightweight liveness/readiness endpoint for deployment checks."""
    database = "ok"
    status_code = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        database = "error"
        status_code = 503

    return JsonResponse(
        {
            "status": "ok" if status_code == 200 else "degraded",
            "service": "vicom-billing-system",
            "database": database,
        },
        status=status_code,
    )
