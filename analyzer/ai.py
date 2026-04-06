import base64
import json
import os
from textwrap import dedent


def _env_flag(name):
    return os.getenv(name, "False").strip().lower() in {"1", "true", "yes", "on"}


def get_ai_runtime_config():
    provider = os.getenv("AI_PROVIDER", "disabled").strip().lower() or "disabled"
    model = os.getenv("AI_MODEL", "").strip() or ("llama-3.3-70b-versatile" if provider == "groq" else "gpt-5-mini")
    pdf_model = os.getenv("AI_PDF_MODEL", "").strip() or "gpt-5"
    api_key_present = bool(
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("GROQ_API_KEY", "").strip()
        or os.getenv("AI_API_KEY", "").strip()
    )
    return {
        "provider": provider,
        "model": model,
        "pdf_model": pdf_model,
        "pdf_review_enabled": _env_flag("AI_PDF_REVIEW_ENABLED"),
        "scoring_enabled": _env_flag("AI_SCORING_ENABLED"),
        "planning_enabled": _env_flag("AI_PLANNING_ENABLED"),
        "api_key_present": api_key_present,
    }


def build_ai_readiness_snapshot(
    *,
    filename,
    role_title,
    role_summary,
    resume_text,
    job_description,
    matched_skills,
    missing_skills,
    resume_score,
    match_rate,
    ats_score,
    roadmap,
):
    config = get_ai_runtime_config()
    enabled_capabilities = [
        label
        for label, enabled in (
            ("pdf_review", config["pdf_review_enabled"]),
            ("scoring", config["scoring_enabled"]),
            ("planning", config["planning_enabled"]),
        )
        if enabled
    ]
    readiness_status = "disabled"
    if enabled_capabilities:
        readiness_status = "waiting_for_provider"
        if config["provider"] != "disabled" and config["api_key_present"]:
            readiness_status = "ready_to_connect"

    payload_preview = {
        "filename": filename,
        "role": role_title,
        "resume_excerpt": resume_text[:1200].strip(),
        "job_description_excerpt": job_description[:800].strip(),
        "current_score": resume_score,
        "match_rate": match_rate,
        "ats_score": ats_score,
        "matched_skills": matched_skills[:12],
        "missing_skills": missing_skills[:12],
    }

    scoring_prompt = dedent(
        f"""
        Review the extracted resume text for the role "{role_title}".
        Return a strict JSON object with:
        - ai_score: integer from 0 to 100
        - rationale: short paragraph
        - strengths: array of strings
        - gaps: array of strings
        - recommendations: array of strings
        Use the current rule-based metrics only as supporting context, not as the final answer.
        Current metrics:
        - Resume score: {resume_score}
        - Role match: {match_rate}
        - ATS score: {ats_score}
        Role summary: {role_summary}
        Matched skills: {", ".join(matched_skills) or "None"}
        Missing skills: {", ".join(missing_skills) or "None"}
        """
    ).strip()

    planning_prompt = dedent(
        f"""
        Create a 4 to 6 week learning roadmap for a candidate targeting "{role_title}".
        The roadmap should be based on these missing skills:
        {", ".join(missing_skills) or "No missing skills provided"}.
        Return JSON with:
        - roadmap: array of objects with week, focus, mission, output
        - explanation: short summary
        Keep each mission concrete and portfolio-oriented.
        Existing roadmap for reference:
        {roadmap}
        """
    ).strip()

    next_steps = []
    if not enabled_capabilities:
        next_steps.append("Set one or more AI_* feature flags to True when you want to activate AI scoring or planning.")
    if config["provider"] == "disabled":
        next_steps.append("Choose an AI provider later by setting AI_PROVIDER, such as openai or local.")
    if not config["api_key_present"]:
        next_steps.append("Add OPENAI_API_KEY or AI_API_KEY only when you are ready to connect a real model.")

    return {
        "active": False,
        "status": readiness_status,
        "provider": config["provider"],
        "model": config["model"],
        "supports": {
            "pdf_review": config["pdf_review_enabled"],
            "scoring": config["scoring_enabled"],
            "planning": config["planning_enabled"],
        },
        "payload_preview": payload_preview,
        "prompt_preview": {
            "scoring": scoring_prompt,
            "planning": planning_prompt,
        },
        "prepared_outputs": {
            "ai_score": None,
            "ai_summary": "",
            "ai_learning_roadmap": [],
        },
        "next_steps": next_steps,
    }


def _resume_analysis_schema():
    return {
        "name": "resume_ai_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "ai_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "summary": {"type": "string"},
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5,
                },
                "gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5,
                },
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 6,
                },
                "roadmap": {
                    "type": "array",
                    "maxItems": 6,
                    "items": {
                        "type": "object",
                        "properties": {
                            "week": {"type": "string"},
                            "focus": {"type": "string"},
                            "mission": {"type": "string"},
                            "output": {"type": "string"},
                        },
                        "required": ["week", "focus", "mission", "output"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["ai_score", "summary", "strengths", "gaps", "recommendations", "roadmap"],
            "additionalProperties": False,
        },
    }


def _build_system_prompt():
    return dedent(
        """
        You are an expert resume reviewer.
        Evaluate the candidate for the requested role using professional hiring judgment.
        Be realistic and specific.
        Scoring rules:
        - 0 to 39: weak alignment
        - 40 to 59: partial alignment
        - 60 to 79: solid readiness with clear gaps
        - 80 to 100: strong readiness
        Roadmap rules:
        - make each week concrete
        - keep tasks portfolio-oriented
        - mention what to build or document
        - avoid vague filler
        """
    ).strip()


def _build_user_prompt(
    *,
    role_title,
    role_summary,
    job_description,
    extracted_text,
    filename,
    matched_skills,
    missing_skills,
    rule_score,
    match_rate,
    ats_score,
):
    return dedent(
        f"""
        Analyze this resume for the role: {role_title}
        Role summary: {role_summary}
        Filename: {filename}
        Rule-based resume score: {rule_score}
        Rule-based role match: {match_rate}
        Rule-based ATS score: {ats_score}
        Detected matched skills: {", ".join(matched_skills) or "None"}
        Detected missing skills: {", ".join(missing_skills) or "None"}

        Job description:
        {job_description.strip() or "No custom job description was provided."}

        Extracted resume text:
        {extracted_text[:12000]}

        Return a strict JSON object only.
        """
    ).strip()


def generate_ai_resume_insights(
    *,
    filename,
    role_title,
    role_summary,
    extracted_text,
    job_description,
    matched_skills,
    missing_skills,
    rule_score,
    match_rate,
    ats_score,
    raw_file_bytes=None,
):
    config = get_ai_runtime_config()
    result = {
        "active": False,
        "status": "disabled",
        "provider": config["provider"],
        "model": config["model"],
        "ai_score": None,
        "summary": "",
        "strengths": [],
        "gaps": [],
        "recommendations": [],
        "roadmap": [],
        "error": "",
    }

    if config["provider"] not in {"openai", "groq"}:
        result["status"] = "provider_not_enabled"
        return result
    if not config["api_key_present"]:
        result["status"] = "missing_api_key"
        return result
    if not (config["scoring_enabled"] or config["planning_enabled"] or config["pdf_review_enabled"]):
        result["status"] = "flags_disabled"
        return result

    try:
        from openai import OpenAI
    except ImportError:
        result["status"] = "sdk_missing"
        result["error"] = "OpenAI SDK is not installed on this runtime."
        return result

    user_prompt = _build_user_prompt(
        role_title=role_title,
        role_summary=role_summary,
        job_description=job_description,
        extracted_text=extracted_text,
        filename=filename,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        rule_score=rule_score,
        match_rate=match_rate,
        ats_score=ats_score,
    )

    client_kwargs = {}
    if config["provider"] == "groq":
        client_kwargs = {
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY", "").strip() or os.getenv("AI_API_KEY", "").strip(),
        }
    client = OpenAI(**client_kwargs)

    try:
        if config["provider"] == "groq":
            model = config["model"]
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _build_system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            parsed = json.loads(completion.choices[0].message.content)
        else:
            model = config["pdf_model"] if config["pdf_review_enabled"] and filename.lower().endswith(".pdf") and raw_file_bytes else config["model"]
            user_content = [
                {
                    "type": "input_text",
                    "text": user_prompt,
                }
            ]
            if config["pdf_review_enabled"] and filename.lower().endswith(".pdf") and raw_file_bytes:
                encoded_pdf = base64.b64encode(raw_file_bytes).decode("utf-8")
                user_content.insert(
                    0,
                    {
                        "type": "input_file",
                        "filename": filename,
                        "file_data": f"data:application/pdf;base64,{encoded_pdf}",
                    },
                )
            response = client.responses.create(
                model=model,
                input=[
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": _build_system_prompt()}],
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        **_resume_analysis_schema(),
                    }
                },
            )
            parsed = json.loads(response.output_text)
    except Exception as error:
        result["status"] = "request_failed"
        result["error"] = str(error)
        return result

    result.update(
        {
            "active": True,
            "status": "active",
            "model": model,
            "ai_score": parsed.get("ai_score"),
            "summary": parsed.get("summary", "").strip(),
            "strengths": parsed.get("strengths", []),
            "gaps": parsed.get("gaps", []),
            "recommendations": parsed.get("recommendations", []),
            "roadmap": parsed.get("roadmap", []),
        }
    )
    return result
