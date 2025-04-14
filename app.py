from flask import Flask, request, send_file
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import os
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def health():
    return "Server is alive!"

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        # Log Rohdaten
        raw_data = request.get_data(as_text=True)
        logging.info("RAW REQUEST BODY:\n%s", raw_data)

        print("Form Data Keys:", request.form.keys())
        print("Form Data Content:", request.form)

        raw_json = request.form.get("data")
        if not raw_json:
            return "No 'data' field in form", 400

        logging.info("\nRAW JSON String:\n%s", raw_json)
        data = json.loads(raw_json)
        logging.info("PARSED JSON:\n%s", data)

        # Lade DOCX Template
        template = DocxTemplate("Extract_Template.docx")

        # FLOWCHART Verarbeitung
        uploaded_file = request.files.get("file")
        if uploaded_file:
            flowchart_path = "flowchart.pdf"
            uploaded_file.save(flowchart_path)
            logging.info(" Flowchart uploaded and saved: %s", uploaded_file.filename)
            logging.info(" Flowchart saved at: %s", os.path.abspath(flowchart_path))

            # Konvertiere PDF zu Bild
            images = convert_from_path(flowchart_path)
            logging.info(" PDF converted to %d image(s)", len(images))
            image = images[0]

            # Temporäre PNG-Datei speichern
            img_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            image.save(img_tempfile.name, "PNG")
            logging.info(" Flowchart image size: %s", image.size)

            # Dynamische Größenlogik
            width_px, height_px = image.size
            dpi = 300  # angenommene DPI
            width_in = width_px / dpi
            height_in = height_px / dpi

            max_width = 6.5
            max_height = 7

            if width_in > height_in:
                flowchart_image = InlineImage(template, img_tempfile.name, width=Inches(max_width))
            else:
                flowchart_image = InlineImage(template, img_tempfile.name, height=Inches(max_height))

            data["flowchart"] = flowchart_image
            logging.info(" InlineImage assigned to template")
        else:
            logging.warning(" No file uploaded with key 'file'")
            data["flowchart"] = ""

        # Template rendern
        template.render(data)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        template.save(tmp.name)

        return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        logging.exception("ERROR during document generation:")
        return f"Error processing document: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
