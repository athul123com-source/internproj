# Resume Insight Studio

Resume Insight Studio is a Django-based resume analysis project inspired by the `AI_Resume_Analyzer_Project.pdf` brief. It evaluates uploaded resumes against a selected role, shows skill gaps, estimates ATS readiness, and generates a practical improvement roadmap inside a modern glassmorphism dashboard.

## Features

- Resume upload support for `PDF`, `DOCX`, and `TXT`
- Optional OCR fallback for scanned/image-based PDFs when `OCR_SPACE_API_KEY` is configured
- Skill extraction and job-role matching
- Missing skill detection and resume scoring
- ATS-focused warnings and strengths
- Learning roadmap for missing skills
- Interview practice questions tailored to the selected role
- Responsive glass-card UI with a matte 3D look
- Django model for storing analysis history

## Tech

- Python
- Django
- PyPDF2
- python-docx
- HTML, CSS, and JavaScript

## Run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Share Online

`localhost` is only visible on your own machine. To share the project with others, deploy it to a hosting platform.

This project now includes:

- `Procfile` for a production start command
- `build.sh` for migrate + collectstatic
- `gunicorn` for serving Django
- `whitenoise` for static files
- environment-variable-based Django settings

Suggested environment variables:

```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=replace-this-with-a-real-secret
DJANGO_ALLOWED_HOSTS=your-app-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app-domain.com
OCR_SPACE_API_KEY=your-ocr-space-api-key
```

Optional AI-ready variables for future integration:

```bash
AI_PROVIDER=disabled
AI_MODEL=gpt-5-mini
AI_PDF_MODEL=gpt-5
AI_PDF_REVIEW_ENABLED=False
AI_SCORING_ENABLED=False
AI_PLANNING_ENABLED=False
OPENAI_API_KEY=
```

The project can now run in hybrid mode when the AI flags are enabled. A good starter setup is:

```bash
AI_PROVIDER=openai
AI_MODEL=gpt-5-mini
AI_PDF_MODEL=gpt-5
AI_PDF_REVIEW_ENABLED=True
AI_SCORING_ENABLED=True
AI_PLANNING_ENABLED=True
OPENAI_API_KEY=your-openai-key
```

If the AI request fails or is not configured, the app falls back to the existing rule-based score and roadmap.

For a lower-cost/free-compatible option, you can switch to Groq with:

```bash
AI_PROVIDER=groq
AI_MODEL=llama-3.3-70b-versatile
AI_PDF_REVIEW_ENABLED=False
AI_SCORING_ENABLED=True
AI_PLANNING_ENABLED=True
GROQ_API_KEY=your-groq-api-key
```

The dashboard also supports skill completion tracking. When a learner marks a missing skill as completed, the report updates the projected role match and resume score for that saved dashboard.

See [SHARE_DEPLOYMENT.txt](/d:/Intern/SHARE_DEPLOYMENT.txt) for a simple deployment guide.

## Notes

- PDF extraction works best for text-based PDFs.
- The current project uses SQLite by default and is ready to be switched to PostgreSQL later if needed.
