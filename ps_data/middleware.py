from .models import VisitCount, VisitRecord


class VisitCountMiddleware:
    """
    Middleware to track page visits.
    Records each request's path and increments the visit count.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Track visit count only for successful GET requests (excluding static files and admin)
        if (request.method == 'GET' and
            response.status_code == 200 and
            not request.path.startswith('/static/') and
            not request.path.startswith('/admin/')):

            try:
                # Increment visit count for this page
                VisitCount.increment(request.path)

                # Record individual visit for analytics
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                VisitRecord.objects.create(
                    page_url=request.path,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                # Silently fail if there's an error to not break the application
                print(f"Error tracking visit: {e}")

        return response

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
