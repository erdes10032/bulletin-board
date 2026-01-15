from django.test import TestCase
from board.forms import PostForm, ResponseForm
from board.models import Category


class FormValidationTests(TestCase):
    """Тесты валидации форм"""

    def setUp(self):
        self.category = Category.objects.create(name='tank')

    def test_post_form_validation(self):
        """Форма поста правильно валидируется"""
        # Хорошие данные
        good_data = {
            'category': self.category.id,
            'title': 'Valid Title',
            'text': 'This is valid text with more than 15 characters'
        }
        form = PostForm(data=good_data)
        self.assertTrue(form.is_valid())

        # Плохие данные - короткий текст
        bad_data_short = {
            'category': self.category.id,
            'title': 'Short Text',
            'text': 'Short'  # Меньше 15 символов
        }
        form = PostForm(data=bad_data_short)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)

        # Плохие данные - заголовок с маленькой буквы
        bad_data_lowercase = {
            'category': self.category.id,
            'title': 'invalid title',
            'text': 'Valid text with more than 15 characters'
        }
        form = PostForm(data=bad_data_lowercase)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_response_form_validation(self):
        """Форма отклика правильно валидируется"""
        # Хорошие данные
        good_data = {'text': 'Valid response text under 50 chars'}
        form = ResponseForm(data=good_data)
        self.assertTrue(form.is_valid())

        # Слишком длинный текст
        long_text = 'A' * 60  # 60 символов > 50
        bad_data = {'text': long_text}
        form = ResponseForm(data=bad_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)