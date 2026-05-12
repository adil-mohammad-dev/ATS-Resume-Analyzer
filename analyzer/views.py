from django.shortcuts import render, redirect
from groq import Groq
import pdfplumber
import os
import re


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def extract_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def home(request):
    return render(request, "index.html")


def clean_ai_output(text):
    text = text.replace("**", "")
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("* ", "- ")

    section_headings = [
        "ATS Score",
        "Application Decision",
        "Job Role Identified",
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
        "Skills",
        "Education",
        "Projects",
        "Experience",
        "Internship",
        "Certifications",
        "Achievements",
        "ATS Improvement Tips",
    ]

    for heading in section_headings:
        text = text.replace(
            heading + ":",
            '<span class="report-heading">' + heading + ':</span>'
        )

    return text


def analyze_resume(request):

    if request.method == "POST":

        resume = request.FILES["resume"]
        job_desc = request.POST.get("jobdesc", "")

        upload_folder = "uploads"

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, resume.name)

        with open(filepath, "wb+") as destination:
            for chunk in resume.chunks():
                destination.write(chunk)

        resume_text = extract_text(filepath)

        resume_lower = resume_text.lower()
        job_lower = job_desc.lower()

        skill_aliases = {
            # IT / Software
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

            # Data / Analytics
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

            # AI / ML
            "machine learning": ["machine learning", "ml"],
            "deep learning": ["deep learning"],
            "tensorflow": ["tensorflow"],
            "pytorch": ["pytorch"],
            "scikit-learn": ["scikit-learn", "sklearn"],

            # Testing / QA
            "manual testing": ["manual testing"],
            "automation testing": ["automation testing"],
            "selenium": ["selenium"],
            "pytest": ["pytest"],
            "test cases": ["test cases", "test case"],

            # Cloud / DevOps
            "aws": ["aws", "amazon web services"],
            "azure": ["azure"],
            "google cloud": ["google cloud", "gcp"],
            "docker": ["docker"],
            "kubernetes": ["kubernetes", "k8s"],
            "linux": ["linux"],
            "ci/cd": ["ci/cd", "cicd", "continuous integration"],

            # Banking / Finance / Accounting / CA
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

            # HR / Management / Operations
            "hr": ["hr", "human resources"],
            "recruitment": ["recruitment", "recruiter", "hiring"],
            "payroll": ["payroll"],
            "employee engagement": ["employee engagement"],
            "operations": ["operations", "operational"],
            "inventory management": ["inventory management", "inventory"],
            "vendor management": ["vendor management"],
            "supply chain": ["supply chain"],
            "project management": ["project management"],

            # Sales / Marketing
            "sales": ["sales", "selling"],
            "marketing": ["marketing"],
            "digital marketing": ["digital marketing"],
            "seo": ["seo", "search engine optimization"],
            "social media marketing": ["social media marketing"],
            "lead generation": ["lead generation"],
            "crm": ["crm"],
            "customer relationship": ["customer relationship"],

            # Teaching / Education
            "teaching": ["teaching", "teacher", "faculty"],
            "lesson planning": ["lesson planning"],
            "classroom management": ["classroom management"],
            "student assessment": ["student assessment"],
            "curriculum": ["curriculum"],
            "communication": ["communication"],

            # Healthcare / Hospitality / Support
            "customer support": ["customer support", "customer service"],
            "bpo": ["bpo", "call center"],
            "healthcare": ["healthcare", "hospital"],
            "patient care": ["patient care"],
            "hospitality": ["hospitality", "hotel"],
            "front office": ["front office", "reception"],
            "food service": ["food service"],

            # Common soft skills
            "problem solving": ["problem solving", "problem-solving"],
            "teamwork": ["teamwork", "team work"],
            "leadership": ["leadership"],
            "time management": ["time management"],
            "adaptability": ["adaptability"],
            "presentation skills": ["presentation skills"],
        }

        role_skill_map = {
            # IT
            "web developer": ["html", "css", "javascript", "bootstrap", "git", "github", "rest api", "database"],
            "frontend developer": ["html", "css", "javascript", "react", "bootstrap", "git", "github"],
            "backend developer": ["python", "django", "flask", "node.js", "express.js", "sql", "database", "rest api", "git"],
            "full stack developer": ["html", "css", "javascript", "python", "django", "node.js", "sql", "rest api", "git", "database"],
            "python developer": ["python", "django", "flask", "sql", "rest api", "git", "database"],
            "software developer": ["python", "java", "javascript", "sql", "git", "database", "problem solving"],

            # Data
            "data analyst": ["sql", "excel", "python", "pandas", "numpy", "power bi", "data analytics", "dashboard", "reporting"],
            "business analyst": ["excel", "sql", "power bi", "data analytics", "communication", "problem solving"],
            "data scientist": ["python", "sql", "pandas", "numpy", "machine learning", "statistics"],

            # Banking / Finance
            "banking": ["banking", "finance", "excel", "kyc", "loan processing", "communication"],
            "accountant": ["accounting", "tally", "gst", "taxation", "bookkeeping", "excel"],
            "finance analyst": ["finance", "financial analysis", "excel", "accounting", "investment"],
            "ca": ["accounting", "auditing", "taxation", "gst", "balance sheet", "financial analysis"],
            "audit assistant": ["auditing", "accounting", "taxation", "excel"],

            # HR / Operations
            "hr executive": ["hr", "recruitment", "payroll", "communication", "employee engagement"],
            "recruiter": ["recruitment", "communication", "hr", "crm"],
            "operations executive": ["operations", "excel", "inventory management", "vendor management"],

            # Sales / Marketing
            "sales executive": ["sales", "communication", "lead generation", "crm"],
            "marketing executive": ["marketing", "digital marketing", "communication", "social media marketing"],
            "digital marketing": ["digital marketing", "seo", "social media marketing", "marketing"],

            # Teaching
            "teacher": ["teaching", "communication", "lesson planning", "classroom management", "student assessment"],
            "faculty": ["teaching", "communication", "curriculum", "student assessment"],

            # Customer support / Hospitality
            "customer support": ["customer support", "communication", "problem solving", "crm"],
            "bpo": ["bpo", "communication", "customer support"],
            "receptionist": ["front office", "communication", "ms office"],
            "hospitality": ["hospitality", "customer service", "communication"],
        }

        role_based_skills = []

        for role, skills in role_skill_map.items():
            if role in job_lower:
                role_based_skills.extend(skills)

        if "intern" in job_lower or "internship" in job_lower:
            for role, skills in role_skill_map.items():
                if role.split()[0] in job_lower:
                    role_based_skills.extend(skills)

        jd_required_skills = []

        for skill, aliases in skill_aliases.items():
            for alias in aliases:
                if alias in job_lower and skill not in jd_required_skills:
                    jd_required_skills.append(skill)

        for skill in role_based_skills:
            if skill not in jd_required_skills:
                jd_required_skills.append(skill)

        resume_skills = []

        for skill, aliases in skill_aliases.items():
            for alias in aliases:
                if alias in resume_lower and skill not in resume_skills:
                    resume_skills.append(skill)

        project_keywords = [
            "project", "developed", "built", "created", "implemented", "designed",
            "deployed", "integrated", "dashboard", "website", "application",
            "system", "portfolio", "management"
        ]

        internship_keywords = ["internship", "intern", "trainee", "industrial training"]
        work_keywords = ["work experience", "professional experience", "worked at", "employment", "company"]
        achievement_keywords = ["certification", "certificate", "achievement", "award", "solved", "completed", "course"]
        education_keywords = ["b.tech", "bachelor", "degree", "engineering", "b.com", "bca", "bba", "mba", "m.com", "diploma", "graduate", "education", "college", "university"]

        project_evidence = [keyword for keyword in project_keywords if keyword in resume_lower]
        internship_evidence = [keyword for keyword in internship_keywords if keyword in resume_lower]
        work_evidence = [keyword for keyword in work_keywords if keyword in resume_lower]
        achievement_evidence = [keyword for keyword in achievement_keywords if keyword in resume_lower]
        education_evidence = [keyword for keyword in education_keywords if keyword in resume_lower]

        matched_skills = []
        missing_skills = []

        for skill in jd_required_skills:
            if skill in resume_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        if len(jd_required_skills) > 0:
            skill_score = int((len(matched_skills) / len(jd_required_skills)) * 75)
        else:
            skill_score = 0

        evidence_score = (
            min(len(project_evidence) * 3, 10)
            + min(len(internship_evidence) * 5, 5)
            + min(len(work_evidence) * 5, 5)
            + min(len(achievement_evidence) * 2, 5)
            + min(len(education_evidence) * 2, 5)
        )

        if evidence_score > 25:
            evidence_score = 25

        ats_score = skill_score + evidence_score

        if len(jd_required_skills) > 0 and len(matched_skills) == 0:
            ats_score = min(ats_score, 25)

        if ats_score > 100:
            ats_score = 100

        if ats_score >= 75:
            decision = "Strong Fit - Recommended to Apply"
        elif ats_score >= 55:
            decision = "Moderate Fit - Can Apply, But Resume Needs Improvement"
        elif ats_score >= 40:
            decision = "Basic Fit - Improve Resume Before Applying"
        else:
            decision = "Low Fit - Not Recommended Until Resume Improves"

        prompt = f"""
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
{project_evidence}

Internship Evidence:
{internship_evidence}

Work Experience Evidence:
{work_evidence}

Achievement / Certification Evidence:
{achievement_evidence}

Education Evidence:
{education_evidence}

Generate a clean professional report in this exact format:

1. ATS Score:
2. Application Decision:
3. Job Role Identified:
4. JD Required Skills:
5. Skills Found In Resume:
6. Matched Skills:
7. Missing Important Skills:
8. Project Relevance:
9. Internship / Work Experience Relevance:
10. Achievement / Certification Relevance:
11. Education Relevance:
12. Is This Resume Suitable For The Job?:
13. Resume Improvement Suggestions:
14. Skills To Learn Before Applying:
15. Final Recommendation:
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )

        result = clean_ai_output(chat_completion.choices[0].message.content)

        request.session["result"] = result
        request.session["ats_score"] = ats_score
        request.session["decision"] = decision
        request.session["matched_count"] = len(matched_skills)
        request.session["missing_count"] = len(missing_skills)
        request.session["jd_count"] = len(jd_required_skills)

        return redirect("/result/")

    return redirect("/")


def result_page(request):

    result = request.session.get("result", None)

    if not result:
        return redirect("/")

    return render(request, "result.html", {
        "result": result,
        "ats_score": request.session.get("ats_score", 0),
        "decision": request.session.get("decision", ""),
        "matched_count": request.session.get("matched_count", 0),
        "missing_count": request.session.get("missing_count", 0),
        "jd_count": request.session.get("jd_count", 0),
    })


def resume_builder(request):
    return render(request, "resume_builder.html")


def build_resume(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        target_role = request.POST.get("target_role", "")
        education = request.POST.get("education", "")
        skills = request.POST.get("skills", "")
        projects = request.POST.get("projects", "")
        experience = request.POST.get("experience", "")
        certifications = request.POST.get("certifications", "")
        achievements = request.POST.get("achievements", "")

        prompt = f"""
You are an expert resume writer and ATS optimization specialist.

Create a professional ATS-friendly resume content for the following candidate.
Support IT and non-IT roles.
Keep it professional, concise, and recruiter-friendly.
Do not use markdown symbols like **, ##, ###.
Use strong action verbs.
Create content suitable for a resume.

Candidate Details:
Name: {full_name}
Email: {email}
Phone: {phone}
Target Role: {target_role}
Education: {education}
Skills: {skills}
Projects: {projects}
Experience / Internship: {experience}
Certifications: {certifications}
Achievements: {achievements}

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

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )

        generated_resume = clean_ai_output(chat_completion.choices[0].message.content)

        request.session["generated_resume"] = generated_resume

        return redirect("/builder-result/")

    return redirect("/resume-builder/")


def builder_result(request):

    generated_resume = request.session.get("generated_resume", None)

    if not generated_resume:
        return redirect("/resume-builder/")

    return render(request, "builder_result.html", {
        "generated_resume": generated_resume
    })