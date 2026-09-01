from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils.decorators import method_decorator
from menber_JESFOD.models import Member, News, Event, FinanceEntry
from .models import Gallery
from .forms import NewsForm, GalleryForm, EventForm, FinanceEntryForm, AdminMemberForm


# ------------------------------------------------------------------ #
#  Access guard                                                       #
# ------------------------------------------------------------------ #
def is_bureau(user):
    try:
        return Member.objects.get(user=user).is_bureau
    except Member.DoesNotExist:
        return False

def is_president(user):
    """Président ou Vice-Président : accès total."""
    try:
        return Member.objects.get(user=user).is_president_or_vp
    except Member.DoesNotExist:
        return False

def is_tresorier(user):
    """Trésorier, Trésorier adjoint, ou Président : accès finances."""
    try:
        return Member.objects.get(user=user).is_tresorier_access
    except Member.DoesNotExist:
        return False

def is_secretaire(user):
    """Secrétaire, Secrétaire adjoint, ou Président : accès séances/news/absences."""
    try:
        return Member.objects.get(user=user).is_secretaire_access
    except Member.DoesNotExist:
        return False

def is_censeur(user):
    """Censeurs, Président : accès discipline/absences/amendes."""
    try:
        return Member.objects.get(user=user).is_censeur_access
    except Member.DoesNotExist:
        return False

def is_com_culture(user):
    """Chargés Com/Culture/Animation/Sport/Santé, Président : accès évènements/médias."""
    try:
        return Member.objects.get(user=user).is_com_culture_access
    except Member.DoesNotExist:
        return False

def is_conseiller(user):
    """Conseiller, Président : accès aux rapports et conseils."""
    try:
        return Member.objects.get(user=user).is_conseiller_access
    except Member.DoesNotExist:
        return False


bureau_required = user_passes_test(is_bureau)
tresorier_required = user_passes_test(is_tresorier)
secretaire_required = user_passes_test(is_secretaire)
president_required = user_passes_test(is_president)
censeur_required = user_passes_test(is_censeur)
com_culture_required = user_passes_test(is_com_culture)
conseiller_required = user_passes_test(is_conseiller)


BUREAU_NOMINATIONS = [
    {"name": "MALIMETA PRINCESSE", "position": "president", "label": "Présidence"},
    {"name": "ANAFACK ANYL", "position": "vice_president", "label": "Vice-Présidence"},
    {"name": "DONFACK LEONEL", "position": "secretaire_general", "label": "Secrétaire Général(e)"},
    {"name": "KEMGMO ANGE", "position": "secretaire_adjoint", "label": "Vice-Secrétaire"},
    {"name": "DJOUFACK ARMEL", "position": "censeur", "label": "Censeur"},
    {"name": "MOMO RICH", "position": "censeur", "label": "Censeur"},
    {"name": "TADONKENG MARLENE", "position": "charge_culturel", "label": "Chargée des Affaires Culturelles"},
    {"name": "MIAFO STANIS", "position": "charge_culturel", "label": "Chargé des Affaires Culturelles"},
    {"name": "SONGMO DILANE", "position": "charge_com", "label": "Chargé(e) de Communication"},
    {"name": "NGAMENI RAISSA", "position": "charge_animation", "label": "Chargée Animation"},
    {"name": "DONFACK MYLENE", "position": "charge_animation", "label": "Chargée Animation"},
    {"name": "GUEMENA VANEL", "position": "tresorier", "label": "Trésorier(e)"},
    {"name": "DONFACK BELVIANE", "position": "commissaire_comptes", "label": "Commissaire aux Comptes"},
    {"name": "TSAFACK LAMINE", "position": "charge_sport", "label": "Chargé(e) des Sports"},
    {"name": "TSAFACK EVRAD", "position": "charge_sport", "label": "Chargé(e) des Sports"},
    {"name": "KEMGMO LOGANE", "position": "sante", "label": "Chargée de la Santé"},
    {"name": "TAGEUFOUET STEPHANE", "position": "conseiller", "label": "Conseiller(e)"},
]


@login_required
@bureau_required
def bureau_setup(request):
    """Vue d'administration pour créer et initialiser les comptes d'accès du bureau."""
    import re
    from django.contrib.auth.models import User

    generated_credentials = []

    if request.method == 'POST' and 'generate_all' in request.POST:
        default_password = request.POST.get('default_password', 'Jesfod2026!').strip() or 'Jesfod2026!'
        
        for nomino in BUREAU_NOMINATIONS:
            name = nomino['name']
            position = nomino['position']
            label = nomino['label']

            parts = name.lower().split()
            username = ".".join(parts)
            username = re.sub(r'[^\w.@+-]', '', username)[:140]

            user, u_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{username}@jesfod.org",
                    'first_name': parts[1].capitalize() if len(parts) > 1 else parts[0].capitalize(),
                    'last_name': parts[0].upper()
                }
            )
            
            user.set_password(default_password)
            user.save()

            member, m_created = Member.objects.get_or_create(
                user=user,
                defaults={
                    'name': name,
                    'email': user.email,
                    'role': 'bureau',
                    'position': position,
                    'is_certified': True,
                    'certification_date': timezone.now()
                }
            )

            member.name = name
            member.role = 'bureau'
            member.position = position
            member.is_certified = True
            if not member.certification_date:
                member.certification_date = timezone.now()
            member.save()

            FinanceEntry.objects.get_or_create(
                member=member,
                type='inscription',
                defaults={'amount': 500, 'is_paid': False}
            )

            generated_credentials.append({
                'name': name,
                'position_display': label,
                'username': username,
                'password': default_password,
                'status': 'Créé' if u_created else 'Mis à jour'
            })

        messages.success(request, f"✓ Accès configurés et générés avec succès pour les {len(generated_credentials)} membres du bureau !")

    nomination_status = []
    from django.contrib.auth.models import User
    for nomino in BUREAU_NOMINATIONS:
        name = nomino['name']
        position = nomino['position']
        label = nomino['label']
        parts = name.lower().split()
        username = ".".join(parts)
        username = re.sub(r'[^\w.@+-]', '', username)[:140]

        existing_user = User.objects.filter(username=username).first()
        existing_member = Member.objects.filter(name__iexact=name).first() or (Member.objects.filter(user=existing_user).first() if existing_user else None)

        nomination_status.append({
            'name': name,
            'position': position,
            'label': label,
            'username': username,
            'exists': bool(existing_user or existing_member),
            'member': existing_member
        })

    return render(request, 'admin_JESFOD/bureau_setup.html', {
        'nomination_status': nomination_status,
        'generated_credentials': generated_credentials,
        'is_admin_page': True,
    })


# ------------------------------------------------------------------ #
#  ADMIN DASHBOARD                                                    #
# ------------------------------------------------------------------ #
@login_required
@bureau_required
def admin_dashboard(request):
    total_members = Member.objects.count()
    certified_members = Member.objects.filter(is_certified=True).count()
    bureau_members = Member.objects.filter(role='bureau').count()
    total_news = News.objects.count()
    total_events = Event.objects.count()
    recent_members = Member.objects.order_by('-user__date_joined')[:5]

    # Finance stats
    total_inscriptions = FinanceEntry.objects.filter(type='inscription', is_paid=True).aggregate(
        total=Sum('amount'))['total'] or 0
    total_fdr = FinanceEntry.objects.filter(type='fdr', is_paid=True).aggregate(
        total=Sum('amount'))['total'] or 0
    total_amendes = FinanceEntry.objects.filter(type='amande', is_paid=True).aggregate(
        total=Sum('amount'))['total'] or 0
    total_tontine = FinanceEntry.objects.filter(type='tontine', is_paid=True).aggregate(
        total=Sum('amount'))['total'] or 0

    # Members not up to date
    all_members = Member.objects.prefetch_related('finances').all()
    members_pas_a_jour = [m for m in all_members if m.situation == 'pas_a_jour']

    context = {
        'total_members': total_members,
        'certified_members': certified_members,
        'bureau_members': bureau_members,
        'total_news': total_news,
        'total_events': total_events,
        'recent_members': recent_members,
        'total_inscriptions': total_inscriptions,
        'total_fdr': total_fdr,
        'total_amendes': total_amendes,
        'total_tontine': total_tontine,
        'members_pas_a_jour': members_pas_a_jour,
        'is_admin_page': True,
        'is_president_role': is_president(request.user),
        'is_tresorier_role': is_tresorier(request.user),
        'is_secretaire_role': is_secretaire(request.user),
        'is_censeur_role': is_censeur(request.user),
        'is_com_culture_role': is_com_culture(request.user),
        'is_conseiller_role': is_conseiller(request.user),
    }
    return render(request, 'admin_JESFOD/dashboard.html', context)



# ------------------------------------------------------------------ #
#  CERTIFICATIONS                                                     #
# ------------------------------------------------------------------ #
@login_required
@bureau_required
def pending_certifications(request):
    pending_members = Member.objects.filter(role='bureau', is_certified=False).order_by('name')
    return render(request, 'admin_JESFOD/pending_certifications.html', {
        'pending_members': pending_members,
        'is_admin_page': True,
    })


@login_required
@bureau_required
def certify_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.is_certified = True
        member.certification_date = timezone.now()
        member.save()
        messages.success(request, f"{member.name} a été certifié avec succès.")
    return redirect('pending_certifications')


# ------------------------------------------------------------------ #
#  MEMBERS CRUD                                                       #
# ------------------------------------------------------------------ #
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class BureauRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_bureau(self.request.user)

class MemberListView(BureauRequiredMixin, ListView):
    model = Member
    template_name = 'admin_JESFOD/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        return Member.objects.prefetch_related('finances').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context


class MemberCreateView(BureauRequiredMixin, CreateView):
    model = Member
    form_class = AdminMemberForm
    template_name = 'admin_JESFOD/member_form.html'
    success_url = reverse_lazy('member_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context

    def form_valid(self, form):
        import re
        from django.contrib.auth.models import User
        
        email = form.cleaned_data.get('email', '').strip()
        name = form.cleaned_data.get('name', '').strip()
        
        # Build username from email prefix or name
        if email:
            username = email.split('@')[0]
        else:
            username = name.replace(' ', '').lower()
            
        username = re.sub(r'[^\w.@+-]', '', username)
        username = username[:140]
        if not username:
            username = "user"
            
        # Ensure uniqueness of username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username[:135]}{counter}"
            counter += 1
            
        # Generate random password
        from django.utils.crypto import get_random_string
        password = get_random_string(length=12)
        
        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Associate and save Member
        member = form.save(commit=False)
        member.user = user
        member.save()
        
        # Auto-create inscription finance entry
        FinanceEntry.objects.get_or_create(
            member=member,
            type='inscription',
            defaults={'amount': 500, 'is_paid': False}
        )
        
        messages.success(
            self.request,
            f"Membre '{member.name}' créé avec succès. Compte associé - Utilisateur : {username} | Mot de passe temporaire : {password} (veuillez le copier)."
        )
        return redirect(self.success_url)


class MemberUpdateView(BureauRequiredMixin, UpdateView):
    model = Member
    form_class = AdminMemberForm
    template_name = 'admin_JESFOD/member_form.html'
    success_url = reverse_lazy('member_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context


class MemberDeleteView(BureauRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy('member_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context


# ------------------------------------------------------------------ #
#  NEWS CREATE                                                        #
# ------------------------------------------------------------------ #
@login_required
@secretaire_required
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_by = request.user
            news.save()
            messages.success(request, 'Actualité ajoutée avec succès !')
            if news.is_published:
                _send_news_notification(news)
            return redirect('admin_dashboard')
    else:
        form = NewsForm()
    return render(request, 'admin_JESFOD/news_form.html', {'form': form, 'is_admin_page': True})


def _send_news_notification(news):
    members = Member.objects.all()
    recipient_emails = [m.email for m in members if m.email]
    if not recipient_emails:
        return
    subject = f'Nouvelle actualité JESFOD : {news.title}'
    message = (
        f"Bonjour,\n\nUne nouvelle actualité a été publiée :\n\n"
        f"Titre : {news.title}\n\n"
        f"{news.content[:200]}{'...' if len(news.content) > 200 else ''}\n\n"
        "Connectez-vous à votre compte JESFOD pour lire la suite.\n\nCordialement,\nL'équipe JESFOD"
    )
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_emails, fail_silently=True)
    except Exception as e:
        print(f"Email sending failed: {e}")


# ------------------------------------------------------------------ #
#  GALLERY CRUD                                                       #
# ------------------------------------------------------------------ #
@login_required
@president_required
def gallery_list(request):
    galleries = Gallery.objects.all().order_by('-created_date')
    return render(request, 'admin_JESFOD/gallery_list.html', {
        'galleries': galleries,
        'is_admin_page': True,
    })


@login_required
@president_required
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.created_by = request.user
            gallery.save()
            messages.success(request, 'Galerie ajoutée avec succès !')
            return redirect('gallery_list')
    else:
        form = GalleryForm()
    return render(request, 'admin_JESFOD/gallery_form.html', {
        'form': form, 'is_admin_page': True, 'title': 'Ajouter une Photo à la Galerie'
    })


@login_required
@president_required
def gallery_update(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=gallery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Galerie mise à jour avec succès !')
            return redirect('gallery_list')
    else:
        form = GalleryForm(instance=gallery)
    return render(request, 'admin_JESFOD/gallery_form.html', {
        'form': form, 'gallery': gallery, 'is_admin_page': True,
        'title': 'Modifier la Galerie'
    })


@login_required
@president_required
def gallery_delete(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        gallery.delete()
        messages.success(request, 'Galerie supprimée avec succès !')
        return redirect('gallery_list')
    return render(request, 'admin_JESFOD/gallery_confirm_delete.html', {
        'gallery': gallery, 'is_admin_page': True
    })


# ------------------------------------------------------------------ #
#  EVENT CRUD                                                         #
# ------------------------------------------------------------------ #
@login_required
@president_required
def event_list(request):
    events = Event.objects.all().order_by('-event_date')
    return render(request, 'admin_JESFOD/event_list.html', {
        'events': events,
        'is_admin_page': True,
    })


@login_required
@president_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Événement ajouté avec succès !')
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'admin_JESFOD/event_form.html', {
        'form': form, 'is_admin_page': True, 'title': 'Créer un Nouvel Événement'
    })


@login_required
@president_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Événement mis à jour avec succès !')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'admin_JESFOD/event_form.html', {
        'form': form, 'event': event, 'is_admin_page': True,
        'title': 'Modifier l\'Événement'
    })


@login_required
@president_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Événement supprimé avec succès !')
        return redirect('event_list')
    return render(request, 'admin_JESFOD/event_confirm_delete.html', {
        'event': event, 'is_admin_page': True
    })


# ------------------------------------------------------------------ #
#  FINANCE MANAGEMENT                                                 #
# ------------------------------------------------------------------ #
@login_required
@tresorier_required
def finance_list(request):
    """Overview table: all members with their financial situation."""
    members = Member.objects.prefetch_related('finances').all().order_by('name')
    recent_entries = FinanceEntry.objects.all()[:50]

    total_inscriptions = FinanceEntry.objects.filter(type='inscription', is_paid=True).aggregate(
        s=Sum('amount'))['s'] or 0
    total_fdr = FinanceEntry.objects.filter(type='fdr', is_paid=True).aggregate(
        s=Sum('amount'))['s'] or 0
    total_amendes_collected = FinanceEntry.objects.filter(type='amande', is_paid=True).aggregate(
        s=Sum('amount'))['s'] or 0
    total_tontine = FinanceEntry.objects.filter(type='tontine', is_paid=True).aggregate(
        s=Sum('amount'))['s'] or 0

    context = {
        'members': members,
        'recent_entries': recent_entries,
        'total_inscriptions': total_inscriptions,
        'total_fdr': total_fdr,
        'total_amendes_collected': total_amendes_collected,
        'total_tontine': total_tontine,
        'is_admin_page': True,
    }
    return render(request, 'admin_JESFOD/finance_list.html', context)



@login_required
@tresorier_required
def finance_create(request):
    """Create a finance entry for any member."""
    if request.method == 'POST':
        form = FinanceEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.recorded_by = request.user
            if entry.is_paid and not entry.date_paid:
                entry.date_paid = timezone.now()
            entry.save()
            if entry.is_paid:
                if _send_receipt_email(entry, request):
                    messages.success(request, f'Entrée financière ajoutée pour {entry.member.name} et reçu envoyé par e-mail.')
                else:
                    messages.success(request, f'Entrée financière ajoutée pour {entry.member.name}.')
            else:
                messages.success(request, f'Entrée financière ajoutée pour {entry.member.name}.')
            return redirect('finance_list')
    else:
        # Pre-fill member if provided in GET param
        initial = {}
        member_id = request.GET.get('member')
        entry_type = request.GET.get('type')
        if member_id:
            initial['member'] = member_id
        if entry_type:
            initial['type'] = entry_type
            if entry_type == 'inscription':
                initial['amount'] = 500
        form = FinanceEntryForm(initial=initial)
    return render(request, 'admin_JESFOD/finance_form.html', {
        'form': form, 'is_admin_page': True, 'title': 'Nouvelle Entrée Financière'
    })


@login_required
@tresorier_required
def finance_update(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if request.method == 'POST':
        form = FinanceEntryForm(request.POST, instance=entry)
        if form.is_valid():
            was_paid = entry.is_paid
            entry = form.save(commit=False)
            if entry.is_paid and not entry.date_paid:
                entry.date_paid = timezone.now()
            entry.save()
            if entry.is_paid and not was_paid:
                if _send_receipt_email(entry, request):
                    messages.success(request, 'Entrée financière mise à jour et reçu envoyé par e-mail.')
                else:
                    messages.success(request, 'Entrée financière mise à jour.')
            else:
                messages.success(request, 'Entrée financière mise à jour.')
            return redirect('finance_list')
    else:
        form = FinanceEntryForm(instance=entry)
    return render(request, 'admin_JESFOD/finance_form.html', {
        'form': form, 'entry': entry, 'is_admin_page': True, 'title': 'Modifier Entrée'
    })


@login_required
@tresorier_required
def finance_delete(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if request.method == 'POST':
        member_name = entry.member.name
        entry.delete()
        messages.success(request, f'Entrée supprimée pour {member_name}.')
        return redirect('finance_list')
    return render(request, 'admin_JESFOD/finance_confirm_delete.html', {
        'entry': entry, 'is_admin_page': True
    })


@login_required
@tresorier_required
def finance_mark_paid(request, pk):
    """Quick-mark an entry as paid via POST."""
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if request.method == 'POST':
        entry.is_paid = True
        entry.date_paid = timezone.now()
        entry.save()
        sent = _send_receipt_email(entry, request)
        if sent:
            messages.success(request, f'✓ {entry.member.name} — {entry.get_type_display()} marqué payé. Reçu envoyé par e-mail.')
        else:
            messages.success(request, f'✓ {entry.member.name} — {entry.get_type_display()} marqué payé.')
    return redirect('finance_list')

# ------------------------------------------------------------------ #
#  ABSENCES & SEANCES                                                 #
# ------------------------------------------------------------------ #
from menber_JESFOD.models import Seance, Absence
from .forms import SeanceForm, AbsenceForm

@login_required
@secretaire_required
def seance_list(request):
    seances = Seance.objects.all().order_by('-date')
    return render(request, 'admin_JESFOD/seance_list.html', {
        'seances': seances,
        'is_admin_page': True,
    })

@login_required
@secretaire_required
def seance_create(request):
    if request.method == 'POST':
        form = SeanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Séance ajoutée avec succès.')
            return redirect('seance_list')
    else:
        form = SeanceForm()
    return render(request, 'admin_JESFOD/seance_form.html', {
        'form': form,
        'is_admin_page': True,
        'title': 'Enregistrer une Séance',
    })


@login_required
@secretaire_required
def seance_update(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if request.method == 'POST':
        form = SeanceForm(request.POST, instance=seance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Séance mise à jour avec succès.')
            return redirect('seance_list')
    else:
        form = SeanceForm(instance=seance)
    return render(request, 'admin_JESFOD/seance_form.html', {
        'form': form, 'seance': seance,
        'is_admin_page': True,
        'title': 'Modifier la Séance',
    })


@login_required
@secretaire_required
def seance_delete(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    if request.method == 'POST':
        seance.delete()
        messages.success(request, 'Séance supprimée avec succès.')
        return redirect('seance_list')
    return render(request, 'admin_JESFOD/seance_confirm_delete.html', {
        'seance': seance, 'is_admin_page': True
    })

@login_required
@secretaire_required
def absence_list(request):
    absences = Absence.objects.select_related('member', 'seance').all().order_by('-seance__date')
    return render(request, 'admin_JESFOD/absence_list.html', {
        'absences': absences,
        'is_admin_page': True,
    })

@login_required
@secretaire_required
def absence_create(request):
    if request.method == 'POST':
        form = AbsenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absence enregistrée avec succès.')
            return redirect('absence_list')
    else:
        form = AbsenceForm()
    return render(request, 'admin_JESFOD/absence_form.html', {
        'form': form,
        'is_admin_page': True,
    })

# ------------------------------------------------------------------ #
#  EXPORTS PDF                                                        #
# ------------------------------------------------------------------ #
from django.template.loader import get_template
from django.http import HttpResponse

def render_to_pdf(template_src, context_dict={}):
    try:
        from xhtml2pdf import pisa
        template = get_template(template_src)
        html = template.render(context_dict)
        response = HttpResponse(content_type='application/pdf')
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Erreur lors de la génération du PDF <pre>' + html + '</pre>')
        return response
    except ImportError:
        return HttpResponse("xhtml2pdf n'est pas installé.")

@login_required
@tresorier_required
def export_finance_pdf(request):
    members = Member.objects.prefetch_related('finances').all().order_by('name')
    total_inscriptions = FinanceEntry.objects.filter(type='inscription', is_paid=True).aggregate(s=Sum('amount'))['s'] or 0
    total_fdr = FinanceEntry.objects.filter(type='fdr', is_paid=True).aggregate(s=Sum('amount'))['s'] or 0
    total_amendes = FinanceEntry.objects.filter(type='amande', is_paid=True).aggregate(s=Sum('amount'))['s'] or 0
    total_tontine = FinanceEntry.objects.filter(type='tontine', is_paid=True).aggregate(s=Sum('amount'))['s'] or 0
    
    context = {
        'members': members,
        'total_inscriptions': total_inscriptions,
        'total_fdr': total_fdr,
        'total_amendes': total_amendes,
        'total_tontine': total_tontine,
        'date': timezone.now(),
        'request': request,
        'logo_url': request.build_absolute_uri('/static/images/logo.jpeg'),
    }
    response = render_to_pdf('admin_JESFOD/pdf_finance.html', context)
    if isinstance(response, HttpResponse) and response.get('Content-Type') == 'application/pdf':
        response['Content-Disposition'] = 'attachment; filename="bilan_financier_jesfod.pdf"'
    return response

@login_required
@president_required
def export_members_pdf(request):
    members = Member.objects.all().order_by('name')
    context = {
        'members': members,
        'date': timezone.now(),
        'request': request,
        'logo_url': request.build_absolute_uri('/static/images/logo.jpeg'),
    }
    response = render_to_pdf('admin_JESFOD/pdf_members.html', context)
    if isinstance(response, HttpResponse) and response.get('Content-Type') == 'application/pdf':
        response['Content-Disposition'] = 'attachment; filename="liste_membres_jesfod.pdf"'
    return response

@login_required
@secretaire_required
def export_absences_pdf(request):
    absences = Absence.objects.select_related('member', 'seance').all().order_by('-seance__date')
    context = {
        'absences': absences,
        'date': timezone.now(),
        'request': request,
        'logo_url': request.build_absolute_uri('/static/images/logo.jpeg'),
    }
    response = render_to_pdf('admin_JESFOD/pdf_absences.html', context)
    if isinstance(response, HttpResponse) and response.get('Content-Type') == 'application/pdf':
        response['Content-Disposition'] = 'attachment; filename="liste_absences_jesfod.pdf"'
    return response

# ------------------------------------------------------------------ #
#  RAPPELS EMAILS & REÇUS                                             #
# ------------------------------------------------------------------ #
@login_required
@secretaire_required
def send_seance_reminder(request, pk):
    seance = get_object_or_404(Seance, pk=pk)
    members = Member.objects.exclude(email='')
    emails = [m.email for m in members]
    if emails:
        subject = f"Rappel de séance: {seance.title}"
        message = f"Bonjour,\n\nN'oubliez pas notre séance '{seance.title}' prévue le {seance.date.strftime('%d/%m/%Y')}.\n\nL'équipe JESFOD"
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, emails, fail_silently=True)
            messages.success(request, f"Rappel envoyé pour la séance {seance.title}.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email: {e}")
    else:
        messages.warning(request, "Aucun membre avec adresse email trouvé.")
    return redirect('seance_list')

@login_required
@tresorier_required
def send_finance_reminder(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if entry.is_paid:
        messages.warning(request, "Cette entrée est déjà payée.")
        return redirect('finance_list')
    if entry.member.email:
        subject = f"Rappel de paiement: {entry.get_type_display()}"
        message = f"Bonjour {entry.member.name},\n\nSauf erreur de notre part, vous n'avez pas encore réglé votre {entry.get_type_display()} d'un montant de {entry.amount} FCFA.\n\nMerci de régulariser votre situation.\n\nL'équipe JESFOD"
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [entry.member.email], fail_silently=True)
            messages.success(request, f"Rappel envoyé à {entry.member.name}.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi: {e}")
    else:
        messages.warning(request, f"Aucune adresse email pour {entry.member.name}.")
    return redirect('finance_list')

@login_required
@tresorier_required
def export_receipt_pdf(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk, is_paid=True)
    context = {
        'entry': entry,
        'date': timezone.now(),
        'request': request,
        'logo_url': request.build_absolute_uri('/static/images/logo.jpeg'),
    }
    response = render_to_pdf('admin_JESFOD/pdf_receipt.html', context)
    if isinstance(response, HttpResponse) and response.get('Content-Type') == 'application/pdf':
        response['Content-Disposition'] = f'attachment; filename="recu_{entry.id}.pdf"'
    return response


def _send_receipt_email(entry, request=None):
    if not entry.is_paid or not entry.member or not entry.member.email:
        return False
    
    try:
        context = {
            'entry': entry,
            'date': timezone.now(),
            'request': request,
            'logo_url': request.build_absolute_uri('/static/images/logo.jpeg') if request else '',
        }
        pdf_file = render_to_pdf('admin_JESFOD/pdf_receipt.html', context)
        
        subject = f"Reçu de paiement JESFOD - {entry.get_type_display()}"
        body = (
            f"Bonjour {entry.member.name},\n\n"
            f"Nous vous confirmons la bonne réception de votre paiement pour '{entry.get_type_display()}' d'un montant de {entry.amount} FCFA.\n"
            f"Vous trouverez ci-joint votre reçu officiel au format PDF.\n\n"
            f"Merci pour votre confiance !\nL'équipe JESFOD"
        )
        
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[entry.member.email],
        )
        if isinstance(pdf_file, HttpResponse) and pdf_file.get('Content-Type') == 'application/pdf':
            email.attach(f"recu_{entry.id}.pdf", pdf_file.content, 'application/pdf')
        
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending receipt email: {e}")
        return False


