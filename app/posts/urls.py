from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet

router = routers.DefaultRouter()

router.register('posts', PostViewSet)

app_name = 'posts'

urlpatterns = [
    path('', include(router.urls)),
]
