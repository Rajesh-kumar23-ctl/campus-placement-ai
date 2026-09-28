GD_TOPIC_PREP_PROMPT = """
You are a senior Group Discussion (GD) Coach and Placement Trainer.
Analyze the following GD topic and provide a comprehensive preparation breakdown for college students.

Topic: "{topic}"
Category: {category}
Difficulty: {difficulty}

Return valid JSON with the following exact keys:
{{
    "topic": "{topic}",
    "category": "{category}",
    "difficulty": "{difficulty}",
    "overview": "Detailed 2-3 sentence overview framing the core debate",
    "opening_statement": "A commanding, balanced opening statement to initiate the discussion",
    "key_arguments_for": ["Argument 1", "Argument 2", "Argument 3"],
    "key_arguments_against": ["Counterargument 1", "Counterargument 2", "Counterargument 3"],
    "real_world_examples": ["Concrete case study or historical example 1", "Example 2"],
    "thirty_sec_speech": "A punchy, concise 30-second speech",
    "one_min_speech": "A structured 1-minute persuasive speech with intro, body, and synthesis",
    "conclusion": "A balanced, forward-looking summary conclusion",
    "things_to_avoid": ["Common mistake or extreme claim 1", "Mistake 2", "Mistake 3"],
    "follow_up_questions": ["Thought-provoking question 1", "Question 2"]
}}
Do NOT output any text outside the JSON object.
"""

GD_SIMULATION_TURN_PROMPT = """
You are simulating an active college placement Group Discussion.
Topic: "{topic}"
Participants in this round:
- Moderator: Guides discussion, ensures decorum, intervenes when needed.
- Participant 1 (Aarav): Data-driven, analytical, references industry trends and numbers.
- Participant 2 (Priya): Human-centric, focuses on ethical, societal, and grassroots impact.
- Participant 3 (Rohan): Pragmatic challenger, plays devil's advocate and questions assumptions.

Discussion History so far:
{history}

The user just spoke:
User: "{user_input}"

Generate the next natural responses from 1 or 2 participants that react specifically to what the user said, either agreeing with evidence or presenting a respectful counter-view, keeping the conversation engaging.

Return valid JSON:
{{
    "speaker_responses": [
        {{
            "speaker": "Participant 1",
            "message": "Direct reaction acknowledging the user's point and adding a data angle..."
        }},
        {{
            "speaker": "Participant 2",
            "message": "Follow-up question or alternative perspective..."
        }}
    ],
    "moderator_note": "Brief guidance on how the candidate can intervene next"
}}
"""

GD_EVALUATION_PROMPT = """
You are an objective Group Discussion Evaluator for college placement rounds.
Topic: "{topic}"

Transcript of the User's participation:
{user_transcript}

Evaluate the user's observable performance across these 5 dimensions:
1. Content (0-10): Depth of arguments, facts, and relevant points.
2. Relevance (0-10): How directly the user addressed the topic and ongoing thread.
3. Clarity (0-10): Articulation, sentence cohesion, and absence of excessive filler words.
4. Structure (0-10): Organization of points (intro, reasoning, conclusion).
5. Fluency (0-10): Flow of expression and conversational naturalness.

Important:
- Evaluate ONLY observable communicative performance.
- Do NOT infer mental health, personality, intelligence, or sensitive characteristics.
- Provide constructive, actionable feedback.

Return valid JSON:
{{
    "content": 8.0,
    "relevance": 8.5,
    "clarity": 7.5,
    "structure": 7.0,
    "fluency": 8.0,
    "strengths": ["Strengths observed..."],
    "improvements": ["Actionable areas to improve..."],
    "better_response": "An exemplary rewritten version of what the user could have articulated",
    "feedback": "Overall constructive summary of performance"
}}
"""
