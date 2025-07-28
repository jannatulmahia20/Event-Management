from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participated_events', blank=True)
    rsvps = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvped_events', blank=True)


   
    image = models.ImageField(
        upload_to='event_images/',
        default='event_images/default_event.jpg',  
        blank=True
    )

    def __str__(self):
        return self.name
