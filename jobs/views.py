import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import Job, Application
from .forms import JobForm
from resumes.models import Resume, CandidateInfo
from .matcher import calculate_match_score
from .recommendation import get_missing_skills
from resumes.skills import SKILLS
from resumes.detection import detect_fake_resume, detect_keyword_stuffing, detect_duplicate_resume

@login_required
def create_job(request):
    if request.user.role != 'recruiter':
        messages.error(request, "Only recruiters can create job postings.")
        return redirect('home')
        
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            # If company name is set in recruiter profile, sync it, else use form field
            profile = getattr(request.user, 'recruiterprofile', None)
            if profile and profile.company_name:
                job.company = profile.company_name
            job.save()
            messages.success(request, "Job posting created successfully!")
            return redirect('recruiter_dashboard')
    else:
        form = JobForm()
        
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Create Job Posting'
    })

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to edit this job.")
        return redirect('recruiter_dashboard')
        
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posting updated successfully!")
            return redirect('recruiter_dashboard')
    else:
        form = JobForm(instance=job)
        
    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Edit Job Posting',
        'job': job
    })

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter != request.user:
        messages.error(request, "You do not have permission to delete this job.")
        return redirect('recruiter_dashboard')
        
    job.delete()
    messages.success(request, "Job posting deleted successfully.")
    return redirect('recruiter_dashboard')

@login_required
def job_list(request):
    """
    Candidate view to browse all jobs, with advanced search and skill filtering.
    """
    jobs = Job.objects.all().order_by('-created_at')
    
    # Search and Filter criteria
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    selected_skill = request.GET.get('skill', '')
    
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if selected_skill:
        jobs = jobs.filter(required_skills__icontains=selected_skill)
        
    # Get all application IDs for this candidate to show "Applied" state in templates
    applied_job_ids = []
    if request.user.role == 'candidate':
        applied_job_ids = Application.objects.filter(candidate=request.user).values_list('job_id', flat=True)
        
    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'selected_skill': selected_skill,
        'all_skills': SKILLS,
        'applied_job_ids': applied_job_ids
    })

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.user.role == 'recruiter':
        # Ensure recruiter owns the job
        if job.recruiter != request.user:
            messages.error(request, "Access denied.")
            return redirect('recruiter_dashboard')
            
        # Get applications and rank them by match_score descending
        applications = Application.objects.filter(job=job).order_by('-match_score')
        
        # Search & Filter within applications
        cand_name = request.GET.get('name', '')
        min_ats = request.GET.get('min_ats', '')
        cand_skill = request.GET.get('skill', '')
        
        filtered_applications = []
        for app in applications:
            resume = app.resume
            # Filter by candidate name
            if cand_name and cand_name.lower() not in app.candidate.username.lower():
                # check parsed candidate name if available
                cand_info = CandidateInfo.objects.filter(resume=resume).first()
                if not cand_info or cand_name.lower() not in cand_info.name.lower():
                    continue
            
            # Filter by Min ATS Score
            if min_ats:
                from resumes.ats import calculate_ats_score
                ats_score, _, _ = calculate_ats_score(resume.parsed_text)
                if ats_score < int(min_ats):
                    continue
                    
            # Filter by Skill keyword
            if cand_skill:
                from resumes.parser import extract_skills
                skills = extract_skills(resume.parsed_text)
                skills_lower = [s.lower() for s in skills]
                if cand_skill.lower() not in skills_lower:
                    continue
                    
            filtered_applications.append(app)
            
        return render(request, 'jobs/job_detail.html', {
            'job': job,
            'applications': filtered_applications,
            'all_skills': SKILLS,
            'cand_name': cand_name,
            'min_ats': min_ats,
            'cand_skill': cand_skill,
        })
        
    else:
        # Candidate view of job details
        already_applied = Application.objects.filter(job=job, candidate=request.user).exists()
        return render(request, 'jobs/job_detail.html', {
            'job': job,
            'already_applied': already_applied
        })

@login_required
def apply_job(request, job_id):
    if request.user.role != 'candidate':
        messages.error(request, "Only candidates can apply for jobs.")
        return redirect('home')
        
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, "You have already applied to this job.")
        return redirect('job_list')
        
    # Get last uploaded resume
    resume = Resume.objects.filter(user=request.user).last()
    if not resume:
        messages.warning(request, "Please upload a resume before applying.")
        return redirect('upload_resume')
        
    # Parse candidate skills
    from resumes.parser import extract_skills
    candidate_skills = extract_skills(resume.parsed_text)
    
    # Parse required job skills
    req_skills = [s.strip() for s in job.required_skills.split(',') if s.strip()]
    
    # Calculate AI Match Score using Enhanced NLP matcher
    match_score, matched_skills_list = calculate_match_score(
        candidate_skills, 
        req_skills, 
        resume_text=resume.parsed_text, 
        job_description=job.description
    )
    
    # Find missing skills
    missing_skills_list = get_missing_skills(candidate_skills, req_skills)
    
    # Create Application
    Application.objects.create(
        job=job,
        candidate=request.user,
        resume=resume,
        match_score=match_score,
        matched_skills=",".join(matched_skills_list),
        missing_skills=",".join(missing_skills_list),
        status='applied'
    )
    
    messages.success(request, f"Applied successfully to {job.title}! Your AI Match score is {match_score}%.")
    return redirect('applied_jobs')

@login_required
def applied_jobs(request):
    if request.user.role != 'candidate':
        return redirect('home')
    apps = Application.objects.filter(candidate=request.user).order_by('-applied_at')
    return render(request, 'candidate/applied_jobs.html', {'applications': apps})

@login_required
def shortlist_candidate(request, app_id):
    app = get_object_or_404(Application, id=app_id)
    if app.job.recruiter != request.user:
        messages.error(request, "Unauthorized action.")
        return redirect('recruiter_dashboard')
        
    app.status = 'shortlisted'
    app.save()
    messages.success(request, f"Candidate {app.candidate.username} shortlisted.")
    return redirect('job_detail', job_id=app.job.id)

@login_required
def reject_candidate(request, app_id):
    app = get_object_or_404(Application, id=app_id)
    if app.job.recruiter != request.user:
        messages.error(request, "Unauthorized action.")
        return redirect('recruiter_dashboard')
        
    app.status = 'rejected'
    app.save()
    messages.success(request, f"Candidate {app.candidate.username} status updated to Rejected.")
    return redirect('job_detail', job_id=app.job.id)

@login_required
def applicant_detail(request, app_id):
    """
    Recruiter view: Detailed analysis of applicant's resume with enhanced ATS breakdown,
    NLP matching scores, and AI fraud checks.
    """
    app = get_object_or_404(Application, id=app_id)
    if app.job.recruiter != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect('recruiter_dashboard')
        
    resume = app.resume
    text = resume.parsed_text
    
    # Calculate detailed ATS metrics
    from resumes.ats import calculate_ats_score
    ats_score, ats_breakdown, suggestions = calculate_ats_score(text)
    
    # Perform Fraud / AI Safety checks
    is_fake, fake_reasons = detect_fake_resume(text)
    is_stuffed, stuffing_reasons = detect_keyword_stuffing(text, SKILLS)
    
    # Check for duplicate resumes in the system
    other_resumes = Resume.objects.exclude(user=app.candidate)
    is_duplicate, duplicate_reason = detect_duplicate_resume(resume, other_resumes)
    
    # Extract structural info for rendering
    from resumes.parser import extract_name, extract_email, extract_phone, extract_skills
    cand_info = CandidateInfo.objects.filter(resume=resume).first()
    
    name = cand_info.name if cand_info else extract_name(text)
    email = cand_info.email if cand_info else extract_email(text)
    phone = cand_info.phone if cand_info else extract_phone(text)
    skills = extract_skills(text)
    
    # Match analysis details
    matched_skills = [s.strip() for s in app.matched_skills.split(',') if s.strip()]
    missing_skills = [s.strip() for s in app.missing_skills.split(',') if s.strip()]
    
    return render(request, 'recruiter/applicant_detail.html', {
        'application': app,
        'resume': resume,
        'ats_score': ats_score,
        'ats_breakdown': ats_breakdown,
        'suggestions': suggestions,
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'is_fake': is_fake,
        'fake_reasons': fake_reasons,
        'is_stuffed': is_stuffed,
        'stuffing_reasons': stuffing_reasons,
        'is_duplicate': is_duplicate,
        'duplicate_reason': duplicate_reason
    })

@login_required
def export_applicants_csv(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter != request.user:
        return HttpResponse("Unauthorized", status=401)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="applicants_{job.title.replace(" ", "_")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Candidate Name', 'Email', 'Phone', 'AI Match Score', 'Status', 'Applied At'])
    
    applications = Application.objects.filter(job=job).order_by('-match_score')
    for app in applications:
        cand_info = CandidateInfo.objects.filter(resume=app.resume).first()
        from resumes.parser import extract_name, extract_email, extract_phone
        name = cand_info.name if cand_info else extract_name(app.resume.parsed_text)
        email = cand_info.email if cand_info else extract_email(app.resume.parsed_text)
        phone = cand_info.phone if cand_info else extract_phone(app.resume.parsed_text)
        
        writer.writerow([
            app.candidate.username,
            name,
            email,
            phone,
            f"{app.match_score}%",
            app.get_status_display(),
            app.applied_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    return response
