from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import json

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

        if not spec_file:
            return "No specification file uploaded", 400

        # Spezifikation speichern
        spec_path = os.path.join(UPLOAD_FOLDER, "spec.pdf")
        spec_file.save(spec_path)

        # Flowchart konvertieren (optional)
        flowchart_path = None
        if flow_file:
            pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(pdf_temp_path)
            images = convert_from_path(pdf_temp_path)
            img = images[0]
            img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
            img.save(img_path, "PNG")
            flowchart_path = img_path

        # → HIER: call to n8n (z. B. über HTTP POST, aktuell ggf. noch lokal)
        # → oder Übergabe an GPT-Assistant etc.
        # Das fertige docx wird erwartet unter: output_path

        # Placeholder (damit der Workflow nicht crasht)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc = DocxTemplate("Extract_Template.docx")
        doc.render({"flowchart": ""})  # Nur Dummy für Demo
        doc.save(output_path)

        return send_file(output_path, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        print("FEHLER:", str(e))
        return f"Error processing document: {str(e)}", 500

@app.route("/download")
def download_file():
    return send_file(os.path.join(UPLOAD_FOLDER, "filled_spec.docx"), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
