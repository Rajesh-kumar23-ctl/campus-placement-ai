APTITUDE_GENERATION_PROMPT = """
You are an expert aptitude test creator for collegiate placement exams (TCS, Infosys, Wipro, Accenture, Amazon).
Generate a new, high-quality multiple choice question for the specified category and difficulty.

Category: {category}
Difficulty: {difficulty}

Your response must be valid JSON in this exact structure:
{{
    "question": "Question text here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option B",
    "explanation": "Detailed step-by-step mathematical or logical explanation",
    "shortcut": "Time-saving exam shortcut or trick",
    "difficulty": "{difficulty}",
    "category": "{category}"
}}
Do NOT output any markdown commentary outside the JSON block.
"""

APTITUDE_EXPLANATION_PROMPT = """
Explain the following aptitude question clearly for a college student preparing for campus recruitment:
Question: {question}
Correct Answer: {correct_answer}
Provide a step-by-step breakdown and a quick shortcut formula.
"""
