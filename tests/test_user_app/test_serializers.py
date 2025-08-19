import pytest 
from users.serializers import UserRegistrationSerializer, LoginSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserSerilaizer:

    def test_registration_serializer(self):
        data = {'username': 'testuser', 'email': 'kovalovdavid92@gmail.com', 'password': '12zxZX12'}
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == 'testuser'
        assert user.email == 'kovalovdavid92@gmail.com'
        assert user.check_password('12zxZX12')

    def test_login_serializer(self, django_user_model):
        user = django_user_model.objects.create(username='testuser', email='kovalovdavid92@gmail.com')
        user.set_password('12zxZX12')
        user.save()
        serializer = LoginSerializer(data={'username': 'testuser', 'email': 'kovalovdavid92@gmail.com', 'password': '12zxZX12'})
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user

    def test_login_fail_serializer(self, django_user_model):
        serializer = LoginSerializer(data={'username': '12', 'email': '21@gmail.com', 'password': '12'})
        assert not serializer.is_valid()