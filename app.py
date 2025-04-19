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

@app.route("/")
def index():
    response = make_response(render_template("index.html"))
    response.headers["Content-Type"] = "text/html"
    return response

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)

        flow_file = request.files.get("file")
        flowchart_path = None

        if flow_file:
            pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(pdf_temp_path)
            images = convert_from_path(pdf_temp_path)
            img = images[0]

            img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
            img.save(img_path, "PNG")
            flowchart_path = img_path

        doc = DocxTemplate("Extract_Template.docx")

        if flowchart_path:
            width_px, height_px = img.size
            dpi = 300
            width_in = width_px / dpi
            height_in = height_px / dpi
            max_width = 5.9
            max_height = 6.7

            if width_in > height_in:
                flow_img = InlineImage(doc, flowchart_path, width=Inches(max_width))
            else:
                flow_img = InlineImage(doc, flowchart_path, height=Inches(max_height))

            spec_data["flowchart"] = flow_img
        else:
            spec_data["flowchart"] = ""

        doc.render(spec_data)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        # WARNUNG ALS COOKIE MITGEBEN
        flags = [key for key in spec_data if key.endswith("_Flag") and spec_data[key]]
        if flags:
            response = send_file(output_path, as_attachment=True)
            response.set_cookie("warning", "true")
            return response
        else:
            flags = []
try:
    spec_data = json.loads(spec_json)
    if isinstance(spec_data, list):
        spec_data = spec_data[0]  # Nur erstes Objekt im Array verwenden
    for key, value in spec_data.items():
        if key.endswith("_Flag") and value is True:
            flags.append(key.replace("_Flag", ""))
except Exception as e:
    flags = []

# Konvertiere Dokument zu base64
encoded_file = base64.b64encode(document_stream.read()).decode("utf-8")
document_stream.seek(0)

# JSON-Antwort senden (Flags + base64-Dokument)
return jsonify({
    "flags": flags,
    "file": encoded_file
})

    except Exception as e:
        return f"Error generating document: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
