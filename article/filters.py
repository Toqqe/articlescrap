import django_filters
from .models import Article

class ArticleFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(field_name='source', lookup_expr='icontains')
    
    class Meta:
        model = Article
        fields = ['source']