from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Member


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
        })
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        })
    )
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom complet',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone (optionnel)',
        })
    )
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Photo de profil'
    )
    school_level = forms.ChoiceField(
        choices=Member.SCHOOL_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Niveau scolaire'})
    )
    role = forms.ChoiceField(
        choices=Member.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Votre rôle'}),
        required=True
    )
    position = forms.ChoiceField(
        choices=Member.POSITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Votre poste (si bureau)'}),
        required=False,
        initial='membre'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom complet'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Téléphone (optionnel)'
        })
        self.fields['profile_photo'].widget.attrs.update({'class': 'form-control'})
        self.fields['school_level'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['position'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'minlength': '8',
            'required': 'true'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe',
            'minlength': '8',
            'required': 'true'
        })
        for field in self.fields.values():
            field.label = ''

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1, self.instance)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password1


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'profile_photo',
                  'school_level', 'role', 'position', 'is_certified']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'school_level': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'profile_photo': 'Photo de profil',
            'school_level': 'Niveau scolaire',
            'position': 'Poste au sein du bureau',
        }
