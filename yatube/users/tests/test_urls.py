from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls_names = {
            'users/signup.html': reverse('users:signup'),
            'users/logged_out.html': reverse('users:logout'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': reverse('users:password_reset'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'
            ),
            'users/password_reset_confirm.html': reverse(
                'users:password_reset_confirm', kwargs={
                    'uidb64': 'NQ',
                    'token': '5tl-3e16ac7ead9890b84399',
                }
            ),
            'users/password_reset_complete.html': reverse(
                'users:password_reset_complete'
            ),
        }
        for template, address in templates_urls_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location(self):
        """Проверка адресов страниц, доступных всем пользователям"""
        urls_unauthorized = [
            reverse('users:signup'),
            reverse('users:logout'),
            reverse('users:login'),
            reverse('users:password_reset'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_confirm', kwargs={
                    'uidb64': 'NQ',
                    'token': '5tl-3e16ac7ead9890b84399'}),
            reverse('users:password_reset_complete'),
        ]
        for url in urls_unauthorized:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_authorized(self):
        """Проверка доступности страниц для авторизованного пользователя"""
        urls_authorized = [
            reverse('users:password_change'),
            reverse('users:password_change_done')
        ]
        for url in urls_authorized:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous(self):
        """Страницы смены пароля перенаправляют анонимного пользователя."""
        urls = [
            reverse('users:password_change'),
            reverse('users:password_change_done')
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}'
                )
