import vcr
from django.test import TestCase
from content.logic import ParseContent


VCR_ROOT = "content/tests/fixtures/vcr"


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
