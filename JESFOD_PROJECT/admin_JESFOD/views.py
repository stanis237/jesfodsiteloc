from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from menber_JESFOD.models import Member, News
from .models import Gallery
from .forms import NewsForm, GalleryForm

def is_bureau(user):
    try:
        member = Member.objects.get(user=user)
        return member.is_bureau
    except Member.DoesNotExist:
        return False

bureau_required = user_passes_test(is_bureau)

@login_required
@bureau_required
def admin_dashboard(request):
    total_members = Member.objects.count()
    certified_members = Member.objects.filter(is_certified=True).count()
    bureau_members = Member.objects.filter(role='bureau').count()
    total_news = News.objects.count()
    recent_members = Member.objects.order_by('-user__date_joined')[:5]
    
    context = {
        'total_members': total_members,
        'certified_members': certified_members,
        'bureau_members': bureau_members,
        'total_news': total_news,
        'recent_members': recent_members,
        'is_admin_page': True
    }
    return render(request, 'admin_JESFOD/dashboard.html', context)

@login_required
@bureau_required
def pending_certifications(request):
    pending_members = Member.objects.filter(role='bureau', is_certified=False).order_by('name')
    return render(request, 'admin_JESFOD/pending_certifications.html', {
        'pending_members': pending_members,
        'is_admin_page': True
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

class MemberListView(ListView):
    model = Member
    template_name = 'admin_JESFOD/member_list.html'
    context_object_name = 'members'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        if hasattr(self.request.user, 'member'):
            from django.contrib import messages
            messages.error(self.request, "Ce user a déjà un profil membre.")
            return self.form_invalid(form)
        return super().form_valid(form)

class MemberCreateView(CreateView):
    model = Member
    fields = ['name', 'email', 'phone', 'address', 'profile_photo', 'school_level', 'role', 'activities', 'is_certified']
    template_name = 'admin_JESFOD/member_form.html'
    success_url = reverse_lazy('member_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_page'] = True
        return context

class MemberUpdateView(UpdateView):
    model = Member
    fields = ['name', 'email', 'phone', 'address', 'profile_photo', 'school_level', 'role', 'activities', 'is_certified']
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
            return redirect('admin_dashboard')
    else:
        form = NewsForm()
    return render(request, 'admin_JESFOD/news_form.html', {'form': form, 'is_admin_page': True})

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
