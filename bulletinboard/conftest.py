# conftest.py

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.auth.models import User, Group, Permission
from django.core.management import call_command
from pytest_factoryboy import register
from board.models import Profile, Category, Post, Response
from factory.django import DjangoModelFactory
import factory
from faker import Faker
from PIL import Image
import io
from django.core import mail
from django.test import Client

# Загружаем .env файл
env_path = Path(__file__).parent / 'bulletinboard' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded test .env from {env_path}")
else:
    print("WARNING: .env not found, using default values")
    os.environ['SECRET_KEY'] = 'django-insecure-test-key-for-pytest-only'

fake = Faker()

# FACTORIES
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    gender = factory.Iterator(['male', 'female'])
    avatar = factory.django.ImageField(color='blue')


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = factory.Iterator([
        'tank', 'heal', 'damage dealer', 'vendor',
        'guildmaster', 'questgiver', 'blacksmith'
    ])


class PostFactory(DjangoModelFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(ProfileFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(lambda n: f'Test Post {n}')
    text = factory.Faker('paragraph', nb_sentences=5)


class ResponseFactory(DjangoModelFactory):
    class Meta:
        model = Response

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Faker('sentence', nb_words=10)
    status = factory.Iterator(['accepted', 'in anticipation', 'rejected'])


# Регистрируем фабрики
register(UserFactory)
register(ProfileFactory)
register(CategoryFactory)
register(PostFactory)
register(ResponseFactory)


# FIXTURES

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически дает доступ к БД для всех тестов"""
    pass


@pytest.fixture
def authors_group():
    group, created = Group.objects.get_or_create(name='authors')
    if created:
        permissions = Permission.objects.filter(
            codename__in=[
                'add_post', 'change_post', 'delete_post',
                'add_response', 'change_response', 'delete_response',
                'view_post', 'view_response'
            ]
        )
        group.permissions.set(permissions)
    return group


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )
    return user


@pytest.fixture
def author_user(db, authors_group):
    user = UserFactory()
    user.groups.add(authors_group)
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def regular_user(db):
    user = UserFactory()
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def another_regular_user(db):
    """Дополнительный обычный пользователь"""
    user = UserFactory(username='another_user', email='another@example.com')
    Profile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def test_category(db):
    return CategoryFactory()


@pytest.fixture
def test_post(db, author_user):
    profile = Profile.objects.get(user=author_user)
    return PostFactory(author=profile)


@pytest.fixture
def test_response(db, test_post, regular_user):
    return ResponseFactory(post=test_post, user=regular_user)


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


@pytest.fixture
def authenticated_client(client, author_user):
    client.force_login(author_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Настройка тестовой БД"""
    with django_db_blocker.unblock():
        call_command('migrate')


@pytest.fixture
def mail_outbox():
    """Фикстура для проверки отправленных email"""
    return mail.outbox


@pytest.fixture
def image_file():
    """Создает временный файл изображения для тестов"""
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), 'white')
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


@pytest.fixture
def test_post_with_responses(test_post, regular_user, another_regular_user):
    """Пост с несколькими откликами"""
    ResponseFactory.create_batch(
        3,
        post=test_post,
        user=regular_user,
        status='in anticipation'
    )
    ResponseFactory.create(
        post=test_post,
        user=another_regular_user,
        status='accepted'
    )
    return test_post


@pytest.fixture
def subscribed_user(regular_user, test_category):
    """Пользователь, подписанный на категорию"""
    test_category.subscribers.add(regular_user)
    return regular_user


@pytest.fixture
def api_client():
    """Клиент для API тестов"""
    from rest_framework.test import APIClient
    return APIClient()