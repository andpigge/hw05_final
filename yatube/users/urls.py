from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    LogoutView
)

from .views import (
    PasswordReset,
    PasswordResetComplete,
    SignUp
)


app_name = 'users'

"""
Пути сброса пароля.
Доступно только авторизированным пользователям.
"""
password_reset = (
    path(
        'password_reset/',
        PasswordReset.as_view(),
        name='reset_form'
    ),
    path(
        'reset/done/',
        PasswordChangeView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetComplete.as_view(),
        name='reset_done'
    ),
)

"""
Пути смены пароля.
Доступно только авторизированным пользователям.
"""
password_change = (
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='done'
    ),
)

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'signup/',
        SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    *password_change,
    *password_reset
]
