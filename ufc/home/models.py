from django.db import models

# Create your models here.

# Model home page stats     
class HomeStat(models.Model):
    ROI = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    accuracy = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    fights_analyzed = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)