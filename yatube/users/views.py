from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = "/auth/login/"
    template_name = "signup.html"

    def form_valid(self, form):
        email = form["email"]
        form.send_sign_up_mail(email)
        return super().form_valid(form)