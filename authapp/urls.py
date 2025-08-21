from django.urls import path
from .views import SCIMUserView, SCIMGroupView

urlpatterns = [
    path('scim/users', SCIMUserView.as_view(), name='scim_users'),
    path('scim/groups', SCIMGroupView.as_view(), name='scim_groups'),
]
