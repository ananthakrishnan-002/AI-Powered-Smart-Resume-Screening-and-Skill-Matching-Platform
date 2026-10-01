from django.db import models
from django.conf import settings
from .utils import extract_text

class Resume(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    resume_file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.resume_file:
            text = extract_text(self.resume_file.path)

            Resume.objects.filter(
                pk=self.pk
            ).update(parsed_text=text)

            from .parser import extract_name, extract_email, extract_phone
            name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)

            CandidateInfo.objects.update_or_create(
                resume=self,
                defaults={
                    'name': name,
                    'email': email,
                    'phone': phone
                }
            )

    def __str__(self):
        return f"{self.user.username} Resume"


class CandidateInfo(models.Model):
    resume = models.OneToOneField(
        Resume,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=200,blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return self.name