# Resume Insight Studio

## Complete Project Explanation

Resume Insight Studio is a web-based application developed using Python and Django. The purpose of the project is to help users evaluate their resumes for specific job roles such as Frontend Developer, Backend Developer, Data Scientist, ML Engineer, and UI/UX Designer. The system analyzes the uploaded resume, extracts its text content, compares it with the selected role requirements, and then generates a detailed report showing how well the resume matches that role.

The project is designed to solve a common problem faced by students and job seekers. Many people create resumes without knowing whether the content is actually aligned with the job they want. A resume may look good visually, but it can still miss important skills, proper structure, ATS-friendly keywords, or measurable achievements. This project helps identify those issues and gives practical improvement suggestions.

## Main Idea of the Project

The main idea is to create an intelligent resume screening system that can:

- accept resumes in different formats
- extract the text from the resume
- identify relevant skills
- compare those skills with a selected job role
- detect missing skills
- calculate scores
- provide improvement suggestions
- save analysis history for the user

So instead of just giving a simple pass or fail result, the system gives a structured career-support dashboard.

## Technologies Used

- Python
- Django
- HTML
- CSS
- JavaScript
- PyPDF2
- python-docx
- OCR.space API
- SQLite for local development
- Neon PostgreSQL for deployed use
- Render for hosting

## How the Project Works

1. User opens the application.
2. User registers and logs in.
3. User can optionally fill in profile details.
4. User goes to the upload page.
5. User selects a target job role.
6. User uploads a resume in PDF, DOCX, or TXT format.
7. User can also paste an optional job description.
8. The system extracts the text from the uploaded file.
9. The extracted text is analyzed based on the selected role.
10. The system shows a separate result page with score, matched skills, missing skills, ATS review, roadmap, recommendations, and other insights.
11. The report is saved in the history page and can be exported as a PDF.

## Core Features

- User registration and login
- Duplicate email validation
- User profile page
- Resume upload page
- Separate analysis result page
- Resume history page
- PDF report export
- Public deployment support

## Resume File Support

The project supports:

- PDF
- DOCX
- TXT

For PDF resumes, the system first tries normal text extraction. If the PDF is scanned or image-based, OCR fallback is available. For DOCX resumes, the system extracts paragraph content and table content as well.

## Authentication Module

The project includes login and registration so that each user has a separate account. Analyses are saved user-wise, which means one user cannot access another user’s reports. Duplicate email validation was also added so the same email cannot be reused for multiple accounts.

## Profile Module

The profile page allows the user to store extra details such as:

- full name
- phone number
- college
- degree
- graduation year
- target role

This makes the project more complete and useful during demonstration.

## Resume Analysis Module

This is the main module of the project. After extracting the text from the resume, the system analyzes it for the selected job role. It checks whether the resume includes important technologies, tools, and concepts expected for that role.

For example, if the selected role is Frontend Developer, the system checks for skills like:

- HTML
- CSS
- JavaScript
- TypeScript
- React
- Redux
- Tailwind
- Webpack
- Git
- Testing
- Accessibility
- Responsive Design
- REST API
- Figma

Then it divides the result into matched skills and missing skills.

## Skill Detection System

The project includes a role-based skill matching engine. It does not only depend on exact words. It also supports:

- aliases
- synonyms
- text normalization
- noisy PDF cleanup
- fragmented text matching

This is important because many PDFs extract text in a broken way. For example, TypeScript may appear as T ypeScript. The system was improved to recognize such patterns better.

## ATS Score

The project also generates an ATS-related score. ATS means Applicant Tracking System. This score helps estimate whether the resume has recruiter-friendly structure and content.

The ATS check looks for things like:

- email presence
- phone number
- LinkedIn or GitHub links
- clear sections
- bullet points
- measurable achievements
- readable layout signals

It also shows warnings if important elements are missing.

## Section-Wise Scoring

The resume is also evaluated section by section. Sections such as:

- summary
- skills
- projects
- experience
- education

are checked separately. This gives the user a better understanding of which parts of the resume are strong and which parts need work.

## Job Description Comparison

An optional job description can be pasted by the user. If a JD is provided, the project compares the resume not only against the selected role profile but also against the actual job requirement text. This makes the result more specific and practical.

## Missing Skill Priority

The project not only lists missing skills but also labels them by priority:

- High
- Medium
- Low

This helps the user understand what should be learned first.

## Recommendations

The project gives improvement recommendations such as:

- what skill to prioritize
- what kind of project evidence to add
- how to improve bullet points
- how to improve role targeting

These recommendations make the result actionable.

## Learning Roadmap

The system generates a weekly learning roadmap for missing skills. This roadmap gives the user a more structured path to improve their resume and skill set over time.

## Interview Questions

The system also generates role-based interview practice questions. These questions are based on the selected role and the current analysis result.

## Course and Resource Suggestions

For some missing skills, the project provides suggested learning resources. This makes the project more useful for students because it does not stop at finding weaknesses; it also suggests how to improve.

## Bullet Improvement Suggestions

A special feature added later is bullet improvement suggestions. The project takes extracted resume lines and suggests stronger rewritten versions. This helps users understand how to present their experience more effectively.

## History Module

Each analysis is saved in the database. The user can revisit previous reports in the history page. The history page also includes filters so the user can search by:

- role
- filename
- score

## Report Export

The user can export a saved analysis report as a PDF. This is useful for documentation, project presentation, or portfolio demonstration.

## UI Design

The project uses a modern glass-card interface with a dashboard-like appearance. The final structure of the application is:

- login and register page
- upload page
- result page
- history page
- profile page

This makes the application cleaner and easier to use compared to showing everything on one page.

## Deployment

The project is deployed on Render so it can be accessed through a public link. Since SQLite is not reliable for persistent storage on free hosting, Neon PostgreSQL is used for the deployed version. Static files are handled using WhiteNoise.

## Strengths of the Project

- practical real-world use case
- built with Django and Python
- supports multiple resume formats
- includes OCR fallback
- gives detailed analysis instead of only a score
- has user authentication and saved history
- has separate pages for better user experience
- deployed online with public access
- good for presentation and demonstration

## Limitations

- heavy scanned PDFs may still be difficult on free hosting
- OCR reliability depends on file quality
- some badly structured PDFs may still extract incomplete text
- the analysis is rule-based, not a full semantic AI model

## Conclusion

Resume Insight Studio is a complete Django-based resume analysis platform that helps users understand how well their resume matches a chosen job role. It combines authentication, file upload, text extraction, skill matching, ATS scoring, section-wise analysis, roadmap generation, recommendations, report storage, and deployment into one practical project. It is a strong college project because it solves a real problem, uses multiple technologies together, and demonstrates both technical development and real-world usefulness.
