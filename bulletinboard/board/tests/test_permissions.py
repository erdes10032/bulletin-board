import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from board.models import Post, Response


@pytest.mark.permission
class TestPostPermissions:
    """Тесты прав доступа к постам"""

    def test_regular_user_cannot_create_post(self, client, regular_user):
        """Обычный пользователь не может создать пост"""
        client.force_login(regular_user)
        response = client.get(reverse('post_create'))

        # Должен быть 403 или редирект
        assert response.status_code in [302, 403]

    def test_author_can_edit_own_post(self, authenticated_client, test_post):
        """Автор может редактировать свой пост"""
        response = authenticated_client.get(
            reverse('post_update', args=[test_post.id])
        )
        assert response.status_code == 200

    def test_author_cannot_edit_others_post(self, client, test_post, another_regular_user):
        """Автор не может редактировать чужой пост"""
        client.force_login(another_regular_user)
        response = client.get(
            reverse('post_update', args=[test_post.id])
        )
        assert response.status_code == 403


@pytest.mark.permission
class TestResponsePermissions:
    """Тесты прав доступа к откликам"""

    def test_user_can_edit_own_response(self, client, test_post, regular_user):
        """Пользователь может редактировать свой отклик"""
        from board.models import Response
        response = Response.objects.create(
            post=test_post,
            user=regular_user,
            text='Test response'
        )

        client.force_login(regular_user)

        # Проверяем, есть ли у пользователя права на изменение отклика
        from django.contrib.auth.models import Permission
        change_response_perm = Permission.objects.get(codename='change_response')
        if not regular_user.has_perm('board.change_response'):
            # Если нет прав, добавим их для теста
            regular_user.user_permissions.add(change_response_perm)

        edit_response = client.get(
            reverse('response_update', args=[test_post.id, response.id])
        )

        # Должен быть доступ (200)
        assert edit_response.status_code == 200