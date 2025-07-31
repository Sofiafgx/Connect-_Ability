const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static('.'));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Create videos directory if it doesn't exist
const videosDir = path.join(__dirname, 'videos');
if (!fs.existsSync(videosDir)) {
    fs.mkdirSync(videosDir);
}

// Endpoint to upload and organize videos
app.post('/upload-video', upload.single('video'), (req, res) => {
    try {
        const { word, videoNumber } = req.body;
        const videoFile = req.file;

        if (!videoFile || !word) {
            return res.status(400).json({ error: 'Missing video file or word' });
        }

        // Create folder for the word if it doesn't exist
        const wordFolder = path.join(videosDir, word);
        if (!fs.existsSync(wordFolder)) {
            fs.mkdirSync(wordFolder, { recursive: true });
        }

        // Save the video file
        const filename = `video_${videoNumber || Date.now()}.webm`;
        const filepath = path.join(wordFolder, filename);
        
        fs.writeFileSync(filepath, videoFile.buffer);

        console.log(`Video saved: ${filepath}`);
        res.json({ 
            success: true, 
            message: `Video saved to ${word} folder`,
            filepath: filepath 
        });

    } catch (error) {
        console.error('Error saving video:', error);
        res.status(500).json({ error: 'Failed to save video' });
    }
});

// Endpoint to get folder structure
app.get('/videos-structure', (req, res) => {
    try {
        const structure = {};
        
        if (fs.existsSync(videosDir)) {
            const folders = fs.readdirSync(videosDir);
            
            folders.forEach(folder => {
                const folderPath = path.join(videosDir, folder);
                if (fs.statSync(folderPath).isDirectory()) {
                    const files = fs.readdirSync(folderPath);
                    structure[folder] = files.filter(file => file.endsWith('.webm'));
                }
            });
        }
        
        res.json(structure);
    } catch (error) {
        console.error('Error reading videos structure:', error);
        res.status(500).json({ error: 'Failed to read videos structure' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    console.log(`Videos will be saved to: ${videosDir}`);
});