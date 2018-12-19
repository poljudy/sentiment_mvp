import pendulum
import vcr
from django.test import TestCase
from content.models import Article
from content.tests.factories import PublisherFactory, ArticleFactory
from feeds.logic import ParseFeeds
from feeds.models import Feed, FeedItem
from feeds.tests.factories import FeedFactory, FeedItemFactory
from feedparser import FeedParserDict


VCR_ROOT = "feeds/tests/fixtures/vcr"


class ParseFeedsTestCase(TestCase):
    @vcr.use_cassette(f"{VCR_ROOT}/parse_feeds__success.yaml")
    def test_parse_feeds__sucess(self):
        # first feed created as part of initial data migration
        feed_1 = Feed.objects.get(uri="https://www.forbes.com/real-time/feed2/")
        feed_2 = FeedFactory(uri="https://www.forbes.com/business/feed/")

        assert FeedItem.objects.filter(feed=feed_1).count() == 0
        assert FeedItem.objects.filter(feed=feed_2).count() == 0

        parser = ParseFeeds()
        parser.parse_feeds()

        assert FeedItem.objects.filter(feed=feed_1).count() == 20
        assert FeedItem.objects.filter(feed=feed_2).count() == 101

    @vcr.use_cassette(f"{VCR_ROOT}/fetch_feed__success.yaml")
    def test_fetch_feed_items__success(self):
        # pendulum has builtin mechanism for mocking now
        MOCKED_LAST_FETCH_TS = pendulum.datetime(2018, 12, 18, 12, 00)
        pendulum.set_test_now(MOCKED_LAST_FETCH_TS)

        feed = FeedFactory(uri="https://www.forbes.com/energy/feed/")

        assert FeedItem.objects.filter(feed=feed).count() == 0

        parser = ParseFeeds()
        parser.fetch_feed_items(feed)

        feed.refresh_from_db()
        assert FeedItem.objects.filter(feed=feed).count() == 99
        assert feed.last_fetch_ts == MOCKED_LAST_FETCH_TS

    @vcr.use_cassette(f"{VCR_ROOT}/fetch_feed__not_rss.yaml")
    def test_fetch_feed_items__not_rss(self):
        feed = FeedFactory(uri="https://www.forbes.com/")

        assert FeedItem.objects.filter(feed=feed).count() == 0

        parser = ParseFeeds()
        parser.fetch_feed_items(feed)

        assert FeedItem.objects.filter(feed=feed).count() == 0

    def test_fetch_feed_items__not_url(self):
        feed = FeedFactory(uri="dummy")

        assert FeedItem.objects.filter(feed=feed).count() == 0

        parser = ParseFeeds()
        parser.fetch_feed_items(feed)

        assert FeedItem.objects.filter(feed=feed).count() == 0

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
