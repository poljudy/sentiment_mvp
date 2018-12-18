from django.views.generic import ListView
from .models import Article


class ArticleListView(ListView):
    model = Article
    template = "content/article_list.html"
    context_object_name = "articles"
    paginate_by = 20

    def get_queryset(self):
        # TODO filter only articles with sentiment
        return self.model.objects.all()
