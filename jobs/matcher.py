import re
import math

# Simple list of English stopwords to filter out from comparison to improve accuracy
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def clean_and_tokenize(text):
    if not text:
        return []
    # Lowercase and split into words/tokens, removing punctuation
    words = re.findall(r'\b[a-z]{2,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def calculate_cosine_similarity(text1, text2):
    tokens1 = clean_and_tokenize(text1)
    tokens2 = clean_and_tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
        
    # Get word counts
    freq1 = {}
    for t in tokens1:
        freq1[t] = freq1.get(t, 0) + 1
        
    freq2 = {}
    for t in tokens2:
        freq2[t] = freq2.get(t, 0) + 1
        
    # Unique tokens in both texts
    vocab = set(freq1.keys()).union(set(freq2.keys()))
    
    dot_product = 0.0
    sum_sq_1 = 0.0
    sum_sq_2 = 0.0
    
    for word in vocab:
        val1 = freq1.get(word, 0)
        val2 = freq2.get(word, 0)
        dot_product += val1 * val2
        sum_sq_1 += val1 ** 2
        sum_sq_2 += val2 ** 2
        
    magnitude = math.sqrt(sum_sq_1) * math.sqrt(sum_sq_2)
    if magnitude == 0:
        return 0.0
        
    return (dot_product / magnitude) * 100

def calculate_match_score(
    candidate_skills,
    required_skills,
    resume_text=None,
    job_description=None
):
    candidate_skills = [
        s.lower().strip()
        for s in candidate_skills
    ]

    required_skills = [
        s.lower().strip()
        for s in required_skills
    ]

    matched = set(
        candidate_skills
    ).intersection(
        set(required_skills)
    )

    if len(required_skills) == 0:
        skill_score = 0.0
    else:
        skill_score = (len(matched) / len(required_skills)) * 100

    # If resume text and description are provided, calculate NLP semantic similarity
    if resume_text and job_description:
        semantic_score = calculate_cosine_similarity(resume_text, job_description)
        # Weighted score: 60% skill matching, 40% semantic description similarity
        total_score = (skill_score * 0.6) + (semantic_score * 0.4)
    else:
        semantic_score = 0.0
        total_score = skill_score

    return round(total_score, 2), list(matched)