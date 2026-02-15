import pytest
from django.utils import timezone
import pytz


@pytest.mark.middleware
class TestTimezoneMiddleware:
    """Тесты middleware для часовых поясов"""

    def test_timezone_middleware_sets_timezone(self, client):
        """Тест установки часового пояса из сессии"""
        session = client.session
        session['django_timezone'] = 'Europe/Moscow'
        session.save()

        response = client.get('/')

        # Проверяем, что часовой пояс активирован
        assert timezone.get_current_timezone_name() == 'Europe/Moscow'

    def test_timezone_context_processor(self, client):
        """Тест контекстного процессора"""
        session = client.session
        session['django_timezone'] = 'Europe/Moscow'
        session.save()

        response = client.get('/')

        # Проверяем наличие времени в контексте
        assert 'current_time' in response.context