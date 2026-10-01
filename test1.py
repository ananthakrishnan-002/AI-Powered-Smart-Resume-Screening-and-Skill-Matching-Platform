from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_valid():
    driver = webdriver.Chrome()
    try:
        driver.get("http://127.0.0.1:8000/users/login/")
        wait = WebDriverWait(driver, 10)
        
        # Login with test_candidate account
        username = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        username.send_keys("test_candidate") 
        
        # Enter valid password
        password = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        password.send_keys("password123") 
        
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        
        # Check if redirected to dashboard
        wait.until(EC.url_contains("dashboard"))
        print("Opened Login Page")
        print("Entered username and password")
        print("TC01 PASSED - Valid Login Successful")
        print("Current URL:", driver.current_url)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_valid()
