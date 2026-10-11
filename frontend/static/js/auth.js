// API Base URL
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Get access token
function getAccessToken() {
    return localStorage.getItem('access_token');
}

// Get refresh token
function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

// Get user data
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Get profile data
function getProfile() {
    const profile = localStorage.getItem('profile');
    return profile ? JSON.parse(profile) : null;
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAccessToken();
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('profile');
    window.location.href = 'login.html';
}

// Refresh access token
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();

    if (!refreshToken) {
        logout();
        return null;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return data.access;
        } else {
            logout();
            return null;
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        logout();
        return null;
    }
}

// Make authenticated API request
async function apiRequest(url, options = {}) {
    let token = getAccessToken();

    if (!token) {
        logout();
        throw new Error('Not authenticated');
    }

    // Set default headers
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    try {
        let response = await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            headers
        });

        // If unauthorized, try refreshing token
        if (response.status === 401) {
            token = await refreshAccessToken();

            if (token) {
                // Retry request with new token
                headers['Authorization'] = `Bearer ${token}`;
                response = await fetch(`${API_BASE_URL}${url}`, {
                    ...options,
                    headers
                });
            } else {
                throw new Error('Authentication failed');
            }
        }

        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Show alert message
function showAlert(container, message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    if (typeof container === 'string') {
        container = document.getElementById(container);
    }

    if (container) {
        container.innerHTML = '';
        container.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Initialize navigation
function initializeNav() {
    const user = getUser();
    const navProfile = document.getElementById('navProfile');
    const navLogout = document.getElementById('navLogout');
    const navLogin = document.getElementById('navLogin');
    const userName = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');

    if (user && isAuthenticated()) {
        if (navProfile) navProfile.style.display = 'block';
        if (navLogout) navLogout.style.display = 'block';
        if (navLogin) navLogin.style.display = 'none';
        if (userName) userName.textContent = user.username;

        if (logoutBtn) {
            logoutBtn.addEventListener('click', function (e) {
                e.preventDefault();
                logout();
            });
        }
    } else {
        if (navProfile) navProfile.style.display = 'none';
        if (navLogout) navLogout.style.display = 'none';
        if (navLogin) navLogin.style.display = 'block';
    }
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeNav();

    // Protect pages that require authentication
    const protectedPages = ['faculty-dashboard.html', 'student-dashboard.html', 'register-student.html',
        'generate-otp.html', 'view-attendance.html', 'mark-attendance.html', 'attendance-history.html'];

    const currentPage = window.location.pathname.split('/').pop();

    if (protectedPages.includes(currentPage) && !isAuthenticated()) {
        window.location.href = 'login.html';
    }

    // Redirect if already logged in
    if (currentPage === 'login.html' && isAuthenticated()) {
        const user = getUser();
        if (user.role === 'FACULTY') {
            window.location.href = 'faculty-dashboard.html';
        } else if (user.role === 'STUDENT') {
            window.location.href = 'student-dashboard.html';
        }
    }
});
