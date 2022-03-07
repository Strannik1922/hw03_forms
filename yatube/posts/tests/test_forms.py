import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm

from ..models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='Описание группы для теста'
        )
        cls.group_other = Group.objects.create(
            title='test-title-other',
            slug='test-slug-other',
            description='Описание группы для нового теста'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Проверочный тест'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """При отправке валидной формы со страницы create
        создаётся новая запись в базе данных
        """

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест',
            'group': '1'
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тест',
                author=self.user,
                group=self.group
            ).exists()
        )

    def test_post_edit(self):
        """При отправке валидной формы со страницы post_edit
        происходит изменение поста с отправленным id в базе данных
        """

        form_data = {
            'text': 'Проверочный тест кода',
            'group': '2'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        edit_post = response.context['post']
        self.assertTrue(
            Post.objects.filter(
                text=edit_post.text,
                author=self.user,
                group=self.group_other
            ).exists
        )
