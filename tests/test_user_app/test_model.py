import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model
from users.models import Role

User = get_user_model()

@pytest.mark.django_db
class TestCustomUser:

    @pytest.fixture
    def user(self):
        return baker.make(User)

    def test_create_user_with_baker(self, user):
        assert user.id is not None
        assert user.role in [Role.ADMIN, Role.MANAGER, Role.USER]

    def test_create_admin(self):
        admin_user = baker.make(User, role=Role.ADMIN)
        assert admin_user.role == Role.ADMIN

    def test_user_password(self):
        user = baker.make(User)
        user.set_password('12zxZX12')
        user.save()
        assert user.check_password('12zxZX12')

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin123@gmail.com',
            password='12zxZX12'
        )
        assert user.is_superuser
        assert user.is_staff


