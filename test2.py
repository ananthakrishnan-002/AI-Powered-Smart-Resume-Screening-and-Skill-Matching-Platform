from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_invalid():
    driver = webdriver.Chrome()
    try:
        driver.get("http://127.0.0.1:8000/users/login/")
        wait = WebDriverWait(driver, 10)
        
        username = wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        username.send_keys("wronguser")
        
        password = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        password.send_keys("wrongpass")
        
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()
        
        # Expecting the Django form validation error (alert-danger class)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "alert-danger")))
        
        print("Opened Login Page")
        print("Entered invalid credentials")
        print("TC02 PASSED - Invalid Login Rejected")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_invalid()
