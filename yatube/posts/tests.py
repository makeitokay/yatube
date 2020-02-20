from django.core import mail
from django.test import TestCase, Client

from .models import User, Post


class EmailTest(TestCase):
    def setUp(self) -> None:
        client = Client()

        self.start_outbox_size = len(mail.outbox)
        client.post("/auth/signup/", {
            "first_name": "Василий",
            "last_name": "Пупкин",
            "username": "vasya2005",
            "email": "vasya@mail.ru",
            "password1": "vasya12345678",
            "password2": "vasya12345678"
        }, follow=True)

    def test_send_email(self):
        """Проверяет, что после регистрации пользователю отправилось письмо"""
        self.assertEqual(len(mail.outbox) - 1, self.start_outbox_size)


class ProfileTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="vasya2005", email="vasya@mail.ru", password="vasya")

    def test_profile_page(self):
        profile_response = self.client.get("/vasya2005/", follow=True)
        self.assertEqual(profile_response.status_code, 200)


class CreatePostTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="vasya2005", email="vasya@mail.ru", password="vasya")

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


class EditPost(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="vasya2005", email="vasya@mail.ru", password="vasya")
        self.other_user = User.objects.create_user(username="fedor2004", email="fedor@yandex.ru", password="fedor")

        # Добавим пост для пользователя vasya2005
        self.client.force_login(self.user)
        self.client.post("/new/", {
            "text": "Очень интересный пост о жизни",
        }, follow=True)

    def test_edit_post(self):
        self.client.post("/vasya2005/1/edit/", {
            "text": "UPD: Пост стал ещё интереснее и жизненнее"
        }, follow=True)

        index_response = self.client.get("/", follow=True)
        self.assertContains(index_response, "UPD: Пост стал ещё интереснее и жизненнее")

        profile_response = self.client.get("/vasya2005/", follow=True)
        self.assertContains(profile_response, "UPD: Пост стал ещё интереснее и жизненнее")

        post_response = self.client.get("/vasya2005/1/", follow=True)
        self.assertContains(post_response, "UPD: Пост стал ещё интереснее и жизненнее")

    def test_edit_not_own_post(self):
        self.client.force_login(self.other_user)

        response = self.client.post("/vasya2005/1/edit/", {
            "text": "Автора взломали"
        }, follow=True)

        self.assertIn(("/", 302), response.redirect_chain)
