from django import forms


class ResumeAnalysisForm(forms.Form):
    resume = forms.FileField(required=True)
    jobdesc = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}),
        required=True,
        label="Job Description"
    )

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        name = resume.name.lower()

        if not name.endswith(".pdf"):
            raise forms.ValidationError("Please upload a valid PDF resume.")

        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume file must be 5MB or smaller.")

        return resume


class ResumeBuilderForm(forms.Form):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=50, required=True)
    location = forms.CharField(max_length=200, required=False)
    linkedin = forms.URLField(required=False)
    portfolio = forms.URLField(required=False)
    target_role = forms.CharField(max_length=150, required=True)
    career_level = forms.ChoiceField(
        choices=[
            ("Fresher", "Fresher"),
            ("Internship Applicant", "Internship Applicant"),
            ("Entry Level", "Entry Level"),
            ("Experienced", "Experienced"),
            ("Career Switcher", "Career Switcher"),
        ],
        required=True,
    )
    resume_type = forms.ChoiceField(
        choices=[
            ("ATS Friendly Professional Resume", "ATS Friendly Professional Resume"),
            ("Fresher Resume", "Fresher Resume"),
            ("Internship Resume", "Internship Resume"),
            ("Career Change Resume", "Career Change Resume"),
            ("Experienced Professional Resume", "Experienced Professional Resume"),
        ],
        required=True,
    )
    resume_tone = forms.ChoiceField(
        choices=[
            ("Professional and concise", "Professional and concise"),
            ("Fresher friendly", "Fresher friendly"),
            ("Corporate", "Corporate"),
            ("Confident and achievement focused", "Confident and achievement focused"),
        ],
        required=False,
    )
    education = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=True)
    skills = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=True)
    projects = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=False)
    experience = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=False)
    certifications = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)
    achievements = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)
