from django.test import TestCase
from django.urls import reverse
from content.models import Article
from content.tests.factories import ArticleFactory


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.URL = reverse("content:article_list")

    def test_no_articles(self):
        response = self.client.get(self.URL)

        assert response.status_code == 200
        assert len(response.context["articles"]) == 0

    def test_only_articles_with_sentiment_are_shown(self):
        for _ in range(3):
            ArticleFactory(status=Article.STATUS_RESPONSE_ERROR)
        for _ in range(4):
            ArticleFactory(status=Article.STATUS_SENTIMENT_ERROR)
        for _ in range(5):
            ArticleFactory(status=Article.STATUS_SENTIMENT_SET)

        response = self.client.get(self.URL)

        assert response.status_code == 200
        assert len(response.context["articles"]) == 5
