import os
import io
import json
from flask import Flask, render_template, request
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

app = Flask(__name__)

CONFIG_FILE = "config.json"

def save_config(pdf_folder, image_path, output_folder):
    # Replace backward slashes with forward slashes in paths
    pdf_folder = pdf_folder.replace('\\', '/')
    image_path = image_path.replace('\\', '/')
    output_folder = output_folder.replace('\\', '/')
    
    config_data = {
        "pdf_folder": pdf_folder,
        "image_path": image_path,
        "output_folder": output_folder
    }
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config_data, config_file)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            config_data = json.load(config_file)
            pdf_folder = config_data.get("pdf_folder", "")
            image_path = config_data.get("image_path", "")
            output_folder = config_data.get("output_folder", "")
            # Replace backward slashes with forward slashes in paths
            pdf_folder = pdf_folder.replace('\\', '/')
            image_path = image_path.replace('\\', '/')
            output_folder = output_folder.replace('\\', '/')
            return pdf_folder, image_path, output_folder
    return "", "", ""

def add_image_to_pdf(pdf_folder, image_path, output_folder):
    img_width, img_height = 330, 70  # Adjust image size as needed
    prefix = "PIQYU_HEALTH_REPORT_" + datetime.now().strftime("%Y%m%d") + "_"

    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            input_pdf_path = os.path.join(pdf_folder, filename)
            output_pdf_path = os.path.join(output_folder, prefix + filename)

            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()

            for page in range(len(reader.pages)):
                page_width, page_height = map(int, reader.pages[page].mediabox.upper_right)
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                x = page_width - img_width-10
                y = page_height - img_height-8

                can.drawImage(image_path, x, y, width=img_width, height=img_height, mask='auto')
                can.save()

                packet.seek(0)
                new_pdf = PdfReader(packet)

                page_obj = reader.pages[page]
                page_obj.merge_page(new_pdf.pages[0])
                writer.add_page(page_obj)

            with open(output_pdf_path, 'wb') as f:
                writer.write(f)

    return "PQ Image is Patched to all the PDFs"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_folder = request.form['pdf_folder']
        image_path = request.form['image_path']
        output_folder = pdf_folder
        message = add_image_to_pdf(pdf_folder, image_path, output_folder)
        save_config(pdf_folder, image_path, output_folder)
        return render_template('index.html', message=message)
    else:
        pdf_folder, image_path, _ = load_config()
        return render_template('index.html', pdf_folder=pdf_folder, image_path=image_path)

if __name__ == '__main__':
    app.run(debug=True)
