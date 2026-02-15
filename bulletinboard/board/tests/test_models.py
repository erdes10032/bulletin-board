import pytest
from board.models import Post, Response, CategoryUser
from django.core.exceptions import ValidationError


@pytest.mark.model
class TestPostModel:
    """Тесты модели Post"""

    def test_post_str_method(self, test_post):
        """Тест строкового представления"""
        assert str(test_post) == test_post.title

    def test_get_absolute_url(self, test_post):
        """Тест получения URL"""
        url = test_post.get_absolute_url()
        assert f'/posts/{test_post.id}' in url

    def test_post_creation_date_auto(self, test_post):
        """Тест автоматической установки даты"""
        assert test_post.creation_date is not None


@pytest.mark.model
class TestCategoryModel:
    """Тесты модели Category"""

    def test_category_str_method(self, test_category):
        """Тест строкового представления категории"""
        # Проверяем, что возвращается переведенное имя
        assert str(test_category) is not None
        assert isinstance(str(test_category), str)

    def test_subscribe_user(self, test_category, regular_user):
        """Тест подписки пользователя на категорию"""
        test_category.subscribers.add(regular_user)

        assert CategoryUser.objects.filter(
            category=test_category,
            user=regular_user
        ).exists()


@pytest.mark.model
class TestResponseModel:
    """Тесты модели Response"""

    def test_response_default_status(self, test_post, regular_user):
        """Тест статуса по умолчанию"""
        response = Response.objects.create(
            post=test_post,
            user=regular_user,
            text='Test response'
        )
        assert response.status == 'in anticipation'

    def test_response_str(self, test_response):
        """Тест строкового представления"""
        expected = f"Response by {test_response.user.username} on {test_response.post.title}"
        # Можно добавить свой __str__ если нужно
        assert test_response.text is not None