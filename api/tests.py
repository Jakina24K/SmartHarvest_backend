from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Users  # Adapte selon ton nom d'app
from rest_framework import status

class UserProfileUpdateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.profile = Users.objects.create(user=self.user, localisation='Tana')

        # Authentifie l'utilisateur
        self.client.login(username='testuser', password='testpass123')

    def test_update_user_profile(self):
        url = '/api/users/me/'  # adapte selon ton router DRF
        data = {
            "user": {
                "username": "updateduser",
                "email": "new@example.com",
                "password": "newpass456"
            },
            "localisation": "Fianarantsoa"
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.profile.localisation, "Fianarantsoa")
        self.assertTrue(self.user.check_password("newpass456"))

    def test_get_user_profile(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testuser")
