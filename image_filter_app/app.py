import os
from flask import Flask, render_template, request, url_for, session, redirect, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageEnhance,ImageFilter
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

DEFAULT_IMAGE = 'sample.png'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/filters', methods=['GET', 'POST'])
def filters():
    if 'current_image' not in session:
        session['current_image'] = DEFAULT_IMAGE
    
    filter_type = request.form.get('filter', 'none')
    uploaded_image = os.path.join(app.config['UPLOAD_FOLDER'], session['current_image'])
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                session['current_image'] = filename
                uploaded_image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if 'filter' in request.form:
            img = Image.open(uploaded_image)
            if filter_type == 'default':
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_none_{os.path.basename(uploaded_image)}')
            elif filter_type == 'grayscale':
                img = ImageOps.grayscale(img)
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_grayscale_{os.path.basename(uploaded_image)}')
            elif filter_type == 'brightness':
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.5)
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_brightness_{os.path.basename(uploaded_image)}')
            elif filter_type == 'contrast':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_contrast_{os.path.basename(uploaded_image)}')
            elif filter_type == 'saturate':
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.5)
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_saturate_{os.path.basename(uploaded_image)}')
            elif filter_type == 'hue-rotate':
                img = img.convert('RGB')
                r, g, b = img.split()
                img = Image.merge('RGB', (g, b, r))
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_hue_rotate_{os.path.basename(uploaded_image)}')
            elif filter_type == 'invert':
                img = ImageOps.invert(img.convert('RGB'))
                filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_invert_{os.path.basename(uploaded_image)}')
            #elif filter_type == 'blur':
                #img = img.filter(ImageFilter.BLUR)
                #filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_blur_{os.path.basename(uploaded_image)}')
                #img.save(filtered_image_path)
            #elif filter_type == 'edge_enhance':
                #img = img.filter(ImageFilter.EDGE_ENHANCE)
                #filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'filtered_edge_enhance_{os.path.basename(uploaded_image)}')
                #img.save(filtered_image_path)
               
            img.save(filtered_image_path)
            session['filtered_image'] = os.path.basename(filtered_image_path)
            uploaded_image = filtered_image_path
        
        if 'action' in request.form and request.form['action'] == 'save':
            return redirect(url_for('download_image', filename=session.get('filtered_image', session['current_image'])))
    
    uploaded_image_url = url_for('static', filename=f'uploads/{os.path.basename(uploaded_image)}')
    return render_template('filters.html', filter_type=filter_type, uploaded_image=uploaded_image_url)
@app.route('/real_time')
def real_time():
    return render_template('real_time.html')
@app.route('/save_photo', methods=['POST'])
def save_photo():
    if 'photo' in request.files:
        photo = request.files['photo']
        # Process the photo here (e.g., save it to disk, perform further operations)
        photo.save('static/uploads/image.png')
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'No image data received.'}), 400

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)