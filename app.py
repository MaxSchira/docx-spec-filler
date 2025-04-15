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

        if not spec_file or spec_file.filename == "":
            return "No specification file uploaded", 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as spec_temp:
            spec_file.save(spec_temp.name)
            spec_temp.seek(0)
            spec_json = json.load(spec_temp)

        # Flowchart vorbereiten
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

            spec_json["flowchart"] = flow_img
        else:
            spec_json["flowchart"] = ""

        doc.render(spec_json)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        return send_file(output_path, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Fehler bei der Dokumentgenerierung: {str(e)}", 500

@app.route("/download")
def download_file():
    return send_file(os.path.join(UPLOAD_FOLDER, "filled_spec.docx"), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
