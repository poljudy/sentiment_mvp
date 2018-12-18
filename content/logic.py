import logging
import requests
from django.db.models import QuerySet
from django.utils.html import strip_tags
from typing import Optional
from requests.exceptions import ConnectionError
from readability import Document
from .models import Publisher, Article


logger = logging.getLogger(__name__)


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
        else:
            article.set_status(Article.STATUS_RESPONSE_ERROR)

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
        clean = strip_tags(content).strip(" \n")
        return clean
