from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
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
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'role', 'gender', 'phone_number', 'school', 'student_id', 'first_name']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'read_only': True}
        }

    def create(self, validated_data):
        # 使用create_user来正确处理密码哈希
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        # 单独设置自定义的role字段
        user.role = validated_data.get('role', 'student')
        user.save()
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
