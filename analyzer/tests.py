from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from docx import Document

from .models import AnalysisRun, UserProfile
from .services import analyze_resume, extract_skills


class ServiceTests(TestCase):
    def test_extract_skills_handles_plain_aliases(self):
        text = "Built responsive interfaces with HTML, CSS, JavaScript, TypeScript, React, Git, and Jest."
        skills = extract_skills(text)
        self.assertIn("html", skills)
        self.assertIn("css", skills)
        self.assertIn("typescript", skills)
        self.assertIn("react", skills)
        self.assertIn("testing", skills)

    def test_analyze_resume_includes_bullet_improvements(self):
        text = "Built React dashboards with TypeScript and Git. Improved load time by 30%."
        analysis = analyze_resume(text, "frontend-developer", "resume.txt")
        self.assertTrue(analysis["bullet_improvements"])
        self.assertIn("after", analysis["bullet_improvements"][0])


class ViewFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="athul", email="athul@example.com", password="Password123")

    def login(self):
        self.client.login(username="athul", password="Password123")

    def build_docx_upload(self, text):
        buffer = BytesIO()
        document = Document()
        document.add_paragraph(text)
        document.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            "resume.docx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "another-user",
                "email": "ATHUL@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        self.assertContains(response, "An account with this email already exists.")

    def test_profile_page_creates_and_updates_profile(self):
        self.login()
        response = self.client.post(
            reverse("profile"),
            {
                "full_name": "Athul Pradeep",
                "phone": "9999999999",
                "college": "ABC College",
                "degree": "B.Tech",
                "graduation_year": 2027,
                "target_role": "Frontend Developer",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.full_name, "Athul Pradeep")
        self.assertContains(response, "Profile updated successfully.")

    def test_upload_creates_analysis_and_history_filters_work(self):
        self.login()
        resume = self.build_docx_upload(
            "HTML CSS JavaScript TypeScript React Redux Webpack Git Jest responsive design REST API Figma"
        )
        response = self.client.post(
            reverse("upload"),
            {
                "role": "frontend-developer",
                "job_description": "Frontend role requiring React, TypeScript, testing, and Git.",
                "resume": resume,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        run = AnalysisRun.objects.get(owner=self.user)
        self.assertContains(response, "Bullet improvement suggestions")
        self.assertGreater(run.resume_score, 0)

        history_response = self.client.get(reverse("history"), {"role": "Frontend Developer", "min_score": "50"})
        self.assertContains(history_response, run.filename)
