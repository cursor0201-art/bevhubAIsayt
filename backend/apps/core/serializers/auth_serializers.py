from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from core.domain.models import Tenant

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    company_name = serializers.CharField(write_only=True, required=False, default="")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'company_name']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        company_name = validated_data.pop('company_name', '')
        password = validated_data.pop('password')
        
        with transaction.atomic():
            # Create user instance
            user = User(**validated_data)
            user.set_password(password)
            
            # Create tenant
            if not company_name:
                company_name = f"{user.username}'s Team"
            tenant = Tenant.objects.create(company_name=company_name)
            user.tenant = tenant
            user.save()
            
            # Auto-create default Workspace for seamless onboarding Time-To-Value (TTV)
            from core.domain.models import Workspace
            Workspace.objects.create(tenant=tenant, name="My First Sandbox")
            
        return user


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role
        }
        return data
