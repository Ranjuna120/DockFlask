// JavaScript for DockFlask

// Function to check health endpoint
async function checkHealth() {
    const responseDiv = document.getElementById('api-response');
    responseDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">Health Check Response</h6>
                    <p class="status-healthy">Status: ${data.status}</p>
                    <p><strong>Timestamp:</strong> ${data.timestamp}</p>
                    <p><strong>Message:</strong> ${data.message}</p>
                </div>
            </div>
        `;
    } catch (error) {
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">Error</h6>
                    <p class="status-error">Failed to fetch health status</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                </div>
            </div>
        `;
    }
}

// Function to get app info
async function getAppInfo() {
    const responseDiv = document.getElementById('api-response');
    responseDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">Application Information</h6>
                    <p><strong>App Name:</strong> ${data.app_name}</p>
                    <p><strong>Version:</strong> ${data.version}</p>
                    <p><strong>Environment:</strong> ${data.environment}</p>
                    <p><strong>Python Version:</strong> ${data.python_version}</p>
                </div>
            </div>
        `;
    } catch (error) {
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">Error</h6>
                    <p class="status-error">Failed to fetch app information</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                </div>
            </div>
        `;
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('DockFlask loaded successfully! 🐳');
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
