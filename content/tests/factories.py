import pytz
from urllib.parse import urljoin
import factory
from content.models import Publisher, Article


class PublisherFactory(factory.DjangoModelFactory):
    name = factory.Faker("company")
    domain = factory.Faker("url")

    class Meta:
        model = Publisher


class ArticleFactory(factory.DjangoModelFactory):
    publisher = factory.SubFactory(PublisherFactory)
    uri = factory.Faker("uri")
    published_ts = factory.Faker("date_time_this_month", tzinfo=pytz.utc)

    class Meta:
        model = Article
