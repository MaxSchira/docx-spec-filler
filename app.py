from flask import Flask, request, send_file, render_template, make_response
import requests
import tempfile
import os

app = Flask(__name__)

N8N_WEBHOOK_URL = "https://maxschira.app.n8n.cloud/webhook/generate-doc"
UPLOAD_FOLDER = tempfile.gettempdir()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        spec_file = request.files.get("spec")
        flow_file = request.files.get("file")
        disclaimer = request.form.get("disclaimer", "")

        if not spec_file or not flow_file:
            return "Missing files", 400

        files = {
            "spec": (spec_file.filename, spec_file.stream, spec_file.mimetype),
            "file": (flow_file.filename, flow_file.stream, flow_file.mimetype)
        }
        data = {"disclaimer": disclaimer}

        response = requests.post(N8N_WEBHOOK_URL, files=files, data=data)
        if response.status_code != 200:
            return f"n8n Error: {response.text}", 500

        # Speichere DOCX-Datei temporär
        temp_path = os.path.join(UPLOAD_FOLDER, "result.docx")
        with open(temp_path, "wb") as f:
            f.write(response.content)

        return send_file(temp_path, as_attachment=True, download_name="filled_specification.docx")

    except Exception as e:
        return f"Bad request - please check your parameters\n{str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
