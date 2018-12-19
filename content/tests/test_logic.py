import vcr
from django.test import TestCase, override_settings
from content.logic import SentimentCalculate, ParseContent
from content.models import Article
from content.tests.factories import ArticleFactory


VCR_ROOT = "content/tests/fixtures/vcr"


class SentimentCalculateTestCase(TestCase):
    @vcr.use_cassette(f"{VCR_ROOT}/get_sentiment__success.yaml")
    def test_get_and_set_sentiment__success(self):
        article = ArticleFactory(
            status=Article.STATUS_CONTENT_FETCHED,
            content_clean="Today is very sunny. Doggs are running.",
        )

        sentiment_calculate = SentimentCalculate(article)
        sentiment_calculate.get_and_set_sentiment()

        article.refresh_from_db()

        assert article.status == Article.STATUS_SENTIMENT_SET

    @vcr.use_cassette(f"{VCR_ROOT}/get_sentiment__bad_url.yaml")
    @override_settings(WATSON_URL="https://example.com")
    def test_get_and_set_sentiment__bad_url(self):
        article = ArticleFactory(status=Article.STATUS_CONTENT_FETCHED)

        sentiment_calculate = SentimentCalculate(article)
        sentiment_calculate.get_and_set_sentiment()

        article.refresh_from_db()

        assert article.status == Article.STATUS_SENTIMENT_ERROR

    def test_save_watson_response__success(self):
        SCORE = 0.472_614
        WATSON_RESPONSE = {
            "usage": {"features": 1, "text_units": 1, "text_characters": 6406},
            "language": "en",
            "sentiment": {"document": {"label": "positive", "score": SCORE}},
        }

        article = ArticleFactory(status=Article.STATUS_CONTENT_FETCHED)

        sentiment_calculate = SentimentCalculate(article)

        sentiment_calculate.save_watson_response(WATSON_RESPONSE)

        article.refresh_from_db()

        assert article.sentiment_score == SCORE
        assert article.sentiment_details == WATSON_RESPONSE
        assert article.status == Article.STATUS_SENTIMENT_SET

    def test_save_watson_response__error(self):
        WATSON_RESPONSE = {}

        article = ArticleFactory(status=Article.STATUS_CONTENT_FETCHED)

        sentiment_calculate = SentimentCalculate(article)

        sentiment_calculate.save_watson_response(WATSON_RESPONSE)

        article.refresh_from_db()

        assert article.sentiment_score == 0
        assert article.status == Article.STATUS_SENTIMENT_ERROR


class ParseContentTestCase(TestCase):
    @vcr.use_cassette(f"{VCR_ROOT}/article_raw_response__success.yaml")
    def test_get_article_raw_response__success(self):
        parser = ParseContent()
        RESPONSE = parser.get_article_raw_response(
            "https://www.forbes.com/sites/toddmillay/2018/12/17/instead-of-predicting-the-future-learn-from-the-past/"
        )

        assert RESPONSE.status_code == 200
        assert RESPONSE.text is not None

    def test_get_article_raw_response__bad_uri(self):
        parser = ParseContent()
        RESPONSE = parser.get_article_raw_response("https://dummy")

        assert RESPONSE is None

    @vcr.use_cassette(f"{VCR_ROOT}/article_raw_response__404.yaml")
    def test_get_article_raw_response__404_response(self):
        parser = ParseContent()
        RESPONSE = parser.get_article_raw_response(
            "https://www.forbes.com/sites/toddmillay/2018/12/17/DUMMY/"
        )

        assert RESPONSE is None

    def test_clean_content__tags(self):
        INPUT = "<div><p>Dummy content.</p></div>"
        EXPECTED_RESULT = "Dummy content."

        parser = ParseContent()

        RESULT = parser.clean_content(INPUT)
        assert RESULT == EXPECTED_RESULT

    def test_clean_content__tags_and_whitespaces(self):
        INPUT = """
         \n \n
        <div>
            <p>Dummy content.</p>
            <p>Is dummy.</p>
        </div>
        <div></div>
        \n\n  \n
        """
        EXPECTED_RESULT = "Dummy content. Is dummy."

        parser = ParseContent()

        RESULT = parser.clean_content(INPUT)
        assert RESULT == EXPECTED_RESULT
