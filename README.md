# Word Video Recorder

A web application that allows users to record exactly 10 videos (5 seconds each) for every word they want to capture. All videos are automatically organized into word-specific folders for easy access by developers.

## Features

- **5-Second Video Recording**: Each video is automatically limited to 5 seconds
- **10 Videos Per Word**: Users must record exactly 10 videos for each word
- **Automatic Organization**: Videos are saved in folders named after each word
- **Real-time Preview**: Live camera feed with recording countdown
- **Progress Tracking**: Visual progress indicator showing completion status
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Local Storage Backup**: Videos can be downloaded locally if server is unavailable
- **Metadata Tracking**: JSON files track video information and timestamps

## File Structure

```
word-video-recorder/
├── index.html          # Main web interface
├── styles.css          # Modern CSS styling
├── script.js           # Frontend JavaScript logic
├── app.py              # Python Flask backend server
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── uploads/            # Created automatically
    ├── word1/          # Folder for first word
    │   ├── word1_video_1_timestamp.webm
    │   ├── word1_video_2_timestamp.webm
    │   ├── ...
    │   ├── word1_video_10_timestamp.webm
    │   └── metadata.json
    ├── word2/          # Folder for second word
    │   ├── word2_video_1_timestamp.webm
    │   └── ...
    └── ...
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- A modern web browser with camera access
- Internet connection for initial setup

### Installation

1. **Clone or download the project files**
   ```bash
   # If you have the files, navigate to the project directory
   cd word-video-recorder
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if you prefer using a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the Flask server**
   ```bash
   python app.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Allow camera and microphone permissions when prompted

## How to Use

### For Users (Recording Videos)

1. **Enter a Word**
   - Type any word in the input field
   - Click "Start Recording for This Word" or press Enter

2. **Record Videos**
   - Your camera will activate automatically
   - Click "Start Recording" to begin a 5-second recording
   - The timer will count down from 5 to 0
   - Recording stops automatically after 5 seconds
   - Repeat until you have 10 videos

3. **Complete the Word**
   - After 10 videos, click "Finish This Word"
   - Or continue recording more videos if desired
   - Click "Record New Word" to start with a different word

### For Developers (Accessing Videos)

All videos are automatically organized in the `uploads/` folder:

- Each word gets its own folder (e.g., `uploads/hello/`)
- Videos are named with timestamps: `word_video_1_2024-01-15T10-30-45-123Z.webm`
- A `metadata.json` file tracks all video information
- Videos are in WebM format, compatible with most video players

### API Endpoints

The Flask server provides several useful endpoints:

- `GET /api/words` - List all words with video counts
- `GET /api/word-stats/<word>` - Get detailed stats for a specific word
- `GET /api/download-word/<word>` - Download all videos for a word as ZIP
- `POST /upload-video` - Upload endpoint (used by frontend)

## Technical Details

### Frontend Features
- **MediaRecorder API**: For video recording
- **getUserMedia API**: For camera access
- **Responsive Design**: Works on desktop and mobile
- **Progress Tracking**: Visual feedback for users
- **Local Storage**: Backup for completed words

### Backend Features
- **Flask**: Lightweight Python web framework
- **Werkzeug**: Secure file upload handling
- **Automatic Folder Creation**: Organizes videos by word
- **Metadata Generation**: JSON files with video information
- **CORS Support**: Cross-origin requests enabled
- **Error Handling**: Comprehensive error management

### Video Specifications
- **Duration**: Exactly 5 seconds (enforced)
- **Format**: WebM with VP9 codec
- **Resolution**: 640x480 (configurable)
- **Audio**: Included
- **Size Limit**: 50MB per video

## Troubleshooting

### Camera Not Working
- Ensure you've granted camera permissions
- Check if another application is using the camera
- Try refreshing the page
- Use HTTPS in production (required for camera access)

### Videos Not Uploading
- Check if the Flask server is running (`python app.py`)
- Verify network connection
- Videos will be available for manual download as backup

### Server Issues
- Ensure Python 3.7+ is installed
- Check if port 5000 is available
- Run `pip install -r requirements.txt` to install dependencies
- Check for any error messages in the terminal

### Python Virtual Environment Issues
If you encounter dependency conflicts:
```bash
python -m venv word_recorder_env
source word_recorder_env/bin/activate  # On Windows: word_recorder_env\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Customization

### Change Video Duration
Edit `script.js` line with `recordingTimeLeft = 5` and the timeout duration.

### Change Video Quality
Modify the `getUserMedia` constraints in `script.js`:
```javascript
video: { width: 1280, height: 720 } // Higher quality
```

### Change Server Port
Modify the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### Change Upload Directory
Modify the `UPLOAD_FOLDER` variable in `app.py`:
```python
UPLOAD_FOLDER = 'my_videos'  # Change folder name
```

## Browser Compatibility

- Chrome 60+ (Recommended)
- Firefox 55+
- Safari 11+
- Edge 79+

**Note**: Camera access requires HTTPS in production environments.

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up HTTPS** (required for camera access)
3. **Configure proper file permissions** for the uploads directory
4. **Set up proper logging** and error handling
5. **Consider using a reverse proxy** like Nginx

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: WSGI utilities and secure filename handling

## License

MIT License - Feel free to modify and distribute as needed.