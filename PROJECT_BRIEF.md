# Resume Insight Studio

## Complete Project Brief

Resume Insight Studio is a Django-based web application that helps users evaluate how well their resume fits a chosen job role. The platform is designed for students, freshers, and job seekers who want a clearer understanding of whether their resume is aligned with the expectations of a target role such as Frontend Developer, Backend Developer, Data Scientist, ML Engineer, or UI/UX Designer.

The system accepts a resume file, extracts the readable content, detects important skills, compares those skills against the selected role, and then generates a structured dashboard. Instead of only giving a simple score, the application explains strengths, missing skills, ATS issues, recommendations, learning paths, and interview preparation prompts. It also saves every analysis so the user can come back later and continue improving.

## Problem Statement

Many job seekers prepare resumes without knowing whether the content actually matches the role they are applying for. A resume may look visually good but still be weak in important areas such as technical skill coverage, ATS readiness, measurable impact, or role-specific project evidence. This leads to poor resume quality, lower shortlist chances, and confusion about what to improve next.

Resume Insight Studio solves this by turning resume review into a guided evaluation flow. The project not only identifies weaknesses but also provides a practical path to improve them.

## Main Objective

The main objective of the project is to build an intelligent resume analysis platform that can:

- accept resumes in multiple formats
- extract and normalize resume text
- identify role-relevant skills
- compare the resume against a selected job role
- highlight matched and missing skills
- compute readiness scores
- provide actionable recommendations
- generate a weekly learning roadmap
- save reports and allow users to track progress over time

## Tech Stack

- Python
- Django
- HTML
- CSS
- JavaScript
- PyPDF2
- python-docx
- ReportLab
- WhiteNoise
- Neon PostgreSQL for deployed storage
- SQLite for local fallback
- Render for deployment

For AI support, the project is also prepared for hybrid scoring using API-based providers such as OpenAI or Groq. In the current setup, Groq support is included as a free-compatible AI path.

## Working Flow of the Project

1. User opens the web application.
2. User registers or logs in.
3. User can optionally fill in profile details such as name, degree, college, graduation year, and target role.
4. User goes to the upload page.
5. User selects a target job role.
6. User uploads a resume in PDF, DOCX, or TXT format.
7. User can also paste an optional job description for more exact comparison.
8. The system extracts the text from the resume.
9. The extracted text is analyzed using role-based logic and optional AI support if enabled.
10. The system generates a separate dashboard with scores, matched skills, missing skills, ATS review, roadmap, recommendations, and resource links.
11. The analysis is saved in history.
12. The user can revisit saved dashboards, export them, delete them, and track learning progress.

## Resume File Support

The system supports:

- PDF
- DOCX
- TXT

PDF support works best for text-based resumes. DOCX extraction reads both paragraph content and table content, which helps with resumes that store skills in structured layouts. Scanned or image-based PDFs are currently rejected with a clear message instead of being processed unreliably, which keeps the deployed app more stable.

## Authentication and User Management

The project includes:

- login
- registration
- logout
- profile management

Registration has validation for:

- duplicate email addresses
- duplicate usernames
- invalid email format
- passwords containing spaces

The login and registration pages are designed as part of the product experience and not as plain default forms. Each authenticated user has their own saved dashboards and progress tracking.

## Profile Module

The profile page allows the user to save personal and academic context such as:

- full name
- phone number
- college
- degree
- graduation year
- target role

This makes the project more personalized and better suited for demonstration.

## Resume Analysis Engine

This is the core module of the project. After text extraction, the system compares the resume content against the selected role profile. Each role has a predefined skill set and summary that acts as a structured benchmark.

For example, if the selected role is Frontend Developer, the analyzer checks for skills such as:

- HTML
- CSS
- JavaScript
- TypeScript
- React
- Redux
- Tailwind
- Vite
- Webpack
- Responsive Design
- Accessibility
- REST API
- Git
- Testing
- Figma

The system then separates the results into:

- matched skills
- missing skills
- prioritized gaps

## Skill Detection Logic

The skill matching system is not based only on exact keywords. It also supports:

- aliases
- synonyms
- normalized tokens
- fragmented PDF text handling
- compressed text matching

This is important because PDFs often extract text in broken or fragmented ways. For example, a word like TypeScript may appear as T ypeScript or be merged with nearby words. The analyzer includes cleanup and matching strategies to handle these cases more reliably.

## Resume Score Calculation

The project currently uses a hybrid-ready scoring approach.

### Rule-Based Score

The default score uses:

- role match percentage
- ATS score

The rule-based final score is calculated as:

- 60% from skill-role match
- 40% from ATS score

### Optional Hybrid AI Score

If AI is enabled, the app can call an external model provider and generate:

- AI score
- AI summary
- AI roadmap
- additional strengths and gaps

When AI scoring is active, the final displayed score becomes a hybrid of:

- rule-based score
- AI score

If AI is unavailable or fails, the application safely falls back to the rule-based flow.

## ATS Analysis

The ATS module evaluates how recruiter-friendly the resume is. It checks for signals such as:

- email address
- phone number
- LinkedIn profile
- GitHub profile
- clear resume sections
- bullet points
- measurable outcomes
- line readability

The ATS output includes:

- ATS score
- strengths
- warnings

This helps users understand whether their resume is not only technically relevant but also structurally strong.

## Section-Wise Scoring

The resume is also evaluated section by section. Key sections include:

- Summary
- Skills
- Projects
- Experience
- Education

This gives a more detailed understanding of which area needs improvement instead of treating the resume as one single score.

## Job Description Comparison

The application accepts an optional job description. If the user pastes a JD, the analyzer compares the resume not only to the built-in role profile but also to the exact job requirement text. This makes the report more specific and useful for real applications.

## Recommendations and Gap Priority

The project provides:

- prioritized missing skills
- actionable recommendations
- suggestions for stronger resume bullets
- interview preparation questions

Missing skills are labeled by priority:

- High
- Medium
- Low

This helps users decide what to focus on first.

## Learning Roadmap

The dashboard generates a weekly upskilling roadmap for missing skills. Each roadmap item includes:

- week number
- focus skill
- mission
- expected output

The roadmap is practical and portfolio-oriented. For example, instead of just saying "learn HTML", it suggests a task like rebuilding a semantic landing page or shipping a typed React project.

If AI planning is enabled, the roadmap can also be generated or improved by the AI provider.

## Learning Resources

The platform provides learning resources for missing skills. These resources now prioritize:

- beginner-friendly YouTube courses

instead of only official documentation. This makes the platform more student-friendly and easier to follow for real learning.

## Learning Progress Tracking

One of the stronger product features added later is progress tracking.

From a saved dashboard, the user can:

- mark a missing skill as completed
- see that skill move out of the missing-skill list
- see the skill appear in the completed learning section
- see the projected role-match and resume score improve

This turns the dashboard into an improvement tracker rather than a one-time report. It also allows the user to undo a completed skill if needed.

## History Module

All analyses are saved in the database and shown in the history page. The history module supports:

- search by file or role
- role filtering
- minimum score filtering
- open saved dashboard
- export report
- delete saved report

This makes the app more useful over time and supports repeated resume improvement.

## PDF Export

Each saved dashboard can be exported as a PDF report. The export includes important analysis details such as:

- filename
- role
- score
- role match
- ATS score
- recommendations
- bullet improvements
- learning resources
- AI review summary if available

## User Interface Design

The project uses a premium dark glass-card UI with matte 3D styling and geometric accents. The layout is split into separate focused pages:

- login
- register
- upload
- result dashboard
- history
- profile

This creates a better user experience than putting every feature on one page. The login and registration pages also use a richer product-style layout instead of plain forms.

## Database and Deployment

For deployment, the project uses:

- Render for hosting
- Neon PostgreSQL for persistent production storage

Local development can still use SQLite if no external database is configured. Django settings are environment-variable based, so deployment stays flexible.

## AI Integration

The project is prepared for AI-assisted resume evaluation. It supports:

- AI provider configuration through environment variables
- hybrid score generation
- AI-generated roadmap and review text
- fallback to rule-based scoring if the provider fails

The app currently supports:

- OpenAI-style integration
- Groq as a free-compatible provider path

This makes the project future-ready without making the main functionality depend entirely on AI.

## Strengths of the Project

- strong real-world use case
- built with a clean Django-based architecture
- supports multiple resume file formats
- handles noisy PDF text better than simple keyword matchers
- provides ATS and role-based evaluation together
- saves user reports and progress
- includes progress-driven score improvement
- supports hybrid AI integration
- deployable with public access
- well suited for demonstration and presentation

## Current Limitations

- scanned or image-based PDFs are not analyzed right now
- PDF text extraction still depends on the quality of the source file
- AI depends on external provider configuration and quota
- progress-based score increases are projected improvements, not proof that the resume itself has been rewritten yet
- the system still uses structured logic and heuristics rather than full semantic resume understanding in every case

## Conclusion

Resume Insight Studio is a full-stack Django project that turns resume review into an interactive improvement platform. It combines authentication, file upload, text extraction, skill detection, ATS analysis, role-fit scoring, roadmap generation, learning resources, progress tracking, report storage, export, and optional AI support into one complete product.

This makes it a strong college project because it solves a practical problem, demonstrates multiple technical layers working together, and goes beyond a basic analysis tool by helping users continuously improve their job readiness.
