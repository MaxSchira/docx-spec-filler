from flask import Flask, request, send_file
from docxtpl import DocxTemplate
import tempfile
import os
import json

app = Flask(__name__)

@app.route("/")
def health():
    return "Server is alive!"

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        # Form-Daten abrufen
        raw_json = request.form.get("data")
        if not raw_json:
            return "Missing 'data' in form submission", 400
        
        data = json.loads(raw_json)

        # Template laden und rendern
        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        # Temporäre Datei speichern und senden
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Error processing document: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
