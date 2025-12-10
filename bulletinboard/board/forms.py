from allauth.account.forms import SignupForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Profile, GENDER_CHOICES, Response
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=CKEditorWidget(config_name='default'),
        min_length=15,
        label=_('Text')
    )

    class Meta:
        model = Post
        fields = [
            'category',
            'title',
            'text',
        ]
        labels = {
            'category': _('Category'),
            'title': _('Title'),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text", "") or ""
        title = cleaned_data.get("title", "") or ""
        if title == text:
            self.add_error('title', _("The title cannot be identical to the text"))

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        if title and title[0].islower():
            raise ValidationError(_("The title must begin with a big letter"))
        return title


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label=_('First Name'),
        widget=forms.TextInput(attrs={'placeholder': _('First Name'), 'required': 'required'})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={'placeholder': _('Last Name'), 'required': 'required'})
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label=_('Gender'),
        widget=forms.Select(attrs={'required': 'required'})
    )
    avatar = forms.ImageField(
        label=_('Avatar'),
        required=True,
        help_text=_('Upload your profile picture')
    )

    def save(self, request):
        user = super().save(request)
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = True


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label=_('First Name'))
    last_name = forms.CharField(max_length=30, required=False, label=_('Last Name'))

    class Meta:
        model = Profile
        fields = ['gender', 'avatar']
        labels = {
            'gender': _('Gender'),
            'avatar': _('Profile Picture'),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            if 'avatar' in self.files:
                profile.avatar = self.files['avatar']
            self.user.save()
        if commit:
            profile.save()
        return profile


class ResponseForm(forms.ModelForm):
    text = forms.CharField(max_length=50, label=_('Text'))
    class Meta:
        model = Response
        fields = [
            'text',
        ]