from django.test import TestCase
from feeds.tests.factories import FeedFactory, FeedItemFactory


class FeedTestCase(TestCase):
    def test_str(self):
        feed = FeedFactory()
        EXPECTED_RESULT = feed.title

        assert str(feed) == EXPECTED_RESULT


class FeedItemTestCase(TestCase):
    def test_str(self):
        feed_item = FeedItemFactory()
        EXPECTED_RESULT = feed_item.title

        assert str(feed_item) == EXPECTED_RESULT
