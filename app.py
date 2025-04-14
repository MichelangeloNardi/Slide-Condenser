import os
from flask import Flask, request, render_template, send_file, after_this_request, jsonify
from werkzeug.utils import secure_filename
from pdf_condenser import PDFCondenser
import tempfile
import shutil
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def cleanup_file(filepath):
    """Remove file after sending it to the client"""
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"Error removing file {filepath}: {e}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview_changes():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    # Save the uploaded file
    input_filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)
    
    try:
        # Process the PDF to get preview information
        condenser = PDFCondenser(input_path)
        images = condenser.convert_pdf_to_images()
        similar_pairs = condenser.find_similar_slides(images)
        
        # Create preview information
        preview_data = {
            'total_slides': len(images),
            'slides_to_merge': len(similar_pairs),
            'merged_slides': [{'from': pair[0], 'to': pair[1]} for pair in similar_pairs],
            'final_slide_count': len(images) - len(similar_pairs)
        }
        
        # Clean up the input file
        cleanup_file(input_path)
        
        return jsonify(preview_data)
    
    except Exception as e:
        cleanup_file(input_path)
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    # Save the uploaded file
    input_filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(input_path)
    
    # Generate output filename
    output_filename = f"condensed_{input_filename}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        # Process the PDF
        condenser = PDFCondenser(input_path)
        num_merged = condenser.process_pdf(output_path)
        
        @after_this_request
        def cleanup(response):
            # Clean up input and output files
            cleanup_file(input_path)
            cleanup_file(output_path)
            return response
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # Clean up in case of error
        cleanup_file(input_path)
        cleanup_file(output_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 