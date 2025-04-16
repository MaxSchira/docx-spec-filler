@app.route("/fill-doc", methods=["POST"])
def fill_doc():
    try:
        spec_json = request.form.get("spec")
        spec_data = json.loads(spec_json)

        flow_file = request.files.get("file")
        flowchart_path = None

        if flow_file:
            pdf_temp_path = os.path.join(UPLOAD_FOLDER, "flowchart.pdf")
            flow_file.save(pdf_temp_path)
            images = convert_from_path(pdf_temp_path)
            img = images[0]

            img_path = os.path.join(UPLOAD_FOLDER, "flowchart.png")
            img.save(img_path, "PNG")
            flowchart_path = img_path

        doc = DocxTemplate("Extract_Template.docx")

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

            spec_data["flowchart"] = flow_img
        else:
            spec_data["flowchart"] = ""

        doc.render(spec_data)
        output_path = os.path.join(UPLOAD_FOLDER, "filled_spec.docx")
        doc.save(output_path)

        # WARNUNG ALS COOKIE MITGEBEN
        flags = [key for key in spec_data if key.endswith("_Flag") and spec_data[key]]
        if flags:
            response = send_file(output_path, as_attachment=True)
            response.set_cookie("warning", "true")
            return response
        else:
            return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating document: {e}", 500
