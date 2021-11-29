import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_1 = Group.objects.create(
            title='Тестовый заголовок 1',
            description='Тестовое описание 1',
            slug='test-slug-1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовое описание 2',
            slug='test-slug-2',
        )
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group_1,
            author=cls.user,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def check_post_attributes(self, post):
        post_text = post.text
        post_group = post.group.slug
        post_author = post.author.username
        post_image = post.image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group_1.slug)
        self.assertEqual(post_author, self.user.username)
        self.assertEqual(post_image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group_1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'not_existing_slug'}
            ): 'core/404.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон главной страниц сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.check_post_attributes(post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон страницы группы сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug})
        )
        post = response.context['page_obj'][0]
        group = response.context['group']
        group_title = group.title
        group_description = group.description
        group_slug = group.slug
        self.check_post_attributes(post)
        self.assertEqual(group_title, self.group_1.title)
        self.assertEqual(group_description, self.group_1.description)
        self.assertEqual(group_slug, self.group_1.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон профайла пользователя сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        post = response.context['page_obj'][0]
        author = response.context['author']
        author_username = author.username
        self.check_post_attributes(post)
        self.assertEqual(author_username, self.user.username)

    def test_post_detail_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        amount = response.context['amount']
        self.check_post_attributes(post)
        self.assertEqual(amount, 1)

    def test_create_edit_pages_show_correct_context(self):
        """Шаблоны страниц создания и редактирования
        постов сформированы с правильным контекстом."""
        urls = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_appear_on_expected_pages(self):
        """При создании поста с указанной группой
        пост появляется на ожидаемых страницах."""
        expected_pages_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for url in expected_pages_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                post = response.context['page_obj'][0]
                self.check_post_attributes(post)

    def test_post_not_in_wrong_group(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cashe_index_page(self):
        """Проверка правильной работы кеширования."""
        test_post = Post.objects.create(
            text='Тестируем кэш',
            group=self.group_2,
            author=self.user,
        )
        content_before_delete = self.authorized_client.get(
            reverse('posts:index')).content
        test_post.delete()
        content_after_delete = self.authorized_client.get(
            reverse('posts:index')).content
        cache.clear()
        content_after_cache_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(
            content_before_delete, content_after_delete
        )
        self.assertNotEqual(
            content_before_delete, content_after_cache_clear
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestAuthor')
        cls.user2 = User.objects.create_user(username='TestFollower')
        cls.user3 = User.objects.create_user(username='TestNotFollower')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.user2)
        cls.authorized_not_follower = Client()
        cls.authorized_not_follower.force_login(cls.user3)
        cls.follow = Follow.objects.create(
            user=cls.user2,
            author=cls.user3
        )

    def setUp(self):
        cache.clear()

    def test_follow_author(self):
        """Авторизованный пользователь может
        подписываться на других пользователей."""
        follow_count = Follow.objects.count()
        self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(user=self.user2, author=self.user).exists()
        )

    def test_unfollow_author(self):
        """Авторизованный пользователь может
        удалять пользователей из своих подписок."""
        follow_count = Follow.objects.count()
        self.authorized_follower.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user3.username})
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(user=self.user2, author=self.user3).exists()
        )

    def test_author_post_appear_in_newsfeed(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан"""
        self.authorized_follower.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=self.user
        )
        response = self.authorized_follower.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, response.context['page_obj'].object_list)

    def test_post_not_in_wrong_newsfeed(self):
        """Новая запись пользователя не появляется
        в ленте тех, кто на него не подписан"""
        new_post = Post.objects.create(
            text='Новый тестовый текст',
            author=self.user
        )
        response = self.authorized_not_follower.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(new_post, response.context['page_obj'].object_list)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='TestAuthor')

        for i in range(13):
            Post.objects.create(
                text=f'Тестовый текст {i+1}',
                group=cls.group,
                author=cls.user
            )

    def setUp(self):
        self.user = User.objects.get(username="TestAuthor")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверяем, что количество постов на первой странице равно 10."""
        url_first_page_with_pagination = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})]

        for url in url_first_page_with_pagination:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка количества постов на второй странице."""
        url_second_page_with_pagination = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]
        for url in url_second_page_with_pagination:
            with self.subTest(url=url):
                response = self.authorized_client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
