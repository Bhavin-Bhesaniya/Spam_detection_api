from rest_framework import serializers
from .models import MyUser

class SpamClassifierSerializer(serializers.Serializer):
    user_message = serializers.CharField()
    user_selected_model = serializers.CharField(max_length=100)