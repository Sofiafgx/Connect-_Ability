#!/usr/bin/env python3
"""
User Interface for Exoplanet Transit Detection
Allows users to input lightcurve data and get AI-powered analysis results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import json
import warnings
warnings.filterwarnings('ignore')

from main import ExoplanetDetectionPipeline
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class ExoplanetDetectorUI:
    """User interface for exoplanet detection system"""
    
    def __init__(self):
        self.pipeline = ExoplanetDetectionPipeline()
        self.current_data = None
        self.analysis_results = None
        
        # Initialize and train the AI model
        print("Initializing AI system...")
        self.pipeline.train_system(n_training_samples=100)
        print("AI system ready!")
        
        # Create GUI
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the graphical user interface"""
        self.root = tk.Tk()
        self.root.title("Exoplanet Transit Detector - AI Analysis")
        self.root.geometry("800x900")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Data Input
        self.input_frame = ttk.Frame(notebook)
        notebook.add(self.input_frame, text="Data Input")
        self.setup_input_tab()
        
        # Tab 2: Analysis Results
        self.results_frame = ttk.Frame(notebook)
        notebook.add(self.results_frame, text="Analysis Results")
        self.setup_results_tab()
        
        # Tab 3: Help & Examples
        self.help_frame = ttk.Frame(notebook)
        notebook.add(self.help_frame, text="Help & Examples")
        self.setup_help_tab()
    
    def setup_input_tab(self):
        """Setup the data input tab"""
        # Title
        title_label = ttk.Label(self.input_frame, text="🌟 Exoplanet Transit Detector", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Input method selection
        method_frame = ttk.LabelFrame(self.input_frame, text="Choose Input Method")
        method_frame.pack(fill='x', padx=10, pady=5)
        
        self.input_method = tk.StringVar(value="file")
        
        ttk.Radiobutton(method_frame, text="📁 Upload File (CSV/TXT)", 
                       variable=self.input_method, value="file").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(method_frame, text="✏️ Manual Entry", 
                       variable=self.input_method, value="manual").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(method_frame, text="🌐 From URL", 
                       variable=self.input_method, value="url").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(method_frame, text="🎲 Generate Demo Data", 
                       variable=self.input_method, value="demo").pack(anchor='w', padx=10, pady=2)
        
        # File upload section
        file_frame = ttk.LabelFrame(self.input_frame, text="File Upload")
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side='left', padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side='left', padx=5)
        
        # Manual entry section
        manual_frame = ttk.LabelFrame(self.input_frame, text="Manual Data Entry")
        manual_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(manual_frame, text="Enter data as: time,flux (one pair per line) or time flux flux_error").pack(anchor='w', padx=5)
        
        self.manual_text = scrolledtext.ScrolledText(manual_frame, height=10, width=70)
        self.manual_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # URL entry section
        url_frame = ttk.LabelFrame(self.input_frame, text="URL Input")
        url_frame.pack(fill='x', padx=10, pady=5)
        
        self.url_entry = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self.url_entry, width=70).pack(side='left', padx=5, pady=5)
        
        # Demo data options
        demo_frame = ttk.LabelFrame(self.input_frame, text="Demo Data Options")
        demo_frame.pack(fill='x', padx=10, pady=5)
        
        self.demo_type = tk.StringVar(value="with_transit")
        ttk.Radiobutton(demo_frame, text="With Transit Signal", 
                       variable=self.demo_type, value="with_transit").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(demo_frame, text="Without Transit (False Positive Test)", 
                       variable=self.demo_type, value="no_transit").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(demo_frame, text="Noisy Data", 
                       variable=self.demo_type, value="noisy").pack(anchor='w', padx=10, pady=2)
        
        # Action buttons
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="🔍 Analyze Data", 
                  command=self.analyze_data, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="📊 Preview Data", 
                  command=self.preview_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Clear", 
                  command=self.clear_data).pack(side='left', padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to analyze lightcurve data")
        status_bar = ttk.Label(self.input_frame, textvariable=self.status_var, 
                              relief='sunken', anchor='w')
        status_bar.pack(fill='x', side='bottom', padx=10, pady=5)
    
    def setup_results_tab(self):
        """Setup the results display tab"""
        # Results header
        header_frame = ttk.Frame(self.results_frame)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="🤖 AI Analysis Results", 
                 font=('Arial', 14, 'bold')).pack()
        
        # Main result display
        self.result_text = scrolledtext.ScrolledText(self.results_frame, height=15, width=80, 
                                                    font=('Consolas', 10))
        self.result_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Action buttons for results
        result_buttons = ttk.Frame(self.results_frame)
        result_buttons.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(result_buttons, text="📈 Show Plots", 
                  command=self.show_plots).pack(side='left', padx=5)
        ttk.Button(result_buttons, text="💾 Save Results", 
                  command=self.save_results).pack(side='left', padx=5)
        ttk.Button(result_buttons, text="📋 Copy to Clipboard", 
                  command=self.copy_results).pack(side='left', padx=5)
    
    def setup_help_tab(self):
        """Setup the help and examples tab"""
        help_text = """
🌟 EXOPLANET TRANSIT DETECTOR - USER GUIDE

📖 WHAT THIS TOOL DOES:
This AI-powered tool analyzes lightcurve data to detect exoplanet transits and distinguish them from false positives.

📊 INPUT DATA FORMATS:

1. CSV/TXT File Format:
   - Two columns: time, flux
   - Three columns: time, flux, flux_error
   - Header row optional
   - Example:
     time,flux
     0.0,1.0000
     0.1,0.9999
     0.2,0.9985  # <- transit dip

2. Manual Entry Format:
   - One line per data point
   - Formats: "time,flux" or "time flux" or "time flux error"
   - Example:
     0.0,1.0000
     0.1,0.9999
     0.2,0.9985

3. URL Input:
   - Direct link to CSV/TXT file
   - Must be publicly accessible

🎯 ANALYSIS OUTPUT:

The AI provides:
• Transit Detection: YES/NO with confidence percentage
• Orbital Period: Estimated planet orbital period (if detected)
• Transit Depth: How much the star dims during transit
• Signal Quality: Signal-to-noise ratio
• Artifact Assessment: Whether signal looks artificial

🔍 INTERPRETATION GUIDE:

Confidence Levels:
• 90-100%: Very likely genuine transit
• 70-89%: Probable transit, worth further investigation  
• 50-69%: Uncertain, could be false positive
• 30-49%: Unlikely to be transit
• 0-29%: Very unlikely, probably artifact

🚀 TIPS FOR BEST RESULTS:

1. Data Quality:
   - At least 1000 data points recommended
   - Continuous time coverage preferred
   - Include flux uncertainties if available

2. Time Coverage:
   - Longer observations better (weeks to months)
   - Multiple transit events improve detection

3. Data Preprocessing:
   - Remove obvious outliers manually if needed
   - Ensure time is in consistent units (days preferred)

📝 EXAMPLE DATA:

For testing, try these sample datasets:
• Demo with transit: Synthetic Kepler-like data with 10-day period planet
• Demo without transit: Pure stellar noise for false positive testing
• Noisy data: Challenging dataset with instrumental artifacts

🔬 TECHNICAL DETAILS:

The AI uses:
• Random Forest classification
• Advanced artifact removal algorithms
• Phase-folding transit search
• Box Least Squares periodogram
• Stellar variability modeling

⚠️ LIMITATIONS:

• Works best with space-based photometry quality
• May miss very small or grazing transits
• False positives possible with stellar activity
• Requires sufficient data coverage

📧 Need help? The AI provides detailed feedback on data quality and suggestions for improvement.
        """
        
        help_display = scrolledtext.ScrolledText(self.help_frame, wrap=tk.WORD, 
                                                font=('Arial', 10))
        help_display.pack(fill='both', expand=True, padx=10, pady=10)
        help_display.insert('1.0', help_text)
        help_display.config(state='disabled')
    
    def browse_file(self):
        """Open file browser for data selection"""
        filename = filedialog.askopenfilename(
            title="Select Lightcurve Data File",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
    
    def load_data(self):
        """Load data based on selected input method"""
        method = self.input_method.get()
        
        try:
            if method == "file":
                return self.load_from_file()
            elif method == "manual":
                return self.load_from_manual()
            elif method == "url":
                return self.load_from_url()
            elif method == "demo":
                return self.generate_demo_data()
            else:
                raise ValueError("Invalid input method selected")
                
        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Failed to load data:\n{str(e)}")
            return None
    
    def load_from_file(self):
        """Load data from file"""
        filepath = self.file_path.get().strip()
        if not filepath:
            raise ValueError("No file selected")
        
        # Try different delimiters and formats
        for delimiter in [',', '\t', ' ', ';']:
            try:
                data = pd.read_csv(filepath, delimiter=delimiter)
                if len(data.columns) >= 2:
                    break
            except:
                continue
        else:
            raise ValueError("Could not parse file format")
        
        return self.standardize_data_format(data)
    
    def load_from_manual(self):
        """Load data from manual text entry"""
        text_data = self.manual_text.get('1.0', tk.END).strip()
        if not text_data:
            raise ValueError("No manual data entered")
        
        # Parse the text data
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
                            flux_err_vals.append(0.0001)  # Default error
                        break
                    except ValueError:
                        continue
        
        if len(time_vals) < 10:
            raise ValueError("Need at least 10 data points")
        
        data = pd.DataFrame({
            'time': time_vals,
            'flux': flux_vals,
            'flux_err': flux_err_vals
        })
        
        return data
    
    def load_from_url(self):
        """Load data from URL"""
        url = self.url_entry.get().strip()
        if not url:
            raise ValueError("No URL provided")
        
        import requests
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse CSV data from URL
        data = pd.read_csv(StringIO(response.text))
        return self.standardize_data_format(data)
    
    def generate_demo_data(self):
        """Generate demonstration data"""
        demo_type = self.demo_type.get()
        
        # Generate base lightcurve
        time = np.linspace(0, 30, 3000)  # 30 days
        flux = np.ones_like(time)
        
        # Add noise
        noise_level = 0.0001 if demo_type != "noisy" else 0.001
        flux += np.random.normal(0, noise_level, len(time))
        
        # Add stellar variability
        stellar_period = 15.7
        flux += 0.005 * np.sin(2 * np.pi * time / stellar_period)
        
        if demo_type == "with_transit":
            # Add transit signal
            period = 8.3
            depth = 0.015
            duration = 0.15
            
            transit_times = np.arange(3, time.max(), period)
            for t_transit in transit_times:
                in_transit = np.abs(time - t_transit) < duration/2
                flux[in_transit] -= depth
        
        elif demo_type == "noisy":
            # Add some instrumental artifacts
            artifact_times = np.random.choice(time, size=20, replace=False)
            for at in artifact_times:
                mask = np.abs(time - at) < 0.05
                flux[mask] += np.random.normal(0, 0.01, np.sum(mask))
        
        data = pd.DataFrame({
            'time': time,
            'flux': flux,
            'flux_err': np.full_like(time, noise_level)
        })
        
        return data
    
    def standardize_data_format(self, data):
        """Standardize data format"""
        # Detect column names
        columns = data.columns.tolist()
        
        # Find time column
        time_col = None
        for col in columns:
            if any(keyword in col.lower() for keyword in ['time', 'bjd', 'mjd', 'jd', 'days']):
                time_col = col
                break
        if time_col is None:
            time_col = columns[0]
        
        # Find flux column
        flux_col = None
        for col in columns:
            if any(keyword in col.lower() for keyword in ['flux', 'mag', 'brightness', 'intensity']):
                flux_col = col
                break
        if flux_col is None:
            flux_col = columns[1]
        
        # Find error column (optional)
        err_col = None
        for col in columns:
            if any(keyword in col.lower() for keyword in ['err', 'error', 'sigma', 'uncertainty']):
                err_col = col
                break
        
        # Create standardized DataFrame
        standardized = pd.DataFrame({
            'time': data[time_col],
            'flux': data[flux_col],
            'flux_err': data[err_col] if err_col else np.full(len(data), 0.0001)
        })
        
        # Remove NaN values
        standardized = standardized.dropna()
        
        # Sort by time
        standardized = standardized.sort_values('time').reset_index(drop=True)
        
        return standardized
    
    def preview_data(self):
        """Preview loaded data"""
        data = self.load_data()
        if data is None:
            return
        
        self.current_data = data
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Data Preview")
        preview_window.geometry("800x600")
        
        # Data statistics
        stats_frame = ttk.LabelFrame(preview_window, text="Data Statistics")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        stats_text = f"""
Data Points: {len(data)}
Time Range: {data['time'].min():.3f} to {data['time'].max():.3f} days
Duration: {data['time'].max() - data['time'].min():.3f} days
Flux Range: {data['flux'].min():.6f} to {data['flux'].max():.6f}
Mean Flux: {data['flux'].mean():.6f}
RMS Noise: {data['flux'].std():.6f}
        """
        
        ttk.Label(stats_frame, text=stats_text, font=('Consolas', 10)).pack(padx=10, pady=5)
        
        # Data sample
        sample_frame = ttk.LabelFrame(preview_window, text="Data Sample (first 10 rows)")
        sample_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        sample_text = scrolledtext.ScrolledText(sample_frame, height=15, font=('Consolas', 9))
        sample_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        sample_text.insert('1.0', data.head(10).to_string(index=False))
        sample_text.config(state='disabled')
        
        self.status_var.set(f"Data loaded: {len(data)} points, {data['time'].max() - data['time'].min():.1f} day span")
    
    def analyze_data(self):
        """Main analysis function"""
        self.status_var.set("Loading data...")
        self.root.update()
        
        # Load data
        data = self.load_data()
        if data is None:
            return
        
        self.current_data = data
        
        # Validate data
        if len(data) < 100:
            messagebox.showwarning("Data Quality Warning", 
                                 "Less than 100 data points. Results may be unreliable.")
        
        self.status_var.set("Running AI analysis...")
        self.root.update()
        
        try:
            # Run through the analysis pipeline
            processed_data = self.pipeline.artifact_detector.remove_instrumental_artifacts(data)
            processed_data = self.pipeline.artifact_detector.detect_stellar_variability(processed_data)
            
            # Detect transits
            transit_result = self.pipeline.transit_detector.detect_transits(processed_data)
            
            # Store results
            self.analysis_results = {
                'data': processed_data,
                'transit_result': transit_result,
                'data_stats': self.calculate_data_statistics(data, processed_data)
            }
            
            # Display results
            self.display_results()
            
            self.status_var.set("Analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Analysis failed:\n{str(e)}")
            self.status_var.set("Analysis failed")
    
    def calculate_data_statistics(self, original_data, processed_data):
        """Calculate comprehensive data statistics"""
        stats = {
            'n_points': len(original_data),
            'time_span': original_data['time'].max() - original_data['time'].min(),
            'cadence': np.median(np.diff(original_data['time'])),
            'original_rms': original_data['flux'].std(),
            'processed_rms': processed_data['flux_stellar_corrected'].std(),
            'noise_reduction': 1 - (processed_data['flux_stellar_corrected'].std() / original_data['flux'].std()),
            'outlier_fraction': 1 - np.mean(processed_data['outlier_mask']),
            'stellar_period': processed_data.get('stellar_period', [None])[0] if 'stellar_period' in processed_data.columns else None
        }
        return stats
    
    def display_results(self):
        """Display analysis results in the results tab"""
        if not self.analysis_results:
            return
        
        tr = self.analysis_results['transit_result']
        stats = self.analysis_results['data_stats']
        
        # Format results text
        confidence_pct = tr['confidence'] * 100
        
        # Determine result interpretation
        if confidence_pct >= 90:
            interpretation = "🎯 VERY LIKELY EXOPLANET TRANSIT"
            color_code = "🟢"
        elif confidence_pct >= 70:
            interpretation = "🔍 PROBABLE TRANSIT - Investigate Further"
            color_code = "🟡"
        elif confidence_pct >= 50:
            interpretation = "⚠️ UNCERTAIN - Could be False Positive"
            color_code = "🟠"
        elif confidence_pct >= 30:
            interpretation = "❌ UNLIKELY TO BE TRANSIT"
            color_code = "🔴"
        else:
            interpretation = "❌ VERY UNLIKELY - Probably Artifact"
            color_code = "⚫"
        
        results_text = f"""
{color_code} AI EXOPLANET DETECTION RESULTS {color_code}
{'='*60}

🤖 DETECTION RESULT:
   Transit Detected: {"YES" if tr['has_transit'] else "NO"}
   Confidence: {confidence_pct:.1f}%
   
🎯 INTERPRETATION: {interpretation}

📊 SIGNAL CHARACTERISTICS:
   Estimated Period: {tr.get('period', 'N/A'):.3f} days
   Transit Depth: {tr.get('depth', 'N/A'):.4f} ({tr.get('depth', 0)*100:.2f}%)
   Signal-to-Noise: {tr.get('snr', 'N/A'):.2f}

📈 DATA QUALITY ASSESSMENT:
   Data Points: {stats['n_points']:,}
   Time Coverage: {stats['time_span']:.2f} days
   Observation Cadence: {stats['cadence']*24*60:.1f} minutes
   Original RMS Noise: {stats['original_rms']*1e6:.1f} ppm
   Processed RMS Noise: {stats['processed_rms']*1e6:.1f} ppm
   Noise Reduction: {stats['noise_reduction']*100:.1f}%
   Outlier Fraction: {stats['outlier_fraction']*100:.1f}%

⭐ STELLAR PROPERTIES:
   Detected Stellar Period: {stats['stellar_period']:.2f} days (rotation/variability)

🔬 DETAILED ANALYSIS:

Data Quality Score: {"EXCELLENT" if stats['n_points'] > 1000 and stats['time_span'] > 10 else "GOOD" if stats['n_points'] > 500 else "FAIR"}

Artifact Removal: {stats['outlier_fraction']*100:.1f}% of data flagged as outliers
Noise Performance: {stats['noise_reduction']*100:.1f}% noise reduction achieved

Transit Search Results:
- Searched {100} different periods from 1-50 days
- Best period candidate: {tr.get('period', 'N/A'):.3f} days
- Transit depth: {tr.get('depth', 0)*1e6:.0f} parts per million
- Signal strength: {tr.get('snr', 0):.1f} sigma detection

🎯 RECOMMENDATION:
"""

        if confidence_pct >= 90:
            results_text += """
✅ HIGH CONFIDENCE DETECTION
   This lightcurve shows strong evidence of exoplanet transits.
   Recommend follow-up observations for confirmation.
   
📋 Next Steps:
   • Verify period stability over longer baseline
   • Check for secondary eclipse (thermal emission)
   • Rule out stellar binary contamination
   • Consider radial velocity follow-up"""
        
        elif confidence_pct >= 70:
            results_text += """
🔍 PROMISING CANDIDATE
   Transit-like signal detected but requires validation.
   Could be genuine exoplanet or astrophysical false positive.
   
📋 Next Steps:
   • Obtain longer time-series data
   • Check for period variations
   • Analyze transit shape in detail
   • Consider ground-based photometry"""
        
        elif confidence_pct >= 50:
            results_text += """
⚠️ MARGINAL DETECTION
   Weak signal that could be instrumental or astrophysical.
   Low probability of being genuine exoplanet transit.
   
📋 Suggestions:
   • Improve data quality if possible
   • Check for systematic effects
   • Consider alternative explanations"""
        
        else:
            results_text += """
❌ NO CONVINCING TRANSIT SIGNAL
   Data does not show evidence of exoplanet transits.
   Any periodic signals likely due to stellar activity or systematics.
   
💡 Consider:
   • Different analysis techniques
   • Longer observation baseline
   • Higher precision photometry"""

        results_text += f"""

📊 STATISTICAL SUMMARY:
   False Positive Probability: {100-confidence_pct:.1f}%
   Detection Significance: {tr.get('snr', 0):.1f}σ
   
⏰ Analysis completed at: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 For questions about this analysis, refer to the Help tab.
        """
        
        # Display in results tab
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', results_text)
        
        # Switch to results tab
        for i, tab_id in enumerate(self.root.winfo_children()[0].tabs()):
            if "Analysis Results" in self.root.winfo_children()[0].tab(tab_id, "text"):
                self.root.winfo_children()[0].select(i)
                break
    
    def show_plots(self):
        """Show analysis plots"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analysis first")
            return
        
        data = self.analysis_results['data']
        tr = self.analysis_results['transit_result']
        
        # Create comprehensive plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Exoplanet Analysis Results - Confidence: {tr["confidence"]*100:.1f}%', fontsize=16)
        
        time = data['time'].values
        
        # Original vs processed lightcurve
        axes[0, 0].plot(time, data['flux'].values, 'k.', alpha=0.3, markersize=1, label='Original')
        axes[0, 0].plot(time, data['flux_stellar_corrected'].values, 'r-', alpha=0.7, linewidth=1, label='Processed')
        axes[0, 0].set_title('Lightcurve: Original vs Processed')
        axes[0, 0].set_ylabel('Relative Flux')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Phase-folded data (if transit detected)
        if tr['has_transit'] and tr.get('period'):
            period = tr['period']
            phase = ((time % period) / period - 0.5) * 24  # Convert to hours from mid-transit
            
            axes[0, 1].plot(phase, data['flux_stellar_corrected'].values, 'b.', alpha=0.5, markersize=2)
            axes[0, 1].set_title(f'Phase-Folded Transit (P={period:.3f}d)')
            axes[0, 1].set_xlabel('Hours from Mid-Transit')
            axes[0, 1].set_ylabel('Relative Flux')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Highlight transit region
            in_transit = np.abs(phase) < 2  # ±2 hours
            if np.any(in_transit):
                axes[0, 1].plot(phase[in_transit], data['flux_stellar_corrected'].values[in_transit], 
                               'r.', markersize=3, alpha=0.8, label='In Transit')
                axes[0, 1].legend()
        else:
            axes[0, 1].text(0.5, 0.5, 'No Transit Detected\nfor Phase Folding', 
                           ha='center', va='center', transform=axes[0, 1].transAxes, fontsize=12)
            axes[0, 1].set_title('Phase-Folded Data')
        
        # Residuals after processing
        residuals = data['flux_stellar_corrected'].values - np.median(data['flux_stellar_corrected'].values)
        axes[1, 0].plot(time, residuals * 1e6, 'g.', alpha=0.5, markersize=1)
        axes[1, 0].set_title(f'Residuals (RMS: {np.std(residuals)*1e6:.0f} ppm)')
        axes[1, 0].set_xlabel('Time (days)')
        axes[1, 0].set_ylabel('Residuals (ppm)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Detection confidence visualization
        confidence_data = [
            ('Transit\nDetected', tr['confidence'] * 100),
            ('False\nPositive', (1 - tr['confidence']) * 100)
        ]
        
        colors = ['green' if tr['has_transit'] else 'gray', 'red' if tr['has_transit'] else 'orange']
        bars = axes[1, 1].bar([0, 1], [cd[1] for cd in confidence_data], color=colors, alpha=0.7)
        axes[1, 1].set_title('Detection Confidence')
        axes[1, 1].set_ylabel('Probability (%)')
        axes[1, 1].set_xticks([0, 1])
        axes[1, 1].set_xticklabels([cd[0] for cd in confidence_data])
        axes[1, 1].set_ylim(0, 100)
        
        # Add percentage labels on bars
        for bar, (_, value) in zip(bars, confidence_data):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def save_results(self):
        """Save analysis results to file"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analysis first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Analysis Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    # Save as JSON
                    results_dict = {
                        'transit_result': self.analysis_results['transit_result'],
                        'data_statistics': self.analysis_results['data_stats'],
                        'analysis_timestamp': pd.Timestamp.now().isoformat()
                    }
                    with open(filename, 'w') as f:
                        json.dump(results_dict, f, indent=2, default=str)
                else:
                    # Save as text
                    with open(filename, 'w') as f:
                        f.write(self.result_text.get('1.0', tk.END))
                
                messagebox.showinfo("Save Successful", f"Results saved to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results:\n{str(e)}")
    
    def copy_results(self):
        """Copy results to clipboard"""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "Please run analysis first")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.result_text.get('1.0', tk.END))
            messagebox.showinfo("Copied", "Results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy results:\n{str(e)}")
    
    def clear_data(self):
        """Clear all data and results"""
        self.current_data = None
        self.analysis_results = None
        self.file_path.set("")
        self.url_entry.set("")
        self.manual_text.delete('1.0', tk.END)
        self.result_text.delete('1.0', tk.END)
        self.status_var.set("Data cleared - Ready for new analysis")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the user interface"""
    print("Starting Exoplanet Detection User Interface...")
    
    try:
        app = ExoplanetDetectorUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()