
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class PredictorTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_predictor_page_loads(self):
        response = self.client.get(reverse('predictor'))
        self.assertEqual(response.status_code, 302)  # Redirects if not logged in

    def test_prediction_valid_input(self):
        # Log in the user
        login = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login)

        # Post valid data to predictor view
        response = self.client.post(reverse('predictor'), {
            'batting_team': 'India',
            'bowling_team': 'Australia',
            'city': 'Mumbai',
            'current_score': 90,
            'overs': 10,
            'wickets': 2,
            'last_five': 30,
        })

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if 'prediction' is in the context data returned by the view
        self.assertIn('prediction', response.context)

        # Optionally check if prediction is a number
        self.assertIsInstance(response.context['prediction'], int)
