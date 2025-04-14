from flask import Flask, request, render_template, send_file, redirect, url_for
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        spec_file = request.files.get("specification")
        flow_file = request.files.get("flowchart")

        if not spec_file or spec_file.filename == "":
            return "No specification file uploaded", 400

        # Spezifikation lesen und JSON extrahieren
        try:
            spec_data = json.load(spec_file)
        except Exception as e:
            return f"Invalid JSON in specification: {e}", 400

        # Flowchart verarbeiten
        flowchart_path = None
        if flow_file:
            pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(pdf_temp_path)
            images = convert_from_path(pdf_temp_path)
            img = images[0]

            img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
            img.save(img_path, "PNG")
            flowchart_path = img_path

        # Word-Dokument erzeugen
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

        return redirect(url_for("download_file"))

    return render_template("index.html")

@app.route("/download")
def download_file():
    return send_file(os.path.join(UPLOAD_FOLDER, "filled_spec.docx"), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
