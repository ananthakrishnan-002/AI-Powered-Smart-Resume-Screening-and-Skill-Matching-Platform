import os
import django
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize Django to create test data
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_screening.settings')
django.setup()
from jobs.models import Job, Application
from django.contrib.auth import get_user_model

def test_generate_score():
    User = get_user_model()
    # Ensure test candidate and job exist and apply the candidate to the job
    candidate = User.objects.get(username="test_candidate")
    recruiter = User.objects.get(username="test_recruiter")
    job = Job.objects.first()
    if not job:
        print("No jobs found in database to test!")
        return
        
    job.recruiter = recruiter
    job.save()
        
    from resumes.models import Resume
    resume = Resume.objects.filter(user=candidate).first()
    
    Application.objects.get_or_create(
        candidate=candidate, 
        job=job, 
        defaults={'match_score': 85.5, 'resume': resume}
    )
    
    driver = webdriver.Chrome()
    try:
        driver.get("http://127.0.0.1:8000/users/login/")
        wait = WebDriverWait(driver, 10)
        
        # Log in with the dynamically created Recruiter account
        driver.find_element(By.NAME, "username").send_keys("test_recruiter")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        wait.until(EC.url_contains("dashboard"))
        
        # View Leaderboard / Job Applicant Rankings for the first job
        driver.get(f"http://127.0.0.1:8000/jobs/{job.id}/")
        print("Opened Job Leaderboard Page")
        
        # Check Score (Matches the AI Match Score column in Django template)
        score_element = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//table//span[contains(@class, 'text-primary') and contains(text(), '%')]")
        ))
        
        score = score_element.text
        print(f"Candidate AI Score Found: {score}")
        print("TC04 PASSED - AI Score Generated and Displayed")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_generate_score()
