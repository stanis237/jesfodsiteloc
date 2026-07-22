from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
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


bureau_required = user_passes_test(is_bureau)


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
class MemberListView(ListView):
    model = Member
    template_name = 'admin_JESFOD/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        return Member.objects.prefetch_related('finances').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context


class MemberCreateView(CreateView):
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


class MemberUpdateView(UpdateView):
    model = Member
    form_class = AdminMemberForm
    template_name = 'admin_JESFOD/member_form.html'
    success_url = reverse_lazy('member_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context


class MemberDeleteView(DeleteView):
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
@bureau_required
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
#  GALLERY CREATE                                                     #
# ------------------------------------------------------------------ #
@login_required
@bureau_required
def gallery_create(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.created_by = request.user
            gallery.save()
            messages.success(request, 'Galerie ajoutée avec succès !')
            return redirect('admin_dashboard')
    else:
        form = GalleryForm()
    return render(request, 'admin_JESFOD/gallery_form.html', {'form': form, 'is_admin_page': True})


# ------------------------------------------------------------------ #
#  EVENT CREATE                                                       #
# ------------------------------------------------------------------ #
@login_required
@bureau_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Événement ajouté avec succès !')
            return redirect('admin_dashboard')
    else:
        form = EventForm()
    return render(request, 'admin_JESFOD/event_form.html', {'form': form, 'is_admin_page': True})


# ------------------------------------------------------------------ #
#  FINANCE MANAGEMENT                                                 #
# ------------------------------------------------------------------ #
@login_required
@bureau_required
def finance_list(request):
    """Overview table: all members with their financial situation."""
    members = Member.objects.prefetch_related('finances').all().order_by('name')

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
        'total_inscriptions': total_inscriptions,
        'total_fdr': total_fdr,
        'total_amendes_collected': total_amendes_collected,
        'total_tontine': total_tontine,
        'is_admin_page': True,
    }
    return render(request, 'admin_JESFOD/finance_list.html', context)


@login_required
@bureau_required
def finance_create(request):
    """Create a finance entry for any member."""
    if request.method == 'POST':
        form = FinanceEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.recorded_by = request.user
            entry.save()
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
@bureau_required
def finance_update(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if request.method == 'POST':
        form = FinanceEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrée financière mise à jour.')
            return redirect('finance_list')
    else:
        form = FinanceEntryForm(instance=entry)
    return render(request, 'admin_JESFOD/finance_form.html', {
        'form': form, 'entry': entry, 'is_admin_page': True, 'title': 'Modifier Entrée'
    })


@login_required
@bureau_required
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
@bureau_required
def finance_mark_paid(request, pk):
    """Quick-mark an entry as paid via POST."""
    entry = get_object_or_404(FinanceEntry, pk=pk)
    if request.method == 'POST':
        entry.is_paid = True
        entry.date_paid = timezone.now()
        entry.save()
        messages.success(request, f'✓ {entry.member.name} — {entry.get_type_display()} marqué payé.')
    return redirect('finance_list')

# ------------------------------------------------------------------ #
#  ABSENCES & SEANCES                                                 #
# ------------------------------------------------------------------ #
from menber_JESFOD.models import Seance, Absence
from .forms import SeanceForm, AbsenceForm

@login_required
@bureau_required
def seance_list(request):
    seances = Seance.objects.all().order_by('-date')
    return render(request, 'admin_JESFOD/seance_list.html', {
        'seances': seances,
        'is_admin_page': True,
    })

@login_required
@bureau_required
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
    })

@login_required
@bureau_required
def absence_list(request):
    absences = Absence.objects.select_related('member', 'seance').all().order_by('-seance__date')
    return render(request, 'admin_JESFOD/absence_list.html', {
        'absences': absences,
        'is_admin_page': True,
    })

@login_required
@bureau_required
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
@bureau_required
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
@bureau_required
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
@bureau_required
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
