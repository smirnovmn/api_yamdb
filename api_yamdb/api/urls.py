from django.urls import path

from . import views

app_name = 'api'


urlpatterns = [
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
