from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

def test_upload_resume():
    driver = webdriver.Chrome()
    try:
        driver.get("http://127.0.0.1:8000/users/login/")
        wait = WebDriverWait(driver, 10)
        
        driver.find_element(By.NAME, "username").send_keys("test_candidate")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        wait.until(EC.url_contains("dashboard"))
        
        driver.get("http://127.0.0.1:8000/candidate/upload/")
        print("Opened Upload Page")
        
        file_input = wait.until(EC.presence_of_element_located((By.NAME, "resume_file")))
        file_path = os.path.abspath("sample_resume.pdf")
        
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(b"%PDF-1.4\n%EOF\n")
                
        file_input.send_keys(file_path)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        try:
            wait.until(EC.url_contains("dashboard"))
            print("TC03 PASSED")
        except TimeoutException:
            print("TIMEOUT! Form validation error or something else:")
            print(driver.page_source)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_upload_resume()
