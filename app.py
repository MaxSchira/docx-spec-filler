from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import os
import json
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route 1: GUI anzeigen
@app.route("/")
def index():
    response = make_response(render_template("index.html"))
    response.headers["Content-Type"] = "text/html"
    return response

@app.route("/upload", methods=["POST"])
def upload():
    spec_file = request.files.get("spec")
    flow_file = request.files.get("file")
    disclaimer = request.form.get("disclaimer", "")

    if not spec_file or not flow_file:
        return "Missing files", 400

    # Debugging Output
    print("[UPLOAD] Files received:")
    print(f"- spec_file: {spec_file.filename}")
    print(f"- flow_file: {flow_file.filename}")
    print(f"- disclaimer: {disclaimer}")

    try:
        files = {
            "spec": (spec_file.filename, spec_file.stream, spec_file.mimetype),
            "file": (flow_file.filename, flow_file.stream, flow_file.mimetype)
        }
        data = {
            "disclaimer": disclaimer
        }

        n8n_url = "https://maxschira.app.n8n.cloud/webhook/generate-doc"
        print(f"[UPLOAD] Sending POST to {n8n_url}...")

        response = requests.post(n8n_url, files=files, data=data)

        print(f"[UPLOAD] n8n Response: {response.status_code}")
        if response.status_code != 200:
            print(response.text)
            return f"n8n returned an error: {response.text}", 500

        # Direkt zurück an Browser
        return send_file(io.BytesIO(response.content), download_name="filled_specification.docx", as_attachment=True)

    except Exception as e:
        print("[UPLOAD] Exception occurred:", e)
        return f"Error forwarding to n8n: {e}", 500

# Route 3: fill-doc – wird von n8n aufgerufen
@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        spec_file = request.files.get("spec")
        flow_file = request.files.get("file")
        disclaimer = request.form.get("disclaimer", "")

        if not spec_file or not flow_file:
            return "Missing files", 400

        # Spezifikation lesen und JSON extrahieren
        try:
            spec_data = json.load(spec_file)
        except Exception as e:
            return f"Invalid JSON in specification: {e}", 400

        spec_data["disclaimer"] = disclaimer

        # Flowchart vorbereiten
        images = convert_from_path(flow_file)
        image = images[0]
        img_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(img_tempfile.name, "PNG")

        # Dynamische Größenlogik
        width_px, height_px = image.size
        dpi = 300
        width_in = width_px / dpi
        height_in = height_px / dpi

        max_width = 5.9
        max_height = 6.7

        if width_in > height_in:
            flowchart_image = InlineImage(DocxTemplate("Extract_Template.docx"), img_tempfile.name, width=Inches(max_width))
        else:
            flowchart_image = InlineImage(DocxTemplate("Extract_Template.docx"), img_tempfile.name, height=Inches(max_height))

        spec_data["flowchart"] = flowchart_image

        # Template rendern
        doc = DocxTemplate("Extract_Template.docx")
        doc.render(spec_data)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        return send_file(output_path, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Error generating document: {e}", 500

# Route 4: Download – für zukünftige Erweiterungen
@app.route("/download")
def download_file():
    return send_file(os.path.join(UPLOAD_FOLDER, "filled_spec.docx"), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
