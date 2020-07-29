from django.urls import path
from .views import StoryCreateAPI

urlpatterns = [
    path('create_story/', StoryCreateAPI.as_view(), name='create_story'),
]
