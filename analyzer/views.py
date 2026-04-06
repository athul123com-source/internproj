from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .forms import ProfileForm, RegisterForm, ResumeUploadForm
from .models import AnalysisRun, UserProfile
from .services import analyze_resume, apply_learning_progress, extract_resume_text


def home(request):
    if request.user.is_authenticated:
        return redirect("upload")
    return redirect("login")


@login_required
def upload_resume(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        resume = form.cleaned_data["resume"]
        role = form.cleaned_data["role"]
        job_description = form.cleaned_data["job_description"]

        try:
            raw_file_bytes = resume.read()
            resume.seek(0)
            extracted_text = extract_resume_text(resume)
            analysis = analyze_resume(
                extracted_text,
                role,
                resume.name,
                job_description=job_description,
                raw_file_bytes=raw_file_bytes,
            )
            run = AnalysisRun.objects.create(
                owner=request.user,
                role=analysis["role"],
                filename=resume.name,
                resume_score=analysis["resume_score"],
                analysis_data=analysis,
            )
            messages.success(request, "Analysis complete.")
            return redirect("detail", run_id=run.id)
        except Exception as error:
            messages.error(request, str(error))

    analysis = None
    recent_queryset = AnalysisRun.objects.filter(owner=request.user)
    recent_runs = recent_queryset[:6]
    latest_run = recent_queryset.first()
    stats = {
        "total_runs": recent_queryset.count(),
        "best_score": recent_queryset.order_by("-resume_score").values_list("resume_score", flat=True).first() or 0,
        "latest_role": latest_run.role if latest_run else "Not analyzed yet",
    }

    return render(
        request,
        "analyzer/home.html",
        {
            "form": form,
            "analysis": analysis,
            "recent_runs": recent_runs,
            "latest_run": latest_run,
            "stats": stats,
        },
    )


@login_required
def history(request):
    runs = AnalysisRun.objects.filter(owner=request.user)
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    min_score = request.GET.get("min_score", "").strip()

    if query:
        runs = runs.filter(Q(filename__icontains=query) | Q(role__icontains=query))
    if role:
        runs = runs.filter(role__iexact=role)
    if min_score.isdigit():
        runs = runs.filter(resume_score__gte=int(min_score))

    role_options = AnalysisRun.objects.filter(owner=request.user).values_list("role", flat=True).distinct()
    title = "Your saved dashboards"
    return render(
        request,
        "analyzer/history.html",
        {
            "runs": runs[:24],
            "page_title": title,
            "filters": {"q": query, "role": role, "min_score": min_score},
            "role_options": role_options,
        },
    )


@login_required
def detail(request, run_id):
    run = get_object_or_404(AnalysisRun, id=run_id)
    if run.owner != request.user:
        raise Http404("This dashboard is not available.")
    analysis = apply_learning_progress(run.analysis_data or {})
    return render(request, "analyzer/detail.html", {"analysis": analysis, "run": run})


@login_required
@require_POST
def toggle_skill_completion(request, run_id):
    run = get_object_or_404(AnalysisRun, id=run_id)
    if run.owner != request.user:
        raise Http404("This dashboard is not available.")

    skill = request.POST.get("skill", "").strip().lower()
    analysis = run.analysis_data or {}
    missing_skills = analysis.get("all_missing_skills") or analysis.get("missing_skills", [])
    if skill not in missing_skills:
        messages.error(request, "That skill is not available for progress tracking on this report.")
        return redirect("detail", run_id=run.id)

    completed_skills = set(analysis.get("completed_skills", []))
    if skill in completed_skills:
        completed_skills.remove(skill)
        messages.success(request, f"Marked {skill} as not completed yet.")
    else:
        completed_skills.add(skill)
        messages.success(request, f"Marked {skill} as completed. Your progress score has been updated.")

    analysis["completed_skills"] = sorted(completed_skills)
    analysis = apply_learning_progress(analysis)
    run.analysis_data = analysis
    run.resume_score = analysis.get("resume_score", run.resume_score)
    run.save(update_fields=["analysis_data", "resume_score"])
    return redirect("detail", run_id=run.id)


@login_required
def export_report(request, run_id):
    run = get_object_or_404(AnalysisRun, id=run_id)
    if run.owner != request.user:
        raise Http404("This dashboard is not available.")

    data = run.analysis_data or {}
    buffer = HttpResponse(content_type="application/pdf")
    buffer["Content-Disposition"] = f'attachment; filename="{run.filename.rsplit(".", 1)[0]}-report.pdf"'

    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    def write_line(text, size=11, gap=18, bold=False):
        nonlocal y
        if y < 60:
            pdf.showPage()
            y = height - 50
        font = "Helvetica-Bold" if bold else "Helvetica"
        pdf.setFont(font, size)
        pdf.drawString(40, y, text[:110])
        y -= gap

    write_line("Resume Insight Studio Report", size=16, gap=26, bold=True)
    write_line(f"Filename: {run.filename}")
    write_line(f"Role: {run.role}")
    write_line(f"Resume Score: {run.resume_score}%")
    if data.get("ai_score") is not None:
        write_line(f"AI Score: {data.get('ai_score', 0)}%")
        write_line(f"Rule-based Score: {data.get('rule_based_resume_score', 0)}%")
        write_line(f"Score Mode: {data.get('score_mode', 'Hybrid AI + Rule-based')}")
    write_line(f"Role Match: {data.get('match_rate', 0)}%")
    write_line(f"ATS Score: {data.get('ats_score', 0)}%")
    write_line(f"Experience Level: {data.get('experience_level', 'Unknown')}")
    write_line(f"Job Description Mode: {'Custom JD used' if data.get('job_description_used') else 'Built-in role profile'}", gap=24)

    write_line("Matched Skills", bold=True)
    for item in data.get("matched_skills", [])[:10]:
        write_line(f"- {item}")

    write_line("Priority Skill Gaps", gap=24, bold=True)
    for item in data.get("prioritized_gaps", [])[:8]:
        write_line(f"- {item['skill']} ({item['priority']})")

    write_line("Recommendations", gap=24, bold=True)
    for item in data.get("recommendations", [])[:6]:
        write_line(f"- {item}")

    if data.get("ai_summary"):
        write_line("AI Review", gap=24, bold=True)
        write_line(data.get("ai_summary", ""))

    write_line("Bullet Improvements", gap=24, bold=True)
    for item in data.get("bullet_improvements", [])[:3]:
        write_line(f"- Before: {item['before']}")
        write_line(f"  After: {item['after']}")

    write_line("Learning Resources", gap=24, bold=True)
    for item in data.get("course_recommendations", [])[:4]:
        write_line(f"- {item['skill']}", bold=True)
        for resource in item.get("resources", [])[:2]:
            write_line(f"  {resource['title']}", gap=14)
            write_line(f"  {resource['url']}", gap=14)

    pdf.save()
    response = buffer
    return response


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Your future analyses will be saved to your dashboard.")
        return redirect("upload")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect("login")


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile_obj)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    recent_runs = AnalysisRun.objects.filter(owner=request.user)[:3]
    return render(
        request,
        "analyzer/profile.html",
        {
            "form": form,
            "profile_obj": profile_obj,
            "recent_runs": recent_runs,
        },
    )
