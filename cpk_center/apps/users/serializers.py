from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'patronymic', 'phone', 'role', 'position', 'is_active', 'full_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    def get_full_name(self, obj): return obj.get_full_name()
