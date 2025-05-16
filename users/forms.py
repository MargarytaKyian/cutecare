from django import forms
from django.contrib.auth.forms import AuthenticationForm, \
    UserCreationForm, UserChangeForm
from .models import User


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Електронна пошта або логін'}
         )
        self.fields['username'].label = "Електронна пошта або логін"


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()


    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )


class ProfileForm(UserChangeForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()


    class Meta:
        model = User
        fields = (
            'image',
            'first_name',
            'last_name',
            'username',
            'email',
        )