from rest_framework import serializers
from django.contrib.auth.models import User
from userprofile.models import Profile, Category, ServiceType, Service, Address, Relation
from userprofile.models import Dialog, Message
from django.db.models import Q
from echoose.settings import DATETIME_FORMAT


class CategorySerializer(serializers.ModelSerializer):
    services_list = serializers.ReadOnlyField(source='services_list.id')
    class Meta:
        model = Category
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'name', 'longitude', 'latitude']

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.profile.id')
    category = serializers.ReadOnlyField(source='category.id')
    address = serializers.ReadOnlyField(source='address.id', required=False)

    class Meta:
        model = Service
        fields = '__all__'

    def check_if_exists(self, validated_data):
        q = Q(user=validated_data['user']) & Q(location=validated_data['location']) \
            & Q(category__pk=validated_data['category_id']) & Q(price=validated_data['price']) \
            & Q(isTutor=validated_data['isTutor']) & Q(isActive=validated_data['isActive'])
        if validated_data.get('address_id') is None:
            q &= Q(address__isnull=True)
        else:
            q &= Q(address=validated_data['address_id'])

        q &= Q(types__in=validated_data['types'])

        services = list(filter(lambda s: s.types.count()==len(validated_data['types']), Service.objects.filter(q)))
        return len(services) != 0

    def check_if_exists_update(self, instance, validated_data):
        if validated_data.get('location') is None:
            validated_data['location'] = instance.location
        if validated_data.get('category_id') is None:
            validated_data['category_id'] = instance.category.id
        if validated_data.get('price') is None:
            validated_data['price'] = instance.price
        if validated_data.get('isTutor') is None:
            validated_data['isTutor'] = instance.isTutor
        if validated_data.get('address_id') is None and not instance.address is None:
            validated_data['address_id'] = instance.address.id
        if validated_data.get('types') is None:
            validated_data['types'] = instance.types
        if validated_data.get('isActive') is None:
            validated_data['isActive'] = instance.isActive

        print(validated_data)

        return self.check_if_exists(validated_data)


    def create(self, validated_data):
        if self.check_if_exists(validated_data):
            return None
        types = validated_data.pop('types')
        service = Service.objects.create(**validated_data)
        service.types.set(types)
        service.save()
        return service

    def update(self, instance, validated_data):
        if self.check_if_exists_update(instance, validated_data):
            return None
        types = None
        if validated_data.get('types') != None:
            types = validated_data.pop('types')


        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if types != None:
            instance.types.set(types)
        instance.save()
        return instance

class RelationSerializer(serializers.ModelSerializer):
    service1 = serializers.ReadOnlyField(source='service1.id')
    service2 = serializers.ReadOnlyField(source='service2.id')

    class Meta:
        model = Relation
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.profile.id')
    dialog = serializers.ReadOnlyField(source='dialog.id')
    datetime = serializers.DateTimeField(format=DATETIME_FORMAT)
    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        message = Message.objects.create(
            author = validated_data['author'],
            dialog = validated_data['dialog'],
            text = validated_data['text']
        )
        message.save()
        dialog = Dialog.objects.get(pk=validated_data['dialog'].pk)
        dialog.last_message = message
        dialog.save()
        print(dialog)
        return message

class DialogSerializer(serializers.ModelSerializer):
    user1 = serializers.ReadOnlyField(source='user1.profile.id')
    user2 = serializers.ReadOnlyField(source='user2.profile.id')
    last_message = MessageSerializer('last_message')
    class Meta:
        model = Dialog
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email')
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            if key == "username":
                continue
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    image = serializers.ImageField(
            max_length=None, use_url=False
        )

    def create(self, validated_data):
        user = UserSerializer.create(UserSerializer(), validated_data=validated_data.get('credentials'))

        try:
            profile = Profile.objects.create(
                user=user,
                isMale=validated_data.get('isMale'),
                birth_date=validated_data.get('birth_date'),
                description=validated_data.get('description')
            )
        except Exception:
            user.delete()
            raise
        return profile

    def update(self, instance, validated_data):
        if validated_data.get('credentials') != None:
            UserSerializer.update(self, instance=instance.user, validated_data=validated_data.get('credentials'))
            validated_data.pop('credentials')
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    class Meta:
        model = Profile
        fields = '__all__'
