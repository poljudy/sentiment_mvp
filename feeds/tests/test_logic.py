import pendulum
from django.test import TestCase
from content.models import Article
from content.tests.factories import ArticleFactory
from feeds.logic import ParseFeeds
from feeds.models import FeedItem
from feeds.tests.factories import FeedFactory, FeedItemFactory
from feedparser import FeedParserDict


class ParseFeedsTestCase(TestCase):
    def test_save_single_item__is_created_with_article(self):
        feed = FeedFactory()

        item = FeedParserDict()
        item["published"] = "Mon, 17 Dec 2018 16:19:00 -0500"
        item["title"] = "Dummy title"
        item["link"] = "https://example.com/article.html"

        parser = ParseFeeds()

        RESULT = parser.save_single_item(feed, item)

        assert isinstance(RESULT, FeedItem)
        assert RESULT.uri == "https://example.com/article.html"
        assert RESULT.title == "Dummy title"
        assert RESULT.feed == feed

        assert Article.objects.get(uri="https://example.com/article.html")

    def test_save_single_item__is_created_existing_article(self):
        ArticleFactory(uri="https://example.com/article.html")

        feed = FeedFactory()

        item = FeedParserDict()
        item["published"] = "Mon, 17 Dec 2018 16:19:00 -0500"
        item["title"] = "Dummy title"
        item["link"] = "https://example.com/article.html"

        parser = ParseFeeds()

        RESULT = parser.save_single_item(feed, item)

        assert isinstance(RESULT, FeedItem)
        assert RESULT.uri == "https://example.com/article.html"
        assert RESULT.title == "Dummy title"
        assert RESULT.feed == feed

    def test_save_single_item__is_existing(self):
        feed = FeedFactory()
        feed_item = FeedItemFactory(feed=feed)

        item = FeedParserDict()

        item["published"] = pendulum.instance(
            feed_item.published_ts
        ).to_rfc1123_string()
        item["title"] = feed_item.title
        item["link"] = feed_item.uri

        parser = ParseFeeds()

        RESULT = parser.save_single_item(feed, item)

        assert isinstance(RESULT, FeedItem)
        assert RESULT.uri == feed_item.uri
        assert RESULT.title == feed_item.title
        assert RESULT.feed == feed_item.feed

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
