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
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: true
            });
            this.videoPreview.srcObject = this.stream;
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Error accessing camera. Please make sure you have granted camera permissions.');
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

        // Initialize MediaRecorder
        this.mediaRecorder = new MediaRecorder(this.stream, {
            mimeType: 'video/webm;codecs=vp9'
        });

        const chunks = [];
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'video/webm' });
            this.saveRecordedVideo(blob);
            this.videoPreview.classList.remove('recording');
        };

        this.mediaRecorder.start();

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
            blob: blob,
            url: URL.createObjectURL(blob),
            timestamp: new Date().toISOString(),
            word: this.currentWord,
            index: this.recordedVideos.length + 1
        };

        this.recordedVideos.push(videoData);
        this.updateVideoCount();
        this.addVideoToList(videoData);
        
        // Send to server
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

        try {
            const response = await fetch('/upload-video', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Video uploaded successfully:', result.message);
            } else {
                const error = await response.json();
                console.error('Failed to upload video:', error.error);
            }
        } catch (error) {
            console.error('Error uploading video:', error);
            // Store locally if server is not available
            this.storeVideoLocally(blob, word, videoIndex);
        }
    }

    storeVideoLocally(blob, word, videoIndex) {
        // Create a download link for local storage
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${word}_video_${videoIndex}.webm`;
        a.style.display = 'none';
        document.body.appendChild(a);
        
        // Auto-download (user will need to save manually)
        // This is a fallback when server is not available
        console.log(`Video ready for download: ${word}_video_${videoIndex}.webm`);
    }

    addVideoToList(videoData) {
        const videoItem = document.createElement('div');
        videoItem.className = 'video-item';
        
        const video = document.createElement('video');
        video.src = videoData.url;
        video.controls = true;
        video.muted = true;
        
        const info = document.createElement('p');
        info.textContent = `Video ${videoData.index}`;
        
        const downloadBtn = document.createElement('button');
        downloadBtn.textContent = 'Download';
        downloadBtn.style.fontSize = '0.8rem';
        downloadBtn.style.padding = '5px 10px';
        downloadBtn.onclick = () => {
            const a = document.createElement('a');
            a.href = videoData.url;
            a.download = `${this.currentWord}_video_${videoData.index}.webm`;
            a.click();
        };
        
        videoItem.appendChild(video);
        videoItem.appendChild(info);
        videoItem.appendChild(downloadBtn);
        
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