import djoser.views
from rest_framework.permissions import IsAuthenticated

from .views import AddUserViewSet

ORIGINAL_GET_PERMISSIONS = djoser.views.UserViewSet.get_permissions


def custom_get_permissions(self):
    if self.action == "me":
        self.permission_classes = [IsAuthenticated]
    return ORIGINAL_GET_PERMISSIONS(self)


djoser.views.UserViewSet.get_permissions = custom_get_permissions
djoser.views.UserViewSet = AddUserViewSet
