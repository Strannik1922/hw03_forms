from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса через /about/author/"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(
            response.status_code, 200,
            ('Нужно проверить доступность страницы /about/author'
             'для неавторизованного пользователя')
        )

    def test_tech_url_exists_at_desired_location(self):
        """Проверка доступности адреса через /about/tech/"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(
            response.status_code, 200,
            ('Нужно проверить доступность страницы /about/tech'
             ' для неавторизованного пользователя')
        )

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(
            response, 'about/author.html',
            ('Нужно проверить, что для страницы "/about/author"'
             ' используется шаблон "about/author.html"')
        )

    def test_tech_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/tech/"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(
            response, 'about/tech.html',
            ('Нужно проверить, что для страницы "/about/tech"'
             ' используется шаблон "about/tech.html"')
        )

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        response = self.guest_client.get('/group/slug/')
        self.assertEqual(response.status_code, 404)

    def test_profile(self):
        response = self.guest_client.get('/profile/username/')
        self.assertEqual(response.status_code, 404)

    def test_post_detail(self):
        response = self.guest_client.get('/posts/post_id/')
        self.assertEqual(response.status_code, 404)

    def test_create_post(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.authorized_client.get('auth/signup/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""

        template_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
            'users/signup.html': '/auth/signup/'
        }
        for template, address in template_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
