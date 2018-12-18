import feedparser
import logging
import pendulum
from typing import Optional
from datetime import datetime
from django.db import IntegrityError
from content.models import Article
from .models import Feed, FeedItem


logger = logging.getLogger(__name__)


class ParseFeeds:
    """Parses feeds rss pages and saves new entries to the db.
    """

    def __init__(self):
        """Set feed instance as attribute.

        Args:
            feed: Feed object from the db
        """
        self.parse_feeds()

    def parse_feeds(self):
        """Go through all the feeds in the system and fetch new articles.
        """
        for feed in Feed.objects.all():
            self.fetch_feed_items(feed)

    def fetch_feed_items(self, feed):
        """Go through each item in feed and save it if new.
        """
        live_feed = feedparser.parse(feed.uri)
        for item in live_feed.entries:
            self.save_single_item(feed, item)

        feed.last_fetch_ts = pendulum.now("UTC")
        feed.save()

    def save_single_item(self, feed: Feed, item: feedparser.FeedParserDict) -> FeedItem:
        """Save single item from rss feed into db as FeedItem instance.

        If item is newly created also created accompanying article.

        Args:
            feed: Feed object from the db
            item: parsed feedparser single item

        Returns:
            new or existing FeedItem instance
        """
        item_published = self.get_single_item_published_time(item)

        feed_item, feed_item_created = FeedItem.objects.get_or_create(
            uri=item.link,
            defaults={
                "feed": feed,
                "title": item.title,
                "published_ts": item_published,
            },
        )

        if feed_item_created:
            article = self.create_article_from_feed_item(feed_item)
            if article:
                feed_item.article = article
                feed_item.save()

        return feed_item

    def get_single_item_published_time(
        self, item: feedparser.FeedParserDict
    ) -> pendulum.datetime:
        """Parse rss item's stringified published time into datetime object.

        Atom feed datetime string is standardized so there should be no
        problem there.

        Timestamp examples:
        - Mon, 17 Dec 2018 16:19:00 -0500
        - Mon, 17 Dec 2018 22:08:27 GMT

        Args:
            item: parsed feedparser single item

        Returns:
            datetime object
        """
        try:
            return pendulum.from_format(item.published, "ddd, D MMM YYYY H:mm:ss ZZ")
        except ValueError:
            # fallback to UTC since some feeds send dates with GMT as timezone
            return pendulum.from_format(item.published, "ddd, D MMM YYYY H:mm:ss")

    def create_article_from_feed_item(self, feed_item: FeedItem) -> Optional[Article]:
        """Create an Article object from provided FeedItem object.

        Article in this phase does not have content yet, only info where to get
        the content.

        Args:
            feed_item: FeedItem object from the db

        Returns:
            new Article object with same uri or None
        """
        try:
            article = Article.objects.create(
                publisher=feed_item.feed.publisher,
                uri=feed_item.uri,
                title=feed_item.title,
                status=Article.STATUS_CREATED,
                published_ts=feed_item.published_ts,
            )
            feed_item.article = article
            feed_item.save()
            return article
        except IntegrityError:
            logger.exception(f"Article {feed_item.uri} was already created.")
            return None
