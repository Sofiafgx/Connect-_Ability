#!/usr/bin/env python3
"""
Web Interface for Exoplanet Transit Detection
Flask-based web application for easy browser access
"""

from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json
import os
from werkzeug.utils import secure_filename
import tempfile

from main import ExoplanetDetectionPipeline

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/workspace/uploads'

# Global pipeline instance
pipeline = None

def initialize_pipeline():
    """Initialize the AI pipeline"""
    global pipeline
    if pipeline is None:
        print("Initializing AI pipeline...")
        pipeline = ExoplanetDetectionPipeline()
        pipeline.train_system(n_training_samples=100)
        print("AI pipeline ready!")

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_lightcurve():
    """Analyze uploaded lightcurve data"""
    initialize_pipeline()
    
    try:
        # Get data from different sources
        data = None
        source_info = ""
        
        if 'file' in request.files and request.files['file'].filename:
            # File upload
            file = request.files['file']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            data = load_data_from_file(filepath)
            source_info = f"File: {filename}"
            
        elif request.form.get('manual_data'):
            # Manual data entry
            manual_data = request.form.get('manual_data')
            data = parse_manual_data(manual_data)
            source_info = "Manual entry"
            
        elif request.form.get('demo_type'):
            # Demo data
            demo_type = request.form.get('demo_type')
            data = generate_demo_data(demo_type)
            source_info = f"Demo data: {demo_type}"
            
        else:
            return jsonify({'error': 'No data provided'}), 400
        
        if data is None or len(data) < 10:
            return jsonify({'error': 'Invalid or insufficient data (need at least 10 points)'}), 400
        
        # Run analysis
        results = run_analysis_pipeline(data)
        results['source_info'] = source_info
        results['data_preview'] = data.head(10).to_dict('records')
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/plot/<plot_type>')
def generate_plot(plot_type):
    """Generate analysis plots"""
    try:
        # This would typically store analysis results in session or database
        # For simplicity, generating demo plot
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if plot_type == 'lightcurve':
            # Generate demo lightcurve
            time = np.linspace(0, 30, 1000)
            flux = np.ones_like(time) + np.random.normal(0, 0.0001, len(time))
            
            # Add transit
            period = 10
            depth = 0.01
            transit_times = np.arange(5, 30, period)
            for t_transit in transit_times:
                in_transit = np.abs(time - t_transit) < 0.1
                flux[in_transit] -= depth
            
            ax.plot(time, flux, 'k.', markersize=1, alpha=0.7)
            ax.set_title('Lightcurve Data')
            ax.set_xlabel('Time (days)')
            ax.set_ylabel('Relative Flux')
            
        elif plot_type == 'phase_folded':
            # Phase-folded transit
            phase = np.linspace(-0.5, 0.5, 100)
            flux = np.ones_like(phase)
            in_transit = np.abs(phase) < 0.05
            flux[in_transit] -= 0.01
            flux += np.random.normal(0, 0.0005, len(phase))
            
            ax.plot(phase * 24, flux, 'b.', markersize=3)
            ax.set_title('Phase-Folded Transit')
            ax.set_xlabel('Hours from Mid-Transit')
            ax.set_ylabel('Relative Flux')
            
        ax.grid(True, alpha=0.3)
        
        # Convert plot to base64 string
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        
        return send_file(img_buffer, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        plt.close('all')

def load_data_from_file(filepath):
    """Load data from uploaded file"""
    try:
        # Try different delimiters
        for delimiter in [',', '\t', ' ', ';']:
            try:
                data = pd.read_csv(filepath, delimiter=delimiter)
                if len(data.columns) >= 2:
                    break
            except:
                continue
        else:
            raise ValueError("Could not parse file format")
        
        return standardize_data_format(data)
    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}")

def parse_manual_data(text_data):
    """Parse manually entered data"""
    lines = [line.strip() for line in text_data.split('\n') if line.strip()]
    
    time_vals = []
    flux_vals = []
    flux_err_vals = []
    
    for line in lines:
        # Try different separators
        for sep in [',', '\t', ' ']:
            parts = [p.strip() for p in line.split(sep) if p.strip()]
            if len(parts) >= 2:
                try:
                    time_vals.append(float(parts[0]))
                    flux_vals.append(float(parts[1]))
                    if len(parts) >= 3:
                        flux_err_vals.append(float(parts[2]))
                    else:
                        flux_err_vals.append(0.0001)
                    break
                except ValueError:
                    continue
    
    if len(time_vals) < 10:
        raise ValueError("Need at least 10 data points")
    
    return pd.DataFrame({
        'time': time_vals,
        'flux': flux_vals,
        'flux_err': flux_err_vals
    })

def generate_demo_data(demo_type):
    """Generate demonstration data"""
    time = np.linspace(0, 30, 2000)
    flux = np.ones_like(time)
    
    # Add noise
    noise_level = 0.0001 if demo_type != "noisy" else 0.001
    flux += np.random.normal(0, noise_level, len(time))
    
    # Add stellar variability
    flux += 0.005 * np.sin(2 * np.pi * time / 15.7)
    
    if demo_type == "with_transit":
        # Add transit
        period = 8.3
        depth = 0.012
        duration = 0.15
        
        transit_times = np.arange(3, time.max(), period)
        for t_transit in transit_times:
            in_transit = np.abs(time - t_transit) < duration/2
            flux[in_transit] -= depth
    
    elif demo_type == "noisy":
        # Add artifacts
        artifact_times = np.random.choice(time, size=15, replace=False)
        for at in artifact_times:
            mask = np.abs(time - at) < 0.05
            flux[mask] += np.random.normal(0, 0.008, np.sum(mask))
    
    return pd.DataFrame({
        'time': time,
        'flux': flux,
        'flux_err': np.full_like(time, noise_level)
    })

def standardize_data_format(data):
    """Standardize data format"""
    columns = data.columns.tolist()
    
    # Find time column
    time_col = columns[0]
    for col in columns:
        if any(keyword in col.lower() for keyword in ['time', 'bjd', 'mjd', 'jd', 'days']):
            time_col = col
            break
    
    # Find flux column
    flux_col = columns[1] if len(columns) > 1 else columns[0]
    for col in columns:
        if any(keyword in col.lower() for keyword in ['flux', 'mag', 'brightness']):
            flux_col = col
            break
    
    # Find error column
    err_col = None
    for col in columns:
        if any(keyword in col.lower() for keyword in ['err', 'error', 'sigma']):
            err_col = col
            break
    
    standardized = pd.DataFrame({
        'time': data[time_col],
        'flux': data[flux_col],
        'flux_err': data[err_col] if err_col else np.full(len(data), 0.0001)
    })
    
    return standardized.dropna().sort_values('time').reset_index(drop=True)

def run_analysis_pipeline(data):
    """Run the complete analysis pipeline"""
    global pipeline
    
    # Process data through pipeline
    processed_data = pipeline.artifact_detector.remove_instrumental_artifacts(data)
    processed_data = pipeline.artifact_detector.detect_stellar_variability(processed_data)
    
    # Detect transits
    transit_result = pipeline.transit_detector.detect_transits(processed_data)
    
    # Calculate statistics
    stats = {
        'n_points': len(data),
        'time_span': data['time'].max() - data['time'].min(),
        'cadence': np.median(np.diff(data['time'])),
        'original_rms': data['flux'].std(),
        'processed_rms': processed_data['flux_stellar_corrected'].std(),
        'noise_reduction': 1 - (processed_data['flux_stellar_corrected'].std() / data['flux'].std()),
        'outlier_fraction': 1 - np.mean(processed_data['outlier_mask']),
        'stellar_period': processed_data.get('stellar_period', [None])[0] if 'stellar_period' in processed_data.columns else None
    }
    
    # Format results
    confidence_pct = transit_result['confidence'] * 100
    
    # Determine interpretation
    if confidence_pct >= 90:
        interpretation = "VERY LIKELY EXOPLANET TRANSIT"
        recommendation = "High confidence detection. Recommend follow-up observations."
        status_class = "success"
    elif confidence_pct >= 70:
        interpretation = "PROBABLE TRANSIT"
        recommendation = "Promising candidate. Requires validation."
        status_class = "warning"
    elif confidence_pct >= 50:
        interpretation = "UNCERTAIN SIGNAL"
        recommendation = "Weak signal. Could be false positive."
        status_class = "info"
    else:
        interpretation = "UNLIKELY TO BE TRANSIT"
        recommendation = "No convincing transit signal detected."
        status_class = "danger"
    
    return {
        'transit_detected': transit_result['has_transit'],
        'confidence_percent': confidence_pct,
        'interpretation': interpretation,
        'recommendation': recommendation,
        'status_class': status_class,
        'period': transit_result.get('period'),
        'depth': transit_result.get('depth'),
        'snr': transit_result.get('snr'),
        'stats': stats,
        'analysis_timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# HTML Templates
@app.route('/templates/index.html')
def serve_template():
    """Serve the HTML template"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 Exoplanet Transit Detector</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 4rem 0;
        }
        .analysis-card {
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .analysis-card:hover {
            transform: translateY(-2px);
        }
        .confidence-meter {
            height: 20px;
            border-radius: 10px;
            background: #e9ecef;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        .result-success { background: linear-gradient(90deg, #28a745, #20c997); }
        .result-warning { background: linear-gradient(90deg, #ffc107, #fd7e14); }
        .result-info { background: linear-gradient(90deg, #17a2b8, #6f42c1); }
        .result-danger { background: linear-gradient(90deg, #dc3545, #e83e8c); }
        
        .data-input-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            margin: 2rem 0;
        }
        .spinner-border-sm {
            width: 1rem;
            height: 1rem;
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <div class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 mb-4">🌟 AI Exoplanet Transit Detector</h1>
            <p class="lead">Upload your lightcurve data and let our AI determine if it contains exoplanet transit signals</p>
            <p class="mb-0">Advanced artifact removal • Machine learning classification • Confidence scoring</p>
        </div>
    </div>

    <div class="container my-5">
        <!-- Input Section -->
        <div class="data-input-section">
            <h3 class="mb-4"><i class="fas fa-upload text-primary"></i> Data Input</h3>
            
            <!-- Navigation Tabs -->
            <ul class="nav nav-tabs" id="inputTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="file-tab" data-bs-toggle="tab" data-bs-target="#file-panel" type="button">
                        <i class="fas fa-file-upload"></i> File Upload
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="manual-tab" data-bs-toggle="tab" data-bs-target="#manual-panel" type="button">
                        <i class="fas fa-keyboard"></i> Manual Entry
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="demo-tab" data-bs-toggle="tab" data-bs-target="#demo-panel" type="button">
                        <i class="fas fa-play-circle"></i> Demo Data
                    </button>
                </li>
            </ul>

            <div class="tab-content mt-3" id="inputTabsContent">
                <!-- File Upload Panel -->
                <div class="tab-pane fade show active" id="file-panel">
                    <form id="fileForm" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="fileInput" class="form-label">Choose lightcurve file (CSV, TXT)</label>
                            <input type="file" class="form-control" id="fileInput" name="file" accept=".csv,.txt,.dat">
                            <div class="form-text">Supported formats: CSV with time,flux columns or space/tab separated values</div>
                        </div>
                    </form>
                </div>

                <!-- Manual Entry Panel -->
                <div class="tab-pane fade" id="manual-panel">
                    <div class="mb-3">
                        <label for="manualData" class="form-label">Enter data (time,flux per line)</label>
                        <textarea class="form-control" id="manualData" name="manual_data" rows="10" 
                                  placeholder="Example:
0.0,1.0000
0.1,0.9999
0.2,0.9985
..."></textarea>
                        <div class="form-text">Format: time,flux or time flux (one pair per line)</div>
                    </div>
                </div>

                <!-- Demo Data Panel -->
                <div class="tab-pane fade" id="demo-panel">
                    <div class="mb-3">
                        <label class="form-label">Select demo dataset</label>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="demo_type" id="demoTransit" value="with_transit" checked>
                            <label class="form-check-label" for="demoTransit">
                                <strong>With Transit Signal</strong> - Synthetic data containing exoplanet transit
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="demo_type" id="demoNoTransit" value="no_transit">
                            <label class="form-check-label" for="demoNoTransit">
                                <strong>Without Transit</strong> - Pure stellar noise for false positive testing
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="demo_type" id="demoNoisy" value="noisy">
                            <label class="form-check-label" for="demoNoisy">
                                <strong>Noisy Data</strong> - Challenging dataset with instrumental artifacts
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <div class="text-center mt-4">
                <button type="button" class="btn btn-primary btn-lg" id="analyzeBtn">
                    <i class="fas fa-search"></i> Analyze Data
                </button>
            </div>
        </div>

        <!-- Loading Indicator -->
        <div id="loadingIndicator" class="text-center my-5" style="display: none;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">🤖 AI is analyzing your data...</p>
        </div>

        <!-- Results Section -->
        <div id="resultsSection" style="display: none;">
            <div class="analysis-card card">
                <div class="card-header">
                    <h3 class="mb-0"><i class="fas fa-chart-line text-success"></i> Analysis Results</h3>
                </div>
                <div class="card-body">
                    <!-- Main Result -->
                    <div class="row mb-4">
                        <div class="col-md-8">
                            <div id="mainResult" class="alert" role="alert">
                                <h4 class="alert-heading" id="resultTitle">Detection Result</h4>
                                <p id="resultInterpretation" class="mb-2"></p>
                                <hr>
                                <p id="resultRecommendation" class="mb-0"></p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h5>Confidence Level</h5>
                                    <div class="confidence-meter mb-3">
                                        <div id="confidenceFill" class="confidence-fill"></div>
                                    </div>
                                    <h3 id="confidencePercent" class="text-primary">--%</h3>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Detailed Results -->
                    <div class="row">
                        <div class="col-md-6">
                            <h5><i class="fas fa-satellite text-info"></i> Transit Properties</h5>
                            <table class="table table-sm">
                                <tr><td>Transit Detected:</td><td id="transitDetected">-</td></tr>
                                <tr><td>Orbital Period:</td><td id="orbitalPeriod">-</td></tr>
                                <tr><td>Transit Depth:</td><td id="transitDepth">-</td></tr>
                                <tr><td>Signal-to-Noise:</td><td id="signalNoise">-</td></tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h5><i class="fas fa-chart-bar text-warning"></i> Data Quality</h5>
                            <table class="table table-sm">
                                <tr><td>Data Points:</td><td id="dataPoints">-</td></tr>
                                <tr><td>Time Coverage:</td><td id="timeCoverage">-</td></tr>
                                <tr><td>Noise Level:</td><td id="noiseLevel">-</td></tr>
                                <tr><td>Outliers Removed:</td><td id="outliersRemoved">-</td></tr>
                            </table>
                        </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="text-center mt-4">
                        <button type="button" class="btn btn-outline-primary" onclick="showPlots()">
                            <i class="fas fa-chart-line"></i> View Plots
                        </button>
                        <button type="button" class="btn btn-outline-success" onclick="downloadResults()">
                            <i class="fas fa-download"></i> Download Results
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Help Section -->
        <div class="mt-5">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-question-circle text-info"></i> How to Use This Tool</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>📊 Data Formats</h6>
                            <ul class="list-unstyled">
                                <li>• CSV with time,flux columns</li>
                                <li>• Space/tab separated values</li>
                                <li>• Optional flux error column</li>
                                <li>• Minimum 100 data points</li>
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <h6>🎯 Confidence Levels</h6>
                            <ul class="list-unstyled">
                                <li>• 90-100%: Very likely transit</li>
                                <li>• 70-89%: Probable transit</li>
                                <li>• 50-69%: Uncertain signal</li>
                                <li>• 0-49%: Unlikely transit</li>
                            </ul>
                        </div>
                        <div class="col-md-4">
                            <h6>🔬 AI Features</h6>
                            <ul class="list-unstyled">
                                <li>• Automatic artifact removal</li>
                                <li>• Stellar variability correction</li>
                                <li>• Period detection</li>
                                <li>• False positive filtering</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('analyzeBtn').addEventListener('click', function() {
            analyzeData();
        });

        async function analyzeData() {
            const loadingIndicator = document.getElementById('loadingIndicator');
            const resultsSection = document.getElementById('resultsSection');
            const analyzeBtn = document.getElementById('analyzeBtn');
            
            // Show loading
            loadingIndicator.style.display = 'block';
            resultsSection.style.display = 'none';
            analyzeBtn.disabled = true;
            
            try {
                const formData = new FormData();
                
                // Get active tab
                const activeTab = document.querySelector('.nav-link.active').id;
                
                if (activeTab === 'file-tab') {
                    const fileInput = document.getElementById('fileInput');
                    if (fileInput.files.length > 0) {
                        formData.append('file', fileInput.files[0]);
                    } else {
                        throw new Error('Please select a file');
                    }
                } else if (activeTab === 'manual-tab') {
                    const manualData = document.getElementById('manualData').value;
                    if (!manualData.trim()) {
                        throw new Error('Please enter data manually');
                    }
                    formData.append('manual_data', manualData);
                } else if (activeTab === 'demo-tab') {
                    const demoType = document.querySelector('input[name="demo_type"]:checked').value;
                    formData.append('demo_type', demoType);
                }
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Analysis failed');
                }
                
                const results = await response.json();
                displayResults(results);
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                loadingIndicator.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        }

        function displayResults(results) {
            const resultsSection = document.getElementById('resultsSection');
            const mainResult = document.getElementById('mainResult');
            
            // Set alert class based on status
            mainResult.className = `alert alert-${results.status_class}`;
            
            // Update main result
            document.getElementById('resultTitle').textContent = 
                results.transit_detected ? '✅ TRANSIT DETECTED' : '❌ NO TRANSIT DETECTED';
            document.getElementById('resultInterpretation').textContent = results.interpretation;
            document.getElementById('resultRecommendation').textContent = results.recommendation;
            
            // Update confidence meter
            const confidenceFill = document.getElementById('confidenceFill');
            const confidencePercent = document.getElementById('confidencePercent');
            
            confidenceFill.style.width = results.confidence_percent + '%';
            confidenceFill.className = `confidence-fill result-${results.status_class}`;
            confidencePercent.textContent = results.confidence_percent.toFixed(1) + '%';
            
            // Update detailed results
            document.getElementById('transitDetected').textContent = results.transit_detected ? 'YES' : 'NO';
            document.getElementById('orbitalPeriod').textContent = 
                results.period ? results.period.toFixed(3) + ' days' : 'N/A';
            document.getElementById('transitDepth').textContent = 
                results.depth ? (results.depth * 100).toFixed(3) + '%' : 'N/A';
            document.getElementById('signalNoise').textContent = 
                results.snr ? results.snr.toFixed(2) + 'σ' : 'N/A';
            
            // Update data quality
            document.getElementById('dataPoints').textContent = results.stats.n_points.toLocaleString();
            document.getElementById('timeCoverage').textContent = results.stats.time_span.toFixed(2) + ' days';
            document.getElementById('noiseLevel').textContent = (results.stats.processed_rms * 1e6).toFixed(0) + ' ppm';
            document.getElementById('outliersRemoved').textContent = (results.stats.outlier_fraction * 100).toFixed(1) + '%';
            
            // Show results
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }

        function showPlots() {
            // Open plots in new windows
            window.open('/plot/lightcurve', '_blank');
            window.open('/plot/phase_folded', '_blank');
        }

        function downloadResults() {
            // Create and download results file
            const resultsText = document.getElementById('resultsSection').innerText;
            const blob = new Blob([resultsText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'exoplanet_analysis_results.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    print("🌟 Starting Exoplanet Detection Web Interface...")
    print("🚀 Initializing AI system (this may take a moment)...")
    
    initialize_pipeline()
    
    print("✅ Ready! Open your browser and go to: http://localhost:5000")
    print("📊 Upload lightcurve data and get AI-powered exoplanet detection results!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)