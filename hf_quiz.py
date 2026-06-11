import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# We will pass an array of already answered questions to prevent repetitions
def generate_quiz(subject, history_list=None):
    hf_token = os.environ.get("HF_API_TOKEN")
    if not hf_token:
        return {"error": "Missing HF_API_TOKEN in your configuration setup."}

    if history_list is None:
        history_list = []

    # Calculate current difficulty tier based on how many questions they have answered
    # 0-2 answered = Beginner | 3-5 answered = Intermediate | 6+ answered = Advanced
    count = len(history_list)
    if count <= 2:
        difficulty = "Beginner / Concept Introduction level (straightforward calculation or core definition)"
    elif count <= 5:
        difficulty = "Intermediate level (requires applying a core formula or combining two steps)"
    else:
        difficulty = "Advanced level (complex field scenarios, multi-step engineering calculations, deep troubleshooting)"

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": f"""
You are an expert professor operating the PetroAI educational assessment terminal.

Target Topic Selection:
- Generate ONE multiple-choice question focusing EXCLUSIVELY on the technical scope of this topic: {subject}.
- If the topic is 'math', generate purely mathematics problems (algebra, calculus, geometry, or statistics). Do not mix other sciences into it.
- Treat terms like 'ptroleeum enginieering', 'petrolieum engeniering', or variations as 'Petroleum Engineering' (drilling, reservoir characterization, production).
- Stay completely focused on the specified discipline. Do not wander off into adjacent general knowledge fields.

Difficulty Steering System:
- The user has already answered {count} questions in this session tracker.
- You MUST target this specific difficulty tier: {difficulty}.
- Start with foundational principles and scale up to advanced calculations as this count rises.

Session Filtering Rules (Preventing Duplication):
- Here is a historical record summary list of questions generated for the user earlier today: {history_list}
- CRITICAL: Read that list carefully. You are strictly FORBIDDEN from generating a question that matches or heavily duplicates any concept or text phrasing in that history log. It must be unique.

Strict Formatting Rules for Mathematics:
- Always write formulas in simple plain-text format, completely avoiding LaTeX styles.
- Use mobile-friendly layouts like: V = m/t, Q = A × v.
- NEVER use the written word 'pi' or carets for exponents like '^2' or '^3'.
- ALWAYS use standard Unicode math symbols: use 'π' instead of 'pi', and true superscripts like '²' or '³' for powers (e.g., A = π * r², or m³).
- NEVER use fractions like \\frac{{}}{{}} or any LaTeX block math symbols.
- Ensure all calculations and equations fit nicely on smartphone viewports.

Return exactly this text structure format below. Do not wrap it in markdown backticks or include extra sentences:

Question: [Insert question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Answer: [Insert only the correct letter here: A, B, C, or D]
Explanation: [Insert deep breakdown analysis here]
"""
            }
        ],
        "max_tokens": 400,
        "temperature": 0.75
    }

    try:
        response = requests.post("https://router.huggingface.co/v1/chat/completions", headers=headers, json=payload, timeout=12)
        if response.status_code != 200:
            return {"error": "Hugging Face engine link unavailable."}
            
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
        
        # Regex parsing engine
        quiz_dict = {}
        q_match = re.search(r"Question:\s*(.*?)\s*(?=A\)|$)", raw_text, re.DOTALL | re.IGNORECASE)
        a_match = re.search(r"A\)\s*(.*?)\s*(?=B\)|$)", raw_text, re.DOTALL | re.IGNORECASE)
        b_match = re.search(r"B\)\s*(.*?)\s*(?=C\)|$)", raw_text, re.DOTALL | re.IGNORECASE)
        c_match = re.search(r"C\)\s*(.*?)\s*(?=D\)|$)", raw_text, re.DOTALL | re.IGNORECASE)
        d_match = re.search(r"D\)\s*(.*?)\s*(?=Answer:|$)", raw_text, re.DOTALL | re.IGNORECASE)
        ans_match = re.search(r"Answer:\s*([A-D])", raw_text, re.IGNORECASE)
        exp_match = re.search(r"Explanation:\s*(.*)", raw_text, re.DOTALL | re.IGNORECASE)

        quiz_dict["question"] = q_match.group(1).strip() if q_match else "Inquiry parameters loading. Tap Next to retry."
        quiz_dict["A"] = a_match.group(1).strip() if a_match else "Option value missing."
        quiz_dict["B"] = b_match.group(1).strip() if b_match else "Option value missing."
        quiz_dict["C"] = c_match.group(1).strip() if c_match else "Option value missing."
        quiz_dict["D"] = d_match.group(1).strip() if d_match else "Option value missing."
        quiz_dict["answer"] = ans_match.group(1).strip().upper() if ans_match else "A"
        quiz_dict["explanation"] = exp_match.group(1).strip() if exp_match else "No secondary breakdown notes logged."
        quiz_dict["error"] = None
        
        return quiz_dict

    except Exception as e:
        return {"error": "PetroAI link is adjusting parameters. Tap Next Question to retry."}