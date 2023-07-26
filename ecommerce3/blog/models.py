from django.db import models
from django.urls import reverse
from django.utils.text import slugify


#category
class Blog(models.Model):
    blog_name      =  models.CharField(max_length=200,unique=True)
    blog_image = models.ImageField(upload_to='photos/blog',default='No image available')
    blog_discription = models.TextField(max_length=200)
    slug = models.SlugField(max_length=250,unique=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.blog_name)
        super(Blog, self).save(*args, **kwargs)
