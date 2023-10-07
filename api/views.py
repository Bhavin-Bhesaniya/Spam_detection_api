from django.views import View
from .forms import UserInputForm, RegistrationForm, LoginForm, RegenerateResetEmailForm, ResetPasswordForm
from .classifier import classify_spam
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import MyUser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
import os
from django.contrib import messages
from .serializers import SpamClassifierSerializer
from django.contrib.sessions.models import Session
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from datetime import timedelta
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.views import PasswordResetView


def get_tokens_for_user_api(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh' : str(refresh),
        'access' : str(refresh.access_token), 
    }


def ratelimit_error(request, exception=None):
    return render(request, 'ratelimit_error.html')


def generate_verification_link(request, email, verification_type):
    user = MyUser.objects.filter(email=email).first()
    if not user:
        raise forms.ValidationError("This email is not associated with any user.")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    current_site = get_current_site(request)
    domain = current_site.domain

    if verification_type == 'password_reset':
        verify_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    else :
        verify_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    
    expiry_time = timezone.now() + timedelta(minutes=2)
    timestamp = int(expiry_time.timestamp())
    request.session['verification_timestamp'] = timestamp     # Store timestamp in the user's session

    verify_url = f'http://{domain}{verify_url}'
    subject = 'Verify your Email'
    message = f'Click the following link to verify your email:\n{verify_url}'
    from_email = os.environ.get('EMAIL_HOST_USER')
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    



@method_decorator(ratelimit(key='ip', rate='10/m', block=True),name="dispatch")
@method_decorator(ratelimit(key='user', rate='10/m', block=True), name="dispatch")
class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        user_input_form = UserInputForm()   
        return render(request, 'index.html', {'user_input_form': user_input_form})

    def post(self, request):
        user_input_form = UserInputForm(request.POST)
        if user_input_form.is_valid():
            user_input = user_input_form.cleaned_data['user_input']
            user_selected_model = user_input_form.cleaned_data['user_selected_model']
            form_submission_count = request.session.get('form_submission_count', 0)
            if form_submission_count >= 10:
                return redirect('register') 
            try:
                result_message = classify_spam(user_input, user_selected_model)
                content = {'user_input_form': user_input_form, 'result_message': result_message}
                request.session['form_submission_count'] = form_submission_count + 1
                return render(request, 'index.html', content)
            except Exception as e:
                error_message = str(e)
                user_input_form.add_error('user_input', error_message)
        else:
            result_message = "Invalid input. Please try again."
            content = {'user_input_form': user_input_form, 'result_message': result_message}
            return render(request, 'index.html', content)
    
        try:
            if request.limited:
                return render(request, 'ratelimit_error.html')
        except Exception as e:
            return render(request, 'ratelimit_error.html')
        return render(request, 'index.html', {'user_input_form': user_input_form})


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email'].strip()
            password = form.cleaned_data['password']
            user = MyUser.objects.create_user(name=name, email=email, password=password, is_email_verified=False)
            if user is not None:
                verification_type = 'register'
                generate_verification_link(request, email, verification_type)
                return render(request, 'mailvalid/checkbox.html')
            else:
                messages.error(request, 'An error occurred during registration.')
                return render(request, 'register.html', {'form': form})
        return render(request, 'register.html', {'form': form})


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = MyUser.objects.get(pk=uid)
            
            if user is not None and not user.is_email_verified:
                if default_token_generator.check_token(user, token):
                    timestamp = request.session.get('verification_timestamp')
                    if timestamp:
                        timestamp = int(timestamp)
                        expiry_time = timezone.make_aware(timezone.datetime.fromtimestamp(timestamp))
                        now = timezone.now()
                        if now <= expiry_time:
                            # Link is considered valid, remove the timestamp from the session
                            del request.session['verification_timestamp']
                            user.is_email_verified = True
                            user.save()
                            return render(request, 'mailvalid/email_verification_success.html')                       
                    else:
                        return render(request, 'mailvalid/email_verification_failure.html', {'email': user.email})
                else:
                    email = user.email
                    return render(request, 'mailvalid/email_verification_failure.html', {'email': email})
            else:
                return render(request, 'mailvalid/email_verification_failure.html')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'mailvalid/email_verification_failure.html')


class LoginView(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('home')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self,request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Please verify your email before logging in.')
                    return render(request, 'login.html', {'form': form})
            else:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})


class RegenerateVerificationEmailView(View):
    def get(self, request):
        form = RegenerateResetEmailForm()
        if request.user.is_authenticated:
            return redirect('home')
        return redirect('register')
        # return render(request, 'mailvalid/email_verification_failure.html', {'form': form})

    def post(self, request):
        form = RegenerateResetEmailForm(request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data['email']
                user = MyUser.objects.filter(email=email).first()
                if user is not None:
                    if user.is_email_verified:
                        messages.error(request, 'Already verified, please log in.')
                        return redirect('login')
                    else:
                        generate_verification_link(request, email)
                        messages.success(request, 'A new verification email has been sent.')
                        return render(request, 'mailvalid/checkbox.html')
                else:
                    messages.error(request, 'Please register your account first')
                    return redirect('register')
            else:
                return render(request, 'mailvalid/email_verification_failure.html', {'form': form})
        except Exception as e:
            messages.error(request, f'Error sending verification email: {str(e)}')
            return redirect('login')  # Redirect to the login page
        else:
            return redirect('home')


@login_required(login_url='login')
def HomeView(request):
    if request.user.is_authenticated:
        user = request.user
        jwttoken = None
        token_generated_today = False

        if request.method == 'POST' and 'generate_token' in request.POST:
            cache_key = f"user_token_{user.id}"
            if cache.get(cache_key):
                token_generated_today = True
            if not cache.get(cache_key):
                jwttoken = get_tokens_for_user_api(user)
                cache.set(cache_key, True, timedelta(days=1).total_seconds())
                subject = 'Your Spam Api generate Token'
                message = f'Please carefully stored your token. \n{jwttoken}'
                from_email = os.environ.get('EMAIL_HOST_USER')
                recipient_list = [user.email]
                send_mail(subject, message, from_email, recipient_list)
        return render(request, 'home.html', {'user': user, 'jwttoken': jwttoken, 'token_generated_today': token_generated_today})


class SpamClassifierApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SpamClassifierSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data.get('user_message')
            user_selected_model = serializer.validated_data.get('user_selected_model')
            message = classify_spam(user_message, user_selected_model)
            if message:
                return Response({"error": message}, status=status.HTTP_200_OK)
            else:
                return Response({"message": message}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        documentation = {
            "Description": "This is API documentation for Spam Classifier API",
            "Endpoints": {
                "POST api/spam-classifier": "Classify user messages for spam. Pass json message in user_message and select model in user_selected_model. Ex - { 'user_message' : 'Your message'}",
                "GET api/spam-classifier": "Retrieve this API documentation.",
            }
        }
        return Response(documentation, status=status.HTTP_200_OK)


class CustomPasswordResetView(PasswordResetView):
    def get(self, request):
        form = ResetPasswordForm(request.POST)
        return render(request, 'reset/password_reset.html', {'form': form})
    
    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = MyUser.objects.filter(email=email).first()
            if user is not None:
                verification_type = 'password_reset'
                generate_verification_link(request, email, verification_type)
                return redirect('password_reset_done')
            else:
                messages.error(request, 'Please register your account first')
                return redirect('register')
        else:
            return render(request, 'reset/password_reset.html', {'form': form})


def ServicesView(request):
    return render(request, 'service.html')

def LogoutView(request):
    logout(request)
    return redirect('login')