RESUME_PARSING_PROMPT = """
You are an expert technical recruiter and resume analyst.
Analyze the following parsed resume text from a student/job applicant.

Resume Text:
\"\"\"
{resume_text}
\"\"\"

Extract the structured details accurately.
CRITICAL RULE: Extract ONLY what is explicitly present. Do NOT invent or hallucinate technologies, internships, or achievements.

Return valid JSON:
{{
    "candidate_name": "Full Name if detected, or Candidate",
    "summary": "Professional 2-3 sentence executive summary of the candidate's profile",
    "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
    "projects": [
        {{
            "title": "Project Name",
            "technologies": ["Tech 1", "Tech 2"],
            "description": "Short description of what was built and impact"
        }}
    ],
    "education": [
        {{
            "institution": "College/University Name",
            "degree": "B.Tech / B.E / B.Sc / etc.",
            "field": "Computer Science / IT / etc.",
            "year": "Graduation Year or Range",
            "score": "CGPA or percentage if mentioned"
        }}
    ],
    "experience": [
        {{
            "role": "Intern / Developer / Role",
            "company": "Company or Organization",
            "duration": "Duration or Dates",
            "highlights": ["Key responsibility or achievement"]
        }}
    ],
    "certifications": ["Certification 1", "Certification 2"],
    "potential_questions": [
        "Resume-specific question directly referencing their project or tech stack 1",
        "Resume-specific question 2",
        "Resume-specific question 3",
        "Resume-specific question 4",
        "Resume-specific question 5"
    ]
}}
"""

RESUME_QUESTIONS_PROMPT = """
You are an interviewer preparing for a resume-based interview for the role of {target_role}.

Candidate Skills: {skills}
Candidate Projects: {projects}
Candidate Experience: {experience}

Generate 5 high-yield, authentic interview questions based strictly on the candidate's actual projects, technologies, and achievements listed above.
Do NOT invent unlisted technologies.

Return valid JSON:
{{
    "questions": [
        "Question 1 referencing specific project or technology...",
        "Question 2...",
        "Question 3...",
        "Question 4...",
        "Question 5..."
    ]
}}
"""
