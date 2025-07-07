from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import json

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Template mapping for different product types
TEMPLATE_MAPPING = {
    "extract": "Extract_Template.docx",
    "powder": "Powder_Template.docx", 
    "synthetic": "Synthetisch_Template.docx",
    "demo": "Extract_Old_Template.docx"  # For demo backward compatibility
}

def extract_data_from_new_format(data):
    """
    Extract data from the new nested JSON format
    Since templates now use snake_case, we can use the data almost directly
    """
    # The new format has the actual data nested under 'extractedData'
    if isinstance(data, list) and len(data) > 1:
        extracted_data = data[1].get('extractedData', {})
    else:
        # Fallback for different structures
        extracted_data = data.get('extractedData', data)
    
    # Ensure all missing fields are empty strings to prevent template errors
    template_data = {}
    for key, value in extracted_data.items():
        template_data[key] = value if value is not None else ""
    
    return template_data

def process_document(product_type, data, flow_file=None):
    """
    Generic function to process documents for any product type
    """
    try:
        # Get the appropriate template
        template_filename = TEMPLATE_MAPPING.get(product_type)
        if not template_filename:
            return f"Unknown product type: {product_type}", 400
            
        # Check if template exists
        if not os.path.exists(template_filename):
            return f"Template not found: {template_filename}", 500
        
        # Process flowchart if provided
        flowchart_path = None
        if flow_file:
            pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(pdf_temp_path)
            images = convert_from_path(pdf_temp_path)
            img = images[0]

            img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
            img.save(img_path, "PNG")
            flowchart_path = img_path

        # Load template
        doc = DocxTemplate(template_filename)

        # Process flowchart image if available
        if flowchart_path:
            width_px, height_px = img.size
            dpi = 300
            width_in = width_px / dpi
            height_in = height_px / dpi
            max_width = 5.9
            max_height = 6.7

            if width_in > height_in:
                flow_img = InlineImage(doc, flowchart_path, width=Inches(max_width))
            else:
                flow_img = InlineImage(doc, flowchart_path, height=Inches(max_height))

            data["flowchart"] = flow_img
        else:
            data["flowchart"] = ""

        # Render document
        doc.render(data)
        output_path = os.path.join(UPLOAD_FOLDER, f"filled_{product_type}_spec.docx")
        doc.save(output_path)

        # Check for flags that would trigger warnings (both _flag and _Flag for compatibility)
        flags = [key for key in data if (key.endswith("_flag") or key.endswith("_Flag")) and data[key]]
        if flags:
            response = send_file(output_path, as_attachment=True)
            response.set_cookie("warning", "true")
            return response
        else:
            return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating document: {e}", 500

@app.route("/")
def index():
    response = make_response(render_template("index.html"))
    response.headers["Content-Type"] = "text/html"
    return response

# Legacy endpoint for demo compatibility
@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    """Legacy endpoint for demo - maintains backward compatibility"""
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)
        
        # Handle legacy format - if it's a list, take the first item
        if isinstance(spec_data, list):
            spec_data = spec_data[0]

        flow_file = request.files.get("file")
        
        return process_document("demo", spec_data, flow_file)

    except Exception as e:
        return f"Error generating document: {e}", 500

# New endpoints for different product types
@app.route("/fill-extract", methods=["POST"])
def fill_extract():
    """Endpoint for Extract products"""
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)
        
        # Transform new format to template format
        template_data = extract_data_from_new_format(spec_data)
        
        flow_file = request.files.get("file")
        
        return process_document("extract", template_data, flow_file)

    except Exception as e:
        return f"Error generating extract document: {e}", 500

@app.route("/fill-powder", methods=["POST"])
def fill_powder():
    """Endpoint for Powder products"""
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)
        
        # Transform new format to template format
        template_data = extract_data_from_new_format(spec_data)
        
        flow_file = request.files.get("file")
        
        return process_document("powder", template_data, flow_file)

    except Exception as e:
        return f"Error generating powder document: {e}", 500

@app.route("/fill-synthetic", methods=["POST"])
def fill_synthetic():
    """Endpoint for Synthetic products"""
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)
        
        # Transform new format to template format
        template_data = extract_data_from_new_format(spec_data)
        
        flow_file = request.files.get("file")
        
        return process_document("synthetic", template_data, flow_file)

    except Exception as e:
        return f"Error generating synthetic document: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
