from rest_framework import permissions
from userprofile.models import Address, Service, Dialog, Message

class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        model = request.path.split('/')[1]
        owner = None
        owners = []
        if model == 'address':
            try:
                obj = Address.objects.get(pk=view.kwargs['pk'])
                owner = obj.user
            except:
                return False

        elif model == 'service':
            try:
                obj = Service.objects.get(pk=view.kwargs['pk'])
                owner = obj.user
            except:
                return False
        elif model == 'dialog':
            try:
                obj = Dialog.objects.get(pk=view.kwargs['pk'])
                owners = [obj.user1, obj.user2]
            except:
                return False
        elif model == 'messages':
            try:
                obj = Dialog.objects.get(pk=view.kwargs['pk'])
                owners = [obj.user1, obj.user2]
            except:
                return False

        if len(owners) > 0 and request.user in owners:
            return True
        if request.user == owner:
            return True
        return False
