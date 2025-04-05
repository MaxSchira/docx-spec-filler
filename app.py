from flask import Flask, request, send_file
from docx import Document
import tempfile
import json

app = Flask(__name__)

@app.route('/')
def health():
    return 'Server is alive!'

@app.route('/fill-doc', methods=['POST'])
def fill_doc():
    data = request.json["data"]
    template_path = "00000_Specification_Extract Vorlage_V2.0.docx"
    doc = Document(template_path)

    for para in doc.paragraphs:
        for key, value in data.items():
            if key in para.text:
                para.text = para.text.replace(key, value)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in data.items():
                    if key in cell.text:
                        cell.text = cell.text.replace(key, value)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        return send_file(tmp.name, as_attachment=True, download_name="demo_spec_filled.docx")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
