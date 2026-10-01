def get_missing_skills(
    candidate_skills,
    required_skills
):

    candidate = set(
        s.lower().strip()
        for s in candidate_skills
    )

    required = set(
        s.lower().strip()
        for s in required_skills
    )

    missing = required - candidate

    return list(missing)

def recommend_jobs_for_candidate(candidate_skills, all_jobs):
    recommended = []
    candidate = set(s.lower().strip() for s in candidate_skills)
    
    for job in all_jobs:
        if not job.required_skills:
            continue
        req_skills = [s.strip().lower() for s in job.required_skills.split(',') if s.strip()]
        if not req_skills:
            continue
            
        matched = candidate.intersection(set(req_skills))
        score = (len(matched) / len(req_skills)) * 100
        
        # Suggest if there is at least 15% overlap
        if score >= 15:
            recommended.append({
                'job': job,
                'match_score': round(score, 2),
                'matched_count': len(matched)
            })
            
    return sorted(recommended, key=lambda x: x['match_score'], reverse=True)