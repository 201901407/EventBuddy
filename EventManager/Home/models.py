from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class User(models.Model):
    email = models.EmailField(max_length=100)
    name = models.CharField(max_length=100)
    password = models.CharField(validators=[RegexValidator(regex='^.{8}$', message='Password length has to be 8', code='nomatch')],max_length=250)

