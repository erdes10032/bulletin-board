from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission, Group
from board.models import Profile, Category, Post, Response

class CriticalPathsTests(TestCase):
    """Тесты основных сценариев использования"""

    def setUp(self):
        # Создаем тестового пользователя с правами автора
        self.user = User.objects.create_user(
            username='testauthor',
            password='testpass123'
        )
        Profile.objects.create(user=self.user, gender='male')

        # Даем права на создание постов и откликов
        add_post_perm = Permission.objects.get(codename='add_post')
        add_response_perm = Permission.objects.get(codename='add_response')
        self.user.user_permissions.add(add_post_perm, add_response_perm)

        # Добавляем в группу авторов
        authors_group, created = Group.objects.get_or_create(name='authors')
        if created:
            # Даем группе необходимые права
            authors_group.permissions.add(
                Permission.objects.get(codename='add_post'),
                Permission.objects.get(codename='change_post'),
                Permission.objects.get(codename='delete_post'),
                Permission.objects.get(codename='add_response'),
                Permission.objects.get(codename='change_response'),
                Permission.objects.get(codename='delete_response'),
            )
        self.user.groups.add(authors_group)

        self.category = Category.objects.create(name='heal')

    def test_post_creation_workflow(self):
        """Весь процесс создания поста работает"""
        # 1. Логин
        self.client.login(username='testauthor', password='testpass123')

        # 2. Переход на форму создания
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 200)

        # 3. Создание поста
        post_data = {
            'category': self.category.id,
            'title': 'Test Workflow Post',
            'text': 'Testing the complete workflow of post creation'
        }

        response = self.client.post(reverse('post_create'), post_data)

        # 4. Проверка редиректа
        self.assertEqual(response.status_code, 302)

        # 5. Проверка создания в БД
        post = Post.objects.filter(title='Test Workflow Post').first()
        self.assertIsNotNone(post)
        print(f"✓ Пост создан: {post.title}")

    def test_response_workflow(self):
        """Весь процесс создания отклика работает"""
        # Создаем автора и пост
        author = User.objects.create_user(username='postauthor', password='pass')
        author_profile = Profile.objects.create(user=author, gender='female')

        # Даем автору права на создание постов
        add_post_perm = Permission.objects.get(codename='add_post')
        author.user_permissions.add(add_post_perm)

        post = Post.objects.create(
            author=author_profile,
            category=self.category,
            title='Post for Responses',
            text='Content for testing responses'
        )

        # Логинимся как обычный пользователь с правами на отклики
        responder = User.objects.create_user(username='responder', password='pass')
        responder_profile = Profile.objects.create(user=responder, gender='male')

        # Даем права на создание откликов
        add_response_perm = Permission.objects.get(codename='add_response')
        responder.user_permissions.add(add_response_perm)

        self.client.login(username='responder', password='pass')

        # Проверяем доступ к форме создания отклика
        response_get = self.client.get(
            reverse('response_create', args=[post.id])
        )
        self.assertEqual(response_get.status_code, 200)

        # Создаем отклик
        response_post = self.client.post(
            reverse('response_create', args=[post.id]),
            {'text': 'Test response'}
        )

        # Должен быть редирект на страницу поста
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(response_post.url.startswith('/posts/'))

        # Проверяем создание в БД
        created_response = Response.objects.filter(
            post=post,
            user=responder,
            text='Test response'
        ).first()

        self.assertIsNotNone(created_response)
        print(f"✓ Отклик создан пользователем: {responder.username}")