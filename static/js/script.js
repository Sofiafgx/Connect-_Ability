// Exoplanet Detection Interface JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resetBtn = document.getElementById('resetBtn');
    const exampleBtn = document.getElementById('exampleBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Example exoplanet data (based on typical confirmed exoplanet parameters)
    const exampleData = {
        confirmed: {
            orbital_period: 3.5234,
            transit_duration: 2.8,
            transit_depth: 850,
            planet_radius: 1.4,
            semi_major_axis: 0.045,
            eq_temperature: 1342,
            impact_parameter: 0.42,
            stellar_temp: 5778,
            stellar_radius: 0.98,
            stellar_mass: 0.95,
            stellar_magnitude: 12.3,
            snr: 18.5
        },
        candidate: {
            orbital_period: 5.7,
            transit_duration: 3.2,
            transit_depth: 450,
            planet_radius: 2.1,
            semi_major_axis: 0.062,
            eq_temperature: 980,
            impact_parameter: 0.58,
            stellar_temp: 5450,
            stellar_radius: 1.1,
            stellar_mass: 1.02,
            stellar_magnitude: 13.1,
            snr: 12.3
        },
        falsePositive: {
            orbital_period: 0.5,
            transit_duration: 0.8,
            transit_depth: 15000,
            planet_radius: 12.5,
            semi_major_axis: 0.012,
            eq_temperature: 2800,
            impact_parameter: 0.1,
            stellar_temp: 6200,
            stellar_radius: 1.5,
            stellar_mass: 1.3,
            stellar_magnitude: 11.5,
            snr: 8.2
        }
    };

    // Load example data
    exampleBtn.addEventListener('click', function() {
        // Randomly select an example
        const examples = ['confirmed', 'candidate', 'falsePositive'];
        const randomExample = examples[Math.floor(Math.random() * examples.length)];
        const data = exampleData[randomExample];

        // Populate form
        for (const [key, value] of Object.entries(data)) {
            const input = document.getElementById(key);
            if (input) {
                input.value = value;
            }
        }

        // Scroll to form
        form.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // Reset form
    resetBtn.addEventListener('click', function() {
        form.reset();
        resultsSection.style.display = 'none';
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Collect form data
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            data[key] = value || 0;
        }

        // Show loading overlay
        loadingOverlay.style.display = 'flex';

        try {
            // Make API request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                displayResults(result);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            alert('Network error: ' + error.message);
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    function displayResults(result) {
        const { prediction, probabilities } = result;

        // Update badge
        const badge = document.getElementById('resultBadge');
        badge.textContent = prediction;
        badge.className = 'result-badge';

        if (prediction === 'Confirmed Exoplanet') {
            badge.classList.add('confirmed');
        } else if (prediction === 'Planetary Candidate') {
            badge.classList.add('candidate');
        } else {
            badge.classList.add('false-positive');
        }

        // Update probability bars
        updateProbabilityBar('falsePositive', probabilities.false_positive);
        updateProbabilityBar('candidate', probabilities.candidate);
        updateProbabilityBar('confirmed', probabilities.confirmed);

        // Update interpretation
        updateInterpretation(prediction, probabilities);

        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function updateProbabilityBar(type, probability) {
        const percent = (probability * 100).toFixed(1);
        const bar = document.getElementById(`${type}Bar`);
        const percentText = document.getElementById(`${type}Percent`);

        bar.style.width = percent + '%';
        percentText.textContent = percent + '%';
    }

    function updateInterpretation(prediction, probabilities) {
        const interpretationDiv = document.getElementById('resultInterpretation');
        let interpretation = '';

        if (prediction === 'Confirmed Exoplanet') {
            const confidence = (probabilities.confirmed * 100).toFixed(1);
            interpretation = `
                <h4>✅ High Confidence Detection</h4>
                <p>The neural network has classified this transit signal as a <strong>Confirmed Exoplanet</strong> 
                with ${confidence}% confidence. The transit parameters are consistent with known exoplanet characteristics:</p>
                <ul style="margin-top: 10px; padding-left: 20px; color: var(--text-secondary);">
                    <li>Transit depth and duration match expected planetary transit patterns</li>
                    <li>Signal-to-noise ratio indicates a reliable detection</li>
                    <li>Planetary and stellar parameters fall within typical ranges for confirmed exoplanets</li>
                    <li>Low probability of false positive scenarios (eclipsing binaries, stellar activity)</li>
                </ul>
                <p style="margin-top: 15px; padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border-left: 3px solid var(--success-color);">
                    <strong>Recommendation:</strong> This target is an excellent candidate for follow-up observations 
                    and detailed characterization studies, including atmospheric analysis and mass determination.
                </p>
            `;
        } else if (prediction === 'Planetary Candidate') {
            const confidence = (probabilities.candidate * 100).toFixed(1);
            interpretation = `
                <h4>⚠️ Potential Planetary Candidate</h4>
                <p>The model has identified this as a <strong>Planetary Candidate</strong> with ${confidence}% confidence. 
                While the signal shows promise, further validation is needed:</p>
                <ul style="margin-top: 10px; padding-left: 20px; color: var(--text-secondary);">
                    <li>Transit signal has planetary-like characteristics but requires verification</li>
                    <li>Some parameters may be in borderline ranges</li>
                    <li>Additional observations would help rule out false positive scenarios</li>
                    <li>Signal strength and/or quality may need improvement for confirmation</li>
                </ul>
                <p style="margin-top: 15px; padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border-left: 3px solid var(--warning-color);">
                    <strong>Recommendation:</strong> Priority target for follow-up observations. Perform additional 
                    transit observations, check for false positive scenarios (eclipsing binaries, background objects), 
                    and conduct radial velocity measurements to confirm planetary nature.
                </p>
            `;
        } else {
            const confidence = (probabilities.false_positive * 100).toFixed(1);
            interpretation = `
                <h4>❌ Likely False Positive</h4>
                <p>The analysis indicates this is a <strong>False Positive</strong> with ${confidence}% confidence. 
                The transit signal likely originates from non-planetary sources:</p>
                <ul style="margin-top: 10px; padding-left: 20px; color: var(--text-secondary);">
                    <li>Signal characteristics inconsistent with genuine planetary transits</li>
                    <li>May be caused by eclipsing binary stars, blended sources, or instrumental artifacts</li>
                    <li>Parameters fall outside typical ranges for confirmed exoplanets</li>
                    <li>High likelihood of stellar activity or systematic noise</li>
                </ul>
                <p style="margin-top: 15px; padding: 15px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid var(--danger-color);">
                    <strong>Recommendation:</strong> Low priority for follow-up. If pursuing further, focus on 
                    understanding the source of the false positive signal (e.g., nearby eclipsing binary, 
                    background contaminant, or data processing artifacts).
                </p>
            `;
        }

        interpretationDiv.innerHTML = interpretation;
    }
});
