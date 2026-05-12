import os
import re

import pdfplumber
from groq import Groq


SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "java script", "js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo db"],
    "django": ["django"],
    "flask": ["flask"],
    "react": ["react", "react.js", "reactjs"],
    "angular": ["angular"],
    "vue.js": ["vue", "vue.js"],
    "node.js": ["node.js", "nodejs", "node"],
    "express.js": ["express.js", "expressjs", "express"],
    "bootstrap": ["bootstrap"],
    "tailwind css": ["tailwind", "tailwind css"],
    "rest api": ["rest api", "restful api", "api"],
    "git": ["git"],
    "github": ["github"],
    "database": ["database", "databases", "dbms"],
    "frontend": ["frontend", "front-end", "front end"],
    "backend": ["backend", "back-end", "back end"],
    "full stack": ["full stack", "fullstack"],
    "deployment": ["deployment", "deployed", "render", "vercel", "netlify"],
    "excel": ["excel", "ms excel", "advanced excel"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "data analytics": ["data analytics", "analytics", "data analysis"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"],
    "statistics": ["statistics", "statistical"],
    "reporting": ["reporting", "reports"],
    "dashboard": ["dashboard", "dashboards"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "manual testing": ["manual testing"],
    "automation testing": ["automation testing"],
    "selenium": ["selenium"],
    "pytest": ["pytest"],
    "test cases": ["test cases", "test case"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "google cloud": ["google cloud", "gcp"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "linux": ["linux"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration"],
    "accounting": ["accounting", "accounts"],
    "finance": ["finance", "financial"],
    "banking": ["banking", "bank"],
    "tally": ["tally", "tally erp"],
    "gst": ["gst"],
    "taxation": ["taxation", "tax"],
    "auditing": ["auditing", "audit"],
    "bookkeeping": ["bookkeeping"],
    "financial analysis": ["financial analysis"],
    "investment": ["investment", "investments"],
    "risk management": ["risk management"],
    "loan processing": ["loan processing"],
    "kyc": ["kyc"],
    "ms office": ["ms office", "microsoft office"],
    "balance sheet": ["balance sheet"],
    "profit and loss": ["profit and loss", "p&l"],
    "hr": ["hr", "human resources"],
    "recruitment": ["recruitment", "recruiter", "hiring"],
    "payroll": ["payroll"],
    "employee engagement": ["employee engagement"],
    "operations": ["operations", "operational"],
    "inventory management": ["inventory management", "inventory"],
    "vendor management": ["vendor management"],
    "supply chain": ["supply chain"],
    "project management": ["project management"],
    "sales": ["sales", "selling"],
    "marketing": ["marketing"],
    "digital marketing": ["digital marketing"],
    "seo": ["seo", "search engine optimization"],
    "social media marketing": ["social media marketing"],
    "lead generation": ["lead generation"],
    "crm": ["crm"],
    "customer relationship": ["customer relationship"],
    "teaching": ["teaching", "teacher", "faculty"],
    "lesson planning": ["lesson planning"],
    "classroom management": ["classroom management"],
    "student assessment": ["student assessment"],
    "curriculum": ["curriculum"],
    "communication": ["communication"],
    "customer support": ["customer support", "customer service"],
    "bpo": ["bpo", "call center"],
    "healthcare": ["healthcare", "hospital"],
    "patient care": ["patient care"],
    "hospitality": ["hospitality", "hotel"],
    "front office": ["front office", "reception"],
    "food service": ["food service"],
    "problem solving": ["problem solving", "problem-solving"],
    "teamwork": ["teamwork", "team work"],
    "leadership": ["leadership"],
    "time management": ["time management"],
    "adaptability": ["adaptability"],
    "presentation skills": ["presentation skills"],
}

ROLE_SKILL_MAP = {
    "web developer": ["html", "css", "javascript", "bootstrap", "git", "github", "rest api", "database"],
    "frontend developer": ["html", "css", "javascript", "react", "bootstrap", "git", "github"],
    "backend developer": ["python", "django", "flask", "node.js", "express.js", "sql", "database", "rest api", "git"],
    "full stack developer": ["html", "css", "javascript", "python", "django", "node.js", "sql", "rest api", "git", "database"],
    "python developer": ["python", "django", "flask", "sql", "rest api", "git", "database"],
    "software developer": ["python", "java", "javascript", "sql", "git", "database", "problem solving"],
    "data analyst": ["sql", "excel", "python", "pandas", "numpy", "power bi", "data analytics", "dashboard", "reporting"],
    "business analyst": ["excel", "sql", "power bi", "data analytics", "communication", "problem solving"],
    "data scientist": ["python", "sql", "pandas", "numpy", "machine learning", "statistics"],
    "banking": ["banking", "finance", "excel", "kyc", "loan processing", "communication"],
    "accountant": ["accounting", "tally", "gst", "taxation", "bookkeeping", "excel"],
    "finance analyst": ["finance", "financial analysis", "excel", "accounting", "investment"],
    "ca": ["accounting", "auditing", "taxation", "gst", "balance sheet", "financial analysis"],
    "audit assistant": ["auditing", "accounting", "taxation", "excel"],
    "hr executive": ["hr", "recruitment", "payroll", "communication", "employee engagement"],
    "recruiter": ["recruitment", "communication", "hr", "crm"],
    "operations executive": ["operations", "excel", "inventory management", "vendor management"],
    "sales executive": ["sales", "communication", "lead generation", "crm"],
    "marketing executive": ["marketing", "digital marketing", "communication", "social media marketing"],
    "digital marketing": ["digital marketing", "seo", "social media marketing", "marketing"],
    "teacher": ["teaching", "communication", "lesson planning", "classroom management", "student assessment"],
    "faculty": ["teaching", "communication", "curriculum", "student assessment"],
    "customer support": ["customer support", "communication", "problem solving", "crm"],
    "bpo": ["bpo", "communication", "customer support"],
    "receptionist": ["front office", "communication", "ms office"],
    "hospitality": ["hospitality", "customer service", "communication"],
}

PROJECT_KEYWORDS = [
    "project", "developed", "built", "created", "implemented", "designed",
    "deployed", "integrated", "dashboard", "website", "application",
    "system", "portfolio", "management"
]

INTERNSHIP_KEYWORDS = ["internship", "intern", "trainee", "industrial training"]
WORK_KEYWORDS = ["work experience", "professional experience", "worked at", "employment", "company"]
ACHIEVEMENT_KEYWORDS = ["certification", "certificate", "achievement", "award", "solved", "completed", "course"]
EDUCATION_KEYWORDS = [
    "b.tech", "bachelor", "degree", "engineering", "b.com", "bca", "bba", "mba", "m.com",
    "diploma", "graduate", "education", "college", "university"
]


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is required for AI integration.")
    return Groq(api_key=api_key)


def extract_text(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text).strip()


def clean_ai_output(text):
    if not text:
        return ""

    text = text.replace("**", "")
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("* ", "- ")

    section_headings = [
        "ATS Score",
        "ATS Score Breakdown",
        "Application Decision",
        "Job Role Identified",
        "Resume Parsing Analysis",
        "Keyword Optimization",
        "Content Quality",
        "JD Required Skills",
        "Skills Found In Resume",
        "Matched Skills",
        "Missing Important Skills",
        "Project Relevance",
        "Internship / Work Experience Relevance",
        "Achievement / Certification Relevance",
        "Education Relevance",
        "Is This Resume Suitable For The Job?",
        "Resume Improvement Suggestions",
        "Skills To Learn Before Applying",
        "Final Recommendation",
        "Professional Summary",
        "Career Objective",
        "Key Skills",
        "Education",
        "Projects",
        "Experience / Internship",
        "Internship",
        "Certifications",
        "Achievements",
        "ATS Improvement Tips",
    ]

    for heading in section_headings:
        text = text.replace(
            heading + ":",
            '<span class="report-heading">' + heading + ":</span>"
        )

    return text.strip()


def calculate_parsing_score(resume_text):
    score = 0
    text = resume_text.lower()

    important_sections = [
        "skills", "education", "experience", "projects",
        "certifications", "achievements"
    ]

    found_sections = sum(1 for section in important_sections if section in text)
    score += min(found_sections * 3, 15)

    if len(resume_text) > 500:
        score += 2

    if "@" in resume_text:
        score += 1

    if any(char.isdigit() for char in resume_text):
        score += 1

    if len(resume_text.split()) >= 250:
        score += 1

    return min(score, 20)


def calculate_content_quality_score(resume_text):
    score = 0
    text = resume_text.lower()

    action_verbs = [
        "developed", "created", "built", "implemented", "designed",
        "managed", "improved", "optimized", "analyzed", "led",
        "coordinated", "prepared", "handled", "assisted", "delivered",
        "achieved", "completed", "worked", "collaborated"
    ]

    measurable_terms = [
        "%", "increased", "reduced", "improved", "optimized",
        "growth", "accuracy", "efficiency", "performance",
        "revenue", "cost", "time", "users", "customers"
    ]

    action_count = 0
    metric_count = 0

    for verb in action_verbs:
        if verb in text:
            action_count += 1

    for term in measurable_terms:
        if term in text:
            metric_count += 1

    score += min(action_count * 2, 10)
    score += min(metric_count * 2, 10)

    return min(score, 20)


def calculate_section_score(resume_text):
    score = 0
    text = resume_text.lower()

    sections = {
        "contact": ["email", "phone", "@", "linkedin"],
        "skills": ["skills"],
        "education": ["education", "b.tech", "b.com", "bca", "degree", "college", "university"],
        "experience": ["experience", "internship", "work experience", "employment"],
        "projects": ["projects", "project"],
        "certifications": ["certification", "certifications", "certificate"],
        "achievements": ["achievement", "achievements", "award"]
    }

    for section, keywords in sections.items():
        for keyword in keywords:
            if keyword in text:
                score += 1.5
                break

    return min(int(score), 10)


def calculate_impact_score(resume_text):
    score = 0
    text = resume_text.lower()

    impact_keywords = [
        "improved", "increased", "reduced", "optimized", "achieved",
        "successfully", "resolved", "enhanced", "automated",
        "saved", "generated", "delivered"
    ]

    for keyword in impact_keywords:
        if keyword in text:
            score += 1

    if "%" in resume_text:
        score += 3

    if any(char.isdigit() for char in resume_text):
        score += 2

    return min(score, 10)


def find_skills(text, alias_map=None):
    if alias_map is None:
        alias_map = SKILL_ALIASES

    found = []
    text = text.lower()

    for skill, aliases in alias_map.items():
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias) + r"\b", text):
                if skill not in found:
                    found.append(skill)
                break

    return found


def build_job_specific_skills(job_text):
    job_text = job_text.lower()
    result = []
    for role, skills in ROLE_SKILL_MAP.items():
        if role in job_text:
            result.extend(skills)

    if "intern" in job_text or "internship" in job_text:
        for role, skills in ROLE_SKILL_MAP.items():
            if role.split()[0] in job_text:
                result.extend(skills)

    return [skill for skill in result if skill not in []]


def collect_evidence(resume_text):
    resume_text = resume_text.lower()

    return {
        "project": [keyword for keyword in PROJECT_KEYWORDS if keyword in resume_text],
        "internship": [keyword for keyword in INTERNSHIP_KEYWORDS if keyword in resume_text],
        "work": [keyword for keyword in WORK_KEYWORDS if keyword in resume_text],
        "achievement": [keyword for keyword in ACHIEVEMENT_KEYWORDS if keyword in resume_text],
        "education": [keyword for keyword in EDUCATION_KEYWORDS if keyword in resume_text],
    }


def calculate_ats_score(jd_required_skills, resume_skills, evidence, resume_text):
    matched_skills = [skill for skill in jd_required_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_required_skills if skill not in resume_skills]

    keyword_score = int((len(matched_skills) / len(jd_required_skills)) * 40) if jd_required_skills else 0
    parsing_score = calculate_parsing_score(resume_text)
    content_quality_score = calculate_content_quality_score(resume_text)
    section_score = calculate_section_score(resume_text)
    impact_score = calculate_impact_score(resume_text)

    ats_score = (
        keyword_score
        + parsing_score
        + content_quality_score
        + section_score
        + impact_score
    )

    if jd_required_skills and len(matched_skills) == 0:
        ats_score = min(ats_score, 35)

    ats_score = min(ats_score, 100)

    if ats_score >= 75:
        decision = "Strong Fit - Recommended to Apply"
    elif ats_score >= 55:
        decision = "Moderate Fit - Can Apply, But Resume Needs Improvement"
    elif ats_score >= 40:
        decision = "Basic Fit - Improve Resume Before Applying"
    else:
        decision = "Low Fit - Not Recommended Until Resume Improves"

    return (
        ats_score,
        decision,
        matched_skills,
        missing_skills,
        keyword_score,
        parsing_score,
        content_quality_score,
        section_score,
        impact_score,
    )


def build_analysis_prompt(
    job_desc,
    resume_text,
    ats_score,
    decision,
    jd_required_skills,
    resume_skills,
    matched_skills,
    missing_skills,
    evidence,
    keyword_score,
    parsing_score,
    content_quality_score,
    section_score,
    impact_score,
):
    return f"""
You are a professional ATS Resume Analyzer and HR screening assistant.

Rules:
- Support IT and non-IT resumes.
- Support jobs and internships.
- Do not invent skills.
- Do not mention candidate type.
- Do not use markdown symbols like **, ##, ###.
- The ATS score is already calculated logically. Do not change it.
- If skills are missing, give practical improvement suggestions.
- Analyze skills, education, projects, internships, work experience, certifications, and achievements.

Job Description:
{job_desc}

Resume:
{resume_text}

Calculated ATS Score:
{ats_score}%

ATS Score Breakdown:
Keyword Optimization Score: {keyword_score}/40
Resume Parsing Score: {parsing_score}/20
Content Quality Score: {content_quality_score}/20
Section Completeness Score: {section_score}/10
Impact / Achievement Score: {impact_score}/10

Application Decision:
{decision}

JD Required Skills:
{jd_required_skills}

Resume Skills Found:
{resume_skills}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Project Evidence:
{evidence['project']}

Internship Evidence:
{evidence['internship']}

Work Experience Evidence:
{evidence['work']}

Achievement / Certification Evidence:
{evidence['achievement']}

Education Evidence:
{evidence['education']}

Generate a clean professional ATS report in this exact format:

1. ATS Score:
2. ATS Score Breakdown:
3. Application Decision:
4. Job Role Identified:
5. Resume Parsing Analysis:
6. Keyword Optimization:
7. Content Quality:
8. JD Required Skills:
9. Skills Found In Resume:
10. Matched Skills:
11. Missing Important Skills:
12. Project Relevance:
13. Internship / Work Experience Relevance:
14. Achievement / Certification Relevance:
15. Education Relevance:
16. Is This Resume Suitable For The Job?:
17. Resume Improvement Suggestions:
18. Skills To Learn Before Applying:
19. Final Recommendation:
"""


def build_resume_prompt(details):
    return f"""
You are an expert resume writer and ATS optimization specialist.

Create a professional ATS-friendly resume content for the following candidate.
Support IT and non-IT roles.
Keep it professional, concise, and recruiter-friendly.
Do not use markdown symbols like **, ##, ###.
Use strong action verbs.
Create content suitable for a resume.

Candidate Details:
Name: {details['full_name']}
Email: {details['email']}
Phone: {details['phone']}
Location: {details.get('location', '')}
LinkedIn: {details.get('linkedin', '')}
Portfolio: {details.get('portfolio', '')}
Target Role: {details['target_role']}
Career Level: {details['career_level']}
Resume Type: {details['resume_type']}
Resume Tone: {details.get('resume_tone', '')}
Education: {details['education']}
Skills: {details['skills']}
Projects: {details.get('projects', '')}
Experience / Internship: {details.get('experience', '')}
Certifications: {details.get('certifications', '')}
Achievements: {details.get('achievements', '')}

Generate resume in this format:

Professional Summary:
Career Objective:
Key Skills:
Education:
Projects:
Experience / Internship:
Certifications:
Achievements:
ATS Improvement Tips:
"""


def validate_pdf_file(uploaded_file):
    name = uploaded_file.name.lower()
    if not name.endswith(".pdf"):
        return False
    return True
