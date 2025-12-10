import os
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions
from .filters import PostFilter, ResponseFilter
from .forms import PostForm, ProfileForm, ResponseForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.core.cache import cache
from pytz import common_timezones
from django.utils.translation import gettext as _
from .serializers import *



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostList(ListView):
    model = Post
    ordering = '-creation_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.all()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'posts-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'posts-{self.kwargs["pk"]}', obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            category = self.get_object().category
            is_subscribed = category.subscribers.filter(id=self.request.user.id).exists()
            author_profile = Profile.objects.get(user=self.request.user)
            if self.get_object().author != author_profile and not self.request.user.groups.filter(
                    name='admin').exists():
                user_responses_to_this_post = Response.objects.filter(
                    post=self.object,
                    user=self.request.user
                ).order_by('-creation_date')
            else:
                user_responses_to_this_post = Response.objects.filter(
                    post=self.object
                ).order_by('-creation_date')
            context['is_subscribed'] = is_subscribed
            context['user_responses_to_post'] = user_responses_to_this_post
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'board.add_post'
    form_class = PostForm
    model = Post
    template_name = 'edit.html'

    def form_valid(self, form):
        author, created = Profile.objects.get_or_create(user=self.request.user)
        form.instance.author = author
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('post')
        return context


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('board.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'edit.html'
    queryset = Post.objects.all()

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            author = Profile.objects.get(user=request.user)
            if self.get_object().author != author and not request.user.groups.filter(name='admin').exists():
                raise PermissionDenied(_("You can edit only your own posts"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        cache_key = f'posts-{self.object.id}'
        cache.delete(cache_key)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('post')
        return context


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_post'
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('post_list')
    queryset = Post.objects.all()

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            author = Profile.objects.get(user=request.user)
            if self.get_object().author != author and not request.user.groups.filter(name='admin').exists():
                raise PermissionDenied(_("You can delete only your own posts"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('post')
        return context


class MainPage(TemplateView):
    template_name = 'main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timezones'] = common_timezones
        return context

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')


class ProfileDetail(DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self, *args, **kwargs):
        return Profile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        context['user'] = self.request.user
        context['user_posts'] = Post.objects.filter(author=profile)
        context['user_responses'] = Response.objects.filter(user=self.request.user)
        context['user_subscriptions'] = Category.objects.filter(subscribers=self.request.user)
        return context

class ProfileUpdate(UpdateView):
    form_class = ProfileForm
    model = Profile
    template_name = 'profile_edit.html'
    success_url = reverse_lazy('profile_detail')

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ResponseList(PermissionRequiredMixin, ListView):
    permission_required = 'board.view_response'
    model = Response
    ordering = '-creation_date'
    template_name = 'responses.html'
    context_object_name = 'responses'
    paginate_by = 10

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        queryset = Response.objects.filter(post__author=profile)
        self.filterset = ResponseFilter(self.request.GET, queryset=queryset)
        if 'post' in self.filterset.form.fields:
            self.filterset.form.fields['post'].queryset = Post.objects.filter(author=profile)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class ResponseCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'board.add_response'
    form_class = ResponseForm
    model = Response
    template_name = 'edit.html'

    def form_valid(self, form):
        author, created = Profile.objects.get_or_create(user=self.request.user)
        post = Post.objects.get(pk=self.kwargs['pk'])
        form.instance.user = author.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('response')
        return context

class ResponseUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('board.change_response',)
    form_class = ResponseForm
    model = Response
    template_name = 'edit.html'
    queryset = Response.objects.all()

    def get_object(self, queryset=None):
        post_pk = self.kwargs.get('post_pk')
        pk = self.kwargs.get('pk')
        return Response.objects.get(pk=pk, post_id=post_pk)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            response = self.get_object()
            if response.user != request.user and not request.user.groups.filter(name='admin').exists():
                raise PermissionDenied(_("You can edit only your own responses"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('response')
        return context


class ResponseDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_response'
    model = Response
    template_name = 'delete.html'
    queryset = Response.objects.all()

    def get_object(self, queryset=None):
        post_pk = self.kwargs.get('post_pk')
        pk = self.kwargs.get('pk')
        return Response.objects.get(pk=pk, post_id=post_pk)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            response = self.get_object()
            if response.user != request.user and not request.user.groups.filter(name='admin').exists():
                raise PermissionDenied(_("You can delete only your own posts"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = _('response')
        return context

@login_required()
def subscribe_to_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if not category.subscribers.filter(id = request.user.id).exists():
        category.subscribers.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def accept_response(request, post_pk, pk):
    response = Response.objects.get(pk=pk, post_id = post_pk)
    profile = Profile.objects.get(user=request.user)
    if response.post.author != profile and not request.user.groups.filter(name='admin').exists():
        raise PermissionDenied(_("Only post author can accept responses"))
    response.status = 'accepted'
    response.save()
    send_mail(
        subject=_('Your response has been accepted'),
        message=_('Your response to post "%s" has been accepted by the author.') % response.post.title,
        from_email=os.getenv('EMAIL_HOST_USER'),
        recipient_list=[response.user.email],
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def reject_response(request, post_pk, pk):
    response = Response.objects.get(pk=pk, post_id=post_pk)
    profile = Profile.objects.get(user=request.user)
    if response.post.author != profile and not request.user.groups.filter(name='admin').exists():
        raise PermissionDenied(_("Only post author can reject responses"))
    response.status = 'rejected'
    response.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))