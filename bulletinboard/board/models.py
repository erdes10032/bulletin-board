from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


POST_CATEGORIES = [
    ('tank', _('Tank')),
    ('heal', _('Heal')),
    ('damage dealer', _('Damage dealer')),
    ('vendor', _('Vendor')),
    ('guildmaster', _('Guildmaster')),
    ('questgiver', _('Questgiver')),
    ('blacksmith', _('Blacksmith')),
    ('leatherworker', _('Leatherworker')),
    ('potion maker', _('Potion maker')),
    ('spell master', _('Spell master')),
]

GENDER_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female')),
]

STATUS_CHOICES = [
    ('accepted', _('Accepted')),
    ('in anticipation', _('In anticipation')),
    ('rejected', _('Rejected')),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, default='male')
    avatar = models.ImageField(upload_to='avatars/')

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=13, choices=POST_CATEGORIES, default='tank')
    subscribers = models.ManyToManyField(User, through='CategoryUser')

    def __str__(self):
        for code, trans_name in POST_CATEGORIES:
            if code == self.name:
                return str(trans_name)
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = RichTextUploadingField()

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def get_absolute_url_with_domain(self):
        from django.conf import settings
        domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1:8000')
        return f"http://{domain}{self.get_absolute_url()}"

    def __str__(self):
        return self.title


class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default='in anticipation')


class CategoryUser(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)