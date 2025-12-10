from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Profile


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_login_by_code_required(self, request, email=None):
        email = self._extract_email(request, email)
        if not email:
            return True
        User = get_user_model()
        user = User.objects.get(email=email)
        email_address, created = EmailAddress.objects.get_or_create(user=user, email=email)
        if not email_address:
            return True
        if email_address.verified:
            return False
        else:
            return True


    def _extract_email(self, request, email=None):
        if email:
            return email
        if hasattr(request, 'POST') and 'email' in request.POST:
            return request.POST.get('email')
        if hasattr(request, 'GET') and 'email' in request.GET:
            return request.GET.get('email')
        if request.user and request.user.is_authenticated:
            return request.user.email
        if hasattr(request, 'session'):
            return request.session.get('account_verified_email')
        if hasattr(request, 'login') and hasattr(request.login, 'email'):
            return request.login.email
        return None

    def send_login_code(self, request, login_code):
        email = login_code.email
        User = get_user_model()
        user = User.objects.get(email=email)
        email_address = EmailAddress.objects.filter(
            user=user,
            mail=email
        ).first()
        if email_address and email_address.verified:
            return False
        return super().send_login_code(request, login_code)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        if signup:
            email = emailconfirmation.email_address.email
            if hasattr(request, 'session'):
                request.session['pending_email'] = email
            return super().send_confirmation_mail(request, emailconfirmation, signup)
        return None

    def clean_email(self, email):
        email = super().clean_email(email)
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("This email is already registered."))
        return email

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        if 'first_name' in form.cleaned_data:
            user.first_name = form.cleaned_data['first_name']
        if 'last_name' in form.cleaned_data:
            user.last_name = form.cleaned_data['last_name']
        if commit:
            user.save()
            self._add_to_authors_group(user)
            Profile.objects.get_or_create(user=user)
            profile = Profile.objects.get(user=user)
            if 'gender' in form.cleaned_data:
                profile.gender = form.cleaned_data['gender']
            if 'avatar' in form.cleaned_data and form.cleaned_data['avatar']:
                profile.avatar = form.cleaned_data['avatar']
            profile.save()
        return user

    def _add_to_authors_group(self, user):
        authors_group, created = Group.objects.get_or_create(name='authors')
        user.groups.add(authors_group)

    def confirm_login(self, request, email_address):
        email_address.verified = True
        email_address.save()
        if hasattr(request, 'session'):
            request.session.pop('pending_email', None)
        return super().confirm_login(request, email_address)

    def login(self, request, user):
        from allauth.account.models import EmailAddress
        email_address = EmailAddress.objects.get(
            user=user,
            email=user.email
        )
        if not email_address.verified:
            email_address.verified = True
            email_address.save()
        return super().login(request, user)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        self._verify_social_email(sociallogin)
        self._add_to_authors_group(user)
        Profile.objects.get_or_create(user=user)
        return user

    def _verify_social_email(self, sociallogin):
        try:
            email_address = EmailAddress.objects.get(
                user=sociallogin.user,
                email=sociallogin.user.email
            )
            email_address.verified = True
            email_address.save()
        except EmailAddress.DoesNotExist:
            EmailAddress.objects.create(
                user=sociallogin.user,
                email=sociallogin.user.email,
                verified=True,
                primary=True
            )

    def _add_to_authors_group(self, user):
        authors_group, created = Group.objects.get_or_create(name='authors')
        user.groups.add(authors_group)

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user and user.pk:
            self._add_to_authors_group(user)
            Profile.objects.get_or_create(user=user)
            self._verify_social_email(sociallogin)