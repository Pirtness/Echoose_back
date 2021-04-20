from django.contrib import admin
from userprofile.models import Profile, Category, ServiceType, Service, Address, Relation, Dialog, Message

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(ServiceType)
admin.site.register(Address)
admin.site.register(Relation)
admin.site.register(Dialog)
admin.site.register(Message)


# Register your models here.
