from django.urls import path
from .views import ArticleAPI

urlpatterns = [
    path('api/v1/articles/', ArticleAPI.as_view(), name='article-view'),
    path('api/v1/articles/<int:id>/', ArticleAPI.as_view(), name='article-detail')
]
