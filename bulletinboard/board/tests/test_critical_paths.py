import pytest
from django.urls import reverse
from board.models import Post, Response
from pytest_django.asserts import assertRedirects


@pytest.mark.critical
@pytest.mark.integration
class TestCriticalPaths:
    """Тесты основных сценариев использования"""
    def test_post_creation_workflow(self, authenticated_client, test_category, author_user):
        """Весь процесс создания поста работает"""
        # 1. Переход на форму создания
        response = authenticated_client.get(reverse('post_create'))
        assert response.status_code == 200

        # 2. Создание поста
        post_data = {
            'category': test_category.id,
            'title': 'Test Workflow Post',
            'text': 'Testing the complete workflow of post creation with enough length'
        }
        response = authenticated_client.post(reverse('post_create'), post_data)

        # 3. Проверка редиректа - теперь на детальную страницу, а не на список
        post = Post.objects.filter(title='Test Workflow Post').first()
        assert post is not None
        assertRedirects(response, reverse('post_detail', args=[post.id]))

        # 4. Проверка создания в БД
        assert post.author.user == author_user
        print(f"Пост создан: {post.title}")

    def test_response_workflow(self, client, test_post, regular_user):
        """Весь процесс создания отклика работает"""
        # Логинимся как обычный пользователь
        client.force_login(regular_user)

        # Проверяем, есть ли у пользователя права на создание отклика
        from django.contrib.auth.models import Permission
        add_response_perm = Permission.objects.get(codename='add_response')
        if not regular_user.has_perm('board.add_response'):
            # Если нет прав, добавим их для теста
            regular_user.user_permissions.add(add_response_perm)

        # Проверяем доступ к форме создания отклика
        response_get = client.get(reverse('response_create', args=[test_post.id]))
        assert response_get.status_code == 200

        # Создаем отклик
        response_post = client.post(
            reverse('response_create', args=[test_post.id]),
            {'text': 'Test response with valid length'}
        )

        # Должен быть редирект на страницу поста
        assertRedirects(response_post, reverse('post_detail', args=[test_post.id]))

        # Проверяем создание в БД
        created_response = Response.objects.filter(
            post=test_post,
            user=regular_user,
            text='Test response with valid length'
        ).first()

        assert created_response is not None
        assert created_response.status == 'in anticipation'
        print(f"Отклик создан пользователем: {regular_user.username}")

    def test_accept_response_workflow(self, client, test_post, author_user, regular_user):
        """Тест принятия отклика автором"""
        # Создаем отклик
        response = Response.objects.create(
            post=test_post,
            user=regular_user,
            text='Test response',
            status='in anticipation'
        )

        # Логинимся как автор
        client.force_login(author_user)

        # Принимаем отклик
        response_post = client.post(
            reverse('response_accept', args=[test_post.id, response.id])
        )

        # Проверяем редирект
        assert response_post.status_code == 302

        # Проверяем изменение статуса
        response.refresh_from_db()
        assert response.status == 'accepted'
        print(f"Отклик принят автором")