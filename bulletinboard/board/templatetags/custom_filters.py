import html
import re

from django import template
from django.utils.html import strip_tags
from django.utils.translation import gettext as _


register = template.Library()


@register.filter
def join_categories(value):
    return ", ".join([category.name for category in value])


@register.filter()
def author(user):
    if user.groups.filter(name='authors').exists():
        return True
    else:
        return False


@register.filter()
def admin(user):
    if user.groups.filter(name='admin').exists():
        return True
    else:
        return False


@register.filter()
def striptags_filter(value):
    text = strip_tags(value)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text