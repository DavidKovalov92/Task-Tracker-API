import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestUserViews:

    def setup_method(self):
        self.client = APIClient()

    def test_register_user_api(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'apiuser',
            'email': 'api@test.com',
            'password': '1234Abcd'
        })

        assert response.status_code == 200
        assert 'id' in response.data

    def test_login_user_api(self, django_user_model):
        django_user_model.objects.create_user(
            username='apiuser2',
            password='1234Abcd'
        )
        response = self.client.post('/api/auth/login/', {
            'username': 'apiuser2',
            'password': '1234Abcd'
        })
        assert response.status_code == 200
        assert response.data['detail'] == 'Logged in'

    def test_get_users_permission_denied(self, django_user_model):
        user = django_user_model.objects.create_user(
            username='regular',
            password='1234Abcd'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/users/')
        assert response.status_code == 403
