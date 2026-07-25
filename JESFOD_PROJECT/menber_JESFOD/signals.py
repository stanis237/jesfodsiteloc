from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Member

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        name = instance.get_full_name() or instance.username
        Member.objects.create(
            user=instance,
            name=name,
            email=instance.email,
            role='reunion',
            position='membre_reunion'
        )
    else:
        try:
            member = instance.member
        except Member.DoesNotExist:
            name = instance.get_full_name() or instance.username
            Member.objects.create(
                user=instance,
                name=name,
                email=instance.email,
                role='reunion',
                position='membre_reunion'
            )
