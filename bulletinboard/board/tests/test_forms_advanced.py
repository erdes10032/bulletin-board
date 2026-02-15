import pytest
from board.forms import CustomSignupForm, ProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.form
class TestAdvancedForms:
    """Продвинутые тесты форм"""

    def test_signup_form_with_avatar(self, image_file):
        """Тест формы регистрации с аватаром"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User',
            'gender': 'male',
        }

        file_data = {
            'avatar': SimpleUploadedFile(
                'test.png',
                image_file.getvalue(),
                content_type='image/png'
            )
        }

        form = CustomSignupForm(data=form_data, files=file_data)
        assert form.is_valid() is True

    def test_profile_form_update_avatar(self, regular_user, image_file):
        """Тест обновления аватара в профиле"""
        profile = regular_user.profile

        file_data = {
            'avatar': SimpleUploadedFile(
                'new_avatar.png',
                image_file.getvalue(),
                content_type='image/png'
            )
        }

        form = ProfileForm(
            data={'first_name': 'Updated', 'last_name': 'Name', 'gender': 'female'},
            files=file_data,
            user=regular_user,
            instance=profile
        )

        assert form.is_valid() is True
        updated_profile = form.save()
        assert updated_profile.avatar.name is not None