import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_certificate_number_sequence():
    pass
    # минимальные зависимости создайте по своим моделям; здесь - схема проверки
    # c1 = Certificate.objects.create(student=..., course=...)
    # c2 = Certificate.objects.create(student=..., course=...)
    # assert c1.certificate_number != c2.certificate_number


def test_verify_api_404(client):
    url = reverse('api:verify', kwargs={'qr_code': 'nope'})
    assert client.get(url).status_code == 404
