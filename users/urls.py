from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, LogoutAPIView, csrf, GetUserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', GetUserViewSet, basename='user')

urlpatterns = router + [
    path('auth/register/', RegistrationAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('csrf/', csrf, name='csrf')
]