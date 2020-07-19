from django.urls import path, include
from rest_framework import routers

from .views import FriendshipViewSet

router = routers.DefaultRouter()

router.register('friends', FriendshipViewSet)

app_name = 'friendship'

urlpatterns = [
    path('', include(router.urls)),
]
