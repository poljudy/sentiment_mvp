from django.test import TestCase
from content.tests.factories import PublisherFactory, ArticleFactory


class PublisherTestCase(TestCase):
    def test_str(self):
        publisher = PublisherFactory()
        EXPECTED_RESULT = publisher.name

        assert str(publisher) == EXPECTED_RESULT


class ArticleTestCase(TestCase):
    def test_str(self):
        article = ArticleFactory()
        EXPECTED_RESULT = f"{article.publisher.name} | {article.title}"

        assert str(article) == EXPECTED_RESULT
