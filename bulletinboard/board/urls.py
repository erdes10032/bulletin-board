from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, MainPage, subscribe_to_category, \
   ProfileDetail, ProfileUpdate, ResponseList, ResponseCreate, ResponseUpdate, ResponseDelete, accept_response, reject_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

urlpatterns = [
   path('', MainPage.as_view(), name='main_page'),
   path('posts/', PostList.as_view(), name='post_list'),
   path('posts/<int:pk>', PostDetail.as_view(), name = 'post_detail'),
   path('posts/create/', PostCreate.as_view(), name='post_create'),
   path('posts/<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
   path('posts/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   path('posts/<int:pk>/response/create/', ResponseCreate.as_view(), name='response_create'),
   path('posts/<int:post_pk>/response/<int:pk>/edit/', ResponseUpdate.as_view(), name='response_update'),
   path('posts/<int:post_pk>/response/<int:pk>/delete/', ResponseDelete.as_view(), name='response_delete'),
   path('category/<int:category_id>/subscribe/', subscribe_to_category, name='subscribe_category'),
   path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
   path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
   path('profile/', ProfileDetail.as_view(), name='profile_detail'),
   path('profile/responses/', ResponseList.as_view(), name='my_responses'),
   path('profile/edit/', ProfileUpdate.as_view(), name='profile_edit'),
   path('post/<int:post_pk>/response/<int:pk>/accept/', accept_response, name='response_accept'),
   path('post/<int:post_pk>/response/<int:pk>/reject/', reject_response, name='response_reject'),
]