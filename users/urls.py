from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, LogoutAPIView, csrf


urlpatterns = [
    path('auth/register/', RegistrationAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('csrf/', csrf, name='csrf')
]