from django.urls import path
from .views import ArticleListView


app_name = "content"
urlpatterns = [path("", ArticleListView.as_view(), name="article_list")]
