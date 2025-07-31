class WordVideoRecorder {
    constructor() {
        this.currentWord = '';
        this.recordedVideos = [];
        this.mediaRecorder = null;
        this.stream = null;
        this.recordingTimer = null;
        this.countdownTimer = null;
        this.recordingTimeLeft = 5;
        this.completedWords = JSON.parse(localStorage.getItem('completedWords') || '[]');
        
        this.initializeElements();
        this.initializeEventListeners();
        this.loadCompletedWords();
    }

    initializeElements() {
        this.wordInput = document.getElementById('wordInput');
        this.startWordBtn = document.getElementById('startWordBtn');
        this.recordingSection = document.getElementById('recordingSection');
        this.currentWordSpan = document.getElementById('currentWord');
        this.videoCount = document.getElementById('videoCount');
        this.videoPreview = document.getElementById('videoPreview');
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.timer = document.getElementById('timer');
        this.videoList = document.getElementById('videoList');
        this.finishWordBtn = document.getElementById('finishWordBtn');
        this.newWordBtn = document.getElementById('newWordBtn');
        this.completedWordsList = document.getElementById('completedWordsList');
    }

    initializeEventListeners() {
        this.startWordBtn.addEventListener('click', () => this.startWordRecording());
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.finishWordBtn.addEventListener('click', () => this.finishWord());
        this.newWordBtn.addEventListener('click', () => this.startNewWord());
        
        this.wordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.startWordRecording();
            }
        });
    }

    async startWordRecording() {
        const word = this.wordInput.value.trim().toLowerCase();
        if (!word) {
            alert('Please enter a word');
            return;
        }

        this.currentWord = word;
        this.recordedVideos = [];
        this.currentWordSpan.textContent = word;
        this.updateVideoCount();
        
        // Hide word input and show recording section
        document.querySelector('.word-input-section').style.display = 'none';
        this.recordingSection.style.display = 'block';
        
        // Initialize camera
        await this.initializeCamera();
        this.clearVideoList();
    }

    async initializeCamera() {
        try {
            console.log('Requesting camera access...');
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: true
            });
            this.videoPreview.srcObject = this.stream;
            console.log('Camera initialized successfully');
            
            // Wait for video to load
            await new Promise((resolve) => {
                this.videoPreview.onloadedmetadata = resolve;
            });
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            let errorMessage = 'Error accessing camera. ';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Please grant camera permissions and reload the page.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No camera found on this device.';
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'Camera access is not supported in this browser.';
            } else {
                errorMessage += 'Please check your camera settings and try again.';
            }
            
            alert(errorMessage);
        }
    }

    startRecording() {
        if (!this.stream) {
            alert('Camera not initialized');
            return;
        }

        this.recordBtn.disabled = true;
        this.stopBtn.disabled = false;
        this.recordingTimeLeft = 5;
        this.timer.textContent = this.recordingTimeLeft;
        
        // Add recording animation
        this.videoPreview.classList.add('recording');

        // Initialize MediaRecorder with fallback options
        let options = {};
        if (MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
            options.mimeType = 'video/webm;codecs=vp9';
        } else if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8')) {
            options.mimeType = 'video/webm;codecs=vp8';
        } else if (MediaRecorder.isTypeSupported('video/webm')) {
            options.mimeType = 'video/webm';
        } else if (MediaRecorder.isTypeSupported('video/mp4')) {
            options.mimeType = 'video/mp4';
        }

        try {
            this.mediaRecorder = new MediaRecorder(this.stream, options);
            console.log('MediaRecorder initialized with:', options.mimeType || 'default settings');
        } catch (error) {
            console.error('Error creating MediaRecorder:', error);
            alert('Error initializing video recorder. Your browser may not support video recording.');
            this.recordBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.videoPreview.classList.remove('recording');
            return;
        }

        const chunks = [];
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = () => {
            const mimeType = options.mimeType || 'video/webm';
            const blob = new Blob(chunks, { type: mimeType });
            this.saveRecordedVideo(blob);
            this.videoPreview.classList.remove('recording');
        };

        this.mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event.error);
            alert('Recording error occurred: ' + event.error);
            this.stopRecording();
        };

        try {
            this.mediaRecorder.start();
            console.log('Recording started successfully');
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Failed to start recording: ' + error.message);
            this.recordBtn.disabled = false;
            this.stopBtn.disabled = true;
            this.videoPreview.classList.remove('recording');
            return;
        }

        // Start countdown timer
        this.countdownTimer = setInterval(() => {
            this.recordingTimeLeft--;
            this.timer.textContent = this.recordingTimeLeft;
            
            if (this.recordingTimeLeft <= 0) {
                this.stopRecording();
            }
        }, 1000);

        // Auto-stop after 5 seconds
        this.recordingTimer = setTimeout(() => {
            this.stopRecording();
        }, 5000);
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
        }

        clearTimeout(this.recordingTimer);
        clearInterval(this.countdownTimer);
        
        this.recordBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.timer.textContent = '5';
        this.videoPreview.classList.remove('recording');
    }

    saveRecordedVideo(blob) {
        const videoData = {
            timestamp: new Date().toISOString(),
            word: this.currentWord,
            index: this.recordedVideos.length + 1
        };

        this.recordedVideos.push(videoData);
        this.updateVideoCount();
        this.addVideoRecordConfirmation(videoData);
        
        // Send to server (this is the only place video is stored)
        this.uploadVideo(blob, this.currentWord, this.recordedVideos.length);

        // Check if we have 10 videos
        if (this.recordedVideos.length >= 10) {
            this.finishWordBtn.style.display = 'inline-block';
            this.recordBtn.disabled = true;
            alert('Great! You have recorded 10 videos for this word. You can finish this word or continue recording more.');
        }
    }

    async uploadVideo(blob, word, videoIndex) {
        const formData = new FormData();
        formData.append('video', blob, `${word}_video_${videoIndex}.webm`);
        formData.append('word', word);
        formData.append('videoIndex', videoIndex);

        // Update the upload status in the existing video item
        const statusElement = document.getElementById(`upload-status-${videoIndex}`);

        try {
            const response = await fetch('/upload-video', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Video uploaded successfully:', result.message);
                
                if (statusElement) {
                    statusElement.textContent = `✅ Uploaded to server successfully`;
                    statusElement.style.color = '#48bb78';
                    
                    // Show it's saved on server only
                    setTimeout(() => {
                        statusElement.textContent = `💾 Saved on developer's server`;
                        statusElement.style.color = '#4299e1';
                    }, 2000);
                }
                
            } else {
                const error = await response.json();
                console.error('Failed to upload video:', error.error);
                if (statusElement) {
                    statusElement.textContent = `✗ Upload failed: ${error.error}`;
                    statusElement.style.color = '#e53e3e';
                }
            }
        } catch (error) {
            console.error('Error uploading video:', error);
            if (statusElement) {
                statusElement.textContent = `✗ Upload error: ${error.message}`;
                statusElement.style.color = '#e53e3e';
            }
        }
        
        // Clear the blob from memory (don't store locally)
        blob = null;
    }

    // No local storage - videos are only saved on the server

    addVideoRecordConfirmation(videoData) {
        const videoItem = document.createElement('div');
        videoItem.className = 'video-item';
        videoItem.style.background = '#f0fff4';
        videoItem.style.border = '2px solid #9ae6b4';
        
        const info = document.createElement('p');
        info.textContent = `✅ Video ${videoData.index} recorded`;
        info.style.color = '#22543d';
        info.style.fontWeight = 'bold';
        info.style.margin = '0';
        
        const timestamp = document.createElement('small');
        timestamp.textContent = `Recorded at: ${new Date(videoData.timestamp).toLocaleTimeString()}`;
        timestamp.style.color = '#68d391';
        timestamp.style.display = 'block';
        timestamp.style.marginTop = '5px';
        
        const status = document.createElement('div');
        status.textContent = '📤 Uploading to server...';
        status.style.color = '#667eea';
        status.style.fontSize = '0.9rem';
        status.style.marginTop = '8px';
        status.id = `upload-status-${videoData.index}`;
        
        videoItem.appendChild(info);
        videoItem.appendChild(timestamp);
        videoItem.appendChild(status);
        
        this.videoList.appendChild(videoItem);
    }

    updateVideoCount() {
        this.videoCount.textContent = this.recordedVideos.length;
    }

    clearVideoList() {
        this.videoList.innerHTML = '';
    }

    finishWord() {
        if (this.recordedVideos.length < 10) {
            if (!confirm(`You have only recorded ${this.recordedVideos.length} videos. Are you sure you want to finish this word?`)) {
                return;
            }
        }

        // Add to completed words
        const completedWord = {
            word: this.currentWord,
            videoCount: this.recordedVideos.length,
            completedAt: new Date().toISOString()
        };

        this.completedWords.push(completedWord);
        localStorage.setItem('completedWords', JSON.stringify(this.completedWords));
        
        this.loadCompletedWords();
        this.newWordBtn.style.display = 'inline-block';
        this.finishWordBtn.style.display = 'none';
        this.recordBtn.disabled = true;

        alert(`Word "${this.currentWord}" completed with ${this.recordedVideos.length} videos!`);
    }

    startNewWord() {
        // Reset everything
        this.currentWord = '';
        this.recordedVideos = [];
        this.wordInput.value = '';
        
        // Stop camera stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        // Reset UI
        document.querySelector('.word-input-section').style.display = 'block';
        this.recordingSection.style.display = 'none';
        this.newWordBtn.style.display = 'none';
        this.finishWordBtn.style.display = 'none';
        this.recordBtn.disabled = false;
        
        this.clearVideoList();
    }

    loadCompletedWords() {
        this.completedWordsList.innerHTML = '';
        
        if (this.completedWords.length === 0) {
            this.completedWordsList.innerHTML = '<p style="color: #718096; font-style: italic;">No completed words yet.</p>';
            return;
        }

        this.completedWords.forEach(wordData => {
            const wordItem = document.createElement('div');
            wordItem.className = 'completed-word';
            
            wordItem.innerHTML = `
                <span>${wordData.word}</span>
                <small>${wordData.videoCount} videos - ${new Date(wordData.completedAt).toLocaleDateString()}</small>
            `;
            
            this.completedWordsList.appendChild(wordItem);
        });
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WordVideoRecorder();
});