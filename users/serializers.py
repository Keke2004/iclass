from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise serializers.ValidationError('用户名或密码错误')

        # 前端发送的role
        request_role = self.context['request'].data.get('role')
        if request_role and self.user.role != request_role:
            raise serializers.ValidationError("角色选择错误，该用户不是'{}'".format(request_role))
        return data

class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        # For 'update' operations, make 'username' read-only.
        if self.instance:
            self.fields['username'].read_only = True

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'role', 'gender', 'phone_number', 'school', 'student_id', 'first_name']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def create(self, validated_data):
        # Use create_user to correctly handle password hashing and set other fields
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'student'),
            gender=validated_data.get('gender'),
            phone_number=validated_data.get('phone_number'),
            school=validated_data.get('school'),
            student_id=validated_data.get('student_id'),
            first_name=validated_data.get('first_name')
        )
        return user

class BasicUserSerializer(serializers.ModelSerializer):
    """
    一个只包含用户基本信息的序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class DirectPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting password directly with username.
    """
    username = serializers.CharField(max_length=150)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate_username(self, value):
        User = get_user_model()
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户不存在")
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return data

    def save(self, **kwargs):
        User = get_user_model()
        user = User.objects.get(username=self.validated_data['username'])
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user
