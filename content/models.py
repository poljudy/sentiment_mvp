from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=250)
    domain = models.URLField(unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CREATED = "created"
    STATUS_PARSING_STARTED = "parsing_started"
    STATUS_PARSING_FINISHED = "parsing_finished"
    STATUS_PARSING_ERROR = "parsing_error"
    STATUS_OPTIONS = (
        (STATUS_CREATED, "Created"),
        (STATUS_PARSING_STARTED, "Parsing Started"),
        (STATUS_PARSING_FINISHED, "Parsing Finished"),
        (STATUS_PARSING_ERROR, "Parsing Error"),
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

    class Meta:
        ordering = ("-published_ts",)

    def __str__(self):
        return f"{self.publisher.name} | {self.title}"
