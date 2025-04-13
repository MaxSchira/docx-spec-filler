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
        # ----------- LOG RAW INPUT -----------
        raw_data = request.get_data(as_text=True)
        print("RAW REQUEST BODY:", raw_data)

        # ----------- PARSE JSON -----------
        data = json.loads(raw_data)
        print("PARSED JSON:", data)

        if not isinstance(data, dict):
            return "Error: JSON is not a flat object", 400

        # ----------- GENERATE DOCX -----------
        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        print("⚠️ ERROR:", str(e))
        return f"Error processing document: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
