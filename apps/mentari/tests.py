from django.test import TestCase, Client
from django.urls import reverse
from apps.mentari.models import ConversationEntry, ReflectionEntry, EssaySubmission

class MentariIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_emotion_chat(self):
        response = self.client.post(
            reverse("mentari:emotion_chat"),
            content_type="application/json",
            data='{"message": "I feel stuck on this problem."}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(ConversationEntry.objects.count(), 1)

    def test_reflection_submission(self):
        response = self.client.post(
            reverse("mentari:submit_reflection"),
            content_type="application/json",
            data='{"message": "Today I learned about derivatives."}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReflectionEntry.objects.count(), 1)

    def test_essay_feedback(self):
        essay = "This is my college essay. I worked hard and learned a lot."
        response = self.client.post(
            reverse("mentari:essay_feedback"),
            content_type="application/json",
            data=f'{{"text": "{essay}"}}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("feedback", response.json())
        self.assertEqual(EssaySubmission.objects.count(), 1)

    def test_algebra_solver(self):
        response = self.client.post(
            reverse("mentari:math_support"),
            content_type="application/json",
            data='{"topic": "algebra", "question": "2*x + 3 = 7"}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Solution", response.json()["result"])

    def test_geometry_solver(self):
        response = self.client.post(
            reverse("mentari:math_support"),
            content_type="application/json",
            data='{"topic": "geometry", "a": "3", "b": "4"}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hypotenuse", response.json()["result"])

    def test_trig_solver(self):
        response = self.client.post(
            reverse("mentari:math_support"),
            content_type="application/json",
            data='{"topic": "trigonometry", "question": "sin(x)**2 + cos(x)**2"}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Simplified", response.json()["result"])

    def test_calculus_solver(self):
        response = self.client.post(
            reverse("mentari:math_support"),
            content_type="application/json",
            data='{"topic": "calculus", "question": "x**2"}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Derivative", response.json()["result"])

    def test_plot_expression(self):
        response = self.client.post(
            reverse("mentari:plot_expression"),
            content_type="application/json",
            data='{"expression": "x**2"}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["image"].startswith("data:image/png"))

