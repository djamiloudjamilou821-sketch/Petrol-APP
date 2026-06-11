import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_quiz(subject, history_list=None):
    hf_token = os.environ.get("HF_API_TOKEN")
    if not hf_token:
        return {"error": "Missing HF_API_TOKEN in your configuration setup."}

    if history_list is None:
        history_list = []

    count = len(history_list)
    if count <= 2:
        difficulty = "Beginner / Concept Introduction level (straightforward principles or core layouts)"
    elif count <= 5:
        difficulty = "Intermediate level (requires applying custom logic or combining structural steps)"
    else:
        difficulty = "Advanced level (complex real-world scenarios, multi-step variations, deep troubleshooting)"

    # 📚 DYNAMIC CONTENT SWITCH: Determine if the topic requires a conversational language layout
    language_subjects = ['english', 'french', 'arabic']
    
    if subject.lower() in language_subjects:
        system_instruction = f"""You are an expert, friendly multilingual linguist operating the PetroAI Language Learning Hub.
The user is an intermediate learner building natural communication fluency.

CRITICAL CONTENT INSTRUCTIONS:
1. NEVER ask for abstract definitions or academic terms (e.g., NEVER ask "What is the term for a word that has the same spelling...").
2. Instead, you MUST randomly focus the exercise on one of these 4 vital practical pillars:
   - GRAMMAR: Practical sentence assembly, prepositions, or error corrections.
   - CONJUGATION: Selecting correct verb tenses based on situational context (crucial for French/Arabic).
   - VOCABULARY IN CONTEXT: Fill-in-the-blanks using conversational phrases, business expressions, or common idioms.
   - PRONUNCIATION & PHONETICS: Spoken accent evaluation questions dealing with word stress patterns, silent letters, or rhyming profiles (e.g., "Which word has a silent letter?", "Which word rhymes with...").

Target Language: Focus 100% on practical learning for: {subject}. Make it interactive, engaging, and friendly!"""
    else:
        system_instruction = f"""You are an expert professor operating the PetroAI technical assessment terminal.

Target Topic Selection:
- Generate ONE multiple-choice question focusing EXCLUSIVELY on the technical scope of this topic: {subject}.
- If the topic is 'math', generate purely mathematics problems (algebra, calculus, geometry, or statistics). Do not mix other sciences into it.
- Treat terms like 'ptroleeum enginieering', 'petrolieum engeniering', or variations as 'Petroleum Engineering' (drilling, reservoir characterization, production).
- Stay completely focused on the specified discipline. Do not wander off into adjacent general knowledge fields."""

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": f"""Generate ONE highly effective multiple-choice evaluation task.

Difficulty Steering System:
- The user has already answered {count} questions in this session tracker.
- You MUST target this specific difficulty tier: {difficulty}.
- Start with foundational structures and scale up to advanced applications as this count rises.

Session Filtering Rules (Preventing Duplication):
- Here is a historical record summary list of questions generated for the user earlier today: {history_list}
- CRITICAL: Read that list carefully. You are strictly FORBIDDEN from generating a question that matches or heavily duplicates any concept or text phrasing in that history log. It must be unique.

Strict Formatting Rules for Mathematics & Symbols:
- Always write formulas or expressions in simple plain-text format, completely avoiding LaTeX styles.
- Use mobile-friendly layouts like: V = m/t, Q = A × v.
- NEVER use the written word 'pi' or carets for exponents like '^2' or '^3'.
- ALWAYS use standard Unicode math symbols: use 'π' instead of 'pi', and true superscripts like '²' or '³' for powers (e.g., A = π * r², or m³).
- NEVER use fractions like \\frac{{}}{{}} or any LaTeX block math symbols.
- Ensure all text fits nicely on small smartphone viewports.

Return exactly this text structure format below. Do not wrap it in markdown backticks or include extra conversational sentences outside the structure:

Question: [Insert the practical exercise or question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

Answer: [Insert only the correct letter here: A, B, C, or D]
Explanation: [Provide a high-quality breakdown explaining the core rules, helpful memory tricks, or equations clearly]"""
            }
        ],
        "max_tokens": 450,
        "temperature": 0.75
    }

    try:
        response = requests.post("https://router.huggingface.co/v1/chat/completions", headers=headers, json=payload, timeout=12)
        if response.status_code != 200:
            return {"error": f"Hugging Face Router error status code: {response.status_code}"}
            
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
        
        # Strip out any accidental wrapping markdown code fences if the model prints them
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```[a-zA-Z]*\n|```$", "", raw_text).strip()
        
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
        print(f"Quiz Generation Error: {e}")
        return {"error": "PetroAI link is adjusting parameters. Tap Next Question to retry."}