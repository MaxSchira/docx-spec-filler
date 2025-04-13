from flask import Flask, request, send_file
from docxtpl import DocxTemplate
import tempfile
import os

app = Flask(__name__)

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        data = request.get_json(force=True)  # <--- nimmt JSON Body direkt
        if not isinstance(data, dict):
            return "Invalid JSON structure", 400

        doc = DocxTemplate("Extract_Template.docx")
        doc.render(data)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Error processing document: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
