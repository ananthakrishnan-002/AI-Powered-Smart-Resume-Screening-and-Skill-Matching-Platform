import os

def insert_code():
    with open('project_report.tex', 'r', encoding='utf-8') as f:
        latex = f.read()

    def get_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            return "% Code not found"

    # Replace placeholders with actual code
    latex = latex.replace('%JOBS_MODELS_PLACEHOLDER%', get_file('../jobs/models.py'))
    latex = latex.replace('%RESUMES_MODELS_PLACEHOLDER%', get_file('../resumes/models.py'))
    latex = latex.replace('%RESUMES_ATS_PLACEHOLDER%', get_file('../resumes/ats.py'))
    latex = latex.replace('%JOBS_MATCHER_PLACEHOLDER%', get_file('../jobs/matcher.py'))
    latex = latex.replace('%JOBS_VIEWS_PLACEHOLDER%', get_file('../jobs/views.py'))
    latex = latex.replace('%RESUMES_VIEWS_PLACEHOLDER%', get_file('../resumes/views.py'))

    with open('project_report.tex', 'w', encoding='utf-8') as f:
        f.write(latex)

if __name__ == '__main__':
    insert_code()
