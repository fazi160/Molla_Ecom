from django.db import models
from django.urls import reverse
from authors.models import author
from categories.models import category
from django.utils.text import slugify
from offer.models import Offer
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# product
class Product(models.Model):
    product_name = models.CharField(unique=True,max_length=50)
    product_price = models.IntegerField()
    product_image = models.ImageField(upload_to='product_images/')
    product_image_thumbnail = ImageSpecField(
        source='product_image',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 90}
    )

    author = models.ForeignKey(author,on_delete=models.CASCADE)
    category = models.ForeignKey(category,on_delete=models.CASCADE)
    product_description = models.TextField(max_length=30, blank=True)
    product_description_detailed = models.TextField(blank=True)
   
    is_available = models.BooleanField(default=False)
    slug = models.SlugField(max_length=250,unique=True)
    quantity = models.IntegerField(default=10)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True )

    def save(self, *args, **kwargs):
        # generate slug field from name field if slug is empty
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('single',args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    def get_offer(self):
        return self.product_price - self.offer.discount_amount



