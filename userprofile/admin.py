from django.contrib import admin
from userprofile.models import Profile, Category, ServiceType, Service, Address

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(ServiceType)
admin.site.register(Address)


# Register your models here.
