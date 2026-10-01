import re

def extract_email(text):
    emails = re.findall(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )
    return emails[0] if emails else ""

def extract_phone(text):
    phones = re.findall(
        r'(\+91[\s-]?\d{10}|\d{10})',
        text
    )
    return phones[0] if phones else ""

def extract_name(text):
    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        if len(line) > 3 and len(line.split()) <= 4:
            return line

    return ""
from .skills import SKILLS

def extract_skills(text):
    found_skills = []

    text = text.lower()

    for skill in SKILLS:
        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))