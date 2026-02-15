import pytest
from django.urls import reverse
from board.models import Profile, Post
from pytest_django.asserts import assertContains, assertRedirects


@pytest.mark.smoke
class TestSmokeTests:
    """Тест основных частей"""

    def test_home_page_loads(self, client):
        """Главная страница загружается"""
        response = client.get('/')
        assert response.status_code == 200
        assertContains(response, 'Добро пожаловать на сайт')

    def test_posts_page_loads(self, client):
        """Страница постов загружается"""
        response = client.get(reverse('post_list'))
        assert response.status_code == 200

    def test_admin_login(self, client):
        """Админ панель доступна"""
        response = client.get('/admin/')
        # Должен быть редирект на логин (302) или доступ (200 если уже залогинен)
        assert response.status_code in [200, 302]


@pytest.mark.model
class TestModelCreationTests:
    """Тесты создания моделей"""

    def test_create_user_and_profile(self, user_factory, profile_factory):
        """Можно создать пользователя и профиль"""
        user = user_factory()
        profile = profile_factory(user=user, gender='male')

        assert str(profile) == user.username
        assert profile.gender == 'male'

    def test_create_post(self, post_factory):
        """Можно создать пост"""
        post = post_factory(title='Test Post')

        assert post.title == 'Test Post'
        assert post.author.user.username is not None