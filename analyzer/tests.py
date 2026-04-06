from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from docx import Document

from .models import AnalysisRun, UserProfile
from .services import analyze_resume, apply_learning_progress, extract_skills


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

    def test_learning_roadmap_is_skill_specific(self):
        analysis = analyze_resume("React Git testing", "frontend-developer", "resume.txt")
        roadmap = analysis["learning_roadmap"]
        self.assertTrue(any("TypeScript" in item["output"] or "TypeScript" in item["mission"] for item in roadmap))
        self.assertTrue(any("Redux Toolkit" in item["output"] or "Redux Toolkit" in item["mission"] for item in roadmap if item["focus"] == "redux"))

    def test_ai_readiness_defaults_to_disabled_without_configuration(self):
        analysis = analyze_resume("React Git testing", "frontend-developer", "resume.txt")
        self.assertEqual(analysis["ai_readiness"]["status"], "disabled")
        self.assertFalse(analysis["ai_readiness"]["active"])
        self.assertIn("scoring", analysis["ai_readiness"]["prompt_preview"])

    def test_ai_readiness_can_prepare_optional_flags_without_enabling_runtime(self):
        with patch.dict(
            "os.environ",
            {
                "AI_PROVIDER": "openai",
                "AI_MODEL": "gpt-5.4-mini",
                "AI_SCORING_ENABLED": "True",
                "AI_PLANNING_ENABLED": "True",
            },
            clear=False,
        ):
            analysis = analyze_resume("React Git testing", "frontend-developer", "resume.txt")
        self.assertEqual(analysis["ai_readiness"]["status"], "waiting_for_provider")
        self.assertTrue(analysis["ai_readiness"]["supports"]["scoring"])
        self.assertTrue(analysis["ai_readiness"]["supports"]["planning"])

    @patch("analyzer.services.generate_ai_resume_insights")
    def test_ai_result_enables_hybrid_score_and_ai_roadmap(self, mocked_ai):
        mocked_ai.return_value = {
            "active": True,
            "status": "active",
            "provider": "openai",
            "model": "gpt-5-mini",
            "ai_score": 84,
            "summary": "AI sees strong frontend fundamentals with a few notable delivery gaps.",
            "strengths": ["Explains frontend work with good technical depth."],
            "gaps": ["Needs clearer portfolio evidence for TypeScript."],
            "recommendations": ["Ship one typed React project and document the architecture choices."],
            "roadmap": [
                {
                    "week": "Week 1",
                    "focus": "typescript",
                    "mission": "Convert a small React app to TypeScript and remove all type errors.",
                    "output": "A TypeScript React repo with typed props, hooks, and README notes.",
                }
            ],
            "error": "",
        }
        analysis = analyze_resume("React Git testing", "frontend-developer", "resume.txt")
        self.assertEqual(analysis["ai_score"], 84)
        self.assertEqual(analysis["score_mode"], "Hybrid AI + Rule-based")
        self.assertEqual(analysis["learning_roadmap"][0]["focus"], "typescript")
        self.assertIn("portfolio evidence", " ".join(analysis["warnings"]).lower())

    def test_learning_progress_increases_score_when_skill_is_completed(self):
        analysis = analyze_resume("React Git testing", "frontend-developer", "resume.txt")
        base_score = analysis["resume_score"]
        analysis["completed_skills"] = ["html"]
        progressed = apply_learning_progress(analysis)
        self.assertGreater(progressed["resume_score"], base_score)
        self.assertIn("html", progressed["completed_skills"])
        self.assertNotIn("html", progressed["missing_skills"])


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

    def test_register_rejects_passwords_with_spaces(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "space-user",
                "email": "space@example.com",
                "password1": "bad pass 123",
                "password2": "bad pass 123",
            },
        )
        self.assertContains(response, "Password cannot contain spaces.")

    def test_register_rejects_duplicate_username_case_insensitive(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "ATHUL",
                "email": "new@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        self.assertContains(response, "This username is already taken.")

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

    def test_logout_url_redirects_cleanly(self):
        self.login()
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "logged out successfully")

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

    def test_marking_skill_completed_updates_saved_score(self):
        self.login()
        run = AnalysisRun.objects.create(
            owner=self.user,
            role="Frontend Developer",
            filename="resume.txt",
            resume_score=63,
            analysis_data=analyze_resume("React Git testing", "frontend-developer", "resume.txt"),
        )
        response = self.client.post(
            reverse("toggle_skill_completion", args=[run.id]),
            {"skill": "html"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        run.refresh_from_db()
        self.assertIn("html", run.analysis_data["completed_skills"])
        self.assertGreater(run.resume_score, run.analysis_data["base_resume_score"])
