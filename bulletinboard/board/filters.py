from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter, CharFilter
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Category, Response, Profile


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label=_('Title')
    )

    category = ModelMultipleChoiceFilter(
        field_name="category",
        queryset=Category.objects.all(),
        label=_('Category'),
    )

    creation_date_after = DateFilter(
        field_name='creation_date',
        lookup_expr='gt',
        label=_('Creation date after'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = []


class ResponseFilter(FilterSet):
    post = ModelMultipleChoiceFilter(
        field_name='post',
        queryset=Post.objects.all(),
        label=_('Post'),
    )

    title = CharFilter(
        field_name='text',
        lookup_expr='icontains',
        label=_('Text')
    )

    creation_date_after = DateFilter(
        field_name='creation_date',
        lookup_expr='gt',
        label=_('Creation date after'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Response
        fields = []