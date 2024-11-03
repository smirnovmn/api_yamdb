from django.urls import include, path
from rest_framework import routers

from . import views

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', views.UsersViewSet, basename='users')
router_v1.register(r'categories', views.CategoryViewSet, basename='categories')
router_v1.register(r'genres', views.GenreViewSet, basename='genres')
router_v1.register(r'titles', views.TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)


urlpatterns = [
    path(
        'v1/auth/signup/',
        views.SignUpView.as_view(),
        name='signup'
    ),
    path(
        'v1/auth/token/',
        views.YamdbTokenObtainPairView.as_view(),
        name='token'
    ),
    path(
        'v1/users/me/',
        views.UserSelfAPIView.as_view(),
        name='user-self-detail'
    ),
    path(
        'v1/users/<slug:username>/',
        views.UsersViewSet.as_view({'get': 'retrieve',
                                    'patch': 'partial_update',
                                    'delete': 'destroy'}),
        name='user-detail'
    ),
    path(
        'v1/',
        include(router_v1.urls)
    ),
]
