from django.db import models
from django.conf import settings


class Job(models.Model):

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    description = models.TextField()

    required_skills = models.TextField(
        help_text="Separate skills with commas"
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    def get_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='applications')
    match_score = models.FloatField(default=0.0)
    matched_skills = models.TextField(blank=True, help_text="Comma-separated matched skills")
    missing_skills = models.TextField(blank=True, help_text="Comma-separated missing skills")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"