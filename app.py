from flask import Flask, request, send_file
from docx import Document
import tempfile
import json
import os

app = Flask(__name__)

@app.route('/')
def health():
    return 'Server is alive!'

@app.route('/fill-doc', methods=['POST'])
def fill_doc():
    try:
        # Robust: JSON auslesen
        payload = request.get_json(force=True)
        if isinstance(payload, dict) and "data" in payload:
            data = payload["data"]
        else:
            try:
                payload_dict = json.loads(payload)
                data = payload_dict["data"]
            except Exception as e:
                print("Could not parse payload:", payload)
                return {"error": "Invalid JSON structure"}, 400

        print("=== Received Data ===")
        print(json.dumps(data, indent=2))

        # Template laden
        template_path = "00000_Specification_Extract Vorlage_V2.0.docx"
        doc = Document(template_path)

        # Ersetze Platzhalter in Absätzen
        for para in doc.paragraphs:
            for key, value in data.items():
                if key in para.text:
                    para.text = para.text.replace(key, str(value or ""))

        # Ersetze Platzhalter in Tabellenzellen
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for key, value in data.items():
                        if key in cell.text:
                            cell.text = cell.text.replace(key, str(value or ""))

        # Temporär speichern und senden
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            return send_file(tmp.name, as_attachment=True, download_name="demo_spec_filled.docx")

    except Exception as e:
        print("Unhandled server error:", str(e))
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
