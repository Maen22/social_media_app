from rest_framework import serializers

from .models import Story


class StorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='full_name')

    class Meta:
        model = Story
        fields = ('owner', 'text', 'created_at')

    def create(self, validated_data):
        user = self.context.get('request').user.profile
        story = Story.objects.create_story(user=user, **validated_data)
        return story
