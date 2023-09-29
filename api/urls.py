from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name ='index'),
    path('register', RegisterView.as_view(), name ='register'),
    path('verify_email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('login', LoginView.as_view(), name ='login'),
    path('logout', LogoutView, name='logout'),
    path('home', HomeView, name ='home'),
    path('services', ServicesView, name ='services'),
    path('regenerate-verification-email', RegenerateVerificationEmailView.as_view(), name='regenerate_verification_email'),
    path('api/spam_classifier', SpamClassifierApi.as_view(), name ='api_sc'),    
]