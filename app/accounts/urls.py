from django.urls import path, include
from rest_framework import routers

from .views import UserRelatedView, ActivateUserView

router = routers.DefaultRouter()

router.register('users', UserRelatedView, basename='api/v1')

urlpatterns = [
    path('', include(router.urls)),
]
