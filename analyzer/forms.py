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
