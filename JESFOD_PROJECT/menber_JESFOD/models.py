from django.db import models
from django.contrib.auth.models import User
# Create your models here.

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
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    school_level = models.CharField(max_length=20, choices=SCHOOL_LEVEL_CHOICES, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reunion')
    is_certified = models.BooleanField(default=False)
    certification_date = models.DateTimeField(null=True, blank=True)
    activities = models.TextField(blank=True, help_text="Activités et responsabilités du membre")

    def __str__(self):
        return self.name

    @property
    def is_bureau(self):
        return self.role == 'bureau'

    def get_school_level_display(self):
        return dict(self.SCHOOL_LEVEL_CHOICES).get(self.school_level, 'Non renseigné')
