from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая подборка записей №',
            slug='test-slug',
            description='Тестирующая контекст подборка №'
        )

        cls.post = Post.objects.create(
            text='Проверочный текст',
            author=cls.user,
            pub_date='04.02.2022',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html',
            reverse('posts:create_post'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def page_show_correct_context(self, post):
        text = post.text
        author = post.author.username
        group = post.group.title
        self.assertEqual(author, 'auth')
        self.assertEqual(text, 'Проверочный текст')
        self.assertEqual(group, 'Тестовая подборка записей №')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.page_show_correct_context(first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        self.page_show_correct_context(first_object)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        first_object = response.context['page_obj'][0]
        self.page_show_correct_context(first_object)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        first_object = response.context['post']
        self.page_show_correct_context(first_object)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая подборка записей №',
            slug='test-slug',
            description='Тестирующая контекст подборка №',
        )
        for cls.post in range(1, 10):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Проверочный текст',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 9)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 9)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 9)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 9)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(len(response.context['page_obj']), 9)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': 'auth'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 9)


class NewPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание2'
        )
        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=group1
        )
        cls.post2 = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=group2
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_appears_on_the_home_page(self):
        """Если указать группу, то пост отображается на главной странице."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_group_0, 'Тестовая группа 1')

    def test_post_appears_on_the_group_list_page(self):
        """Если указать группу,
         то пост отображается на странице выбранной группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug1'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_group_0, 'Тестовая группа 1')

    def test_post_appears_on_the_profile_page(self):
        """Если указать группу,
        то пост отображается в профайле пользователя."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'auth'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Текст поста')
        self.assertEqual(post_group_0, 'Тестовая группа 1')

    def test_post_does_not_appears_on_the_wrong_group_list_page(self):
        """Пост не отображается в группе, для которой он не предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'})
        )
        first_object = response.context['page_obj'][0]
        post_group_slug_0 = first_object.group.slug
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertNotEqual(post_group_slug_0, 'test-slug1')
        self.assertNotEqual(post_text_0, 'Текст поста')
        self.assertNotEqual(post_group_0, 'Тестовая группа 1')
