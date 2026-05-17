from flask import render_template, request

def register_quiz(app):
    # QUIZ
    @app.route("/quiz", methods=["GET", "POST"])
    def quiz():
        questions = [
            {
                "q": "What does porosity measure?",
                "options": {
                    "A": "Pressure in the well",
                    "B": "Empty space in rock",
                    "C": "Oil color",
                    "D": "Drilling speed"
                },
                "answer": "B",
                "explanation": "Porosity is the percentage of empty space in a rock that can store fluids."
            },
            {
                "q": "What is permeability?",
                "options": {
                    "A": "Ability of rock to allow fluid flow",
                    "B": "Oil price",
                    "C": "Well depth",
                    "D": "Rock color"
                },
                "answer": "A",
                "explanation": "Permeability describes how easily fluids pass through rock."
            },
            {
                "q": "API gravity measures what?",
                "options": {
                    "A": "Water pressure",
                    "B": "Oil density",
                    "C": "Gas volume only",
                    "D": "Drilling speed"
                },
                "answer": "B",
                "explanation": "API gravity compares oil density to water."
            },
            {
                "q": "What is reservoir pressure?",
                "options": {
                    "A": "Pressure inside oil reservoir",
                    "B": "Air pressure at surface",
                    "C": "Pump speed",
                    "D": "Pipe thickness"
                },
                "answer": "A",
                "explanation": "Reservoir pressure is the pressure of fluids trapped underground."
            },
            {
                "q": "What is production rate?",
                "options": {
                    "A": "Time of drilling",
                    "B": "Amount of oil produced per time",
                    "C": "Rock hardness",
                    "D": "Pipe size"
                },
                "answer": "B",
                "explanation": "Production rate is how much oil is produced per unit time."
            }
        ]

        results = []
        score = 0

        if request.method == "POST":
            for i, q in enumerate(questions):
                user_answer = request.form.get("question" + q["q"])

                correct = (user_answer == q["answer"])

                if correct:
                    score += 1

                results.append({
                    "question": q["q"],
                    "your_answer": user_answer,
                    "correct_answer": q["answer"],
                    "is_correct": correct,
                    "explanation": q["explanation"]
                })

            return render_template(
                "quiz.html",
                questions=questions,
                results=results,
                score=score,
                total=len(questions)
            )

        return render_template("quiz.html", questions=questions, results=None)