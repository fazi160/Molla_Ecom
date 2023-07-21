from django.db import models
from django.utils import timezone
# Create your models here.
class Offer(models.Model):
    offer_name = models.CharField(max_length=100)
    discount_amount = models.PositiveIntegerField()
    start_date = models.DateField(default=timezone.now)  # Use DateField instead of DateTimeField
    end_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.offer_name

    def is_offer_expired(self):
        return timezone.now().date() >= self.end_date
