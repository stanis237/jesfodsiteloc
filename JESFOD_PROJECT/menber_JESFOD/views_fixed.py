from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from django.utils import timezone
from .forms import MemberForm, CustomLoginForm, CustomRegisterForm
from .models import Member, News, Event, FinanceEntry
from admin_JESFOD.models import Gallery


# ------------------------------------------------------------------ #
#  Internal helper: handle login on POST                             #
# ------------------------------------------------------------------ #
def _handle_login(request):
    if request.method != 'POST':
        return None
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    if not username or not password:
        messages.error(request, "Nom d'utilisateur et mot de passe requis.")
        return None
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        member, _ = Member.objects.get_or_create(user=user)
        if member.is_bureau:
            return redirect('admin_dashboard')
        return redirect('member_dashboard')
    messages.error(request, 'Identifiants invalides.')
    return None


# ------------------------------------------------------------------ #
#  HOME PAGE                                                          #
# ------------------------------------------------------------------ #
def home(request):
    login_result = _handle_login(request)
    if login_result:
        return login_result

    member = None
    if request.user.is_authenticated:
        member, _ = Member.objects.get_or_create(user=request.user)

    # Bureau sorted by position rank
    POSITION_ORDER = {
        'president': 1, 'vice_president': 2, 'secretaire_general': 3,
        'secretaire_adjoint': 4, 'tresorier': 5, 'tresorier_adjoint': 6,
        'charge_com': 7, 'conseiller': 8, 'membre': 9,
    }
    bureau_qs = list(Member.objects.filter(role='bureau'))
    bureau_members = sorted(bureau_qs, key=lambda m: POSITION_ORDER.get(m.position, 99))[:8]

    from .models import Seance
    reunion_members = Member.objects.all().order_by('-user__date_joined')
    seances = Seance.objects.all().order_by('-date')[:5]

    news = News.objects.filter(is_published=True)[:5]
    galleries = Gallery.objects.filter(is_published=True)[:5]
    events = Event.objects.filter(is_published=True, event_date__gte=timezone.now()).order_by('event_date')[:6]
    total_members = Member.objects.count()
    total_news = News.objects.filter(is_published=True).count()

    return render(request, 'home.html', {
        'member': member,
        'bureau_members': bureau_members,
        'reunion_members': reunion_members,
        'seances': seances,
        'news': news,
        'galleries': galleries,
        'events': events,
        'total_members': total_members,
        'total_members_count': total_members,
        'total_news': total_news,
    })


# ------------------------------------------------------------------ #
#  AUTH                                                               #
# ------------------------------------------------------------------ #
def custom_login(request):
    login_result = _handle_login(request)
    if login_result:
        return login_result
    form = CustomLoginForm(request.POST if request.method == 'POST' else None)
    return render(request, 'menber_JESFOD/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            member = Member.objects.get(user=user)
            # Auto-create inscription finance entry (unpaid by default)
            FinanceEntry.objects.get_or_create(
                member=member,
                type='inscription',
                defaults={'amount': 500, 'is_paid': False}
            )
            if member.role == 'bureau':
                return redirect('admin_dashboard')
            return redirect('member_dashboard')
        else:
            messages.error(request, 'Erreur dans le formulaire. Corrigez les erreurs.')
    else:
        form = CustomRegisterForm()
    return render(request, 'menber_JESFOD/register.html', {'form': form})


# ------------------------------------------------------------------ #
#  MEMBER DASHBOARD                                                   #
# ------------------------------------------------------------------ #
@login_required
def member_dashboard(request):
    member, created = Member.objects.get_or_create(user=request.user)
    if member.is_bureau:
        return redirect('admin_dashboard')
    if created:
        messages.info(request, 'Profil membre créé. Complétez vos informations.')
        FinanceEntry.objects.get_or_create(
            member=member,
            type='inscription',
            defaults={'amount': 500, 'is_paid': False}
        )

    # Profile edit
    if request.method == 'POST' and 'edit_profile' in request.POST:
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour !')
        else:
            messages.error(request, 'Erreur lors de la mise à jour.')
    else:
        form = MemberForm(instance=member)

    # Finance data
    finances = member.finances.all()
    inscription_entry = finances.filter(type='inscription').first()
    fdr_entries = finances.filter(type='fdr').order_by('-created_date')
    amande_entries = finances.filter(type='amande', is_paid=False).order_by('-created_date')
    tontine_entries = finances.filter(type='tontine').order_by('-created_date')

    # Stats
    total_members = Member.objects.count()
    total_news = News.objects.filter(is_published=True).count()

    # Upcoming events
    upcoming_events = Event.objects.filter(
        is_published=True, event_date__gte=timezone.now()
    ).order_by('event_date')[:3]

    # Recent news
    news_list = News.objects.filter(is_published=True)[:4]

    context = {
        'member': member,
        'edit_form': form,
        'total_members': total_members,
        'total_news': total_news,
        # Finance
        'inscription_entry': inscription_entry,
        'fdr_entries': fdr_entries,
        'amande_entries': amande_entries,
        'tontine_entries': tontine_entries,
        'total_fdr': member.total_fdr,
        'total_amendes': member.total_amendes,
        'total_tontine': member.total_tontine,
        'situation': member.situation,
        # Content
        'upcoming_events': upcoming_events,
        'news_list': news_list,
        'is_member_page': True,
    }
    return render(request, 'menber_JESFOD/dashboard.html', context)


# ------------------------------------------------------------------ #
#  CERTIFICATION                                                      #
# ------------------------------------------------------------------ #
@login_required
def certification(request):
    member, created = Member.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, 'Profil membre créé.')
    if member.is_certified:
        return render(request, 'menber_JESFOD/certification.html',
                      {'member': member, 'already_certified': True})
    if request.method == 'POST' and 'certify' in request.POST:
        if member.is_bureau:
            member.is_certified = True
            member.certification_date = timezone.now()
            member.save()
            messages.success(request, 'Profil certifié avec succès !')
            return redirect('member_dashboard')
        else:
            messages.error(request, 'Seuls les membres du bureau peuvent être certifiés.')
    return render(request, 'menber_JESFOD/certification.html',
                  {'member': member, 'is_member_page': True})


# ------------------------------------------------------------------ #
#  NEWS                                                               #
# ------------------------------------------------------------------ #
@login_required
def news_list(request):
    news = News.objects.filter(is_published=True).order_by('-created_date')
    return render(request, 'menber_JESFOD/news_list.html', {'news': news, 'is_member_page': True})


class NewsDetailView(DetailView):
    model = News
    template_name = 'menber_JESFOD/news_detail.html'
    context_object_name = 'news'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member_page'] = True
        return context


# ------------------------------------------------------------------ #
#  PROFILE                                                            #
# ------------------------------------------------------------------ #
class MemberDetailView(DetailView):
    model = Member
    template_name = 'menber_JESFOD/profile.html'
    context_object_name = 'member'

    def get_object(self):
        return Member.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member_page'] = True
        return context


# ------------------------------------------------------------------ #
#  ACTIVITIES                                                         #
# ------------------------------------------------------------------ #
@login_required
def member_activities(request):
    member, _ = Member.objects.get_or_create(user=request.user)
    activities = member.activities.split('\n') if member.activities else []
    return render(request, 'menber_JESFOD/activities.html', {
        'member': member,
        'activities': activities,
        'is_member_page': True,
    })
