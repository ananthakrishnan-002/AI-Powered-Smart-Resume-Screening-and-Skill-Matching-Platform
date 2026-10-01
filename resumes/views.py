from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Resume
from .forms import ResumeUploadForm
from .ats import calculate_ats_score
from .parser import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
)


from django.db.models import Avg
from jobs.models import Job, Application
from jobs.recommendation import recommend_jobs_for_candidate
from resumes.skills import SKILLS

def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'recruiter':
            return redirect('recruiter_dashboard')
        else:
            return redirect('candidate_dashboard')
    return render(request, "home.html")


@login_required
def candidate_dashboard(request):
    if request.user.role == 'recruiter':
        return redirect('recruiter_dashboard')
        
    resume = Resume.objects.filter(user=request.user).last()

    context = {
        "resume": resume
    }

    if resume:
        text = resume.parsed_text

        ats_score, ats_breakdown, suggestions = calculate_ats_score(text)
        candidate_skills = extract_skills(text)

        # Get job recommendations
        all_jobs = Job.objects.all()
        recommended_jobs = recommend_jobs_for_candidate(candidate_skills, all_jobs)
        
        # Get applied jobs count
        applied_count = Application.objects.filter(candidate=request.user).count()

        context.update({
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": candidate_skills,
            "ats_score": ats_score,
            "ats_breakdown": ats_breakdown,
            "suggestions": suggestions,
            "recommended_jobs": recommended_jobs[:5],
            "applied_count": applied_count,
        })

    return render(
        request,
        "candidate/dashboard.html",
        context
    )


@login_required
def recruiter_dashboard(request):
    if request.user.role != 'recruiter':
        return redirect('candidate_dashboard')
        
    # Get all jobs posted by this recruiter
    recruiter_jobs = Job.objects.filter(recruiter=request.user)
    job_count = recruiter_jobs.count()
    
    # Get all applications for jobs posted by this recruiter
    applications = Application.objects.filter(job__recruiter=request.user)
    candidate_count = applications.values('candidate').distinct().count()
    shortlisted_count = applications.filter(status='shortlisted').count()
    
    # Average ATS score (or Match Score)
    avg_match_score = applications.aggregate(Avg('match_score'))['match_score__avg'] or 0.0
    avg_match_score = round(avg_match_score, 1)

    # Latest Jobs and Recent Applicants
    latest_jobs = recruiter_jobs.order_by('-created_at')[:5]
    recent_applicants = applications.order_by('-applied_at')[:5]

    # Analytics: Skill distribution & ATS distribution of ALL resumes
    all_resumes = Resume.objects.all()
    
    # Skill distribution
    skill_counts = {}
    for r in all_resumes:
        for skill in extract_skills(r.parsed_text):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:7]
    skills_labels = [s[0] for s in sorted_skills]
    skills_data = [s[1] for s in sorted_skills]

    # ATS score distribution of uploaded resumes
    ats_distribution = {'0-40': 0, '41-70': 0, '71-100': 0}
    for r in all_resumes:
        score, _, _ = calculate_ats_score(r.parsed_text)
        if score <= 40:
            ats_distribution['0-40'] += 1
        elif score <= 70:
            ats_distribution['41-70'] += 1
        else:
            ats_distribution['71-100'] += 1

    return render(
        request,
        "recruiter/dashboard.html",
        {
            'job_count': job_count,
            'candidate_count': candidate_count,
            'shortlisted_count': shortlisted_count,
            'avg_match_score': avg_match_score,
            'latest_jobs': latest_jobs,
            'recent_applicants': recent_applicants,
            'skills_labels': skills_labels,
            'skills_data': skills_data,
            'ats_distribution_labels': list(ats_distribution.keys()),
            'ats_distribution_data': list(ats_distribution.values()),
        }
    )


@login_required
def upload_resume(request):
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can upload resumes.")
        return redirect('home')

    if request.method == "POST":
        form = ResumeUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            # Delete old resume if exists (keep only last resume for candidate simplicity)
            Resume.objects.filter(user=request.user).delete()
            
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            messages.success(request, "Resume uploaded and analyzed successfully!")
            return redirect("candidate_dashboard")

    else:
        form = ResumeUploadForm()

    return render(
        request,
        "candidate/upload_resume.html",
        {
            "form": form
        }
    )