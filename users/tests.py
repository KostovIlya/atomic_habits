from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class RegisterUserTestCase(APITestCase):

    def test_register_user(self):
        """Тестирования регистрации пользователей"""

        data = dict(email="test@test.ru", password="test")

        response_data = dict(email="test@test.ru")

        response = self.client.post('/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), response_data)
        self.assertEqual(str(User.objects.get(email=data['email'])), 'test@test.ru')
