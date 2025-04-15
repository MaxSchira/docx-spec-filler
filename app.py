from flask import Flask, request, send_file, make_response
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

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    spec_file = request.files.get("spec")
    flow_file = request.files.get("file")
    disclaimer = request.form.get("disclaimer", "")

    if not spec_file or not flow_file:
        return "Missing files", 400

    try:
        spec_data = json.load(spec_file)
    except Exception as e:
        return f"Invalid JSON in specification: {e}", 400

    # Temporäre Speicherung des Flowcharts
    pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
    flow_file.save(pdf_temp_path)

    try:
        images = convert_from_path(pdf_temp_path)
        img = images[0]
        img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
        img.save(img_path, "PNG")
    except Exception as e:
        return f"Flowchart processing failed: {e}", 500

    # Word-Dokument vorbereiten
    doc = DocxTemplate("Extract_Template.docx")

    # Bild dynamisch skalieren
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

@app.route("/", methods=["GET"])
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Flowchart Upload</title></head>
    <body>
        <h1>Upload Spec + Flowchart</h1>
        <form action="/fill-doc" method="post" enctype="multipart/form-data">
            <input type="file" name="spec" required><br><br>
            <input type="file" name="file" required><br><br>
            <textarea name="disclaimer" placeholder="Optional disclaimer text"></textarea><br><br>
            <input type="submit" value="Upload and Generate">
        </form>
    </body>
    </html>
    """
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
