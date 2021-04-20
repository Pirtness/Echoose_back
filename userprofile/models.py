from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

LOCATION_TYPES = (('Remotely', 'Удаленно'), ("Student's home", "У ученика"),
    ("Tutor's home", "У преподавателя"))

STATUS = (('blocked', 'Заблокирован'), ('Match', 'Совпадение'),
    ('Like', 'Понравился'), ('Archived', 'Архивирован'))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    isMale = models.BooleanField(null = True) #True = male, False = female
    birth_date = models.DateField(null=True)
    description = models.CharField(null=True, blank=True, max_length=5000)
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
    address = models.ForeignKey('Address', related_name='services_list', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='services_list', on_delete=models.CASCADE)
    location = models.CharField(choices=LOCATION_TYPES, default='Any', max_length=200)
    category = models.ForeignKey('Category', related_name='services_list', on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, null=True, blank=True)
    price = models.IntegerField(null = True)
    isTutor = models.BooleanField(null=False) #True = tutor, False = student
    types = models.ManyToManyField(ServiceType, default=[])
    isActive = models.BooleanField(null=False, default=True)

class Relation(models.Model):
    service1 = models.ForeignKey('Service', related_name='+', on_delete=models.CASCADE)
    service2 = models.ForeignKey('Service', related_name='+', on_delete=models.CASCADE)
    status1 = models.CharField(choices=STATUS, max_length=200, null=True)
    status2 = models.CharField(choices=STATUS, max_length=200, null=True)

class Dialog(models.Model):
    user1 = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    last_message = models.ForeignKey('Message', related_name='+', null=True, on_delete=models.CASCADE)

    # class Meta:
    #     ordering = ['-last_message']

class Message(models.Model):
    dialog = models.ForeignKey(Dialog, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    text = models.CharField(max_length=5113, null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-datetime']
