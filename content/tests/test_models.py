import pytest
from django.test import TestCase
from content.models import Article
from content.tests.factories import PublisherFactory, ArticleFactory


class PublisherTestCase(TestCase):
    def test_str(self):
        publisher = PublisherFactory()
        EXPECTED_RESULT = publisher.name

        assert str(publisher) == EXPECTED_RESULT


class ArticleTestCase(TestCase):
    def setUp(self):
        self.article = ArticleFactory()

    def test_str(self):
        EXPECTED_RESULT = f"{self.article.publisher.name} | {self.article.title}"

        assert str(self.article) == EXPECTED_RESULT

    def test_set_status__success(self):
        EXPECTED_STATUS = Article.STATUS_CONTENT_FETCHED

        assert self.article.status != EXPECTED_STATUS

        self.article.set_status(EXPECTED_STATUS)

        self.article.refresh_from_db()
        assert self.article.status == EXPECTED_STATUS

    def test_set_status__assertions_error(self):
        with pytest.raises(AssertionError):
            self.article.set_status("dummy")
