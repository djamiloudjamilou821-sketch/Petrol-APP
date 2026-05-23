from flask import render_template, request, jsonify
from models import Formula
import math

def register_formulas(app):

    @app.route("/formulas")
    def formulas():

        formulas = Formula.query.all()

        return render_template(
            "formulas.html",
            formulas=formulas
        )


    @app.route("/formula/<int:id>", methods=["GET", "POST"])
    def formula_page(id):

        formula = Formula.query.get_or_404(id)

        result = None

        import re

        variables = list(set(
            re.findall(r"\b[a-zA-Z_]+\b", formula.python_formula)
        ))

        reserved = [
            "pow",
            "sqrt",
            "sin",
            "cos",
            "tan",
            "log",
            "exp"
        ]

        variables = [v for v in variables if v not in reserved]

        if request.method == "POST":

            values = {}

            for var in variables:

                try:
                    values[var] = float(request.form[var])

                except:
                    values[var] = 0

            try:
                result = eval(formula.python_formula, {}, values)

            except ZeroDivisionError:
                result = "Error: Division by zero"

            except Exception as e:
                result = f"Error: {e}"

        return render_template(
            "formula_page.html",
            formula=formula,
            result=result,
            variables=variables
        )