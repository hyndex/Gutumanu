from .models import AuditLog


class AuditLogMiddleware:
    """Middleware that records each request in the audit log."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            user = request.user if request.user.is_authenticated else None
            body = ''
            if request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    body = request.body.decode('utf-8')
                except Exception:
                    body = ''
            AuditLog.objects.create(
                user=user,
                method=request.method,
                path=request.get_full_path(),
                ip_address=request.META.get('REMOTE_ADDR'),
                body=body,
            )
        except Exception:
            # Avoid breaking requests due to audit issues
            pass
        return response
