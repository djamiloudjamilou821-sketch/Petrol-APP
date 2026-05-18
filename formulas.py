from flask import render_template, request, jsonify
from models import Formula

def register_formulas(app):

    @app.route("/formulas")
    def formulas():

        formulas = Formula.query.all()

        return render_template(
            "formulas.html",
            formulas=formulas
        )
    # -------------------------
    # FLOW RATE
    # Q = V / t
    # -------------------------
    @app.route("/flow", methods=["GET", "POST"])
    def flow():
        result = None

        if request.method == "POST":
            try:
                v = float(request.form["v"])
                t = float(request.form["t"])

                if t != 0:
                    result = v / t
                else:
                    result = "Error"
            except ValueError:
                result = "Error: Please enter valid numbers"
        return render_template("flow.html", result=result)

    @app.route("/api/flow", methods=["POST"])
    def api_flow():
        data = request.get_json()

        try:
            v = float(data["v"])
            t = float(data["t"])

            if t == 0:
                return jsonify({"error": "Time cannot be zero"}), 400

            return jsonify({
                "formula": "Q = V / t",
                "result": v / t
            })

        except:
            return jsonify({"error": "Invalid input"}), 400

    # -------------------------
    # API GRAVITY
    # API = (141.5 / SG) - 131.5
    # -------------------------
    @app.route("/api", methods=["GET", "POST"])
    def api():
        result = None

        if request.method == "POST":
            try:
                sg = float(request.form["sg"])
                result = (141.5 / sg) - 131.5
            except ValueError:
                result = "Error: Please enter valid numbers"

        return render_template("api.html", result=result)

    @app.route("/api/api-gravity", methods=["POST"])
    def api_api_gravity():
        data = request.get_json()

        try:
            sg = float(data["sg"])

            return jsonify({
                "formula": "API = (141.5 / SG) - 131.5",
                "result": (141.5 / sg) - 131.5
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
    # -------------------------
    # DENSITY
    # ρ = m / V
    # -------------------------
    @app.route("/density", methods=["GET", "POST"])
    def density():
        result = None

        if request.method == "POST":
            try:
                m = float(request.form.get("m", 0))
                v = float(request.form.get("v", 0))

                if v == 0:
                    result = "Error: Volume cannot be zero"
                else:
                    result = m / v

            except ValueError:
                result = "Error: Please enter valid numbers"

        return render_template("density.html", result=result)

    @app.route("/api/density", methods=["POST"])
    def api_density():
        data = request.get_json()

        try:
            m = float(data["m"])
            v = float(data["v"])

            if v == 0:
                return jsonify({
                    "error": "Volume cannot be zero"
                }), 400

            result = m / v

            return jsonify({
                "formula": "ρ = m / V",
                "mass": m,
                "volume": v,
                "result": result
            })

        except:
            return jsonify({
                "error": "Invalid input"
            }), 400
    # -------------------------
    # PRESSURE
    # P = ρgh
    # -------------------------
    @app.route("/pressure", methods=["GET", "POST"])
    def pressure():
        result = None

        if request.method == "POST":
            try:
                rho = float(request.form["rho"])
                g = float(request.form["g"])
                h = float(request.form["h"])

                result = rho * g * h
            except ValueError:
                result = "Error: Please enter valid numbers"

        return render_template("pressure.html", result=result)

    @app.route("/api/pressure", methods=["POST"])
    def api_pressure():
        data = request.get_json()

        try:
            rho = float(data["rho"])
            g = float(data["g"])
            h = float(data["h"])

            return jsonify({
                "formula": "P = ρgh",
                "result": rho * g * h
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
    # -------------------------
    # VOLUME
    # V = Q × t
    # -------------------------
    @app.route("/volume", methods=["GET", "POST"])
    def volume():
        result = None

        if request.method == "POST":
            try:
                q = float(request.form["q"])
                t = float(request.form["t"])

                result = q * t

            except ValueError:
                result = "Error: Please enter valid numbers"

        return render_template("volume.html", result=result)

    @app.route("/api/volume", methods=["POST"])
    def api_volume():
        data = request.get_json()

        try:
            q = float(data["q"])
            t = float(data["t"])

            return jsonify({
                "formula": "V = Q × t",
                "result": q * t
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
    # -------------------------
    # TIME
    # t = V / Q
    # -------------------------
    @app.route("/time", methods=["GET", "POST"])
    def time():
        result = None

        if request.method == "POST":
            try:
                v = float(request.form["v"])
                q = float(request.form["q"])

                if q == 0:
                    result = "Error: Q cannot be zero"
                else:
                    result = v / q

            except ValueError:
                result = "Error: Please enter valid numbers"

        return render_template("time.html", result=result)

    @app.route("/api/time", methods=["POST"])
    def api_time():
        data = request.get_json()

        try:
            v = float(data["v"])
            q = float(data["q"])

            if q == 0:
                return jsonify({"error": "Flow rate cannot be zero"}), 400

            return jsonify({
                "formula": "t = V / Q",
                "result": v / q
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
    # -------------------------
    # HEIGHT
    # h = P / (ρg)
    # -------------------------
    @app.route("/height", methods=["GET", "POST"])
    def height():
        result = None

        if request.method == "POST":
            try:
                p = float(request.form["p"])
                rho = float(request.form["rho"])
                g = float(request.form["g"])

                if (rho * g) == 0:
                    result = "Error: (rho * g) cannot be zero"
                else:
                    result = p / (rho * g)

            except ValueError:
                result = "Error: Please enter valid numbers"
        return render_template("height.html", result=result)

    @app.route("/api/height", methods=["POST"])
    def api_height():
        data = request.get_json()

        try:
            p = float(data["p"])
            rho = float(data["rho"])
            g = float(data["g"])

            if rho * g == 0:
                return jsonify({"error": "Invalid density or gravity"}), 400

            return jsonify({
                "formula": "h = P / (ρg)",
                "result": p / (rho * g)
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
