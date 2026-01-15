from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from board.models import Profile, Category, Post, Response


class SmokeTests(TestCase):
    """Тест основных частей"""

    def test_home_page_loads(self):
        """Главная страница загружается"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to the site')

    def test_posts_page_loads(self):
        """Страница постов загружается"""
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login(self):
        """Админ панель доступна"""
        response = self.client.get('/admin/')
        # Должен быть редирект на логин (302) или доступ (200 если уже залогинен)
        self.assertIn(response.status_code, [200, 302])


class ModelCreationTests(TestCase):
    """Тесты создания моделей"""

    def test_create_user_and_profile(self):
        """Можно создать пользователя и профиль"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        profile = Profile.objects.create(user=user, gender='male')

        self.assertEqual(str(profile), 'testuser')
        self.assertEqual(profile.gender, 'male')

    def test_create_post(self):
        """Можно создать пост"""
        user = User.objects.create_user(username='author', password='pass')
        profile = Profile.objects.create(user=user, gender='male')
        category = Category.objects.create(name='tank')

        post = Post.objects.create(
            author=profile,
            category=category,
            title='Test Post',
            text='Test content with enough length'
        )

        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author.user.username, 'author')