from django.test import TestCase
from .models import ExternalArticle
from django.utils import timezone

class ExternalArticleModelTest(TestCase):
    def test_str_returns_title(self):
        article = ExternalArticle.objects.create(
            title="Black Hole Breakthrough",
            summary="A historic discovery",
            original_url="https://nasa.gov/bhb",
            published_date=timezone.now(),
            tags=["space", "black holes"],
            complexity_level="advanced",
            source="nasa",
            source_name="NASA"
        )
        self.assertEqual(str(article), "Black Hole Breakthrough")
