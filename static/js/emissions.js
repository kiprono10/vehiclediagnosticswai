// Auto Advisor - Emissions Prediction Functionality
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const predictionForm = document.getElementById('prediction-form');
    const resultSection = document.getElementById('prediction-result');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Engine size slider
    const engineSizeSlider = document.getElementById('engine-size');
    const engineSizeValue = document.getElementById('engine-size-value');
    
    // Year slider
    const yearSlider = document.getElementById('year');
    const yearValue = document.getElementById('year-value');
    
    // Update engine size display when slider changes
    if (engineSizeSlider && engineSizeValue) {
        engineSizeSlider.addEventListener('input', function() {
            engineSizeValue.textContent = engineSizeSlider.value;
        });
        // Initialize value display
        engineSizeValue.textContent = engineSizeSlider.value;
    }
    
    // Update year display when slider changes
    if (yearSlider && yearValue) {
        yearSlider.addEventListener('input', function() {
            yearValue.textContent = yearSlider.value;
        });
        // Initialize value display
        yearValue.textContent = yearSlider.value;
    }
    
    // Handle prediction form submission
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading spinner
            if (loadingSpinner) loadingSpinner.classList.remove('d-none');
            
            // Hide previous results
            if (resultSection) resultSection.innerHTML = '';
            
            // Get form data
            const formData = new FormData(predictionForm);
            
            // Send prediction request to server
            fetch('/predict_emissions', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
                
                // Display results
                if (data.error) {
                    showError(data.error);
                } else {
                    displayResults(data);
                }
            })
            .catch(error => {
                // Hide loading spinner
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
                
                console.error('Error:', error);
                showError("There was an error processing your request. Please try again.");
            });
        });
    }
    
    // Display error message
    function showError(message) {
        if (resultSection) {
            resultSection.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Error</h4>
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    // Display prediction results
    function displayResults(data) {
        if (!resultSection) return;
        
        // Get vehicle type and fuel type from form
        const vehicleType = document.getElementById('vehicle-type').value;
        const fuelType = document.getElementById('fuel-type').value;
        
        // Create result content
        const resultHTML = `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Emissions Prediction Results</h4>
                </div>
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3 text-center">
                            <div class="rating-badge rating-${data.rating}">${data.rating}</div>
                            <p class="mt-2">Emissions Rating</p>
                        </div>
                        <div class="col-md-9">
                            <h5>${capitalizeFirst(vehicleType)} - ${capitalizeFirst(fuelType)}</h5>
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Emission Type</th>
                                        <th>Value</th>
                                        <th>Unit</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>CO<sub>2</sub></td>
                                        <td>${data.co2}</td>
                                        <td>g/km</td>
                                    </tr>
                                    <tr>
                                        <td>NO<sub>x</sub></td>
                                        <td>${data.nox}</td>
                                        <td>g/km</td>
                                    </tr>
                                    <tr>
                                        <td>Particulate Matter</td>
                                        <td>${data.pm}</td>
                                        <td>g/km</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <h5>Recommendations to Improve Emissions</h5>
                    <ul class="list-group list-group-flush">
                        ${data.recommendations.map(rec => `<li class="list-group-item">${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        resultSection.innerHTML = resultHTML;
        
        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Helper function to capitalize first letter
    function capitalizeFirst(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
});
