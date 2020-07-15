from django.urls import path, include
from rest_framework import routers

from .views import UserRelatedView, ActivateUserView

router = routers.DefaultRouter()

router.register('users', UserRelatedView, basename='api/v1')

urlpatterns = [
    path('activate/<int:pk>/<str:token>/', ActivateUserView.as_view()),
    path('', include(router.urls)),
]
