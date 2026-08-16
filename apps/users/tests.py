import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_user_str_safe():
    user = get_user_model().objects.create_user(username='ivan', password='x')
    assert str(user) == 'ivan'   # регресс: AttributeError 'specialization'


def test_full_name_sync():
    user = get_user_model().objects.create_user(
        username='a', password='x', full_name='Ali Valiyev')
    assert user.first_name == 'Ali'
    assert user.last_name == 'Valiyev'
