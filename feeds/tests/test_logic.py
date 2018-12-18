import pendulum
from django.test import TestCase
from content.models import Article
from content.tests.factories import ArticleFactory
from feeds.logic import ParseFeeds
from feeds.tests.factories import FeedFactory, FeedItemFactory
from feedparser import FeedParserDict


class ParseFeedsTestCase(TestCase):
    def test_get_single_item_published_time__with_timezone(self):
        EXPECTED_RESULT = pendulum.datetime(
            2018, 12, 17, 16, 19, 00, tz="America/New_York"
        )
        parser = ParseFeeds()

        item = FeedParserDict()
        item["published"] = "Mon, 17 Dec 2018 16:19:00 -0500"

        RESULT = parser.get_single_item_published_time(item)
        assert RESULT == EXPECTED_RESULT

    def test_get_single_item_published_time__without_timezone(self):
        EXPECTED_RESULT = pendulum.datetime(2018, 12, 17, 16, 19, 00, tz="UTC")
        parser = ParseFeeds()

        item = FeedParserDict()
        item["published"] = "Mon, 17 Dec 2018 16:19:00"

        result = parser.get_single_item_published_time(item)
        assert result == EXPECTED_RESULT

    def test_get_single_item_published_time__with_gmt(self):
        EXPECTED_RESULT = pendulum.datetime(2018, 12, 17, 16, 19, 00, tz="UTC")
        parser = ParseFeeds()

        item = FeedParserDict()
        item["published"] = "Mon, 17 Dec 2018 16:19:00 GMT"

        result = parser.get_single_item_published_time(item)
        assert result == EXPECTED_RESULT

    def test_create_article_from_feed_item__success(self):
        feed_item = FeedItemFactory()

        parser = ParseFeeds()

        RESULT = parser.create_article_from_feed_item(feed_item)

        assert RESULT.uri == feed_item.uri
        assert RESULT.title == feed_item.title
        assert RESULT.published_ts == feed_item.published_ts
        assert RESULT.status == Article.STATUS_CREATED

    def test_create_article_from_feed_item__article_exists(self):
        feed_item = FeedItemFactory()

        ArticleFactory(uri=feed_item.uri)

        parser = ParseFeeds()

        RESULT = parser.create_article_from_feed_item(feed_item)
        assert RESULT is None
