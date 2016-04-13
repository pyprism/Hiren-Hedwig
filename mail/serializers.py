from rest_framework import serializers
from .models import Message, DomainSettings, Domain, ThreadedView, Account
from django.contrib.auth import update_session_auth_hash


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('id', 'username', 'created_at', 'updated_at'
                  , 'password', 'confirm_password')
        read_only_fields = ('created_at', 'updated_at', 'initialized')

        # def update(self, instance, validated_data):
        #     instance.username = validated_data.get('username', instance.username)
        #
        #     instance.save()
        #     password = validated_data.get('password', None)
        #     confirm_password = validated_data.get('confirm_password', None)
        #
        #     if password and confirm_password and password == confirm_password:
        #         instance.set_password(password)
        #         instance.save()
        #
        #     #update_session_auth_hash(self.context.get('request'), instance)
        #
        #     return instance


class ThreadedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadedView


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain


class DomainSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainSettings


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
