from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import json
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    response = make_response(render_template("index.html"))
    response.headers["Content-Type"] = "text/html"
    return response

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        # Dateien empfangen
        spec_file = request.files["spec"]
        flow_file = request.files["file"]

        # temporär speichern
        spec_path = os.path.join(UPLOAD_FOLDER, "spec.pdf")
        flow_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
        spec_file.save(spec_path)
        flow_file.save(flow_path)

        # an n8n senden
        webhook_url = "https://maxschira.app.n8n.cloud/webhook/generate-doc"
        files = {
            "spec": open(spec_path, "rb"),
            "file": open(flow_path, "rb"),
            "disclaimer": (None, request.form.get("disclaimer", ""))
        }
        response = requests.post(webhook_url, files=files)

        # Ergebnisdatei zurücksenden
        if response.ok:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            return send_file(tmp_path, as_attachment=True, download_name="filled_specification.docx")
        else:
            return f"Fehler von n8n: {response.status_code} - {response.text}", 500

    except Exception as e:
        return f"Fehler: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
