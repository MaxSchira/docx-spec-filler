from flask import Flask, request, send_file, jsonify
from docxtpl import DocxTemplate
import tempfile
import os
import json
import logging

# Initialisiere Flask & Logging
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def health():
    return " Server is alive!"

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        # Versuche JSON-Body zu laden
        raw_data = request.get_data(as_text=True)
        logging.info(" Raw request body:\n%s", raw_data)

        # JSON parsen
        data = json.loads(raw_data)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid format – expected flat JSON object"}), 400

        # Lade und rendere das Template
        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        # Speichere das ausgefüllte Dokument temporär
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            logging.info(" Document rendered successfully.")
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except json.JSONDecodeError as e:
        logging.error(" JSON Decode Error: %s", str(e))
        return jsonify({"error": "Invalid JSON format", "details": str(e)}), 400

    except Exception as e:
        logging.exception(" Error during document generation:")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
