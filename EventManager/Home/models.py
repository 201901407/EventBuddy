from django.db import models
import uuid, datetime
from django.utils import timezone

# Create your models here.

class User(models.Model):
    user_id = models.CharField(max_length=100,default=uuid.uuid4)
    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=250)
    def getUserDetails(self):
        return self.email

class Event(models.Model):
    event_id = models.CharField(max_length=100,default=uuid.uuid4)
    event_name = models.CharField(max_length = 120)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    host_email = models.EmailField(max_length = 100)
    host_name = models.CharField(max_length = 100)
    event_description = models.CharField(max_length = 300)
    registration_deadline = models.DateTimeField(default=timezone.now)
    event_poster = models.URLField(max_length=150,default = '')
    def getEventDetails(self):
        return [self.event_name,self.event_start,self.event_end,self.host,self.event_description]

class Participant(models.Model):
    pevent_id = models.CharField(max_length=100)
    participant_email = models.EmailField(max_length = 100)
    participant_name = models.CharField(max_length=100)
    participant_contactno = models.IntegerField()
    group_registration = models.BooleanField()
    no_of_members = models.IntegerField()


    


