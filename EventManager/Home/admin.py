from django.contrib import admin
from Home.models import User,Event,Participant
# Register your models here.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(Participant)