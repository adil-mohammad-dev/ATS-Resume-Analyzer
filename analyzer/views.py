from django.shortcuts import render, redirect
from groq import Groq
import pdfplumber
import os


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


def analyze_resume(request):

    if request.method == "POST":

        resume = request.FILES["resume"]
        job_desc = request.POST.get("jobdesc", "")

        # Create uploads folder automatically on Render/local
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

        # Skill aliases
        skill_aliases = {
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

            "excel": ["excel", "ms excel", "advanced excel"],
            "power bi": ["power bi", "powerbi"],
            "tableau": ["tableau"],
            "data analytics": ["data analytics", "analytics", "data analysis"],
            "pandas": ["pandas"],
            "numpy": ["numpy"],
            "matplotlib": ["matplotlib"],
            "seaborn": ["seaborn"],
            "statistics": ["statistics", "statistical"],

            "machine learning": ["machine learning", "ml"],
            "deep learning": ["deep learning"],
            "tensorflow": ["tensorflow"],
            "pytorch": ["pytorch"],
            "scikit-learn": ["scikit-learn", "sklearn"],

            "manual testing": ["manual testing"],
            "automation testing": ["automation testing"],
            "selenium": ["selenium"],
            "pytest": ["pytest"],
            "junit": ["junit"],
            "test cases": ["test cases", "test case"],

            "aws": ["aws", "amazon web services"],
            "azure": ["azure"],
            "google cloud": ["google cloud", "gcp"],
            "docker": ["docker"],
            "kubernetes": ["kubernetes", "k8s"],
            "linux": ["linux"],
            "ci/cd": ["ci/cd", "cicd", "continuous integration"],

            "cybersecurity": ["cybersecurity", "cyber security"],
            "networking": ["networking", "computer networks"],
            "firewall": ["firewall"],
            "penetration testing": ["penetration testing", "pentesting"],

            "figma": ["figma"],
            "ui/ux": ["ui/ux", "ui ux", "user interface", "user experience"],
            "wireframing": ["wireframing", "wireframe"],

            "database": ["database", "databases", "dbms"],
            "frontend": ["frontend", "front-end", "front end"],
            "backend": ["backend", "back-end", "back end"],
            "full stack": ["full stack", "fullstack"],
            "deployment": ["deployment", "deployed", "render", "vercel", "netlify"],
            "problem solving": ["problem solving", "problem-solving"],
            "communication": ["communication"],
            "teamwork": ["teamwork", "team work"],
        }

        # Role-based skills for jobs and internships
        role_skill_map = {
            "web developer": [
                "html", "css", "javascript", "bootstrap", "git", "github",
                "rest api", "database"
            ],
            "frontend developer": [
                "html", "css", "javascript", "react", "bootstrap",
                "tailwind css", "git", "github"
            ],
            "backend developer": [
                "python", "django", "flask", "node.js", "express.js",
                "sql", "mysql", "database", "rest api", "git"
            ],
            "full stack developer": [
                "html", "css", "javascript", "python", "django", "node.js",
                "express.js", "sql", "mysql", "rest api", "git", "github"
            ],
            "python developer": [
                "python", "django", "flask", "sql", "mysql", "rest api",
                "git", "database"
            ],
            "django developer": [
                "python", "django", "sql", "mysql", "rest api", "git",
                "html", "css"
            ],
            "java developer": [
                "java", "sql", "mysql", "rest api", "git", "database"
            ],
            "data analyst": [
                "sql", "excel", "python", "pandas", "numpy", "power bi",
                "tableau", "data analytics", "matplotlib", "statistics"
            ],
            "business analyst": [
                "excel", "sql", "power bi", "tableau", "data analytics",
                "communication", "problem solving"
            ],
            "data scientist": [
                "python", "sql", "pandas", "numpy", "machine learning",
                "statistics", "matplotlib", "seaborn", "scikit-learn"
            ],
            "machine learning engineer": [
                "python", "machine learning", "deep learning", "tensorflow",
                "pytorch", "scikit-learn", "numpy", "pandas"
            ],
            "ai engineer": [
                "python", "machine learning", "deep learning", "tensorflow",
                "pytorch", "api", "numpy", "pandas"
            ],
            "qa tester": [
                "manual testing", "automation testing", "selenium",
                "test cases", "sql", "git"
            ],
            "software tester": [
                "manual testing", "automation testing", "selenium",
                "test cases", "sql"
            ],
            "devops engineer": [
                "linux", "docker", "kubernetes", "aws", "ci/cd", "git",
                "github"
            ],
            "cloud engineer": [
                "aws", "azure", "google cloud", "linux", "docker",
                "networking"
            ],
            "database developer": [
                "sql", "mysql", "postgresql", "mongodb", "database"
            ],
            "ui ux designer": [
                "ui/ux", "figma", "wireframing", "html", "css"
            ],
            "cybersecurity analyst": [
                "cybersecurity", "networking", "linux", "firewall",
                "penetration testing"
            ],
            "android developer": [
                "java", "sql", "api", "git", "github"
            ],
            "software developer": [
                "python", "java", "javascript", "sql", "git", "github",
                "database", "problem solving"
            ],
        }

        role_based_skills = []

        for role, skills in role_skill_map.items():
            if role in job_lower:
                role_based_skills.extend(skills)

        # Support internship wording
        if "intern" in job_lower or "internship" in job_lower:
            if "web" in job_lower:
                role_based_skills.extend(role_skill_map["web developer"])
            elif "frontend" in job_lower or "front end" in job_lower:
                role_based_skills.extend(role_skill_map["frontend developer"])
            elif "backend" in job_lower:
                role_based_skills.extend(role_skill_map["backend developer"])
            elif "full stack" in job_lower or "fullstack" in job_lower:
                role_based_skills.extend(role_skill_map["full stack developer"])
            elif "python" in job_lower:
                role_based_skills.extend(role_skill_map["python developer"])
            elif "data" in job_lower:
                role_based_skills.extend(role_skill_map["data analyst"])
            elif "qa" in job_lower or "testing" in job_lower:
                role_based_skills.extend(role_skill_map["qa tester"])

        # Extract JD required skills
        jd_required_skills = []

        for skill, aliases in skill_aliases.items():
            for alias in aliases:
                if alias in job_lower and skill not in jd_required_skills:
                    jd_required_skills.append(skill)

        for skill in role_based_skills:
            if skill not in jd_required_skills:
                jd_required_skills.append(skill)

        # Extract resume skills
        resume_skills = []

        for skill, aliases in skill_aliases.items():
            for alias in aliases:
                if alias in resume_lower and skill not in resume_skills:
                    resume_skills.append(skill)

        # Evidence keywords
        project_keywords = [
            "project", "developed", "built", "created", "implemented",
            "designed", "deployed", "integrated", "dashboard", "website",
            "web app", "application", "system", "portfolio", "management"
        ]

        internship_keywords = [
            "internship", "intern", "trainee", "industrial training"
        ]

        work_keywords = [
            "work experience", "professional experience", "worked at",
            "software developer", "web developer", "engineer", "employment"
        ]

        achievement_keywords = [
            "certification", "certificate", "achievement", "award",
            "solved", "completed", "course", "hackathon", "scaler", "infosys"
        ]

        education_keywords = [
            "b.tech", "bachelor", "degree", "engineering",
            "computer science", "diploma", "graduate", "education",
            "college", "university"
        ]

        project_evidence = [
            keyword for keyword in project_keywords if keyword in resume_lower
        ]

        internship_evidence = [
            keyword for keyword in internship_keywords if keyword in resume_lower
        ]

        work_evidence = [
            keyword for keyword in work_keywords if keyword in resume_lower
        ]

        achievement_evidence = [
            keyword for keyword in achievement_keywords if keyword in resume_lower
        ]

        education_evidence = [
            keyword for keyword in education_keywords if keyword in resume_lower
        ]

        # Match skills
        matched_skills = []
        missing_skills = []

        for skill in jd_required_skills:
            if skill in resume_skills:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # ATS score calculation
        if len(jd_required_skills) > 0:
            skill_score = int((len(matched_skills) / len(jd_required_skills)) * 75)
        else:
            skill_score = 0

        project_score = min(len(project_evidence) * 3, 10)
        internship_score = min(len(internship_evidence) * 5, 5)
        work_score = min(len(work_evidence) * 5, 5)
        achievement_score = min(len(achievement_evidence) * 2, 5)
        education_score = min(len(education_evidence) * 2, 5)

        evidence_score = (
            project_score
            + internship_score
            + work_score
            + achievement_score
            + education_score
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

Very Important Rules:
- Do not invent skills.
- Do not mention candidate type.
- Do not contradict the calculated matched skills and missing skills.
- Do not say a skill is missing if it is already present in Resume Skills Found.
- Use only the provided lists below.
- The ATS score is already calculated logically. Do not change it.
- Analyze full resume including skills, projects, internships, work experience, certifications, achievements, and education.
- Support both jobs and internships.

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
3. JD Required Skills:
4. Skills Found In Resume:
5. Matched Skills:
6. Missing Important Skills:
7. Project Relevance:
8. Internship / Work Experience Relevance:
9. Achievement / Certification Relevance:
10. Education Relevance:
11. Is This Resume Suitable For The Job?:
12. Resume Improvement Suggestions:
13. Skills To Learn Before Applying:
14. Final Recommendation:
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

        result = chat_completion.choices[0].message.content

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