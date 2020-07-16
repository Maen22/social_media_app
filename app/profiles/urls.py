from django.urls import path, include
from .views import ProfileViewSet, SearchForProfiles
from rest_framework import routers

router = routers.DefaultRouter()

router.register('profiles', ProfileViewSet, basename='api/v1')

urlpatterns = [
    path('profile_search/', SearchForProfiles.as_view()),
    path('', include(router.urls)),
]