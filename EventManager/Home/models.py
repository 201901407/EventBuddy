from django.db import models

# Create your models here.

class User(models.Model):
    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=250)

class Event(models.Model):
    event_name = models.CharField(max_length = 120)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    host = models.EmailField(max_length = 100)
    event_description = models.CharField(max_length = 300)


