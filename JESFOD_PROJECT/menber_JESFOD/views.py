from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .forms import MemberForm, CustomLoginForm, CustomRegisterForm, NewsForm
from .models import Member, News
from admin_JESFOD.models import Gallery

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
        member, created = Member.objects.get_or_create(user=user)
        if not member.is_certified:
            messages.info(request, 'Veuillez certifier votre profil.')
        if member.is_bureau:
            return redirect('admin_dashboard')
        return redirect('member_dashboard')
    messages.error(request, 'Identifiants invalides.')
    return None

def home(request):
    login_result = _handle_login(request)
    if login_result:
        return login_result
    member = None
    if request.user.is_authenticated:
        member, _ = Member.objects.get_or_create(user=request.user)
    bureau_members = Member.objects.filter(role='bureau')[:6]
    news = News.objects.filter(is_published=True)[:5]
    galleries = Gallery.objects.filter(is_published=True)[:5]
    return render(request, 'home.html', {
        'member': member,
        'bureau_members': bureau_members,
        'news': news,
        'galleries': galleries
    })

def custom_login(request):
    login_result = _handle_login(request)
    if login_result:
        return login_result
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
    else:
        form = CustomLoginForm()
    return render(request, 'menber_JESFOD/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            member = Member.objects.get(user=user)
            if member.role == 'bureau':
                return redirect('/adminjesfod/')
            else:
                return redirect('member_dashboard')
        else:
            messages.error(request, 'Erreur dans le formulaire. Corrigez les erreurs.')
    else:
        form = CustomRegisterForm()
    return render(request, 'menber_JESFOD/register.html', {'form': form})

@login_required
def member_dashboard(request):
    member, created = Member.objects.get_or_create(user=request.user)
    if member.is_bureau:
        return redirect('admin_dashboard')
    if created:
        messages.info(request, 'Profil membre créé. Complétez vos informations.')
    total_members = Member.objects.count()
    total_news = News.objects.count()
    
    if request.method == 'POST' and 'edit_profile' in request.POST:
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour !')
        else:
            messages.error(request, 'Erreur mise à jour.')
    else:
        form = MemberForm(instance=member)
    
    news_list = News.objects.filter(is_published=True)[:5]
    context = {
        'member': member,
        'news_list': news_list,
        'total_members': total_members,
        'total_news': total_news,
        'edit_form': form,
        'is_member_page': True
    }
    return render(request, 'menber_JESFOD/dashboard.html', context)

@login_required
def certification(request):
    member, created = Member.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, 'Profil membre créé. Complétez vos informations.')
    if member.is_certified:
        return render(request, 'menber_JESFOD/certification.html', {'member': member, 'already_certified': True})
    if request.method == 'POST' and 'certify' in request.POST:
        if member.is_bureau:
            member.is_certified = True
            member.certification_date = timezone.now()
            member.save()
            messages.success(request, 'Profil certifié avec succès !')
            return redirect('member_dashboard')
        else:
            messages.error(request, 'Seuls les membres du bureau peuvent être certifiés.')
    return render(request, 'menber_JESFOD/certification.html', {'member': member, 'is_member_page': True})

@login_required
def news_list(request):
    member, _ = Member.objects.get_or_create(user=request.user)
    news = News.objects.filter(is_published=True).order_by('-created_date')
    if not member.is_bureau:
        # For reunion members, show all published news, not just their own
        pass  # Remove the filter that was limiting to their own news
    return render(request, 'menber_JESFOD/news_list.html', {'news': news, 'is_member_page': True})

@login_required
def news_create(request):
    member, _ = Member.objects.get_or_create(user=request.user)
    if not member.is_bureau:
        messages.error(request, 'Accès réservé au bureau.')
        return redirect('news_list')
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.created_by = member.user
            news.save()
            messages.success(request, 'Actualité publiée !')
            
            # Send email notifications to all members
            if news.is_published:
                members = Member.objects.all()
                recipient_emails = [member.email for member in members if member.email]
                
                if recipient_emails:
                    subject = f'Nouvelle actualité JESFOD: {news.title}'
                    message = f"""
Bonjour,

Une nouvelle actualité a été publiée sur JESFOD:

Titre: {news.title}

{news.content[:200]}{'...' if len(news.content) > 200 else ''}

Pour lire l'actualité complète, connectez-vous à votre compte JESFOD.

Cordialement,
L'équipe JESFOD
                    """
                    
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            recipient_emails,
                            fail_silently=True,
                        )
                    except Exception as e:
                        # Log the error but don't fail the news creation
                        print(f"Email sending failed: {e}")
            
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'menber_JESFOD/news_form.html', {'form': form, 'is_member_page': True})

class NewsDetailView(DetailView):
    model = News
    template_name = 'menber_JESFOD/news_detail.html'
    context_object_name = 'news'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member_page'] = True
        return context

class MemberDetailView(DetailView):
    model = Member
    template_name = 'menber_JESFOD/profile.html'
    context_object_name = 'member'

    def get_object(self):
        member = Member.objects.get(user=self.request.user)
        return member

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member_page'] = True
        return context

@login_required
def member_activities(request):
    member, _ = Member.objects.get_or_create(user=request.user)
    # Get activities from the member's activities field
    activities = member.activities.split('\n') if member.activities else []
    return render(request, 'menber_JESFOD/activities.html', {
        'member': member,
        'activities': activities,
        'is_member_page': True
    })

class MemberUpdateView(UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'menber_JESFOD/profile_form.html'
    success_url = '/menber/profile/'

    def get_object(self):
        return Member.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member_page'] = True
        return context
