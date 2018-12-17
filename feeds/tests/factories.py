import pytz
import factory
from content.tests.factories import PublisherFactory, ArticleFactory
from feeds.models import Feed, FeedItem


class FeedFactory(factory.DjangoModelFactory):
    publisher = factory.SubFactory(PublisherFactory)
    uri = factory.Faker("uri")
    last_fetch_ts = factory.Faker("date_time_this_month", tzinfo=pytz.utc)

    class Meta:
        model = Feed


class FeedItemFactory(factory.DjangoModelFactory):
    feed = factory.SubFactory(FeedFactory)
    uri = factory.Faker("uri")
    article = factory.SubFactory(ArticleFactory)
    published_ts = factory.Faker("date_time_this_month", tzinfo=pytz.utc)

    class Meta:
        model = FeedItem
