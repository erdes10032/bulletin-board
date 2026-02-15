import pytest
from board.forms import PostForm, ResponseForm, ProfileForm


@pytest.mark.form
class TestFormValidation:
    """Тесты валидации форм"""

    def test_post_form_valid_data(self, test_category):
        """Форма поста с валидными данными"""
        form_data = {
            'category': test_category.id,
            'title': 'Valid Title',
            'text': 'This is valid text with more than 15 characters'
        }
        form = PostForm(data=form_data)
        assert form.is_valid() is True

    def test_post_form_invalid_short_text(self, test_category):
        """Форма поста с коротким текстом"""
        form_data = {
            'category': test_category.id,
            'title': 'Short Text',
            'text': 'Short'  # Меньше 15 символов
        }
        form = PostForm(data=form_data)
        assert form.is_valid() is False
        assert 'text' in form.errors

    def test_post_form_title_lowercase(self, test_category):
        """Заголовок с маленькой буквы"""
        form_data = {
            'category': test_category.id,
            'title': 'invalid title',
            'text': 'Valid text with more than 15 characters'
        }
        form = PostForm(data=form_data)
        assert form.is_valid() is False
        assert 'title' in form.errors

    @pytest.mark.parametrize('title,text,should_be_valid', [
        ('Valid Title', 'This is a valid text with enough length', True),
        ('invalid', 'This is a valid text with enough length', False),
        ('Valid', 'short', False),
        ('', 'This is a valid text with enough length', False),
    ])
    def test_post_form_parametrized(self, test_category, title, text, should_be_valid):
        """Параметризованный тест формы поста"""
        form_data = {
            'category': test_category.id,
            'title': title,
            'text': text
        }
        form = PostForm(data=form_data)
        assert form.is_valid() == should_be_valid

    def test_response_form_valid_data(self):
        """Форма отклика с валидными данными"""
        form_data = {'text': 'Valid response text'}
        form = ResponseForm(data=form_data)
        assert form.is_valid() is True

    def test_response_form_long_text(self):
        """Слишком длинный текст отклика"""
        long_text = 'A' * 51  # 51 символ > 50
        form_data = {'text': long_text}
        form = ResponseForm(data=form_data)
        assert form.is_valid() is False
        assert 'text' in form.errors

    def test_profile_form_with_user(self, regular_user, image_file):
        """Форма профиля с пользователем"""
        # Получаем профиль пользователя
        profile = regular_user.profile
        # Создаем временный файл для avatar
        from django.core.files.uploadedfile import SimpleUploadedFile
        # avatar обязателен в форме
        form_data = {
            'first_name': 'New First',
            'last_name': 'New Last',
            'gender': 'female',
        }

        file_data = {
            'avatar': SimpleUploadedFile(
                'test_avatar.png',
                image_file.getvalue(),
                content_type='image/png'
            )
        }

        # Передаем instance профиля и user, а также файлы
        form = ProfileForm(data=form_data, files=file_data, user=regular_user, instance=profile)

        # Проверяем ошибки, если форма невалидна
        if not form.is_valid():
            print(f"Form errors: {form.errors}")

        assert form.is_valid() is True