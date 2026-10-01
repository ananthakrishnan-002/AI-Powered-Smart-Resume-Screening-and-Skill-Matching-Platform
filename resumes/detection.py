import re
from jobs.matcher import calculate_cosine_similarity

def detect_fake_resume(text):
    """
    Checks if the resume is suspicious (e.g. template placeholders, extremely short content).
    """
    is_fake = False
    reasons = []
    
    if not text or len(text.strip()) == 0:
        return True, ["Resume contains no readable text. It might be scanned or empty."]
        
    words = text.split()
    if len(words) < 30:
        is_fake = True
        reasons.append("Resume content is extremely short (under 30 words).")
        
    # Check for common resume template placeholder patterns
    placeholders = [
        r'\[your name\]', r'insert name', r'lorem ipsum', r'your\.email@address\.com',
        r'\[company name\]', r'insert job title', r'insert company name', r'xyz street'
    ]
    
    for placeholder in placeholders:
        if re.search(placeholder, text, re.IGNORECASE):
            is_fake = True
            reasons.append(f"Found template placeholder text matching '{placeholder.replace('\\', '')}'.")
            
    # Check for missing essential sections
    text_lower = text.lower()
    missing_sections = []
    if "education" not in text_lower and "study" not in text_lower:
        missing_sections.append("Education")
    if "experience" not in text_lower and "work" not in text_lower and "intern" not in text_lower:
        missing_sections.append("Experience/Work history")
    if "skills" not in text_lower:
        missing_sections.append("Skills")
        
    if len(missing_sections) == 3:
        is_fake = True
        reasons.append("Missing all standard resume sections (Education, Experience, Skills).")
        
    return is_fake, reasons

def detect_keyword_stuffing(text, skills_list):
    """
    Checks if skill keywords are unnaturally stuffed in the text (e.g. repeated excessively).
    """
    is_stuffed = False
    reasons = []
    
    text_lower = text.lower()
    words = re.findall(r'\b[a-z]{2,}\b', text_lower)
    total_words = len(words)
    
    if total_words == 0:
        return False, []
        
    for skill in skills_list:
        skill_lower = skill.lower()
        # Find raw count of skill in words list
        count = words.count(skill_lower)
        
        # If a skill is repeated more than 6 times and represents more than 4% of the entire resume text, it is suspicious keyword stuffing.
        density = (count / total_words) * 100
        if count >= 6 and density > 4.0:
            is_stuffed = True
            reasons.append(f"Skill '{skill}' is repeated {count} times (density: {density:.1f}%). Possible keyword stuffing.")
            
    return is_stuffed, reasons

def detect_duplicate_resume(resume_obj, other_resumes):
    """
    Compares current resume with others in the system using Cosine Similarity.
    If similarity is > 85%, it's classified as a potential duplicate.
    """
    for other in other_resumes:
        if other.id == resume_obj.id or other.user == resume_obj.user:
            continue
            
        similarity = calculate_cosine_similarity(resume_obj.parsed_text, other.parsed_text)
        if similarity >= 85.0:
            return True, f"Highly similar to resume of candidate '{other.user.username}' (Similarity: {similarity:.1f}%)"
            
    return False, ""
