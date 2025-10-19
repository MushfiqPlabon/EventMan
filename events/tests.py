from django.test import TestCase
from django.urls import reverse

class HomeViewTest(TestCase):
    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_context_data(self):
        response = self.client.get(reverse('home'))
        self.assertIn('featured_events', response.context)
        self.assertIn('total_events', response.context)
        self.assertIn('total_categories', response.context)