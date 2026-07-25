from django import forms
from menber_JESFOD.forms import MemberForm
from .models import News, Gallery
from menber_JESFOD.models import Event, FinanceEntry, Member


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Titre de l'actualité"}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenu'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'description', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la galerie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'event_date', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Titre de l'événement"}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': "Description"}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FinanceEntryForm(forms.ModelForm):
    class Meta:
        model = FinanceEntry
        fields = ['member', 'type', 'amount', 'is_paid', 'period', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '500'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07/2026'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observations...'}),
        }
        labels = {
            'member': 'Membre',
            'type': 'Type de paiement',
            'amount': 'Montant (FCFA)',
            'is_paid': 'Payé',
            'period': 'Période',
            'notes': 'Notes / Motif',
        }

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get("member")
        finance_type = cleaned_data.get("type")

        if member and finance_type == 'inscription':
            # Check if this is a new instance or an update
            qs = FinanceEntry.objects.filter(member=member, type='inscription')
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                self.add_error('type', 'Ce membre a déjà payé ou enregistré une inscription. L\'inscription est unique.')
        
        return cleaned_data


class AdminMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone', 'address', 'profile_photo', 'school_level', 'role', 'position', 'activities', 'is_certified']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet du membre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'adresse.email@exemple.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+237 6xx xxx xxx'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse de résidence'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'school_level': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'activities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Activités et responsabilités...'}),
            'is_certified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom complet',
            'email': 'Adresse email',
            'phone': 'Numéro de téléphone',
            'address': 'Adresse / Ville',
            'profile_photo': 'Photo de profil',
            'school_level': 'Niveau d\'études',
            'role': 'Type de membre (Rôle)',
            'position': 'Poste occupé (si membre du Bureau)',
            'activities': 'Activités et responsabilités',
            'is_certified': 'Membre certifié',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Le nom complet est obligatoire.")
        return name


from menber_JESFOD.models import Seance, Absence

class SeanceForm(forms.ModelForm):
    class Meta:
        model = Seance
        fields = ['title', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la séance'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title': 'Titre',
            'date': 'Date de la séance',
        }

class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['member', 'seance', 'motif', 'justifiee']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'seance': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motif de l\'absence'}),
            'justifiee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'member': 'Membre absent',
            'seance': 'Séance concernée',
            'motif': 'Motif',
            'justifiee': 'Absence justifiée ?',
        }
