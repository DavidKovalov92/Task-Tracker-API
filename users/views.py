from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializer import UserRegistrationSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .permissions import RoleHelper

User = get_user_model()

class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            login(request, user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            return Response({"detail": "Logged in"}, status=200)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

 
class GetUserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if RoleHelper.is_admin(user):
            return User.objects.all()
        elif RoleHelper.is_manager(user):
            return User.objects.filter(teams__members=user).distinct()
        else:
            return User.objects.none()

