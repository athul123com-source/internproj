from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, ResumeUploadForm
from .models import AnalysisRun
from .services import analyze_resume, extract_resume_text


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

        try:
            extracted_text = extract_resume_text(resume)
            analysis = analyze_resume(extracted_text, role, resume.name)
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
    title = "Your saved dashboards"
    return render(request, "analyzer/history.html", {"runs": runs[:24], "page_title": title})


@login_required
def detail(request, run_id):
    run = get_object_or_404(AnalysisRun, id=run_id)
    if run.owner != request.user:
        raise Http404("This dashboard is not available.")
    analysis = run.analysis_data or None
    return render(request, "analyzer/detail.html", {"analysis": analysis, "run": run})


@login_required
def export_report(request, run_id):
    run = get_object_or_404(AnalysisRun, id=run_id)
    if run.owner != request.user:
        raise Http404("This dashboard is not available.")

    data = run.analysis_data or {}
    lines = [
        "Resume Analyzer Studio Report",
        f"Filename: {run.filename}",
        f"Role: {run.role}",
        f"Resume Score: {run.resume_score}%",
        "",
        f"Role Match: {data.get('match_rate', 0)}%",
        f"ATS Score: {data.get('ats_score', 0)}%",
        f"Experience Level: {data.get('experience_level', 'Unknown')}",
        "",
        "Matched Skills:",
        *[f"- {item}" for item in data.get("matched_skills", [])],
        "",
        "Missing Skills:",
        *[f"- {item}" for item in data.get("missing_skills", [])],
        "",
        "Recommendations:",
        *[f"- {item}" for item in data.get("recommendations", [])],
        "",
        "Interview Questions:",
        *[f"- {item}" for item in data.get("interview_questions", [])],
    ]
    response = HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{run.filename.rsplit(".", 1)[0]}-report.txt"'
    return response


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Your future analyses will be saved to your dashboard.")
        return redirect("upload")
    return render(request, "registration/register.html", {"form": form})
