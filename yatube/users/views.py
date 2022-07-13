from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetCompleteView,
)

from .forms import CreationFormUser


class SignUp(CreateView):
    form_class = CreationFormUser

    template_name = 'users/signup.html'

    success_url = reverse_lazy('posts:index')


class PasswordReset(PasswordResetView):
    """ Сменить пароль может только зарегистрированный пользователь. """
    template_name = 'users/password_reset_form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PasswordResetComplete(PasswordResetCompleteView):
    """ Подтверждения отправки письма на почту,
        может видеть только зарегистрированный пользователь. """
    template_name = 'users/password_reset_done.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
