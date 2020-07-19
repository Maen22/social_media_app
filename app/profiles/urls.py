from django.urls import path, include
from .views import ProfileViewSet, SearchForProfiles
from rest_framework import routers

router = routers.DefaultRouter()

router.register('profiles', ProfileViewSet)

app_name = 'profile'

urlpatterns = [
    path('', include(router.urls)),
    path('profile_search/', SearchForProfiles.as_view()),

]