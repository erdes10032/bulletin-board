import pytest
from django.urls import reverse
from rest_framework import status
from board.models import Post, Response


@pytest.mark.api
class TestPostAPI:
    """Тесты API для постов"""

    def test_list_posts_unauthenticated(self, api_client, test_post):
        """Неавторизованный пользователь может видеть посты"""
        url = reverse('post-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_create_post_authenticated(self, api_client, author_user, test_category):
        """Авторизованный пользователь может создать пост"""
        api_client.force_authenticate(user=author_user)
        url = reverse('post-list')

        # Для HyperlinkedModelSerializer нужно передавать URL, а не ID
        category_url = reverse('category-detail', args=[test_category.id])

        # Также нужно получить URL автора (профиля)
        author_profile = author_user.profile
        author_url = reverse('profile-detail', args=[author_profile.id])

        data = {
            'author': author_url,  # URL автора
            'category': category_url,  # URL категории
            'title': 'API Test Post',
            'text': 'This is a test post created via API with enough length'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(title='API Test Post').exists()

    def test_filter_posts_by_category(self, api_client, test_category, test_post):
        """Тест фильтрации постов по категории"""
        url = reverse('post-list')
        response = api_client.get(url, {'category': test_category.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0


@pytest.mark.api
class TestResponseAPI:
    """Тесты API для откликов"""

    def test_create_response(self, api_client, regular_user, test_post):
        """Создание отклика через API"""
        api_client.force_authenticate(user=regular_user)
        url = reverse('response-list')

        # Для HyperlinkedModelSerializer нужно передавать URL
        post_url = reverse('post-detail', args=[test_post.id])
        user_url = reverse('user-detail', args=[regular_user.id])

        data = {
            'post': post_url,  # URL поста
            'user': user_url,  # URL пользователя
            'text': 'API test response'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED