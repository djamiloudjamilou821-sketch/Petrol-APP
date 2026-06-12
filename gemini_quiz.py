import os
import re
import random
from google import genai
from google.genai import types
from google.genai.errors import ClientError

def generate_quiz(subject: str, history_list: list = None) -> dict:
    # 1. Initialize client using the key from your .env or Render dashboard
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY in your local environment configuration."}
        
    client = genai.Client(api_key=api_key)
    primary_model = "gemini-2.5-flash" 

    if history_list is None:
        history_list = []

    # Calculate current difficulty tier dynamically based on progress history length
    count = len(history_list)
    if count <= 2:
        difficulty = "Beginner / Concept Introduction level (straightforward foundational rules or simple equations)"
    elif count <= 5:
        difficulty = "Intermediate level (requires combining two steps or checking situational syntax rules)"
    else:
        difficulty = "Advanced level (complex field scenarios, deep engineering troubleshooting, or nuanced communication structures)"

    # 📚 DYNAMIC CONTENT SWITCH: Tailor system context instructions based on topic selected
    language_subjects = ['english', 'french', 'arabic']
    
    if subject.lower() in language_subjects:
        system_instruction = f"""You are an expert, friendly multilingual linguist operating the PetroAI Language Learning Hub.
The user is an intermediate language student working on communication fluency.

CRITICAL LEARNING INSTRUCTIONS:
1. NEVER ask for dry academic definition terms (e.g., NEVER ask "What is the term for a word that has the same spelling...").
2. Instead, you MUST randomly focus the question text block on one of these 4 vital practical pillars:
   - GRAMMAR: Practical sentence structures, preposition corrections, or word assemblies.
   - CONJUGATION: Choosing correct verb tenses inside the context of an active sentence (especially critical for French/Arabic).
   - VOCABULARY IN CONTEXT: Fill-in-the-blanks using real-world conversation expressions, professional idioms, or key vocabulary phrases.
   - PRONUNCIATION & PHONETICS: Spoken accent mechanics covering word stress patterns, silent letters, or rhyming profiles.

Target Focus language: {subject}. Make it interactive, professional, and friendly for phone screens!"""
    else:
        system_instruction = f"""You are an expert professor operating the PetroAI technical engineering assessment terminal.

Target Topic Selection:
- Generate ONE multiple-choice question focusing EXCLUSIVELY on the technical scope of this topic: {subject}.
- If the topic is 'math', generate purely mathematics problems (algebra, calculus, geometry). Do not mix other engineering sectors.
- Treat terms like 'ptroleeum enginieering', 'petrolieum engeniering', or typical typo variations as 'Petroleum Engineering' (drilling dynamics, reservoir fluid characterization, extraction).
- Stay focused on the technical core data. Do not wander off into general trivia knowledge."""

    # Construct the final strict formatting user instruction
    prompt_text = f"""Generate ONE highly effective multiple-choice evaluation task following these boundaries.

Difficulty Steering System:
- Active tier to build: {difficulty} (User has completed {count} questions today).

Session Filtering Rules (Preventing Duplication):
- Exclude all question styles or identical text match frameworks found in this session history: {history_list}
- The question must be completely unique.

Strict Formatting Rules for Mathematics & Text Layouts:
- Always write formulas or expressions in simple plain-text format, completely avoiding LaTeX components.
- Use clean layouts like: V = m/t, Q = A × v.
- NEVER use the written word 'pi' or carets for exponents like '^2' or '^3'.
- ALWAYS use standard Unicode math symbols natively supported on mobile phones: use 'π' instead of 'pi', and true superscripts like '²' or '³' for powers (e.g., A = π * r², or m³).
- NEVER use fractions like \\frac{{}}{{}} or raw LaTeX formatting blocks.
- Do not output markdown backticks or triple code block wrappers.

Return EXACTLY this structure format below:
Question: [Insert question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [Single letter letter: A, B, C, or D]
Explanation: [Provide a high-quality explanation breaking down the logic, rules, or math cleanly]
"""

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.75,
        system_instruction=system_instruction
    )

    # =========================================================
    # ⚡ AUTOMATIC MODEL FALLBACK & RETRY LOOP (NON-BLOCKING)
    # =========================================================
    max_retries = 3
    text = None
    
    for attempt in range(max_retries):
        try:
            # Dynamic Model Swap: On the final attempt, shift to the quiet 1.5 generation backup line
            active_model = primary_model if attempt < 2 else "gemini-2.5-flash-lite"
            
            response = client.models.generate_content(
                model=active_model,
                contents=contents,
                config=generate_content_config,
            )
            
            text = response.text
            if not text:
                return {"error": "No data returned from the PetroAI link engine."}

            break  # Success! Exit the retry loop

        except ClientError as e:
            # Catch Rate Limits (429) and Overloads (503)
            if (e.code == 429 or e.code == 503) and attempt < max_retries - 1:
                print(f"⚠️ Track traffic status {e.code} hit. Re-routing attempt {attempt + 1} instantly...")
                continue  # Retries immediately without using server-freezing time.sleep()
            else:
                return {"error": f"API Error: {e.message} (Status Code: {e.code})"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

    if not text:
        return {"error": "PetroAI core generation link timed out. Please try again."}

    # =========================================================
    # 🧼 TEXT PARSING ENGINE
    # =========================================================
    # Strip out accidental markdown code fences if the model prints them
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|```$", "", text).strip()

    quiz_data = {}
    q_match = re.search(r"Question:\s*(.*?)\s*(?=A\)|$)", text, re.DOTALL | re.IGNORECASE)
    a_match = re.search(r"A\)\s*(.*?)\s*(?=B\)|$)", text, re.DOTALL | re.IGNORECASE)
    b_match = re.search(r"B\)\s*(.*?)\s*(?=C\)|$)", text, re.DOTALL | re.IGNORECASE)
    c_match = re.search(r"C\)\s*(.*?)\s*(?=D\)|$)", text, re.DOTALL | re.IGNORECASE)
    d_match = re.search(r"D\)\s*(.*?)\s*(?=Answer:|$)", text, re.DOTALL | re.IGNORECASE)
    ans_match = re.search(r"Answer:\s*([A-D])", text, re.IGNORECASE)
    exp_match = re.search(r"Explanation:\s*(.*)", text, re.DOTALL | re.IGNORECASE)

    # Fallback strings if regex capture groups miss structural markers
    quiz_data['question'] = q_match.group(1).strip() if q_match else "Inquiry parameter formatting error. Tap Next to reload."
    quiz_data['A'] = a_match.group(1).strip() if a_match else "Option value missing."
    quiz_data['B'] = b_match.group(1).strip() if b_match else "Option value missing."
    quiz_data['C'] = c_match.group(1).strip() if c_match else "Option value missing."
    quiz_data['D'] = d_match.group(1).strip() if d_match else "Option value missing."
    quiz_data['answer'] = ans_match.group(1).strip().upper() if ans_match else "A"
    quiz_data['explanation'] = exp_match.group(1).strip() if exp_match else "No secondary documentation noted."
    quiz_data['error'] = None

    return quiz_data