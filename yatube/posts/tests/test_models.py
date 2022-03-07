from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_value_title_field_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = PostModelTest.group
        expected_value = task.title
        self.assertEqual(expected_value, str(task))

    def test_value_text_field_post(self):
        """Проверяем, что у моделей корректно работает __str__."""
        task = PostModelTest.post
        expected_value = task.text
        self.assertEqual(expected_value, str(task))
