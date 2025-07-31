from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import os
import json
import zipfile
from datetime import datetime
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """Create uploads directory if it doesn't exist"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created {UPLOAD_FOLDER} directory")

def ensure_word_dir(word):
    """Create word-specific directory if it doesn't exist"""
    word_dir = os.path.join(UPLOAD_FOLDER, word)
    if not os.path.exists(word_dir):
        os.makedirs(word_dir)
        print(f"Created directory for word: {word}")
    return word_dir

def get_metadata_path(word):
    """Get the path to metadata file for a word"""
    return os.path.join(UPLOAD_FOLDER, word, 'metadata.json')

def load_metadata(word):
    """Load metadata for a word, create if doesn't exist"""
    metadata_path = get_metadata_path(word)
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'word': word,
            'videos': [],
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }

def save_metadata(word, metadata):
    """Save metadata for a word"""
    metadata_path = get_metadata_path(word)
    metadata['updatedAt'] = datetime.now().isoformat()
    metadata['totalVideos'] = len(metadata['videos'])
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

@app.route('/')
def index():
    """Serve the main HTML page"""
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/styles.css')
def styles():
    """Serve CSS file"""
    with open('styles.css', 'r') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/css'}

@app.route('/script.js')
def script():
    """Serve JavaScript file"""
    with open('script.js', 'r') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'application/javascript'}

@app.route('/debug')
def debug():
    """Serve debug page"""
    with open('debug.html', 'r') as f:
        return f.read()

@app.route('/developer')
def developer():
    """Serve developer dashboard"""
    with open('developer.html', 'r') as f:
        return f.read()

@app.route('/upload-video', methods=['POST'])
def upload_video():
    """Handle video upload"""
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form data
        word = request.form.get('word', '').strip().lower()
        video_index = request.form.get('videoIndex', '1')
        
        if not word:
            return jsonify({'error': 'Word is required'}), 400
        
        # Ensure directories exist
        ensure_upload_dir()
        word_dir = ensure_word_dir(word)
        
        # Generate filename with timestamp
        timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
        filename = f"{word}_video_{video_index}_{timestamp}.webm"
        filename = secure_filename(filename)
        
        # Save file
        file_path = os.path.join(word_dir, filename)
        file.save(file_path)
        
        # Update metadata
        metadata = load_metadata(word)
        video_info = {
            'index': int(video_index),
            'filename': filename,
            'originalName': file.filename,
            'size': os.path.getsize(file_path),
            'uploadedAt': datetime.now().isoformat(),
            'path': file_path
        }
        
        metadata['videos'].append(video_info)
        save_metadata(word, metadata)
        
        print(f"✅ VIDEO UPLOADED: {filename}")
        print(f"📁 Word: '{word}' | Video #{video_index} | Size: {os.path.getsize(file_path)} bytes")
        print(f"💾 Saved to: {file_path}")
        print(f"📊 Total videos for '{word}': {len(metadata['videos'])}")
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded successfully',
            'filename': filename,
            'word': word,
            'videoIndex': video_index,
            'totalVideos': len(metadata['videos'])
        })
        
    except Exception as e:
        print(f"Error uploading video: {str(e)}")
        return jsonify({'error': 'Failed to upload video'}), 500

@app.route('/api/word-stats/<word>')
def get_word_stats(word):
    """Get statistics for a specific word"""
    try:
        metadata = load_metadata(word)
        if not metadata['videos']:
            return jsonify({'error': 'Word not found'}), 404
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': 'Failed to get word stats'}), 500

@app.route('/api/words')
def list_words():
    """List all words with their video counts"""
    try:
        words = []
        
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify(words)
        
        for entry in os.listdir(UPLOAD_FOLDER):
            entry_path = os.path.join(UPLOAD_FOLDER, entry)
            if os.path.isdir(entry_path):
                word = entry
                try:
                    metadata = load_metadata(word)
                    words.append({
                        'word': word,
                        'videoCount': len(metadata['videos']),
                        'createdAt': metadata.get('createdAt'),
                        'updatedAt': metadata.get('updatedAt')
                    })
                except:
                    # If metadata doesn't exist, count files manually
                    video_files = [f for f in os.listdir(entry_path) 
                                 if f.endswith(('.webm', '.mp4', '.avi', '.mov'))]
                    words.append({
                        'word': word,
                        'videoCount': len(video_files),
                        'createdAt': None,
                        'updatedAt': None
                    })
        
        return jsonify(words)
        
    except Exception as e:
        print(f"Error listing words: {str(e)}")
        return jsonify({'error': 'Failed to list words'}), 500

@app.route('/api/download-word/<word>')
def download_word_videos(word):
    """Download all videos for a word as a ZIP file"""
    try:
        word_dir = os.path.join(UPLOAD_FOLDER, word)
        
        if not os.path.exists(word_dir):
            return jsonify({'error': 'Word not found'}), 404
        
        # Create temporary zip file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
            for filename in os.listdir(word_dir):
                if filename.endswith(('.webm', '.mp4', '.avi', '.mov')):
                    file_path = os.path.join(word_dir, filename)
                    zip_file.write(file_path, filename)
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=f'{word}_videos.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"Error creating zip: {str(e)}")
        return jsonify({'error': 'Failed to create zip file'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    ensure_upload_dir()
    print("Starting Word Video Recorder Server...")
    print(f"Videos will be organized in the '{UPLOAD_FOLDER}' folder by word")
    print("Each word will have its own folder with all videos")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)