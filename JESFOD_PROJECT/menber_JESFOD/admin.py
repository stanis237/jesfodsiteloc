from django.contrib import admin
from .models import Member, News, Event, FinanceEntry, Seance, Absence, Presence

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'role', 'email', 'phone', 'is_certified', 'school_level')
    list_filter = ('role', 'position', 'is_certified', 'school_level')
    search_fields = ('name', 'email', 'phone', 'user__username')
    ordering = ('name',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_date', 'is_published')
    list_filter = ('is_published', 'created_date')
    search_fields = ('title', 'content')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'created_by', 'is_published')
    list_filter = ('is_published', 'event_date')
    search_fields = ('title', 'description', 'location')

@admin.register(FinanceEntry)
class FinanceEntryAdmin(admin.ModelAdmin):
    list_display = ('member', 'type', 'amount', 'is_paid', 'date_paid', 'period')
    list_filter = ('type', 'is_paid', 'created_date')
    search_fields = ('member__name', 'notes', 'period')

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_date')
    search_fields = ('title',)

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('member', 'seance', 'justifiee', 'motif')
    list_filter = ('justifiee',)
    search_fields = ('member__name', 'motif')

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('member', 'seance', 'timestamp', 'latitude', 'longitude')
    search_fields = ('member__name',)
