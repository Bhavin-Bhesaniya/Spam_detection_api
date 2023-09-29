from rest_framework import serializers
from .models import MyUser
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class SpamClassifierSerializer(serializers.Serializer):
    user_message = serializers.CharField(max_length=100)
    user_selected_model = serializers.CharField(max_length=100)


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=16, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=16, style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        print(user)
        if password != password2:
            raise serializers.ValidationError('Password does not match')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if MyUser.objects.filter(email=email).exists():
            user = MyUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:8000/api/user/reset_password/' + uid + '/' + token
            print(link)
            # Email 
            data = {
                'subject': 'Reset Password',
                'body' : link,
                'to': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationError('Not registed user')
    

class UserResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=16, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=16, style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError('Password does not match')
            id = smart_str(urlsafe_base64_decode(uid))
            user = MyUser.objects.get(id=id)
            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(password)
                user.save()
                return attrs
            else:
                raise ValidationError('Token does not match or expired')
        except DjangoUnicodeDecodeError as e:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError('Token is not Valid') 

"""
{
  "email": "test@gmail.com",
  "name": "tester",
  "password": "Bh@vin12.",
}
"""