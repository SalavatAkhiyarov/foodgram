from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import IsAuthenticated

ORIGINAL_GET_PERMISSIONS = DjoserUserViewSet.get_permissions


def custom_get_permissions(self):
    if self.action == "me":
        self.permission_classes = [IsAuthenticated]
    return ORIGINAL_GET_PERMISSIONS(self)


DjoserUserViewSet.get_permissions = custom_get_permissions
