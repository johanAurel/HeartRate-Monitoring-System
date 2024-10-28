# myapp/middleware.py

class UserContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Assume you have a way to get the user from the request
        user = request.user
        # Store user-related info in the request for later use
        request.user_context = user.username if user.is_authenticated else None

        response = self.get_response(request)
        return response
