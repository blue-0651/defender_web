from .models import Announcement
from rest_framework import serializers
from .models import User
from rest_framework import serializers
from .models import Client

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title','userId', 'memo', 'createDate']
        read_only_fields = ['createDate']




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'pw', 'isAdmin', 'createDate', 'email', 'store_name',
                 'phone_number', 'search_count', 'business_license_image','usage_start_date', 'usage_end_date' )
        extra_kwargs = {
            'pw': {'write_only': True},
        }
class UserLoginSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    pw = serializers.CharField(required=True, write_only=True)

class ClientSerializer(serializers.ModelSerializer):
    # 복호화된 전화번호를 반환할 필드 추가
    decrypted_phone = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'name', 'nickName', 'phoneNumber', 'decrypted_phone', 'gender', 'ages', 'isBadClient', 'extra',
                  'createDate', 'registeredBy', 'store_name']
        read_only_fields = ['createDate', 'decrypted_phone']

    def get_decrypted_phone(self, obj):
        """복호화된 전화번호 반환"""
        return obj.decrypt_phone()


class ClientSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)


class ClientVerifySerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(required=True)