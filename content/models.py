from django.db import models
from django.contrib.postgres.fields import JSONField


class Publisher(models.Model):
    name = models.CharField(max_length=250)
    domain = models.URLField(unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CREATED = "created"
    STATUS_CONTENT_FETCHED = "content_fetched"
    STATUS_RESPONSE_ERROR = "response_error"
    STATUS_SENTIMENT_SET = "sentiment_set"
    STATUS_SENTIMENT_ERROR = "sentiment_error"

    STATUS_OPTIONS = (
        (STATUS_CREATED, "Created"),
        (STATUS_CONTENT_FETCHED, "Content Fetched"),
        (STATUS_RESPONSE_ERROR, "Response Error"),
        (STATUS_SENTIMENT_SET, "Sentiment Set"),
        (STATUS_SENTIMENT_ERROR, "Sentiment Error"),
    )

    publisher = models.ForeignKey(
        Publisher, related_name="articles", on_delete=models.CASCADE
    )
    uri = models.URLField(unique=True)
    title = models.TextField()
    content_source = models.TextField(default="", blank=True)
    content_clean = models.TextField(default="", blank=True)
    published_ts = models.DateTimeField()
    status = models.CharField(
        choices=STATUS_OPTIONS, default=STATUS_CREATED, max_length=30
    )
    sentiment_score = models.FloatField(default=0)
    sentiment_details = JSONField(default=dict)
    sentiment_calculated_ts = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-published_ts",)

    def __str__(self):
        return f"{self.publisher.name} | {self.title}"

    def set_status(self, status: str):
        """Set status from choices in Article.STATUS_OPTIONS.

        Args:
            status: one of possible STATUS_OPTIONS
        """
        assert status in dict(self.STATUS_OPTIONS).keys()

        self.status = status
        self.save()
