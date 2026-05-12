import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect

from .forms import ResumeAnalysisForm, ResumeBuilderForm
from .utils import (
    build_analysis_prompt,
    build_job_specific_skills,
    build_resume_prompt,
    calculate_ats_score,
    clean_ai_output,
    collect_evidence,
    extract_text,
    find_skills,
    get_groq_client,
)


def home(request):
    return render(request, "index.html")


def analyze_resume(request):
    if request.method != "POST":
        return redirect("home")

    form = ResumeAnalysisForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "index.html", {"form_errors": form.errors})

    resume_file = form.cleaned_data["resume"]
    job_desc = form.cleaned_data["jobdesc"]

    storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
    filename = storage.save(resume_file.name, resume_file)
    filepath = storage.path(filename)

    try:
        resume_text = extract_text(filepath)
        if not resume_text:
            raise ValueError("Unable to extract text from the uploaded PDF.")

        job_lower = job_desc.lower()
        resume_lower = resume_text.lower()

        jd_required_skills = find_skills(job_lower)
        role_skills = build_job_specific_skills(job_lower)
        for skill in role_skills:
            if skill not in jd_required_skills:
                jd_required_skills.append(skill)

        resume_skills = find_skills(resume_lower)
        evidence = collect_evidence(resume_lower)

        (
            ats_score,
            decision,
            matched_skills,
            missing_skills,
            keyword_score,
            parsing_score,
            content_quality_score,
            section_score,
            impact_score,
        ) = calculate_ats_score(jd_required_skills, resume_skills, evidence, resume_text)

        prompt = build_analysis_prompt(
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
        )

        client = get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        result = clean_ai_output(chat_completion.choices[0].message.content)

        request.session["result"] = result
        request.session["ats_score"] = ats_score
        request.session["decision"] = decision
        request.session["matched_count"] = len(matched_skills)
        request.session["missing_count"] = len(missing_skills)
        request.session["jd_count"] = len(jd_required_skills)
        request.session["keyword_score"] = keyword_score
        request.session["parsing_score"] = parsing_score
        request.session["content_quality_score"] = content_quality_score
        request.session["section_score"] = section_score
        request.session["impact_score"] = impact_score

        return redirect("result_page")

    except Exception as error:
        return render(request, "index.html", {
            "form_errors": {"resume": [str(error)]}
        })

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def result_page(request):
    result = request.session.get("result")
    if not result:
        return redirect("home")

    keyword_score = request.session.get("keyword_score", 0)
    parsing_score = request.session.get("parsing_score", 0)
    content_quality_score = request.session.get("content_quality_score", 0)
    section_score = request.session.get("section_score", 0)
    impact_score = request.session.get("impact_score", 0)

    # Calculate pixel widths for progress bars (max width 240px)
    keyword_pct = int(min(keyword_score / 40 * 240, 240)) if keyword_score else 0
    parsing_pct = int(min(parsing_score / 20 * 240, 240)) if parsing_score else 0
    content_quality_pct = int(min(content_quality_score / 20 * 240, 240)) if content_quality_score else 0
    section_pct = int(min(section_score / 10 * 240, 240)) if section_score else 0
    impact_pct = int(min(impact_score / 10 * 240, 240)) if impact_score else 0

    return render(request, "result.html", {
        "result": result,
        "ats_score": request.session.get("ats_score", 0),
        "decision": request.session.get("decision", ""),
        "matched_count": request.session.get("matched_count", 0),
        "missing_count": request.session.get("missing_count", 0),
        "jd_count": request.session.get("jd_count", 0),
        "keyword_score": keyword_score,
        "parsing_score": parsing_score,
        "content_quality_score": content_quality_score,
        "section_score": section_score,
        "impact_score": impact_score,
        "keyword_pct": keyword_pct,
        "parsing_pct": parsing_pct,
        "content_quality_pct": content_quality_pct,
        "section_pct": section_pct,
        "impact_pct": impact_pct,
    })


def resume_builder(request):
    return render(request, "resume_builder.html")


def build_resume(request):
    if request.method != "POST":
        return redirect("resume_builder")

    form = ResumeBuilderForm(request.POST)
    if not form.is_valid():
        return render(request, "resume_builder.html", {"form_errors": form.errors})

    details = form.cleaned_data
    prompt = build_resume_prompt(details)

    try:
        client = get_groq_client()
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        generated_resume = clean_ai_output(chat_completion.choices[0].message.content)
        request.session["generated_resume"] = generated_resume
        return redirect("builder_result")
    except Exception as error:
        return render(request, "resume_builder.html", {
            "form_errors": {"resume_builder": [str(error)]}
        })


def builder_result(request):
    generated_resume = request.session.get("generated_resume")
    if not generated_resume:
        return redirect("resume_builder")

    return render(request, "builder_result.html", {
        "generated_resume": generated_resume,
    })
