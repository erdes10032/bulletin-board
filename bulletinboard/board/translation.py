from .models import Category, Post, Response, Profile
from modeltranslation.translator import register, \
    TranslationOptions


@register(Post)
class MyModelTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


@register(Response)
class MyModelTranslationOptions(TranslationOptions):
    fields = ('text', 'status',)
