from flask import Flask, request, render_template, send_file, jsonify
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
    return render_template("index.html")

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

        # Flowchart verarbeiten
        pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
        flow_file.save(pdf_temp_path)
        images = convert_from_path(pdf_temp_path)
        img = images[0]

        img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
        img.save(img_path, "PNG")

        # Word-Dokument erzeugen
        doc = DocxTemplate("Extract_Template.docx")

        width_px, height_px = img.size
        dpi = 300
        width_in = width_px / dpi
        height_in = height_px / dpi
        max_width = 5.9
        max_height = 6.7

        if width_in > height_in:
            flow_img = InlineImage(doc, img_path, width=Inches(max_width))
        else:
            flow_img = InlineImage(doc, img_path, height=Inches(max_height))

        spec_data["flowchart"] = flow_img
        spec_data["disclaimer"] = disclaimer

        doc.render(spec_data)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating document: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
