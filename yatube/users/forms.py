from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def send_sign_up_mail(self, recipient):
        send_mail(
            "Регистрация на Yatube",
            "Поздравляем с успешной регистрацией на Yatube!",
            "noreply@yatube.com",
            [recipient],
            fail_silently=False
        )