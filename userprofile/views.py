from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userprofile.models import Profile, Category, ServiceType, Service, Address
from userprofile.serializers import UserSerializer, ProfileSerializer, CategorySerializer
from userprofile.serializers import ServiceTypeSerializer, ServiceSerializer, AddressSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
import os


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class ProfileViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(instance, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], name='upload_image')
    def upload_image(self, request):
        try:
            file = request.data['file']
        except KeyError:
            raise ParseError('Request has no resource file attached')
        profile = Profile.objects.get(user=request.user)
        if (profile.image != None):
            if os.path.isfile(profile.image.path):
                os.remove(profile.image.path)
        profile.image = file
        profile.save()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def create(self, request):
        category = Category.objects.get(pk=request.data.get('category_id'))
        if request.data.get('address_id') != None:
            address = Address.objects.get(pk = request.data.get('address_id'))
            if address.user.id != request.user.id:
                return Response(status=status.HTTP_404_NOT_FOUND)
        data = request.data
        data['user'] = request.user
        serializer = ServiceSerializer(data=data)
        serializer.is_valid()
        serializer.create(validated_data=request.data)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = Service.objects.get(pk=pk)
        data = request.data
        if request.data.get('address_id') != None:
            address = Address.objects.get(pk = request.data.get('address_id'))
            if address.user.id != request.user.id:
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceSerializer(data=data)
        serializer.is_valid()
        serializer.update(instance, validated_data=request.data)
        return Response(serializer.data)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def create(self, request):
        data = request.data
        data['user_id'] = request.user.id
        serializer = AddressSerializer(data=data)
        serializer.is_valid()
        serializer.create(validated_data=data)
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = Address.objects.get(pk=pk)
        data = request.data
        data['user_id'] = request.user.id
        serializer = AddressSerializer(data=data)
        serializer.is_valid()
        serializer.update(instance, validated_data=data)
        return Response(serializer.data)
