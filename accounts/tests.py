from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword123!',
        )
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_successful_login_returns_jwt_tokens(self):
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login_returns_401(self):
        data = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RBACRegistrationTests(APITestCase):
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='AdminPassword123!',
            role='ADMIN' 
        )

        self.normal_user = User.objects.create_user(
            username='standard_user',
            password='StandardPassword123!',
            role='EDITOR'
        )

        self.register_url = reverse('create-user')
        
        self.new_user_data = {
            'username': 'new_employee',
            'password': 'SecurePassword123!',
            'role': 'VIEWER'
        }

    def test_admin_can_create_new_user(self):
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(self.register_url, self.new_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='new_employee').exists())

    def test_normal_user_cannot_create_new_user(self):
        self.client.force_authenticate(user=self.normal_user)
        
        response = self.client.post(self.register_url, self.new_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username='new_employee').exists())

    def test_unauthenticated_user_cannot_create_new_user(self):
        response = self.client.post(self.register_url, self.new_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)