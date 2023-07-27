# Create your models here.
from django.db import models

from django.contrib.auth.models import User

class UserOTP(models.Model):

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    time_st=models.DateTimeField(auto_now=True)
    otp=models.IntegerField()

class ReferralCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, unique=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.code
    