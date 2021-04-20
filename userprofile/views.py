from rest_framework.views import APIView
from rest_framework.response import Response

from userprofile.models import Profile, Category, ServiceType, Service, Address
from userprofile.models import Relation, Dialog, Message
from django.contrib.auth.models import User

from userprofile.serializers import UserSerializer, ProfileSerializer, CategorySerializer
from userprofile.serializers import ServiceTypeSerializer, ServiceSerializer, AddressSerializer
from userprofile.serializers import RelationSerializer, DialogSerializer, MessageSerializer

from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer

from rest_framework import status, viewsets
from rest_framework.decorators import action
import os, math
from django.db.models import Q
from userprofile.models import LOCATION_TYPES, STATUS

from rest_framework.permissions import IsAuthenticated, AllowAny
from userprofile.permissions import IsOwner

from userprofile.my_pagination import StandardResultsSetPagination


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous and self.action in ['list']:
            return self.queryset.filter(user=user)
        return self.queryset

    def get_permissions(self):
        if self.action in ['create', 'check_username']:
            self.permission_classes = [AllowAny, ]
        else:
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    def list(self, request):
        profile = Profile.objects.get(user=request.user)
        print(profile.image.name)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid()
        serializer.create(validated_data=request.data)
        profile = Profile.objects.get(user__username=request.data['credentials']['username'])
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid()
        serializer.update(instance, validated_data=request.data)
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], name='upload_image')
    def upload_image(self, request):
        try:
            file = request.data['file']
        except KeyError:
            raise ParseError('Request has no resource file attached')
        profile = Profile.objects.get(user=request.user)
        if (profile.image):
            if os.path.isfile(profile.image.path):
                os.remove(profile.image.path)
        file.name = profile.user.username + '.jpg'
        profile.image = file
        profile.image.name = file.name
        profile.save()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], name='check_username')
    def check_email(self, request):
        count = len(Profile.objects.filter(user__email=request.data['email']))
        if count > 0:
            return Response({'error' : 'Email exists'})
        return Response({'answer' : 'ok'})

    @action(detail=False, methods=['post'], name='check_username')
    def check_username(self, request):
        count = len(Profile.objects.filter(user__username=request.data['username']))
        if count > 0:
            return Response({'error' : 'Username exists'})
        return Response({'answer' : 'ok'})



class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous and self.action in ['list']:
            return self.queryset.filter(user=user)
        return self.queryset

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner, ]
        else:
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def create(self, request):
        category = Category.objects.get(pk=request.data.get('category_id'))
        if request.data.get('address_id') != None:
            address = Address.objects.get(pk = request.data.get('address_id'))
            if address.user.id != request.user.id:
                return Response({'error':'address not exists'}, status=status.HTTP_404_NOT_FOUND)
        elif request.data.get('location') != LOCATION_TYPES[0][0]:
            print(request.data.get('location'))
            return Response({'error':'address required'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = request.data
        data['user'] = request.user
        serializer = ServiceSerializer(data=data)
        serializer.is_valid()
        service = serializer.create(validated_data=request.data)
        if service is None:
            return Response({'error':'Service already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        service_id = service.id
        serializer = ServiceSerializer(Service.objects.get(pk=service_id))
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = Service.objects.get(pk=pk)
        data = request.data
        data['user'] = request.user
        if request.data.get('address_id') != None:
            address = Address.objects.get(pk = request.data.get('address_id'))
            if address.user.id != request.user.id:
                return Response({'error':'address not exists'}, status=status.HTTP_404_NOT_FOUND)
        elif instance.address == None:
            if request.data.get('location') != None and request.data.get('location') != LOCATION_TYPES[0][0]:
                return Response({'error':'address required'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            elif request.data.get('location') == None and instance.location != LOCATION_TYPES[0][0]:
                return Response({'error':'address required'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = ServiceSerializer(data=data)
        serializer.is_valid()
        service = serializer.update(instance, validated_data=request.data)
        if service is None:
            return Response({'error':'Service already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        service_id = service.id
        serializer = ServiceSerializer(Service.objects.get(pk=service_id))
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def location_types(self, request):
        content = []
        for i in range(len(LOCATION_TYPES)):
            content.append(LOCATION_TYPES[i][0])
        return Response({'answer':content})

    @action(detail=False, methods=['get'])
    def categories(self, request):
        serializer = CategorySerializer(Category.objects.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def service_types(self, request):
        serializer = ServiceTypeSerializer(ServiceType.objects.all(), many=True)
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous and self.action in ['list']:
            return self.queryset.filter(user=user)
        return self.queryset

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner, ]
        else:
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()


    def create(self, request):
        data = request.data
        data['user_id'] = request.user.id
        serializer = AddressSerializer(data=data)
        serializer.is_valid()
        address_id = serializer.create(validated_data=data).id
        serializer = AddressSerializer(Address.objects.get(pk=address_id))
        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = Address.objects.get(pk=pk)
        data = request.data
        data['user_id'] = request.user.id
        serializer = AddressSerializer(data=data)
        serializer.is_valid()
        address_id = serializer.update(instance, validated_data=data).id
        serializer = AddressSerializer(Address.objects.get(pk=address_id))
        return Response(serializer.data)


class OfferViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated, ]

    def get_remoteness_query(self, lon, lat, dist):
        min_lon = lon-dist/abs(math.cos(math.radians(lat))*111.0)
        max_lon = lon+dist/abs(math.cos(math.radians(lat))*111.0)
        min_lat = lat-(dist/111.0)
        max_lat = lat+(dist/111.0)
        return Q(address__longitude__range=(min_lon, max_lon)) & Q(address__latitude__range=(min_lat, max_lat))

    # return services that should not be shown
    def get_related_services(self, service):
        q = Q(service1 = service) & (Q(status1=STATUS[0][0])| Q(status1=STATUS[1][0]))
        services = list(map(lambda rel: rel.service2.id, Relation.objects.filter(q)))
        q = Q(service2 = service) & (Q(status1=STATUS[0][0])| Q(status1=STATUS[1][0]))
        services += list(map(lambda rel: rel.service1.id, Relation.objects.filter(q)))
        q = Q(service1 = service) & (Q(status1=STATUS[2][0])| Q(status1=STATUS[3][0]))
        services += list(map(lambda rel: rel.service2.id, Relation.objects.filter(q)))
        q = Q(service2 = service) & (Q(status2=STATUS[2][0])| Q(status2=STATUS[3][0]))
        services += list(map(lambda rel: rel.service1.id, Relation.objects.filter(q)))
        print(services)
        return services

    def get_offers_query(self, service, request):
        typesID = list(map(lambda t: t.id, service.types.all()))
        related = self.get_related_services(service)
        q = Q(category=service.category) & Q(isTutor=request.data['findTutor']) & Q(isActive=True) \
            &(Q(price__isnull=True)| Q(price__range=(request.data['min_price'], request.data['max_price']))) \
            & Q(location=service.location) & ~Q(user=request.user) & Q(types__in=typesID) \
            & ~Q(pk__in=related)
        if service.location != LOCATION_TYPES[0][0]: #если не удаленка
            q &= self.get_remoteness_query(service.address.longitude,\
                service.address.latitude, request.data['distance'])
        return q

    def get_services_for_like_query(self, service, request):
        typesID = list(map(lambda t: t.id, service.types.all()))
        #related = self.get_related_services(service)
        q = Q(category=service.category) & ~Q(isTutor=service.isTutor) & Q(isActive=True) \
            & Q(location=service.location) & Q(user=request.user) & Q(types__in=typesID)
        #    & ~Q(pk__in=related)
        if service.location != LOCATION_TYPES[0][0]: #если не удаленка
            q &= self.get_remoteness_query(service.address.longitude,\
                service.address.latitude, request.data['distance'])
        return q


    def create(self, request):
        services = Service.objects.filter(Q(isActive=True)&Q(user=request.user)\
            &~Q(isTutor=request.data['findTutor']))
        if len(services) == 0:
            return Response('You have not any active services of the type')
        query = None
        for service in services:

            q = self.get_offers_query(service, request)
            query = q if query == None else query | q

        print(query)
        offers = Service.objects.filter(query).distinct()
        serializer = ServiceSerializer(offers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def matches(self, request):
        services = Service.objects.filter(user=request.user)
        q = Q(service1__in=services)&Q(status1=STATUS[1][0])
        matched_services = list(map(lambda r: r.service2, Relation.objects.filter(q)))

        q = Q(service2__in=services)&Q(status1=STATUS[1][0])
        matched_services += list(map(lambda r: r.service1, Relation.objects.filter(q)))

        serializer = ServiceSerializer(matched_services, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def archives(self, request):
        services = Service.objects.filter(user=request.user)
        q = Q(service1__in=services)&Q(status1=STATUS[3][0])
        matched_services = list(map(lambda r: r.service2, Relation.objects.filter(q)))

        q = Q(service2__in=services)&Q(status2=STATUS[3][0])
        matched_services += list(map(lambda r: r.service1, Relation.objects.filter(q)))

        serializer = ServiceSerializer(matched_services, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        service = Service.objects.get(pk=pk)
        query = self.get_services_for_like_query(service, request)
        services = Service.objects.filter(query).distinct()
        #services = list(filter(lambda s: service.id not in self.get_related_services(s), services))
        print(services)

        if (len(services) == 0):
            return Response({'error':'No your services'})

        responses = []

        for s in services:
            q = Q(service1=s) & Q(service2=service) | Q(service2=s) & Q(service1=service)
            relation = Relation.objects.filter(q)
            if len(relation) > 0:
                relation = relation[0]
            else:
                relation = None

            if request.data['status'] == 'Like':
                if relation is None:
                    relation = Relation.objects.create(service1=s, service2=service, status1=STATUS[2][0])
                    responses.append({'answer' : 'Like was sent'})
                elif relation.service1 == s:
                    if relation.status2 == STATUS[2][0] or relation.status2 == STATUS[1][0]:
                        relation.status1 = relation.status2 = STATUS[1][0]
                        responses.append({'answer' : 'Match!'})
                    elif relation.status2 == STATUS[0][0]:
                        relation.status1 = STATUS[0][0]
                        responses.append({'error' : "You don't match("})
                    else:
                        relation.status1 = STATUS[2][0]
                        responses.append({'answer' : 'Like was sent'})
                else:
                    if relation.status1 == STATUS[2][0] or relation.status1 == STATUS[1][0]:
                        relation.status1 = relation.status2 = STATUS[1][0]
                        responses.append({'answer' : 'Match!'})
                    elif relation.status1 == STATUS[0][0]:
                        relation.status2 = STATUS[0][0]
                        responses.append({'error' : "You don't match("})
                    else:
                        relation.status2 = STATUS[2][0]
                        responses.append({'answer' : 'Like was sent'})

            elif request.data['status'] == 'Dislike':
                if relation is None:
                    relation = Relation.objects.create(service1=s, service2=service, status1=STATUS[0][0], status2=STATUS[0][0])
                    responses.append({'answer' : 'Dislike was sent'})
                else:
                    relation.status1 = relation.status2 = STATUS[0][0]
                    responses.append({'answer' : 'Dislike was sent'})

            elif request.data['status'] == 'Archive':
                if relation is None:
                    relation = Relation.objects.create(service1=s, service2=service, status1=STATUS[3][0])
                    responses.append({'answer' : 'Added to archive'})
                elif relation.service1 == s:
                    if relation.status2 == STATUS[0][0]:
                        relation.status1 = STATUS[0][0]
                        responses.append({'error' : "You don't match("})
                    elif relation.status2 == STATUS[1][0]:
                        relation.status2 = STATUS[2][0]
                        relation.status1 = STATUS[3][0]
                        responses.append({'answer' : 'Added to archive'})
                    else:
                        relation.status1 = STATUS[3][0]
                        responses.append({'answer' : 'Added to archive'})
                elif relation.service2 == s:
                    if relation.status1 == STATUS[0][0]:
                        relation.status2 = STATUS[0][0]
                        responses.append({'error' : "You don't match("})
                    elif relation.status1 == STATUS[1][0]:
                        relation.status1 = STATUS[2][0]
                        relation.status2 = STATUS[3][0]
                        responses.append({'answer' : 'Added to archive'})
                    else:
                        relation.status2 = STATUS[3][0]
                        responses.append({'answer' : 'Added to archive'})
            relation.save()
        if len(responses) == 0:
            return Response({'error':'nothing happened'})
        elif len(responses) == 1:
            return Response(responses[0])
        else:
            return Response({'answers':responses})



class DialogViewSet(viewsets.ModelViewSet, GenericAsyncAPIConsumer):
    pagination_class = StandardResultsSetPagination
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous and self.action in ['list']:
            return self.queryset.filter(Q(user1=user)|Q(user2=user))
        return self.queryset

    def get_permissions(self):
        if self.action in ['update', 'list']:
            self.permission_classes = [IsAuthenticated, ]
        elif self.action in ['retrieve']:
            self.permission_classes = [IsOwner, ]
        else:
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def swap_users(self, serializer):
        ser_data = []
        for i in range(len(serializer.data)):
            ser_data.append({})
            ser_data[i].update(serializer.data[i])

            if ser_data[i]['user1'] != self.request.user.profile.pk:
                ser_data[i]['user2'] = ser_data[i]['user1']
                ser_data[i]['user1'] = self.request.user.profile.pk
        return ser_data

    def swap_users_single(self, serializer):
        ser_data = serializer.data
        if ser_data['user1'] != self.request.user.profile.pk:
            ser_data['user2'] = ser_data['user1']
            ser_data['user1'] = self.request.user.profile.pk
        return ser_data



    def list(self, request):
        user = self.request.user
        dialogs = Dialog.objects.filter(Q(user1=user)|Q(user2=user))
        page = self.paginate_queryset(dialogs)
        serializer = DialogSerializer(dialogs, many=True)
        return self.get_paginated_response(self.swap_users(serializer))

    def create(self, request):
        print(request.data)
        u1 = request.user
        u2 = User.objects.get(profile__pk=request.data.get('receiver_id'))
        print(u1)
        print(u2)
        print(request.data.get('receiver_id'))

        dialog = Dialog.objects.filter(Q(user1=u1)&Q(user2=u2)|Q(user1=u2)&Q(user2=u1))
        if len(dialog) > 0:
            serializer = DialogSerializer(dialog[0])
            return Response(self.swap_users_single(serializer))
            #return Response({'error':'Dialog already exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if u1 == u2:
            return Response({'error':'Cant create dialog with yourself'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        q = Q(service1__user=u1)&Q(service2__user=u2)|Q(service1__user=u2)&Q(service2__user=u1)
        relations = Relation.objects.filter(q)
        matched = False
        for r in relations:
            if r.status1 == STATUS[1][0] and r.status2 == STATUS[1][0]:
                matched = True
                break
        if not matched:
            return Response({'error':'Cant create dialog, you have no matches'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = {}
        data['user1'] = u1
        data['user2'] = u2
        serializer = DialogSerializer(data=data)
        serializer.is_valid()
        dialog_id = serializer.create(validated_data=data).id
        serializer = DialogSerializer(Dialog.objects.get(pk=dialog_id))
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def unread(self, request):
        user = request.user
        dialogs = Dialog.objects.filter((Q(user1=user)|Q(user2=user))&Q(last_message__read=False)&~Q(last_message__author=request.user))
        serializer = DialogSerializer(dialogs, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        if request.method == 'GET':
            messages = Message.objects.filter(dialog_id=pk)
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = MessageSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        elif request.method == 'POST':

            data = request.data
            data['author'] = request.user
            d = Dialog.objects.get(pk=pk)
            data['dialog'] = d
            serializer = MessageSerializer(data=data)
            serializer.is_valid()
            message_id = serializer.create(validated_data=data).id
            serializer = MessageSerializer(Message.objects.get(pk=message_id))
            return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def unread_messages(self, request, pk=None):
        messages = Message.objects.filter(Q(dialog_id=pk)&Q(read=False)&~Q(author=request.user))
        for i in range(len(messages)):
            messages[i].read = True
            messages[i].save()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
