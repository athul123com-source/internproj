import re
import zipfile
import os
from io import BytesIO

from PyPDF2 import PdfReader
from docx import Document
import requests


JOB_ROLES = {
    "frontend-developer": {
        "title": "Frontend Developer",
        "summary": "Builds interactive, accessible, high-performance user interfaces for web products.",
        "skills": [
            "html",
            "css",
            "javascript",
            "typescript",
            "react",
            "redux",
            "tailwind",
            "vite",
            "webpack",
            "responsive design",
            "accessibility",
            "rest api",
            "git",
            "testing",
            "figma",
        ],
        "tools": ["React", "TypeScript", "Figma", "Jest", "Vite"],
        "interview_themes": ["component design", "state management", "browser performance", "accessibility"],
    },
    "backend-developer": {
        "title": "Backend Developer",
        "summary": "Designs APIs, services, data models, and reliable server-side systems.",
        "skills": [
            "python",
            "django",
            "node.js",
            "express",
            "sql",
            "postgresql",
            "mongodb",
            "rest api",
            "authentication",
            "docker",
            "git",
            "testing",
            "redis",
            "microservices",
            "api design",
        ],
        "tools": ["Django", "Express", "PostgreSQL", "Docker", "Redis"],
        "interview_themes": ["api design", "database modeling", "scalability", "security"],
    },
    "data-scientist": {
        "title": "Data Scientist",
        "summary": "Uses data, statistics, and machine learning to generate predictive insights.",
        "skills": [
            "python",
            "pandas",
            "numpy",
            "sql",
            "machine learning",
            "statistics",
            "data visualization",
            "scikit-learn",
            "feature engineering",
            "model evaluation",
            "power bi",
            "tableau",
            "communication",
            "deep learning",
            "nlp",
        ],
        "tools": ["Python", "Pandas", "scikit-learn", "Jupyter", "Tableau"],
        "interview_themes": ["feature engineering", "model metrics", "experimentation", "storytelling"],
    },
    "ml-engineer": {
        "title": "ML Engineer",
        "summary": "Operationalizes machine learning systems and deploys models into production.",
        "skills": [
            "python",
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "mlops",
            "docker",
            "kubernetes",
            "feature engineering",
            "model deployment",
            "sql",
            "fastapi",
            "api design",
            "aws",
            "git",
        ],
        "tools": ["PyTorch", "TensorFlow", "FastAPI", "Docker", "AWS"],
        "interview_themes": ["deployment", "monitoring", "data pipelines", "model tradeoffs"],
    },
    "ui-ux-designer": {
        "title": "UI/UX Designer",
        "summary": "Designs usable, engaging interfaces with strong research and product thinking.",
        "skills": [
            "figma",
            "wireframing",
            "prototyping",
            "user research",
            "design systems",
            "accessibility",
            "visual design",
            "interaction design",
            "usability testing",
            "information architecture",
            "storytelling",
            "responsive design",
            "collaboration",
            "design thinking",
            "journey mapping",
        ],
        "tools": ["Figma", "Framer", "Miro", "Maze", "Adobe XD"],
        "interview_themes": ["design process", "research synthesis", "visual hierarchy", "hand-off quality"],
    },
}

SKILL_SYNONYMS = {
    "js": "javascript",
    "ts": "typescript",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "node-js": "node.js",
    "expressjs": "express",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "nextjs": "next.js",
    "next.js": "next.js",
    "tailwindcss": "tailwind",
    "tailwind-css": "tailwind",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "postgre": "postgresql",
    "postgressql": "postgresql",
    "ml": "machine learning",
    "machinelearning": "machine learning",
    "deeplearning": "deep learning",
    "scikitlearn": "scikit-learn",
    "powerbi": "power bi",
    "scikitlearn": "scikit-learn",
    "restful": "rest api",
    "restapis": "rest api",
    "restapi": "rest api",
    "api": "api design",
    "apis": "api design",
    "uiux": "interaction design",
    "wireframes": "wireframing",
    "prototypes": "prototyping",
    "figjam": "figma",
    "nlp": "nlp",
    "aws": "aws",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
}

SKILL_ALIASES = {
    "html": ["html5"],
    "css": ["css3"],
    "javascript": ["javascript", "java script", "js", "ecmascript"],
    "typescript": ["typescript", "type script", "ts"],
    "react": ["react", "reactjs", "react.js"],
    "redux": ["redux", "redux toolkit"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "vite": ["vite"],
    "webpack": ["webpack"],
    "responsive design": ["responsive design", "responsive ui", "mobile-first", "mobile first"],
    "accessibility": ["accessibility", "a11y", "wcag", "accessible design"],
    "rest api": ["rest api", "restful api", "restful apis", "rest services"],
    "git": ["git", "github", "gitlab"],
    "testing": ["testing", "unit testing", "integration testing", "pytest", "jest"],
    "figma": ["figma", "figjam"],
    "python": ["python"],
    "django": ["django"],
    "node.js": ["node.js", "nodejs", "node js"],
    "express": ["express", "expressjs", "express js"],
    "sql": ["sql", "mysql", "sqlite"],
    "postgresql": ["postgresql", "postgres", "postgre sql"],
    "mongodb": ["mongodb", "mongo db", "mongo"],
    "authentication": ["authentication", "auth", "oauth", "jwt"],
    "docker": ["docker", "containerization", "containers"],
    "redis": ["redis"],
    "microservices": ["microservices", "micro services"],
    "api design": ["api design", "api architecture", "apis"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "machine learning": ["machine learning", "ml"],
    "statistics": ["statistics", "statistical analysis"],
    "data visualization": ["data visualization", "data visualisation", "visualization", "visualisation"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "feature engineering": ["feature engineering"],
    "model evaluation": ["model evaluation", "model validation"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "communication": ["communication", "stakeholder communication"],
    "deep learning": ["deep learning", "deep neural networks"],
    "nlp": ["nlp", "natural language processing"],
    "tensorflow": ["tensorflow", "tensor flow"],
    "pytorch": ["pytorch", "py torch"],
    "mlops": ["mlops", "ml ops", "machine learning operations"],
    "kubernetes": ["kubernetes", "k8s"],
    "model deployment": ["model deployment", "deployment", "serving"],
    "fastapi": ["fastapi", "fast api"],
    "aws": ["aws", "amazon web services"],
    "wireframing": ["wireframing", "wireframes", "wireframe"],
    "prototyping": ["prototyping", "prototype", "prototypes"],
    "user research": ["user research", "ux research"],
    "design systems": ["design systems", "design system"],
    "visual design": ["visual design", "ui design"],
    "interaction design": ["interaction design", "ui/ux", "ui ux", "ux"],
    "usability testing": ["usability testing", "usability tests"],
    "information architecture": ["information architecture", "ia"],
    "storytelling": ["storytelling", "presentation storytelling"],
    "collaboration": ["collaboration", "cross-functional collaboration"],
    "design thinking": ["design thinking"],
    "journey mapping": ["journey mapping", "customer journey mapping"],
}

LEARNING_RESOURCES = {
    "react": ["React official docs", "Frontend Mentor React challenges"],
    "typescript": ["TypeScript handbook", "Type Challenges"],
    "django": ["Django official tutorial", "Django REST tutorial"],
    "postgresql": ["PostgreSQL tutorial", "SQLBolt practice"],
    "docker": ["Docker getting started", "Play with Docker labs"],
    "machine learning": ["Google ML Crash Course", "Kaggle Learn"],
    "scikit-learn": ["scikit-learn user guide", "Hands-On ML exercises"],
    "tensorflow": ["TensorFlow tutorials", "TensorFlow developer guides"],
    "pytorch": ["PyTorch tutorials", "Learn PyTorch"],
    "fastapi": ["FastAPI docs", "FastAPI full-stack examples"],
    "figma": ["Figma beginner course", "Figma community files"],
    "user research": ["Nielsen Norman research methods", "UX research field guide"],
}

SECTION_PATTERNS = {
    "summary": ["summary", "profile", "objective", "about"],
    "skills": ["skills", "technical skills", "core skills", "tech stack"],
    "projects": ["projects", "project experience", "personal projects"],
    "experience": ["experience", "work experience", "employment", "internship"],
    "education": ["education", "academic background", "qualification"],
}


def extract_resume_text(uploaded_file):
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()

    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(raw))
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
        if not has_meaningful_text(text):
            ocr_text = extract_text_with_ocr(raw, uploaded_file.name)
            if has_meaningful_text(ocr_text):
                return ocr_text
            if is_likely_scanned_pdf(raw):
                raise ValueError(
                    "This PDF looks like an image/scanned resume, and OCR is not configured or could not extract enough text. "
                    "Please upload a text-based PDF, DOCX, or TXT file."
                )
            raise ValueError(
                "Text could not be extracted reliably from this PDF, and OCR could not recover enough text either. "
                "Please try a DOCX or TXT file."
            )
        return text

    if name.endswith(".docx"):
        try:
            document = Document(BytesIO(raw))
            return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()).strip()
        except Exception:
            return extract_docx_text_fallback(raw)

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def normalize_resume_text(text):
    normalized = text.lower()
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"(?<=[a-z])/(?=[a-z])", " ", normalized)
    normalized = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", normalized)
    normalized = re.sub(r"(?<=[a-z])\.(?=[a-z])", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def build_loose_skill_pattern(variant):
    cleaned = variant.lower().strip()
    parts = re.split(r"[\s./+-]+", cleaned)
    token_patterns = []

    for part in parts:
        alnum = re.sub(r"[^a-z0-9]", "", part)
        if not alnum:
            continue
        token_patterns.append(r"\s*".join(re.escape(char) for char in alnum))

    if not token_patterns:
        return None

    joined = r"[\s./+-]*".join(token_patterns)
    return rf"(^|[^a-z0-9]){joined}([^a-z0-9]|$)"


def has_meaningful_text(text):
    cleaned = re.sub(r"\s+", " ", text).strip()
    return len(cleaned) >= 40 and len(re.findall(r"[a-zA-Z]{2,}", cleaned)) >= 8


def is_likely_scanned_pdf(raw):
    pdf_text = raw.decode("latin1", errors="ignore")
    has_image_object = "/Subtype /Image" in pdf_text or "/XObject" in pdf_text
    has_text_font = "/Font" in pdf_text or "BT" in pdf_text
    return has_image_object and not has_meaningful_text(pdf_text) and not has_text_font


def extract_text_with_ocr(raw, filename):
    api_key = os.getenv("OCR_SPACE_API_KEY", "").strip()
    if not api_key:
        return ""

    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            data={
                "apikey": api_key,
                "language": "eng",
                "isOverlayRequired": False,
                "detectOrientation": True,
                "scale": True,
                "OCREngine": 2,
            },
            files={"file": (filename, raw)},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return ""

    parsed_results = payload.get("ParsedResults") or []
    texts = [item.get("ParsedText", "") for item in parsed_results if item.get("ParsedText")]
    return "\n".join(texts).strip()


def extract_docx_text_fallback(raw):
    with zipfile.ZipFile(BytesIO(raw)) as docx_zip:
        xml = docx_zip.read("word/document.xml").decode("utf-8", errors="ignore")
    text = re.sub(r"<w:p[^>]*>", "\n", xml)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def analyze_resume(text, role_key, filename, job_description=""):
    role = JOB_ROLES[role_key]
    extracted_skills = extract_skills(text)
    jd_analysis = analyze_job_description(job_description, role)
    target_skills = jd_analysis["target_skills"] or role["skills"]
    matched_skills = [skill for skill in target_skills if skill in extracted_skills]
    missing_skills = [skill for skill in target_skills if skill not in extracted_skills]
    match_rate = round((len(matched_skills) / len(target_skills)) * 100) if target_skills else 0
    ats = compute_ats_signals(text)
    resume_score = round(match_rate * 0.6 + ats["score"] * 0.4)
    experience_level = detect_experience_level(text)
    highlights = extract_highlights(text)
    section_scores = compute_section_scores(text, extracted_skills)
    prioritized_gaps = prioritize_missing_skills(missing_skills, jd_analysis["jd_skills"])
    course_recommendations = build_course_recommendations(missing_skills)

    return {
        "filename": filename,
        "role": role["title"],
        "role_summary": role["summary"],
        "job_description_used": bool(job_description.strip()),
        "job_description_summary": jd_analysis["summary"],
        "resume_score": resume_score,
        "match_rate": match_rate,
        "ats_score": ats["score"],
        "experience_level": experience_level,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "prioritized_gaps": prioritized_gaps,
        "section_scores": section_scores,
        "course_recommendations": course_recommendations,
        "strengths": [
            f"{len(matched_skills)} relevant skills match the target role.",
            *ats["strengths"][:2],
            "Resume includes readable content blocks that can be sharpened into stronger bullets." if highlights else "",
        ],
        "warnings": ats["warnings"],
        "recommendations": build_recommendations(missing_skills),
        "learning_roadmap": build_learning_roadmap(missing_skills),
        "interview_questions": build_interview_questions(role, matched_skills, missing_skills),
        "highlights": highlights,
        "suggested_tools": role["tools"],
    }


def tokenize_text(text):
    cleaned = re.sub(r"[^\w.+#/-]+", " ", text.lower())
    return [token for token in cleaned.split() if token]


def normalize_skill(token):
    normalized = re.sub(r"[^a-z0-9]", "", token.lower())
    return SKILL_SYNONYMS.get(normalized, token.lower())


def extract_skills(text):
    text_lower = normalize_resume_text(text)
    raw_lower = text.lower()
    known_skills = {skill for role in JOB_ROLES.values() for skill in role["skills"]}
    found = set()

    for skill in known_skills:
        variants = SKILL_ALIASES.get(skill, [skill])
        for variant in variants:
            pattern = rf"(^|[^a-z0-9]){re.escape(variant)}([^a-z0-9]|$)"
            loose_pattern = build_loose_skill_pattern(variant)
            if re.search(pattern, text_lower) or (loose_pattern and re.search(loose_pattern, raw_lower)):
                found.add(skill)
                break

    for token in tokenize_text(text):
        normalized = normalize_skill(token)
        if normalized in known_skills:
            found.add(normalized)

    return sorted(found)


def analyze_job_description(job_description, role):
    if not job_description or not job_description.strip():
        return {
            "summary": "Using the built-in role profile because no custom job description was provided.",
            "jd_skills": [],
            "target_skills": role["skills"],
        }

    jd_skills = extract_skills(job_description)
    target_skills = []
    for skill in role["skills"]:
        if skill in jd_skills or not jd_skills:
            target_skills.append(skill)
    for skill in jd_skills:
        if skill not in target_skills:
            target_skills.append(skill)

    return {
        "summary": f"Compared against a custom job description with {len(jd_skills)} detected relevant skills.",
        "jd_skills": jd_skills,
        "target_skills": target_skills or role["skills"],
    }


def extract_section_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = {name: [] for name in SECTION_PATTERNS}
    current_section = None

    for line in lines:
        matched_section = None
        line_lower = line.lower()
        for section, markers in SECTION_PATTERNS.items():
            if any(line_lower == marker or line_lower.startswith(f"{marker}:") for marker in markers):
                matched_section = section
                break
        if matched_section:
            current_section = matched_section
            continue
        if current_section:
            sections[current_section].append(line)

    return {name: "\n".join(content).strip() for name, content in sections.items()}


def compute_section_scores(text, extracted_skills):
    sections = extract_section_text(text)
    score_map = []
    for section, content in sections.items():
        if not content:
            score = 18 if section != "summary" else 10
        else:
            section_skills = extract_skills(content)
            length_bonus = min(len(content.split()), 80) // 4
            score = min(100, 25 + len(section_skills) * 12 + length_bonus)
        score_map.append({"section": section.title(), "score": score})
    return score_map


def prioritize_missing_skills(missing_skills, jd_skills):
    priorities = []
    for index, skill in enumerate(missing_skills):
        if skill in jd_skills or index < 2:
            label = "High"
        elif index < 5:
            label = "Medium"
        else:
            label = "Low"
        priorities.append({"skill": skill, "priority": label})
    return priorities


def build_course_recommendations(missing_skills):
    items = []
    for skill in missing_skills[:5]:
        resources = LEARNING_RESOURCES.get(skill, [f"{skill.title()} roadmap", f"{skill.title()} practical tutorial"])
        items.append({"skill": skill, "resources": resources})
    return items


def compute_ats_signals(text):
    lower = text.lower()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    bullet_count = len(re.findall(r"(?:\u2022|-)\s", text))
    quantified_achievements = len(re.findall(r"\b\d+%|\b\d+\+|\$\d+", text))
    email_present = bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I))
    phone_present = bool(re.search(r"(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}", text))
    linkedin_present = "linkedin.com" in lower
    github_present = "github.com" in lower
    section_keywords = ["summary", "experience", "education", "skills", "projects"]
    present_sections = [section for section in section_keywords if section in lower]
    warnings = []

    if not email_present:
        warnings.append("Add a professional email address.")
    if not phone_present:
        warnings.append("Include a contact phone number.")
    if not linkedin_present:
        warnings.append("Add a LinkedIn profile for recruiter trust.")
    if bullet_count < 4:
        warnings.append("Use more bullet points to improve scanability.")
    if quantified_achievements < 2:
        warnings.append("Add measurable outcomes like percentages, counts, or revenue impact.")
    if len(present_sections) < 4:
        warnings.append("Structure the resume with clear ATS-friendly sections.")
    if any(len(line) > 140 for line in lines):
        warnings.append("Shorten long lines so key details are not buried.")

    score = max(
        38,
        min(
            96,
            48
            + len(present_sections) * 7
            + min(bullet_count, 10) * 2
            + quantified_achievements * 5
            + (6 if email_present else 0)
            + (4 if phone_present else 0)
            + (4 if linkedin_present else 0)
            + (3 if github_present else 0)
            - len(warnings) * 4,
        ),
    )

    strengths = []
    if email_present:
        strengths.append("Contains an email address.")
    if phone_present:
        strengths.append("Contains a phone number.")
    if linkedin_present:
        strengths.append("Includes LinkedIn profile.")
    if quantified_achievements >= 2:
        strengths.append("Shows measurable impact.")
    if len(present_sections) >= 4:
        strengths.append("Uses standard ATS-friendly sections.")

    return {"score": score, "warnings": warnings, "strengths": strengths}


def detect_experience_level(text):
    lower = text.lower()
    years = [int(match.group(1)) for match in re.finditer(r"(\d+)\+?\s+years?", lower)]
    max_years = max(years) if years else 0
    if max_years >= 5 or re.search(r"senior|lead|architect|principal", lower):
        return "Advanced"
    if max_years >= 2 or re.search(r"internship|associate|junior", lower):
        return "Intermediate"
    return "Early career"


def extract_highlights(text):
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if 25 <= len(line) <= 150][:4]


def build_recommendations(missing_skills):
    recommendations = [
        "Rewrite at least two bullets using action verbs plus measurable outcomes.",
        "Tailor the summary section to the chosen role instead of keeping it generic.",
    ]
    if missing_skills:
        recommendations.insert(0, f"Prioritize {missing_skills[0]} because it appears in the target role profile.")
    if len(missing_skills) > 1:
        recommendations.insert(1, f"Add one project bullet demonstrating {missing_skills[1]}.")
    return recommendations


def build_learning_roadmap(missing_skills):
    roadmap = []
    for index, skill in enumerate(missing_skills[:6], start=1):
        roadmap.append(
            {
                "week": f"Week {index}",
                "focus": skill,
                "mission": f"Build or document one practical artifact that proves {skill} competence.",
                "output": f"Portfolio-ready proof for {skill}",
            }
        )
    return roadmap


def build_interview_questions(role, matched_skills, missing_skills):
    return [
        f"Walk through a project where you used {matched_skills[0] if matched_skills else role['skills'][0]} to solve a real problem.",
        f"How would you prioritize learning {missing_skills[0] if missing_skills else role['skills'][1]} while still delivering team value?",
        f"Which tradeoffs matter most in {role['interview_themes'][0]} for a {role['title']} role?",
        "Describe how you collaborate with stakeholders when requirements are ambiguous.",
        "What metric would you track to prove your work improved the product or system?",
    ]
