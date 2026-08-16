"""
Zoom Server-to-Server OAuth API Client
Документация: https://developers.zoom.us/docs/api/rest/
"""
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ZoomAPIClient:
    """Клиент для работы с Zoom API"""

    def __init__(self, account_id=None, client_id=None, client_secret=None):
        config = settings.ZOOM_CONFIG
        self.account_id = account_id or config['ACCOUNT_ID']
        self.client_id = client_id or config['CLIENT_ID']
        self.client_secret = client_secret or config['CLIENT_SECRET']
        self.base_url = config['BASE_URL']
        self.token_url = config['TOKEN_URL']

    def get_access_token(self):
        """Получение access token (с кешированием)"""
        cache_key = f'zoom_token_{self.client_id}'
        token = cache.get(cache_key)

        if token:
            return token

        try:
            response = requests.post(
                self.token_url,
                headers={
                    'Authorization': 'Basic ' + self._get_basic_auth(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': settings.ZOOM_CONFIG['GRANT_TYPE'],
                    'account_id': self.account_id
                }
            )
            response.raise_for_status()
            data = response.json()

            # Кеш на 1 час (токен живёт 1 час)
            cache.set(cache_key, data['access_token'], timeout=3500)

            return data['access_token']
        except requests.RequestException as e:
            logger.error(f"Zoom token error: {e}")
            raise

    def _get_basic_auth(self):
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

    # ==================== MEETINGS ====================

    def create_meeting(self, user_id, meeting_data):
        """Создание встречи"""
        url = f"{self.base_url}/users/{user_id}/meetings"
        response = requests.post(url, headers=self._headers(), json=meeting_data)
        response.raise_for_status()
        return response.json()

    def get_meeting(self, meeting_id):
        """Получение информации о встрече"""
        url = f"{self.base_url}/meetings/{meeting_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def update_meeting(self, meeting_id, meeting_data):
        """Обновление встречи"""
        url = f"{self.base_url}/meetings/{meeting_id}"
        response = requests.patch(url, headers=self._headers(), json=meeting_data)
        response.raise_for_status()
        return response.json()

    def delete_meeting(self, meeting_id):
        """Удаление встречи"""
        url = f"{self.base_url}/meetings/{meeting_id}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return response.status_code == 204

    def list_meetings(self, user_id, type='scheduled'):
        """Список встреч пользователя"""
        url = f"{self.base_url}/users/{user_id}/meetings"
        params = {'type': type, 'page_size': 300}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    # ==================== USERS ====================

    def get_user(self, user_id='me'):
        """Получение информации о пользователе Zoom"""
        url = f"{self.base_url}/users/{user_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def list_users(self, page_size=30):
        """Список пользователей"""
        url = f"{self.base_url}/users"
        params = {'page_size': page_size}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    # ==================== RECORDINGS ====================

    def get_meeting_recordings(self, meeting_id):
        """Получение записей встречи"""
        url = f"{self.base_url}/meetings/{meeting_id}/recordings"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def delete_recording(self, meeting_id):
        """Удаление всех записей встречи"""
        url = f"{self.base_url}/meetings/{meeting_id}/recordings"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return response.status_code == 204

    # ==================== WEBHOOKS ====================

    def verify_webhook(self, payload, timestamp, token, signature):
        """Проверка подписи webhook"""
        import hashlib
        import hmac

        message = f"v0:{timestamp}:{payload}"
        expected = hmac.new(
            token.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"v0={expected}" == signature
