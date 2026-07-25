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
        required=True,
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
        required=True,
        initial='reunion'
    )
    position = forms.ChoiceField(
        choices=Member.POSITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Votre poste'}),
        required=False,
        initial='membre_reunion'
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

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé par un autre compte.")
        return username

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Le nom complet est obligatoire.")
        return name


    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà associée à un compte.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password1

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            email = self.cleaned_data.get('email', '').strip()
            if email and user.email != email:
                user.email = email
                user.save()

            name = self.cleaned_data.get('name', '').strip() or user.username
            phone = self.cleaned_data.get('phone', '').strip()
            profile_photo = self.cleaned_data.get('profile_photo')
            school_level = self.cleaned_data.get('school_level', '')
            role = self.cleaned_data.get('role', 'reunion')
            position = self.cleaned_data.get('position')
            if role == 'reunion' or not position:
                position = 'membre_reunion'

            member, _ = Member.objects.get_or_create(user=user)
            member.name = name
            member.email = email or user.email
            member.phone = phone
            if profile_photo:
                member.profile_photo = profile_photo
            member.school_level = school_level
            member.role = role
            member.position = position
            member.save()
        return user


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'profile_photo',
                  'school_level', 'role', 'position']
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
            'name': 'Nom complet',
            'email': 'Email',
            'phone': 'Téléphone',
            'address': 'Adresse',
            'profile_photo': 'Photo de profil',
            'school_level': 'Niveau scolaire',
            'role': 'Type de membre',
            'position': 'Poste au sein du bureau',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Le nom complet est obligatoire.")
        return name

