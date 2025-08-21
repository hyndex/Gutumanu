from django.http import JsonResponse
from django.views import View


class SCIMUserView(View):
    """Basic SCIM endpoint for users."""
    def get(self, request):
        return JsonResponse({'Resources': []})

    def post(self, request):
        return JsonResponse({'status': 'created'}, status=201)


class SCIMGroupView(View):
    """Basic SCIM endpoint for groups."""
    def get(self, request):
        return JsonResponse({'Resources': []})

    def post(self, request):
        return JsonResponse({'status': 'created'}, status=201)
