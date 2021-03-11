from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from userprofile.models import Profile, Category, ServiceType, Service, Address
from userprofile.models import Relation

from userprofile.serializers import UserSerializer, ProfileSerializer, CategorySerializer
from userprofile.serializers import ServiceTypeSerializer, ServiceSerializer, AddressSerializer
from userprofile.serializers import RelationSerializer

from rest_framework import status, viewsets
from rest_framework.decorators import action
import os, math
from django.db.models import Q
from userprofile.models import LOCATION_TYPES


class HelloView(APIView):
    #permission_classes = (IsAuthenticated,)

    def get(self, request):
        print(request)
        content = {'message': 'Hello, World!'}
        return Response(content)
    def post(self, request):
        content = {'message': 'УРА ПОСТ!!!!!!!'}
        return Response(content)

class ProfileViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid()
        serializer.create(validated_data=request.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.data)

    def update(self, request, pk=None):
        instance = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid()
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


class OfferViewSet(viewsets.ModelViewSet):

    def get_remoteness_query(self, lon, lat, dist):
        min_lon = lon-dist/abs(math.cos(math.radians(lat))*111.0)
        max_lon = lon+dist/abs(math.cos(math.radians(lat))*111.0)
        min_lat = lat-(dist/111.0)
        max_lat = lat+(dist/111.0)
        return Q(address__longitude__range=(min_lon, max_lon)) & Q(address__latitude__range=(min_lat, max_lat))

    def get_offers_query(self, service, request):
        typesID = list(map(lambda t: t.id, service.types.all()))
        q = Q(category=service.category) & Q(isTutor=request.data['findTutor']) & Q(isActive=True) \
            &(Q(price__isnull=True)| Q(price__range=(request.data['min_price'], request.data['max_price']))) \
            & Q(location=service.location) & ~Q(user=request.user) & Q(types__in=typesID)
        if service.location != LOCATION_TYPES[0][0]: #если не удаленка
            q &= self.get_remoteness_query(service.address.longitude,\
                service.address.latitude, request.data['distance'])
        print(q)
        return q

    def get_services_for_like_query(self, service, request):
        typesID = list(map(lambda t: t.id, service.types.all()))
        q = Q(category=service.category) & ~Q(isTutor=service.isTutor) & Q(isActive=True) \
            & Q(location=service.location) & Q(user=request.user) & Q(types__in=typesID)
        if service.location != LOCATION_TYPES[0][0]: #если не удаленка
            q &= self.get_remoteness_query(service.address.longitude,\
                service.address.latitude, request.data['distance'])
        return q


    def list(self, request):
        services = Service.objects.filter(Q(isActive=True)&Q(user=request.user)\
            &~Q(isTutor=request.data['findTutor']))
        if len(services) == 0:
            return Response('У вас нет активных услуг такого типа')
        query = None
        for service in services:
            q = self.get_offers_query(service, request)
            query = q if query == None else query | q

        print(query)
        offers = Service.objects.filter(query).distinct()
        serializer = ServiceSerializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def like_service(self, request):
        service = Service.objects.get(pk=request.data['service_id'])
        query = self.get_services_for_like_query(service, request)
        services = Service.objects.filter(query).distinct()
        if (len(services) == 0):
            return Response('Тут что-то не так')
        relations = []
        for s in services:
            r = Relation.objects.create(service1=s, service2=service, status1='Like')
            relations.append(r)
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)
