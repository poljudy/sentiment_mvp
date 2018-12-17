from django.contrib import admin
from .models import Publisher, Article


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name", "domain"]
    search_fields = ["name", "domain"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "publisher", "status"]
    list_select_related = ["publisher"]
    list_filter = ["status"]
    date_hierarchy = "published_ts"
    search_fields = ["title", "uri"]
