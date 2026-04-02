from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


ROLE_CHOICES = [
    ("frontend-developer", "Frontend Developer"),
    ("backend-developer", "Backend Developer"),
    ("data-scientist", "Data Scientist"),
    ("ml-engineer", "ML Engineer"),
    ("ui-ux-designer", "UI/UX Designer"),
]


class ResumeUploadForm(forms.Form):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "role-select"}),
    )
    resume = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.docx,.txt"}),
    )

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        extension = resume.name.rsplit(".", 1)[-1].lower() if "." in resume.name else ""
        if extension not in {"pdf", "docx", "txt"}:
            raise forms.ValidationError("Please upload a PDF, DOCX, or TXT resume.")
        if resume.size > 7 * 1024 * 1024:
            raise forms.ValidationError("Please upload a file smaller than 7MB.")
        return resume


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
