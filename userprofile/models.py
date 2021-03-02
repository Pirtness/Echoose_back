from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

LOCATION_TYPES = (('Remotely', 'Удаленно'), ("Student's home", "У ученика"),
    ("Tutor's home", "У преподавателя"), ('Any', 'Любое'))

SERVICE_TYPES = (('homework', 'Домашняя работа'), ('exam', 'Экзамен'),
    ('improve', 'Улучшить знания'), ('topic', 'Разобрать тему'))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    isMale = models.BooleanField(null = True) #True = male, False = female
    age = models.IntegerField(null=True)
    image = models.ImageField(
        upload_to='images/', blank=True, null=True
    )

class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses_list', on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, null = False)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)


class Category(models.Model):
    name = models.CharField(max_length = 100, null = False)

class ServiceType(models.Model):
    name = models.CharField(max_length = 100, null = False)

class Service(models.Model):
    address = models.ForeignKey('Address', related_name='services_list', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey(User, related_name='services_list', on_delete=models.CASCADE)
    location = models.CharField(choices=LOCATION_TYPES, default='Any', max_length=200)
    category = models.ForeignKey('Category', related_name='services_list', on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, null=True, blank=True)
    price = models.IntegerField()
    isTutor = models.BooleanField(null=False) #True = tutor, False = student
    types = models.ManyToManyField(ServiceType, default=[])
    isActive = models.BooleanField(null=False, default=True)
