from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_http_status_ok(self):
        """Проверка доступности адресов /about/author/ и /about/tech/."""
        urls = ['/about/author/', '/about/tech/']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_accessible_by_name(self):
        """URL, генерируемые при помощи имён about:author
        и 'about:tech', доступны."""
        urls = ['about:author', 'about:tech']
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech'
        }
        for template, address in templates_urls_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse(address))
                self.assertTemplateUsed(response, template)
