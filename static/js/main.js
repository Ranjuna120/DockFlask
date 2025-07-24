// JavaScript for DockFlask Pro

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('DockFlask Pro loaded successfully! 🐳');
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to cards on scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        });
        
        document.querySelectorAll('.card').forEach(card => {
            observer.observe(card);
        });
    }
});

// API Functions
async function checkHealth() {
    const responseDiv = document.getElementById('api-response');
    const button = event.target;
    
    // Add loading state
    button.classList.add('loading');
    button.disabled = true;
    
    responseDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Checking system health...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-heartbeat text-success"></i> Health Check Response
                    </h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Status:</strong> <span class="status-healthy">${data.status}</span></p>
                            <p><strong>Database:</strong> <span class="badge bg-${data.database === 'connected' ? 'success' : 'danger'}">${data.database}</span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Users:</strong> ${data.users_count}</p>
                            <p><strong>Current User:</strong> ${data.authenticated_user || 'Anonymous'}</p>
                        </div>
                    </div>
                    <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                    <p><strong>Message:</strong> ${data.message}</p>
                </div>
            </div>
        `;
    } catch (error) {
        responseDiv.innerHTML = `
            <div class="card api-response-card border-danger">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-exclamation-triangle text-danger"></i> Error
                    </h6>
                    <p class="status-error">Failed to fetch health status</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <small class="text-muted">Please check if the server is running.</small>
                </div>
            </div>
        `;
    } finally {
        // Remove loading state
        button.classList.remove('loading');
        button.disabled = false;
    }
}

async function getAppInfo() {
    const responseDiv = document.getElementById('api-response');
    const button = event.target;
    
    // Add loading state
    button.classList.add('loading');
    button.disabled = true;
    
    responseDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Fetching application information...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        
        responseDiv.innerHTML = `
            <div class="card api-response-card">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-info-circle text-info"></i> Application Information
                    </h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>App Name:</strong> ${data.app_name}</p>
                            <p><strong>Version:</strong> <span class="badge bg-primary">${data.version}</span></p>
                            <p><strong>Environment:</strong> <span class="badge bg-${data.environment === 'development' ? 'warning' : 'success'}">${data.environment}</span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Python Version:</strong> ${data.python_version}</p>
                            <p><strong>Database:</strong> ${data.database}</p>
                            <p><strong>Features:</strong></p>
                            <ul class="list-unstyled">
                                ${data.features.map(feature => `<li><i class="fas fa-check text-success"></i> ${feature}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        responseDiv.innerHTML = `
            <div class="card api-response-card border-danger">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fas fa-exclamation-triangle text-danger"></i> Error
                    </h6>
                    <p class="status-error">Failed to fetch app information</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                </div>
            </div>
        `;
    } finally {
        // Remove loading state
        button.classList.remove('loading');
        button.disabled = false;
    }
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Real-time character count for textareas
document.querySelectorAll('textarea').forEach(textarea => {
    const maxLength = textarea.getAttribute('maxlength');
    if (maxLength) {
        const counter = document.createElement('small');
        counter.className = 'text-muted form-text';
        counter.textContent = `0 / ${maxLength} characters`;
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const current = this.value.length;
            counter.textContent = `${current} / ${maxLength} characters`;
            counter.className = current > maxLength * 0.9 ? 'text-warning form-text' : 'text-muted form-text';
        });
    }
});

// Auto-save functionality for forms (draft saving)
function enableAutoSave(formId, saveUrl) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    let saveTimeout;
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveDraft(formId, saveUrl);
            }, 2000); // Save after 2 seconds of inactivity
        });
    });
}

async function saveDraft(formId, saveUrl) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    try {
        const response = await fetch(saveUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Draft': 'true'
            }
        });
        
        if (response.ok) {
            showNotification('Draft saved automatically', 'info');
        }
    } catch (error) {
        console.log('Draft save failed:', error);
    }
}

// Show notifications
function showNotification(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search');
    if (!searchInput) return;
    
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(this.value);
        }, 300);
    });
}

async function performSearch(query) {
    if (query.length < 2) return;
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

function displaySearchResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted">No results found.</p>';
        return;
    }
    
    resultsContainer.innerHTML = results.map(result => `
        <div class="search-result">
            <h6><a href="${result.url}">${result.title}</a></h6>
            <p class="text-muted small">${result.excerpt}</p>
        </div>
    `).join('');
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', initializeSearch);

// Export functions for global use
window.DockFlaskPro = {
    checkHealth,
    getAppInfo,
    validateForm,
    showNotification,
    copyToClipboard,
    enableAutoSave
};
