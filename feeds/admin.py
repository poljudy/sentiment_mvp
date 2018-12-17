from django.contrib import admin
from .models import Feed, FeedItem


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ["title", "publisher", "last_fetch_ts"]
    list_select_related = ["publisher"]


@admin.register(FeedItem)
class FeedItem(admin.ModelAdmin):
    list_display = ["title", "feed", "fetched_ts", "published_ts"]
    list_select_related = ["feed"]
    search_fields = ["title", "uri"]
