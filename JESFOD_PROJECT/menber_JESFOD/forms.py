from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Member, News

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe',
            'required': True
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
            'placeholder': 'Email'
        })
    )
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom complet'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Téléphone (optionnel)'
        })
    )
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        }),
        label='Photo de profil'
    )

    school_level = forms.ChoiceField(
        choices=Member.SCHOOL_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Niveau scolaire'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'phone', 'school_level', 'role', 'password1', 'password2')

    role = forms.ChoiceField(
        choices=Member.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Votre rôle'
        }),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
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
        self.fields['profile_photo'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['school_level'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe'
        })
        for field in self.fields.values():
            field.label = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            member = Member.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                role=self.cleaned_data['role'],
                school_level=self.cleaned_data.get('school_level', ''),
                profile_photo=self.cleaned_data.get('profile_photo')
            )
        return user

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'profile_photo', 'school_level', 'role', 'is_certified']
        widgets = {
            'role': forms.Select(choices=Member.ROLE_CHOICES),
            'school_level': forms.Select(choices=Member.SCHOOL_LEVEL_CHOICES),
        }
        labels = {
            'profile_photo': 'Photo de profil',
            'school_level': 'Niveau scolaire',
        }

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de l\'actualité'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
