from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import json
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    response = make_response(render_template("index.html"))
    response.headers["Content-Type"] = "text/html"
    return response

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        print("Eingehender Request empfangen")

        if "spec" not in request.files:
            print("Spezifikationsdatei fehlt!")
            return "No specification file uploaded", 400

        spec_file = request.files["spec"]
        flow_file = request.files.get("file")

        print(f"Spezifikationsdatei erhalten: {spec_file.filename}")
        if flow_file:
            print(f"Flowchart-Datei erhalten: {flow_file.filename}")

        webhook_url = "https://maxschira.app.n8n.cloud/webhook/generate-doc"
        files = {
            "spec": (spec_file.filename, spec_file.read(), spec_file.mimetype),
        }

        if flow_file:
            files["file"] = (flow_file.filename, flow_file.read(), flow_file.mimetype)

        response = requests.post(webhook_url, files=files)
        print("Anfrage an n8n gesendet")

        if response.status_code != 200:
            print("Fehler von n8n:", response.status_code, response.text)
            return "n8n returned error", 500

        output = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        output.write(response.content)
        output.close()
        print("Dokument erfolgreich empfangen und gespeichert")

        return send_file(output.name, as_attachment=True, download_name="filled_spec.docx")

    except Exception as e:
        print("Ausnahmefehler beim Verarbeiten:")
        import traceback
        traceback.print_exc()
        return f"Error processing request: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5050)), debug=True)
