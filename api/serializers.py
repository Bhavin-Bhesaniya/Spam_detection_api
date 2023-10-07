from rest_framework import serializers
from .models import MyUser
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SpamClassifierSerializer(serializers.Serializer):
    user_message = serializers.CharField(max_length=100)
    user_selected_model = serializers.CharField(max_length=100)