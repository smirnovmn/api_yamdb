
from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'categories', views.CategoryViewSet, basename='categories')
router_v1.register(r'genres', views.GenreViewSet, basename='genres')
router_v1.register(r'titles', views.TitleViewSet, basename='titles')


urlpatterns = [
    path(
        'v1/',
        include(router_v1.urls)
    ),
    path(
        'v1/auth/signup/',
        views.SignUpView.as_view(),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        views.CustomTokenObtainPairView.as_view(),
        name='token'
    ),
    path(
        'v1/users/me/',
        views.UserSelfAPIView.as_view(),
        name='user-self-detail'
    ),
    path(
        'v1/users/<slug:username>/',
        views.UserDetailAPIView.as_view(),
        name='user-detail'
    ),
    path(
        'v1/users/',
        views.UsersAPIView.as_view(),
        name='users'
    ),
]
