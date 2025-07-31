const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Create uploads directory if it doesn't exist
const createUploadsDir = async () => {
    try {
        await fs.access('uploads');
    } catch (error) {
        await fs.mkdir('uploads', { recursive: true });
        console.log('Created uploads directory');
    }
};

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const word = req.body.word;
        const wordDir = path.join('uploads', word);
        
        try {
            await fs.access(wordDir);
        } catch (error) {
            await fs.mkdir(wordDir, { recursive: true });
            console.log(`Created directory for word: ${word}`);
        }
        
        cb(null, wordDir);
    },
    filename: (req, file, cb) => {
        const word = req.body.word;
        const videoIndex = req.body.videoIndex;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `${word}_video_${videoIndex}_${timestamp}.webm`;
        cb(null, filename);
    }
});

const upload = multer({ 
    storage: storage,
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB limit
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('video/')) {
            cb(null, true);
        } else {
            cb(new Error('Only video files are allowed!'), false);
        }
    }
});

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle video upload
app.post('/upload-video', upload.single('video'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No video file uploaded' });
        }

        const { word, videoIndex } = req.body;
        const filePath = req.file.path;
        
        console.log(`Video uploaded: ${req.file.filename}`);
        console.log(`Word: ${word}, Video Index: ${videoIndex}`);
        console.log(`File saved to: ${filePath}`);

        // Create metadata file for the word if it doesn't exist
        const metadataPath = path.join('uploads', word, 'metadata.json');
        let metadata = {};
        
        try {
            const metadataContent = await fs.readFile(metadataPath, 'utf8');
            metadata = JSON.parse(metadataContent);
        } catch (error) {
            // File doesn't exist, create new metadata
            metadata = {
                word: word,
                videos: [],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
        }

        // Add video info to metadata
        const videoInfo = {
            index: parseInt(videoIndex),
            filename: req.file.filename,
            originalName: req.file.originalname,
            size: req.file.size,
            uploadedAt: new Date().toISOString(),
            path: filePath
        };

        metadata.videos.push(videoInfo);
        metadata.updatedAt = new Date().toISOString();
        metadata.totalVideos = metadata.videos.length;

        // Save updated metadata
        await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));

        res.json({
            success: true,
            message: 'Video uploaded successfully',
            filename: req.file.filename,
            word: word,
            videoIndex: videoIndex,
            totalVideos: metadata.totalVideos
        });

    } catch (error) {
        console.error('Error uploading video:', error);
        res.status(500).json({ error: 'Failed to upload video' });
    }
});

// Get word statistics
app.get('/api/word-stats/:word', async (req, res) => {
    try {
        const word = req.params.word;
        const metadataPath = path.join('uploads', word, 'metadata.json');
        
        const metadataContent = await fs.readFile(metadataPath, 'utf8');
        const metadata = JSON.parse(metadataContent);
        
        res.json(metadata);
    } catch (error) {
        res.status(404).json({ error: 'Word not found' });
    }
});

// List all words with their video counts
app.get('/api/words', async (req, res) => {
    try {
        const uploadsDir = 'uploads';
        const words = [];
        
        try {
            const entries = await fs.readdir(uploadsDir, { withFileTypes: true });
            
            for (const entry of entries) {
                if (entry.isDirectory()) {
                    const word = entry.name;
                    const metadataPath = path.join(uploadsDir, word, 'metadata.json');
                    
                    try {
                        const metadataContent = await fs.readFile(metadataPath, 'utf8');
                        const metadata = JSON.parse(metadataContent);
                        words.push({
                            word: word,
                            videoCount: metadata.totalVideos || 0,
                            createdAt: metadata.createdAt,
                            updatedAt: metadata.updatedAt
                        });
                    } catch (error) {
                        // If metadata doesn't exist, count files manually
                        const wordDir = path.join(uploadsDir, word);
                        const files = await fs.readdir(wordDir);
                        const videoFiles = files.filter(file => 
                            file.endsWith('.webm') || file.endsWith('.mp4')
                        );
                        
                        words.push({
                            word: word,
                            videoCount: videoFiles.length,
                            createdAt: null,
                            updatedAt: null
                        });
                    }
                }
            }
        } catch (error) {
            // uploads directory doesn't exist yet
            console.log('No uploads directory found');
        }
        
        res.json(words);
    } catch (error) {
        console.error('Error listing words:', error);
        res.status(500).json({ error: 'Failed to list words' });
    }
});

// Download all videos for a word as a zip file
app.get('/api/download-word/:word', async (req, res) => {
    try {
        const word = req.params.word;
        const wordDir = path.join('uploads', word);
        
        // Check if directory exists
        await fs.access(wordDir);
        
        const archiver = require('archiver');
        const archive = archiver('zip', { zlib: { level: 9 } });
        
        res.attachment(`${word}_videos.zip`);
        archive.pipe(res);
        
        // Add all video files to the archive
        const files = await fs.readdir(wordDir);
        for (const file of files) {
            if (file.endsWith('.webm') || file.endsWith('.mp4')) {
                const filePath = path.join(wordDir, file);
                archive.file(filePath, { name: file });
            }
        }
        
        archive.finalize();
        
    } catch (error) {
        console.error('Error creating zip:', error);
        res.status(500).json({ error: 'Failed to create zip file' });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'File too large' });
        }
    }
    
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// Initialize server
const startServer = async () => {
    await createUploadsDir();
    
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
        console.log(`Videos will be organized in the 'uploads' folder by word`);
        console.log(`Each word will have its own folder with all 10 videos`);
    });
};

startServer().catch(console.error);