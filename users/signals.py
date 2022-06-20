from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Instance will be gonna sender from post_save create_profile (User)
        user = instance
        profile = Profile.objects.create(
            user=user,
            nickname=user.username,
            email=user.email,
            name=user.first_name,
        )
        print(f'create_profile {profile.nickname} successfully created')


@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.name
        user.last_name = profile.surname
        user.username = profile.nickname
        user.email = profile.email
        user.save()


@receiver(post_delete, sender=Profile)
def delete_profile(sender, instance, **kwargs):
    user = instance.user
    user.delete()
    print(f'delete_profile: {instance.name} successfully deleted')