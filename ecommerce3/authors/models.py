from django.db import models
from django.urls import reverse
from categories.models import category
from django.utils.text import slugify

# Create your models here.
class author(models.Model):
    author_name = models.CharField(max_length=200)
    author_image = models.ImageField(upload_to='photos/author',default='No image available')
  
    author_discription = models.TextField(max_length=200)
    slug = models.SlugField(max_length=250,unique=True)

    def save(self, *args, **kwargs):
        # generate slug field from name field if slug is empty
        if not self.slug:
            self.slug = slugify(self.author_name)
        super(author, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('product_by_author', args={self.slug} )
    
    def __str__(self):
        return self.author_name
