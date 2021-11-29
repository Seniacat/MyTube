from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
        )

    def setUp(self):
        cache.clear()

    def test_url_exists_at_desired_location(self):
        """Проверка адресов страниц, доступных всем пользователям"""
        urls = [
            '/', f'/group/{self.group.slug}/',
            f'/profile/{self.author.username}/', f'/posts/{self.post.id}/'
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_authorized(self):
        """Проверка доступности страниц для авторизованного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_anonymous(self):
        """Страницы создания, редактирования и комментирования постов
         перенаправляют анонимного пользователя."""
        urls = ['/create/', f'/posts/{self.post.id}/edit/',
                f'/posts/{self.post.id}/comment/',
                f'/profile/{self.author.username}/follow/',
                f'/profile/{self.author.username}/unfollow/'
                ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={url}'
                )

    def test_post_edit_url_accessible_for_author(self):
        """Проверка возможности редактирования поста его автором."""
        response = self.authorized_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_not_author(self):
        """Страница редактирования поста перенаправляет
        пользователя, не являющегося автором поста."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_wrong_url_returns_404(self):
        """Проверка вывода ошибки 404 при запросе
        к несуществующей странице."""
        response = self.guest_client.get('/group/not_exist/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/group/not_exist/': 'core/404.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
