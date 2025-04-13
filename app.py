from flask import Flask, request, send_file
from docxtpl import DocxTemplate
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
        raw_data = request.get_data(as_text=True)
        logging.info(" RAW REQUEST BODY:\n%s", raw_data)

        data = json.loads(raw_data)
        logging.info(" PARSED JSON:\n%s", data)

        if not isinstance(data, dict):
            return "Error: JSON is not a flat object", 400

        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        logging.exception(" ERROR during document generation:")
        return f"Error processing document: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
