from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from .models import Article
from .serializers import ArticleSerializer
from .filters import ArticleFilter
# Create your views here.


class ArticleAPI(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter 
    def get(self, request, id=None):
        if id is not None:
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return Response({"success":False, "detail":"Not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = ArticleSerializer(article)
            return Response({"sucess":True,"data":serializer.data})
        
        articles = Article.objects.all()

        filtered_articles = ArticleFilter(request.query_params, queryset=articles)
        if filtered_articles.is_valid():
            serializer = ArticleSerializer(filtered_articles.qs, many=True)
            return Response({'success':True, 'data':serializer.data})
        
        serializer = ArticleSerializer(articles, many=True)
        
        return Response({'success':True, 'data':serializer.data})