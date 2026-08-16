from rest_framework import permissions, serializers
from rest_framework.decorators import api_view, permission_classes

from .models import Certificate


class PublicCertificateSerializer(serializers.ModelSerializer):
    status_valid = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['certificate_number', 'issue_date', 'expiry_date', 'status', 'status_valid']

    def get_status_valid(self, obj):
        return obj.status == 'issued'


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_certificate_api(request, qr_code):
    """Публичная проверка сертификата по QR-коду: /api/certificates/verify/<qr>/"""
    cert = Certificate.objects.filter(qr_code=qr_code).first()
    if cert is None:
        return {'found': False, 'detail': 'Sertifikat topilmadi'}, 404
    return {'found': True, 'certificate': PublicCertificateSerializer(cert).data}
