import logging
import pendulum
import requests
from django.conf import settings
from django.db.models import QuerySet
from django.utils.html import strip_tags
from typing import Optional
from requests.exceptions import ConnectionError
from readability import Document
from watson_developer_cloud import NaturalLanguageUnderstandingV1, WatsonApiException
from watson_developer_cloud.natural_language_understanding_v1 import (
    Features,
    SentimentOptions,
)
from .models import Publisher, Article


logger = logging.getLogger(__name__)


class SentimentCalculate:
    """Calculates sentiment score for given article.

    Done with IBM Watson NLU.
    """

    def __init__(self, article: Article):
        self.article = article

    def get_and_set_sentiment(self):
        """Get IBM Watson sentiment analysis reponse and save it on
        the article instance.
        """
        nlu = self.get_watson_nlu()

        try:
            response = nlu.analyze(
                text=self.article.content_clean,
                features=Features(sentiment=SentimentOptions()),
            ).get_result()

            self.save_watson_response(response)

        except WatsonApiException as e:
            # if api key is incorrect etc.
            self.article.set_status(Article.STATUS_SENTIMENT_ERROR)
            logger.exception(e)

    def get_watson_nlu(self) -> NaturalLanguageUnderstandingV1:
        """Return an instance of IBM Watson's NaturalLanguageUnderstandingV1
        with auth set.
        """
        return NaturalLanguageUnderstandingV1(
            version=settings.WATSON_API_VERSION,
            iam_apikey=settings.ENV.str("WATSON_IAM_APIKEY").strip("\"'"),
            url=settings.WATSON_URL,
        )

    def save_watson_response(self, response: dict):
        """Save IBM Watson response to article instance.

        Args:
            response: watson formated dict with sentiment results
        """
        if response.get("sentiment"):
            self.article.sentiment_score = response["sentiment"]["document"]["score"]
            self.article.sentiment_calculated_ts = pendulum.now("UTC")
            self.article.sentiment_details = response
            self.article.save()

            self.article.set_status(Article.STATUS_SENTIMENT_SET)
        else:
            self.article.set_status(Article.STATUS_SENTIMENT_ERROR)


class ParseContent:
    """Parses saved article content.

    Use .parse_publishers() method to start parsing all publishers articles.
    """

    def parse_publishers(self):
        """Go through all the publishers in the system and parse new articles.
        """
        for publisher in Publisher.objects.all():
            self.parse_newly_created_articles(publisher)

    def parse_newly_created_articles(self, publisher: Publisher):
        """Go through all articles and fetch their content.

        Args:
            publisher: Publisher db instance
        """
        for article in publisher.articles.filter(status=Article.STATUS_CREATED):
            self.parse_new_article(article)

    def parse_new_article(self, article: Article):
        """Fetch content for a single article.

        Args:
            article: Article db instance with STATUS_CREATED
        """
        response = self.get_article_raw_response(article.uri)

        if response:
            doc = Document(response.text)

            article.content_source = response.text
            article.content_clean = self.clean_content(doc.summary())

            article.save()

            article.set_status(Article.STATUS_CONTENT_FETCHED)

            self.set_article_sentiment_score(article)
        else:
            article.set_status(Article.STATUS_RESPONSE_ERROR)

    def set_article_sentiment_score(self, article: Article):
        """Calculate sentiment score for article.

        Args:
            article: Article instance with clean content set
        """
        SentimentCalculate(article).get_and_set_sentiment()

    def get_article_raw_response(self, uri: str) -> Optional[requests.Response]:
        """Get response from the publisher for given uri.

        Args:
            uri: full uri to the article

        Returns:
            Response object or None
        """
        try:
            response = requests.get(uri)

            if response.status_code == 200:
                return response
            else:
                logger.exception(
                    f"Status code {response.status_code} returned for article {uri}"
                )
                return None
        except ConnectionError:
            logger.exception(f"Failed to make a connection to host when fetching {uri}")
            return None

    def clean_content(self, content: str) -> str:
        """Clean content from html tags.

        Args:
            content: dirty dirty html content

        Returns:
            content cleaned from html tags
        """
        # clean from tags
        clean = strip_tags(content)
        # clean from all the extra whitespace
        clean = " ".join(clean.split())

        return clean
