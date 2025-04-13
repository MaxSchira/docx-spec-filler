from flask import Flask, request, send_file
from docxtpl import DocxTemplate
import tempfile
import os
import json

app = Flask(__name__)

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        # Nutze Form-Data Input
        raw_json = request.form.get("data")
        if not raw_json:
            return "Missing 'data' in form", 400

        data = json.loads(raw_json)

        # Template laden & befüllen
        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Error processing document: {str(e)}", 500

@app.route("/")
def health():
    return "Server is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
