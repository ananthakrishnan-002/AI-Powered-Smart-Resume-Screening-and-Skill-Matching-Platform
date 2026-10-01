from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'required_skills', 'location', 'salary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed Job Description...'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, JavaScript (comma-separated)'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote, Mumbai'}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6-10 LPA'}),
        }
