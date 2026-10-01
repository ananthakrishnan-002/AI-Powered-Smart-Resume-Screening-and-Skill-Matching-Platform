from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def test_upload_resume():
    driver = webdriver.Chrome()
    try:
        driver.get("http://127.0.0.1:8000/users/login/")
        wait = WebDriverWait(driver, 10)
        
        # Log in with the dynamically created Candidate account
        driver.find_element(By.NAME, "username").send_keys("test_candidate")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login to complete
        wait.until(EC.url_contains("dashboard"))
        
        # Open Resume Upload Page
        driver.get("http://127.0.0.1:8000/candidate/upload/")
        print("Opened Upload Page")
        
        # Upload PDF (Matches the Django resume_file input)
        file_input = wait.until(EC.presence_of_element_located((By.NAME, "resume_file")))
        
        # IMPORTANT: Make sure you have a REAL PDF file named 'sample_resume.pdf' in this folder!
        # The AI parser will crash with a 500 error if the PDF is fake/corrupted.
        file_path = os.path.abspath("sample_resume.pdf")
        
        file_input.send_keys(file_path)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect back to dashboard after processing
        wait.until(EC.url_contains("dashboard"))
        print("TC03 PASSED - PDF Uploaded and Python Parsing Initiated")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_upload_resume()
