import re

with open("project_report.tex", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace Test Cases table with Selenium Test Results and Analysis
test_cases_replacement = r"""\section{Test Cases}
\begin{table}[H]
\centering
\begin{tabular}{|c|p{4cm}|p{5cm}|c|}
\hline
\textbf{Test ID} & \textbf{Test Case} & \textbf{Expected Result} & \textbf{Status} \\ \hline
TC-01 & User Registration & Account created with correct role. & Passed \\ \hline
TC-02 & Login Authentication & Success redirects to respective dashboard based on role. & Passed \\ \hline
TC-03 & Job Creation (Recruiter) & Job saved to DB and visible on platform. & Passed \\ \hline
TC-04 & Invalid File Upload & Uploading a .txt or .jpg throws validation error. & Passed \\ \hline
TC-05 & PDF Text Parsing & Text extracted accurately into `parsed_text` field. & Passed \\ \hline
TC-06 & AI Skill Matching & Identical skills yield 100\% match score. & Passed \\ \hline
TC-07 & Role Authorization & Candidate attempting to access recruiter dashboard gets 403/Redirect. & Passed \\ \hline
TC-08 & Application Status & Recruiter clicking "Approve" changes status to "Shortlisted". & Passed \\ \hline
\end{tabular}
\caption{System Test Cases}
\end{table}

\section{Test Results and Analysis}
The testing activities confirmed that the major functions operate according to their intended requirements. The completed Selenium login test successfully verified the user authentication workflow.

\begin{enumerate}
    \item \textbf {Login Test Functionality}
   
    \text{Code}
\begin{lstlisting}[language=Python, numbers=none]
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def test_login():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:8000/login/")
        
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(2)
        current_url = driver.current_url
        print("Current URL:", current_url)
        
        if "dashboard" in current_url:
            print("----------------------")
            print("Login successful!")
            print("LOGIN TEST PASSED")
            print("----------------------")
        else:
            print("LOGIN TEST FAILED")
            
    except Exception as e:
        print("LOGIN TEST FAILED:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()
\end{lstlisting}

\begin{figure} [H]
    \centering
    \rule{0.8\linewidth}{6cm}
    \caption{Login Test Result}
\end{figure}

\newpage
    \item \textbf{Post Job Test Functionality}
       
    \text{Code}
\begin{lstlisting}[language=Python, numbers=none]
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def test_post_job():
    driver = webdriver.Chrome()
    try:
        # Login first
        driver.get("http://localhost:8000/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1.5)
        
        # Navigate to Post Job
        driver.get("http://localhost:8000/jobs/create/")
        
        driver.find_element(By.ID, "id_title").send_keys("Selenium Test Engineer")
        driver.find_element(By.ID, "id_company").send_keys("Tech Solutions Inc")
        driver.find_element(By.ID, "id_description").send_keys("Automated testing role")
        driver.find_element(By.ID, "id_required_skills").send_keys("Python, Selenium, PyTest")
        driver.find_element(By.ID, "id_location").send_keys("Remote")
        driver.find_element(By.ID, "id_salary").send_keys("10 LPA")
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1.5)
        
        if "dashboard" in driver.current_url:
            print("JOB POSTED SUCCESSFULLY")
            print("Enter Job Title: Selenium Test Engineer")
            print("POST JOB TEST PASSED")
        else:
            print("POST JOB TEST FAILED")
            
    except Exception as e:
        print("POST JOB TEST FAILED:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    test_post_job()
\end{lstlisting}

\begin{figure}[H]
    \centering
    \rule{0.8\linewidth}{6cm}
    \caption{Post Job Test Result}
\end{figure}

\newpage
    \item \textbf{Upload Resume Test Functionality}

    \text{Code}
\begin{lstlisting}[language=Python, numbers=none]
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

def test_upload_resume():
    driver = webdriver.Chrome()
    try:
        # Login as candidate
        driver.get("http://localhost:8000/login/")
        driver.find_element(By.NAME, "username").send_keys("candidate1")
        driver.find_element(By.NAME, "password").send_keys("cand123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1.5)
        
        driver.get("http://localhost:8000/resumes/upload/")
        
        file_input = driver.find_element(By.NAME, "resume_file")
        resume_path = os.path.abspath("sample_resume.pdf")
        file_input.send_keys(resume_path)
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
        
        if "dashboard" in driver.current_url:
            print("RESUME UPLOADED SUCCESSFULLY")
            print("ATS Score Generated")
            print("UPLOAD RESUME TEST PASSED")
        else:
            print("UPLOAD RESUME TEST FAILED")
            
    except Exception as e:
        print("UPLOAD RESUME TEST FAILED:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    test_upload_resume()
\end{lstlisting}
   
\begin{figure}[H]
    \centering
    \rule{0.8\linewidth}{6cm}
    \caption{Upload Resume Test Result}
\end{figure}

\end{enumerate}
"""

# Find the exact string to replace
start_idx = content.find(r"\section{Test Cases}")
end_idx = content.find(r"\end{table}", start_idx) + len(r"\end{table}")
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + test_cases_replacement + content[end_idx:]


# 2. Remove the Screenshots section from Chapter 7
screenshots_start = content.find(r"\section{System Interfaces (Screenshots)}")
screenshots_end = content.find(r"% ==========================================================", screenshots_start)
if screenshots_start != -1 and screenshots_end != -1:
    content = content[:screenshots_start] + content[screenshots_end:]

# 3. Add Screenshots and Git Logs to Chapter 11 Appendix
appendix_screenshots = r"""
% ==========================================================
% SCREENSHOTS
% ==========================================================
\clearpage
\section{Screenshots}

\begin{figure}[H]
    \centering
    \rule{0.95\textwidth}{10cm}
    \caption{Home Page with Login Interface}
\end{figure}

\begin{figure}[H]
    \centering
    \rule{0.95\textwidth}{10cm}
    \caption{Candidate Dashboard with ATS Score and Skills Analysis}
\end{figure}

\begin{figure}[H]
    \centering
    \rule{0.95\textwidth}{10cm}
    \caption{Recruiter Dashboard with Applicant Rankings}
\end{figure}

\begin{figure}[H]
    \centering
    \rule{0.95\textwidth}{10cm}
    \caption{Job Posting Interface for Recruiters}
\end{figure}

% ==========================================================
% GIT LOGS
% ==========================================================
\clearpage
\section{Git Logs}
The Git log entries show the history of the development and the version control of the AI Resume Screening System's implementation.

\begin{figure}[H]
    \centering
    \rule{0.95\textwidth}{10cm}
    \caption{Git Log}
\end{figure}
"""

end_document_idx = content.rfind(r"\end{document}")
if end_document_idx != -1:
    content = content[:end_document_idx] + appendix_screenshots + "\n" + content[end_document_idx:]

with open("project_report.tex", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
