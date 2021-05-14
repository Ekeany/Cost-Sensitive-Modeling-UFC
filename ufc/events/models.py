from django.db import models

# Create your models here.
class EventManager(models.Manager):
    # Query to get the upcoming event using future boolean
    def is_next(self):
        return self.get_queryset().filter(future=True)
    
    # Query to get past events using future boolean
    def is_past(self):
        return self.get_queryset().filter(future=False)
        
class Event(models.Model):
    future = models.BooleanField(default=True)
    event_name = models.CharField(max_length=255, blank="False")
    expected_returns = models.IntegerField(default=0, blank="False")
    num_fights_predicted = models.IntegerField(default=0, blank="False")
    num_total_fights = models.IntegerField(default=0, blank="False")
    ROI = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    accuracy = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    event_date = models.DateField(auto_now=False, auto_now_add=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = EventManager()
    
class Fight(models.Model):
    event = models.ForeignKey(Event, related_name='fights', on_delete=models.CASCADE)
    red_fighter_name = models.CharField(max_length=255, blank="False")
    blue_fighter_name = models.CharField(max_length=255, blank="False")
    red_fighter_odds = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    blue_fighter_odds = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    # Not sure what field to make prediction
    prediction_made = models.BooleanField(default=True)
    red_fighter_pred = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    blue_fighter_pred = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    expected_return = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    ROI = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    # Not sure what field to make winner
    winner = models.IntegerField(default='null', blank="True")
