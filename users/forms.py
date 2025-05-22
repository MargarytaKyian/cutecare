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
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileForm(UserChangeForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    middle_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    image = forms.ImageField(label='Фото профілю', required=False,
                             widget=forms.FileInput(attrs={'class':'hidden'})
    )
    city = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=250, required=False)
    postal_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = (
            'image', 
            'username', 
            'first_name', 
            'last_name', 
            'middle_name', 
            'email', 
            'phone_number', 
            'city',
            'address',
            'postal_code',
        )