from flask import Flask, request, render_template, send_file, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import os
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
        spec_file = request.files.get("spec")
        flow_file = request.files.get("file")

        if not spec_file or not flow_file:
            return "Missing files", 400

        # Spezifikation als JSON laden
        spec_data = json.loads(spec_file.read())

        # Flowchart verarbeiten
        flowchart_path = None
        pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
        flow_file.save(pdf_temp_path)
        images = convert_from_path(pdf_temp_path)
        img = images[0]
        img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
        img.save(img_path, "PNG")
        flowchart_path = img_path

        # Word-Dokument erzeugen
        doc = DocxTemplate("Extract_Template.docx")
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
        doc.render(spec_data)

        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating document: {e}", 500
