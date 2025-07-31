# Connect Ability - Video Recording Application

A web-based video recording application that captures 10 videos of 5 seconds each and organizes them into folders by word.

## Features

- **Clean Interface**: Modern UI with "Connect Ability" title and input field
- **Video Recording**: Records 5-second videos using your camera and microphone
- **Automatic Organization**: Creates folders for each word and saves videos accordingly
- **Progress Tracking**: Shows current video count and recording status
- **Purple "Start filming" Button**: Uses the specified color #7966c8
- **Grey "Go to next" Button**: Appears after each recording
- **Automatic File Management**: Server-side organization of video files

## Setup Instructions

### Prerequisites
- Node.js (version 14 or higher)
- A web browser with camera and microphone access
- Modern browser that supports MediaRecorder API

### Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start the Server**
   ```bash
   npm start
   ```
   
   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

3. **Open the Application**
   - Open your browser and go to `http://localhost:3000`
   - Allow camera and microphone permissions when prompted

## Usage Instructions

### Recording Videos

1. **Enter a Word**: Type any word in the input field (e.g., "hello", "goodbye", "thanks")

2. **Start Recording**: Click the purple "Start filming" button
   - The camera will activate and show your video feed
   - Recording automatically starts for 5 seconds
   - A countdown timer shows the remaining time

3. **Continue Recording**: After each video, click the grey "Go to next" button
   - This prepares the interface for the next recording
   - Repeat until you've recorded 10 videos

4. **View Results**: After completing all 10 videos, click "View Saved Videos" to see the organized structure

### File Organization

The application automatically creates the following structure:
```
videos/
├── [word1]/
│   ├── video_1.webm
│   ├── video_2.webm
│   └── ... (up to 10 videos)
├── [word2]/
│   ├── video_1.webm
│   └── ...
└── ...
```

Each word gets its own folder containing all the recorded videos for that word.

## Technical Details

### Frontend (index.html)
- Uses HTML5 MediaRecorder API for video capture
- Responsive design with modern CSS styling
- Real-time status updates and progress tracking
- Automatic 5-second recording timer

### Backend (server.js)
- Express.js server for handling file uploads
- Multer middleware for processing video files
- Automatic folder creation and file organization
- RESTful API endpoints for video management

### API Endpoints

- `POST /upload-video`: Uploads and saves video files
- `GET /videos-structure`: Returns the current folder/file structure

## Browser Compatibility

- Chrome 47+
- Firefox 29+
- Safari 14.1+
- Edge 79+

## Troubleshooting

### Camera Access Issues
- Ensure you've granted camera and microphone permissions
- Check if another application is using the camera
- Try refreshing the page and allowing permissions again

### Server Issues
- Make sure Node.js is installed correctly
- Check if port 3000 is available
- Verify all dependencies are installed with `npm install`

### Video Recording Problems
- Ensure your browser supports MediaRecorder API
- Check browser console for error messages
- Try using a different browser if issues persist

## File Formats

- Videos are saved in WebM format (.webm)
- Compatible with most modern browsers and media players
- Can be converted to other formats using tools like FFmpeg if needed

## Development

To modify the application:

1. **Frontend Changes**: Edit `index.html` for UI modifications
2. **Backend Changes**: Edit `server.js` for server-side functionality
3. **Styling**: CSS is embedded in the HTML file
4. **Dependencies**: Add new packages to `package.json`

## License

MIT License - Feel free to use and modify as needed.