from django.core import mail
from django.test import TestCase, Client, override_settings

from .models import User, Post, Group


# Disable caching by using DummyCache
TEST_CACHE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


class GeneralTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_not_found_error(self):
        response = self.client.get("/fsgdgdgbr/hdfbdfbth")
        self.assertEqual(response.status_code, 404)


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

    def test_email_subject(self):
        self.assertEqual(mail.outbox[-1].subject, "Регистрация на Yatube")


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
        # Отправляем запрос на главную страницу, чтобы она закешировалась
        self.client.get("/", follow=True)

    def test_publish_post(self):
        self.client.force_login(self.user)
        new_post_response = self.client.get("/new/", follow=True)
        self.assertEqual(new_post_response.status_code, 200)

    def test_publish_login_required(self):
        new_post_response = self.client.get("/new/", follow=True)
        self.assertIn(("/auth/login/?next=/new/", 302), new_post_response.redirect_chain)

    @override_settings(CACHES=TEST_CACHE)
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

    def test_cache(self):
        self.client.force_login(self.user)
        self.client.post("/new/", {
            "text": "Очень интересный пост о жизни",
        }, follow=True)
        self.assertNotContains(self.client.get("/", follow=True), "Очень интересный пост о жизни")


@override_settings(CACHES=TEST_CACHE)
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

        self.assertIn(("/vasya2005/1/", 302), response.redirect_chain)


@override_settings(CACHES=TEST_CACHE)
class ImageTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username="test", email="test@test.ru", password="test")
        self.group = Group.objects.create(title="testGroup", slug="testGroup")
        self.client.force_login(self.user)

        # Создадим пост с картинкой (картинка test_image.jpg лежит в корневой папке)
        with open("../test_image.jpg", mode="rb") as image:
            self.client.post("/new/", {"text": "test", "image": image, "group": self.group.id})

    def test_index(self):
        response = self.client.get("/", follow=True)
        self.assertContains(response, '<img class="card-img"')

    def test_post_page(self):
        response = self.client.get("/test/1/", follow=True)
        self.assertContains(response, '<img class="card-img"')

    def test_profile(self):
        response = self.client.get("/test/", follow=True)
        self.assertContains(response, '<img class="card-img"')

    def test_group(self):
        response = self.client.get("/group/testGroup", follow=True)
        self.assertContains(response, '<img class="card-img"')

    def test_graphic_secure(self):
        with open("posts/urls.py", mode="rb") as image:
            self.client.post("/new/", {"text": "test", "image": image})
            # Если форма создания не валидна, то пост не должен был добавиться в базу данных:
            self.assertFalse(Post.objects.filter(pk=2).exists())