from django.db import models
from content.models import Publisher, Article


class Feed(models.Model):
    publisher = models.ForeignKey(
        Publisher, related_name="feeds", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    uri = models.URLField()
    last_fetch_ts = models.DateTimeField()

    def __str__(self):
        return self.title


class FeedItem(models.Model):
    feed = models.ForeignKey(Feed, related_name="feed_items", on_delete=models.CASCADE)
    title = models.TextField()
    uri = models.URLField(unique=True)
    article = models.OneToOneField(
        Article, blank=True, null=True, on_delete=models.SET_NULL
    )
    fetched_ts = models.DateTimeField(auto_now_add=True)
    published_ts = models.DateTimeField()

    class Meta:
        ordering = ("-published_ts",)

    def __str__(self):
        return self.title
