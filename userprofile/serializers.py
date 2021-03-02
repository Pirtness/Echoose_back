from rest_framework import serializers
from django.contrib.auth.models import User
from userprofile.models import Profile, Category, ServiceType, Service, Address


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    types = ServiceTypeSerializer(many=True, required=False)
    category = serializers.ReadOnlyField(source='category.id')

    class Meta:
        model = Service
        fields = '__all__'

    def create(self, validated_data):
        types = validated_data.pop('types')
        service = Service.objects.create(**validated_data)
        service.types.set(types)
        service.save()
        return service

    def update(self, instance, validated_data):
        types = None
        if validated_data.get('types') != None:
            types = validated_data.pop('types')


        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if types != None:
            instance.types.set(types)
        instance.save()
        return instance

class CategorySerializer(serializers.ModelSerializer):
    services_list = ServiceSerializer(many=True)

    class Meta:
        model = Category
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    #services_list = ServiceSerializer(many=True)

    class Meta:
        model = Address
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    addresses_list = AddressSerializer(many=True)
    services_list = ServiceSerializer(many=True)
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
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    image = serializers.ImageField(
            max_length=None, use_url=True
        )

    def create(self, validated_data):
        user = UserSerializer.create(UserSerializer(), validated_data=validated_data.get('credentials'))

        try:
            profile = Profile.objects.create(
                user=user,
                isMale=validated_data.get('isMale'),
                age=validated_data.get('age')
            )
        except Exception:
            user.delete()
            raise
        return profile

    def update(self, instance, validated_data):
        if validated_data.get('credentials') != None:
            UserSerializer.update(self, instance=instance.user, validated_data=validated_data.get('credentials'))

    class Meta:
        model = Profile
        fields = '__all__'
