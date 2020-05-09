from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.utils.timezone import now

def getExistingField(field_name):
    return AbstractUser._meta.get_field(field_name)
