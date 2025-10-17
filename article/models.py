from django.db import models

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=250) ## art title
    html_description = models.TextField()  ## art desc with html tags
    clear_description = models.TextField() ## clear art desc
    source = models.URLField(unique=True)  ## url artice
    date = models.DateTimeField() ## art created date
    
    def __str__(self):
        return self.source