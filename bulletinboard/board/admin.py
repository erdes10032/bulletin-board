from django.contrib import admin
from .models import Post, Response
from modeltranslation.admin import \
    TranslationAdmin


class PostAdmin(TranslationAdmin):
    model = Post


class ResponseAdmin(TranslationAdmin):
    model = Response


admin.site.register(Post)
admin.site.register(Response)
