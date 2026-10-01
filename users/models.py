from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='candidate'
    )

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15, blank=True)
    education = models.TextField(blank=True)
    skills = models.TextField(blank=True)

class RecruiterProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(max_length=200, blank=True)

# Signals to auto-create profiles on registration
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'candidate':
            CandidateProfile.objects.get_or_create(user=instance)
        elif instance.role == 'recruiter':
            RecruiterProfile.objects.get_or_create(user=instance)