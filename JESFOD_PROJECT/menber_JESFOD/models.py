from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="news/", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='member_news')
    created_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    event_date = models.DateTimeField()
    image = models.ImageField(upload_to='events/', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title


class Member(models.Model):
    ROLE_CHOICES = [
        ('bureau', 'Bureau Member'),
        ('reunion', 'Reunion Member'),
    ]
    POSITION_CHOICES = [
        ('president', 'Président(e)'),
        ('vice_president', 'Vice-Président(e)'),
        ('secretaire_general', 'Secrétaire Général(e)'),
        ('secretaire_adjoint', 'Secrétaire Adjoint(e)'),
        ('tresorier', 'Trésorier(e)'),
        ('tresorier_adjoint', 'Trésorier(e) Adjoint(e)'),
        ('charge_com', 'Chargé(e) de Communication'),
        ('conseiller', 'Conseiller(e)'),
        ('membre', 'Membre du Bureau'),
        ('membre_reunion', 'Membre de Réunion'),
    ]
    SCHOOL_LEVEL_CHOICES = [
        ('primaire', 'Primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('universite', 'Université'),
        ('master', 'Master'),
        ('doctorat', 'Doctorat'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    school_level = models.CharField(max_length=20, choices=SCHOOL_LEVEL_CHOICES, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reunion')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='membre',
                                help_text="Poste occupé au sein du bureau (si applicable)")
    is_certified = models.BooleanField(default=False)
    certification_date = models.DateTimeField(null=True, blank=True)
    activities = models.TextField(blank=True, help_text="Activités et responsabilités du membre")

    def __str__(self):
        return self.name

    @property
    def is_bureau(self):
        return self.role == 'bureau'

    @property
    def inscription_paid(self):
        return self.finances.filter(type='inscription', is_paid=True).exists()

    @property
    def total_fdr(self):
        from django.db.models import Sum
        total = self.finances.filter(type='fdr', is_paid=True).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @property
    def total_amendes(self):
        from django.db.models import Sum
        total = self.finances.filter(type='amande', is_paid=False).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @property
    def total_tontine(self):
        from django.db.models import Sum
        total = self.finances.filter(type='tontine', is_paid=True).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @property
    def total_dettes(self):
        from django.db.models import Sum
        total = self.finances.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    @property
    def total_seances(self):
        return Seance.objects.count()

    @property
    def seances_present(self):
        return max(0, self.total_seances - self.absences.count())

    @property
    def situation(self):
        """Returns 'a_jour' if inscription is paid and no unpaid amendes, else 'pas_a_jour'."""
        if self.inscription_paid and self.total_amendes == 0:
            return 'a_jour'
        return 'pas_a_jour'

    def get_school_level_display(self):
        return dict(self.SCHOOL_LEVEL_CHOICES).get(self.school_level, 'Non renseigné')


class FinanceEntry(models.Model):
    TYPE_CHOICES = [
        ('inscription', 'Inscription'),
        ('fdr', 'Fonds de Roulement'),
        ('amande', 'Amende'),
        ('tontine', 'Tontine'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='finances')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=0, default=500,
                                 help_text="Montant en FCFA")
    is_paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True, blank=True)
    period = models.CharField(max_length=20, blank=True,
                              help_text="Période ex: 07/2026 (pour FDR/Tontine)")
    notes = models.TextField(blank=True, help_text="Observations / motif amende")
    created_date = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='recorded_finances')

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Entrée Financière'
        verbose_name_plural = 'Entrées Financières'

    def __str__(self):
        return f"{self.member.name} — {self.get_type_display()} — {self.amount} FCFA"

    def save(self, *args, **kwargs):
        if self.is_paid and not self.date_paid:
            self.date_paid = timezone.now()
        super().save(*args, **kwargs)


class Seance(models.Model):
    title = models.CharField(max_length=200, default="Séance ordinaire")
    date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} du {self.date.strftime('%d/%m/%Y')}"

class Absence(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='absences')
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='absences')
    motif = models.CharField(max_length=200, blank=True, null=True, help_text="Motif de l'absence")
    justifiee = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-seance__date']
        unique_together = ('member', 'seance')

    def __str__(self):
        return f"Absence de {self.member.name} - {self.seance}"

