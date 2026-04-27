import os
import threading
import webbrowser
import tempfile
import secrets
import shutil
import mimetypes
from io import BytesIO

from flask import Flask, request, jsonify, send_file
from werkzeug.datastructures import FileStorage
from converters import documents, images, pdf_tools, spreadsheets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'), static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

CONVERTER_MODULES = {
    'image': images,
    'document': documents,
    'spreadsheet': spreadsheets,
    'pdf': pdf_tools,
}

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'webp', 'bmp', 'docx', 'pptx', 'xlsx', 'pdf', 'csv'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def open_browser():
    webbrowser.open_new_tab('http://localhost:5000')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health')
def health():
    return jsonify(status="ok")

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify(error='Missing file upload'), 400

    converter_type = request.form.get('converter_type')
    if not converter_type:
        return jsonify(error='Missing converter_type'), 400

    target_format = request.form.get('target_format')
    if not target_format:
        return jsonify(error='Missing target_format'), 400

    converter_module = CONVERTER_MODULES.get(converter_type)
    if converter_module is None:
        return jsonify(error='Unsupported converter_type'), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify(error='No selected file'), 400
        
    if not allowed_file(uploaded_file.filename):
        return jsonify(error='File type not allowed'), 400

    # Step C: Create a UNIQUE, RANDOM temp directory using Python's secrets module
    temp_dir = tempfile.mkdtemp(prefix=secrets.token_hex(16) + '_')
    try:
        # Step D: Save the uploaded file there
        input_filename = uploaded_file.filename
        input_path = os.path.join(temp_dir, input_filename)
        uploaded_file.save(input_path)

        # Step E: Call the correct converter module
        output_path = converter_module.convert(input_path, target_format, temp_dir)
        
        # Step F: Read the output file into memory (as bytes)
        with open(output_path, 'rb') as f:
            file_data = f.read()
            
        output_filename = os.path.basename(output_path)
        mimetype, _ = mimetypes.guess_type(output_path)
        
        # Return response from memory
        return send_file(
            BytesIO(file_data),
            mimetype=mimetype or 'application/octet-stream',
            as_attachment=True,
            download_name=output_filename
        )
    except NotImplementedError as exc:
        return jsonify(error=str(exc)), 501
    except Exception as exc:
        return jsonify(error=str(exc)), 500
    finally:
        # Step G: IMMEDIATELY delete the entire temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify(error='File too large. Maximum size is 50MB.'), 413

def start_browser():
    threading.Timer(1.0, open_browser).start()

if __name__ == '__main__':
    start_browser()
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
