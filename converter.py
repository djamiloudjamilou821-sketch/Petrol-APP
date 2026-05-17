from flask import render_template, request, jsonify

def register_converter(app):

    # ⚙️ CORE LOGIC (REUSABLE FUNCTION)
    def perform_conversion(value, conversion):

        # 🌍 LENGTH
        if conversion == "m_to_ft":
            return round(value * 3.28084, 4)

        elif conversion == "ft_to_m":
            return round(value / 3.28084, 4)

        # ⚖️ PRESSURE
        elif conversion == "psi_to_bar":
            return round(value * 0.0689476, 4)

        elif conversion == "bar_to_psi":
            return round(value / 0.0689476, 4)

        # 🛢️ OIL & GAS VOLUME
        elif conversion == "bbl_to_l":
            return round(value * 158.987, 4)

        elif conversion == "l_to_bbl":
            return round(value / 158.987, 6)

        elif conversion == "bbl_to_m3":
            return round(value * 0.158987, 6)

        elif conversion == "m3_to_bbl":
            return round(value / 0.158987, 4)

        elif conversion == "l_to_m3":
            return round(value / 1000, 6)

        elif conversion == "m3_to_l":
            return round(value * 1000, 2)

        else:
            return "Unknown conversion type"

    # CONVERTER
    @app.route("/converter", methods=["GET", "POST"])
    def converter():
        result = None

        if request.method == "POST":
            value = float(request.form.get("value"))
            conversion = request.form.get("conversion")

            # 🌍 Length conversions
            if conversion == "m_to_ft":
                result = round(value * 3.28084, 4)
            elif conversion == "ft_to_m":
                result = round(value / 3.28084, 4)

            # ⚖️ Pressure conversions
            elif conversion == "psi_to_bar":
                result = round(value * 0.0689476, 4)
            elif conversion == "bar_to_psi":
                result = round(value / 0.0689476, 4)

            # 🛢️ OIL & GAS VOLUME CONVERSIONS
            elif conversion == "bbl_to_l":
                result = round(value * 158.987, 4)

            elif conversion == "l_to_bbl":
                result = round(value / 158.987, 6)

            elif conversion == "bbl_to_m3":
                result = round(value * 0.158987, 6)

            elif conversion == "m3_to_bbl":
                result = round(value / 0.158987, 4)

            elif conversion == "l_to_m3":
                result = round(value / 1000, 6)

            elif conversion == "m3_to_l":
                result = round(value * 1000, 2)

        return render_template("converter.html", result=result)

    # 📡 API VERSION (FOR FLUTTER)
    @app.route("/api/converter", methods=["POST"])
    def api_converter():
        data = request.get_json()

        try:
            value = float(data["value"])
            conversion = data["conversion"]

            result = perform_conversion(value, conversion)

            if isinstance(result, str):
                return jsonify({"error": result}), 400

            return jsonify({
                "conversion": conversion,
                "input": value,
                "result": result
            })

        except:
            return jsonify({"error": "Invalid input"}), 400
