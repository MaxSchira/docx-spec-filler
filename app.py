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
        spec_file = request.files.get("spec")
        flow_file = request.files.get("file")

        if not spec_file or spec_file.filename == "":
            return "No specification file uploaded", 400

        # Dateien zwischenspeichern
        spec_path = os.path.join(UPLOAD_FOLDER, "spec.pdf")
        spec_file.save(spec_path)

        flow_path = None
        if flow_file:
            flow_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(flow_path)

        # FormData vorbereiten
        files = {
            "spec": open(spec_path, "rb"),
        }
        if flow_path:
            files["file"] = open(flow_path, "rb")

        # Anfrage an n8n senden
        n8n_url = "https://maxschira.app.n8n.cloud/webhook/generate-doc"
        response = requests.post(n8n_url, files=files)

        for f in files.values():
            f.close()

        if response.status_code != 200:
            return f"Fehler von n8n: {response.status_code} - {response.text}", 500

        # Antwortdatei an den Client zurückgeben
        output_doc = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        output_doc.write(response.content)
        output_doc.close()

        return send_file(output_doc.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Fehler bei der Verarbeitung: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
