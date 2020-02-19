from django.core import mail
from django.test import TestCase, Client

from .models import User


class EmailTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.start_outbox_size = len(mail.outbox)
        self.signup_response = self.client.post("/auth/signup/", {
            "first_name": "Василий",
            "last_name": "Пупкин",
            "username": "vasya2005",
            "email": "vasya@mail.ru",
            "password1": "vasya12345678",
            "password2": "vasya12345678"
        }, follow=True)

        self.user = User.objects.get(username="vasya2005")

    def test_send_email(self):
        self.assertEqual(len(mail.outbox) - 1, self.start_outbox_size)

    def test_profile_page(self):
        profile_response = self.client.get("/vasya2005/", follow=True)
        self.assertEqual(profile_response.status_code, 200)

    def test_publish_post(self):
        self.client.force_login(self.user)
        new_post_response = self.client.get("/new/", follow=True)
        self.assertEqual(new_post_response.status_code, 200)

    def test_publish_login_required(self):
        new_post_response = self.client.get("/new/", follow=True)
        self.assertIn(("/auth/login/?next=/new/", 302), new_post_response.redirect_chain)

    def test_new_post(self):
        self.client.force_login(self.user)
        self.client.post("/new/", {
            "text": "Очень интересный пост о жизни",
        }, follow=True)

        index_response = self.client.get("/", follow=True)
        self.assertContains(index_response, "Очень интересный пост о жизни")

        profile_response = self.client.get("/vasya2005/", follow=True)
        self.assertContains(profile_response, "Очень интересный пост о жизни")

        post_response = self.client.get("/vasya2005/1/", follow=True)
        self.assertContains(post_response, "Очень интересный пост о жизни")

    def test_edit_post(self):
        self.client.force_login(self.user)
        self.client.post("/new/", {
            "text": "Очень интересный пост о жизни",
        }, follow=True)

        self.client.post("/vasya2005/1/edit/", {
            "text": "UPD: Пост стал ещё интереснее и жизненнее"
        }, follow=True)

        index_response = self.client.get("/", follow=True)
        self.assertContains(index_response, "UPD: Пост стал ещё интереснее и жизненнее")

        profile_response = self.client.get("/vasya2005/", follow=True)
        self.assertContains(profile_response, "UPD: Пост стал ещё интереснее и жизненнее")

        post_response = self.client.get("/vasya2005/1/", follow=True)
        self.assertContains(post_response, "UPD: Пост стал ещё интереснее и жизненнее")