import re

def calculate_ats_score(text):
    if not text or len(text.strip()) == 0:
        return 0, {
            'total_score': 0,
            'formatting_score': 0,
            'education_score': 0,
            'experience_score': 0,
            'projects_score': 0,
            'certification_score': 0
        }, ["Upload a non-empty resume to get an ATS score."]

    text_lower = text.lower()
    word_count = len(text.split())
    
    formatting_score = 0
    education_score = 0
    experience_score = 0
    projects_score = 0
    certification_score = 0
    suggestions = []

    # 1. Formatting Score (Max 20)
    # Give points based on length (150-800 words is optimal for 1-2 pages)
    if 150 <= word_count <= 800:
        formatting_score += 10
    elif word_count > 0:
        formatting_score += 5
        suggestions.append("Optimize resume word count. A standard professional resume should be between 150 and 800 words.")

    # Check for contact details formatting (e.g. presence of email & phone)
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+', text_lower))
    has_phone = bool(re.search(r'(\+91)?[6-9]\d{9}', text_lower) or re.search(r'\b\d{10}\b', text_lower))
    if has_email and has_phone:
        formatting_score += 10
    else:
        if not has_email:
            suggestions.append("Ensure your email address is clearly visible in the contact section.")
        if not has_phone:
            suggestions.append("Add a valid 10-digit mobile number for communication.")

    # 2. Education Score (Max 20)
    # Check for degree keywords
    degrees = [
        r'\bb\.?tech\b', r'\bm\.?tech\b', r'\bb\.?c\.?a\b', r'\bm\.?c\.?a\b',
        r'\bb\.?s\.?c\b', r'\bm\.?s\.?c\b', r'\bb\.?e\b', r'\bm\.?e\b',
        r'\bbba\b', r'\bmba\b', r'\bph\.?d\b', r'\bbachelor\b', r'\bmaster\b',
        r'\bgraduate\b', r'\bdiploma\b', r'\bdegree\b'
    ]
    has_education_section = "education" in text_lower or "study" in text_lower or "academic" in text_lower
    
    degree_matches = [d for d in degrees if re.search(d, text_lower)]
    if degree_matches:
        education_score += 15
    if has_education_section:
        education_score += 5
        
    if education_score < 20:
        if not has_education_section:
            suggestions.append("Add an explicit 'Education' section header to help parsing systems identify your qualifications.")
        if not degree_matches:
            suggestions.append("Specify your degrees (e.g. MCA, B.Tech, B.Sc) clearly rather than just mentioning school/college.")

    # 3. Experience Score (Max 20)
    # Check for experience keywords and internships
    experience_keywords = ["experience", "work", "history", "employment", "intern", "internship", "professional", "freelance"]
    has_exp_section = "experience" in text_lower or "employment" in text_lower or "work history" in text_lower
    
    exp_matches = [kw for kw in experience_keywords if kw in text_lower]
    if exp_matches:
        experience_score += 10
    if len(exp_matches) >= 3:
        experience_score += 5
    if has_exp_section:
        experience_score += 5
        
    if experience_score < 20:
        if not has_exp_section:
            suggestions.append("Structure your work history under an 'Experience' or 'Work History' header.")
        suggestions.append("Describe past projects or responsibilities using action verbs (e.g. Developed, Led, Analyzed).")

    # 4. Projects Score (Max 20)
    # Check for project headers
    has_project = "project" in text_lower or "projects" in text_lower
    has_github = "github" in text_lower or "gitlab" in text_lower or "bitbucket" in text_lower
    
    if has_project:
        projects_score += 15
    if has_github:
        projects_score += 5
        
    if projects_score < 20:
        if not has_project:
            suggestions.append("Add a 'Projects' section detailing personal, open-source, or academic projects.")
        if not has_github:
            suggestions.append("Link your GitHub profile to showcase code repositories for projects.")

    # 5. Certification Score (Max 20)
    # Check for certifications
    cert_keywords = ["certification", "certifications", "certificate", "certificates", "certified", "credential", "course", "training"]
    cert_matches = [c for c in cert_keywords if c in text_lower]
    
    if cert_matches:
        certification_score += 15
    if len(cert_matches) >= 2:
        certification_score += 5
        
    if certification_score < 20:
        suggestions.append("Include relevant certifications, professional courses, or specialized training to stand out.")

    total_score = formatting_score + education_score + experience_score + projects_score + certification_score

    score_breakdown = {
        'total_score': total_score,
        'formatting_score': formatting_score,
        'education_score': education_score,
        'experience_score': experience_score,
        'projects_score': projects_score,
        'certification_score': certification_score
    }

    return total_score, score_breakdown, suggestions