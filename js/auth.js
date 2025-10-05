/**
 * Authentication service for AlphaWealth
 * Handles user authentication, session management, and API calls
 */

class AuthService {
    constructor() {
        this.currentUser = null;
        this.accessToken = null;
        this.apiBaseUrl = 'http://localhost:8788/api';
        this.init();
    }

    init() {
        // Check for existing session
        const storedToken = localStorage.getItem('supabase_access_token');
        const storedUser = localStorage.getItem('user_email');
        
        if (storedToken && storedUser) {
            this.accessToken = storedToken;
            this.currentUser = { email: storedUser };
            this.updateAuthState();
        }
    }

    async signUp(email, password, fullName = null) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    full_name: fullName
                })
            });

            const data = await response.json();

            if (data.success) {
                this.accessToken = data.session?.access_token;
                this.currentUser = data.user;
                
                // Store in localStorage
                localStorage.setItem('supabase_access_token', this.accessToken);
                localStorage.setItem('user_email', this.currentUser.email);
                
                this.updateAuthState();
                return { success: true, user: this.currentUser };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Sign up error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async signIn(email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/signin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });

            const data = await response.json();

            if (data.success) {
                this.accessToken = data.session?.access_token;
                this.currentUser = data.user;
                
                // Store in localStorage
                localStorage.setItem('supabase_access_token', this.accessToken);
                localStorage.setItem('user_email', this.currentUser.email);
                
                this.updateAuthState();
                return { success: true, user: this.currentUser };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Sign in error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async signOut() {
        try {
            if (this.accessToken) {
                await fetch(`${this.apiBaseUrl}/auth/signout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                });
            }
        } catch (error) {
            console.error('Sign out error:', error);
        } finally {
            // Clear local storage regardless of API call success
            this.accessToken = null;
            this.currentUser = null;
            localStorage.removeItem('supabase_access_token');
            localStorage.removeItem('user_email');
            this.updateAuthState();
        }
    }

    async getCurrentUser() {
        if (!this.accessToken) {
            return null;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/user`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.currentUser = data.user;
                localStorage.setItem('user_email', this.currentUser.email);
                return this.currentUser;
            } else {
                // Token is invalid, sign out
                await this.signOut();
                return null;
            }
        } catch (error) {
            console.error('Get current user error:', error);
            return null;
        }
    }

    async getProfile() {
        if (!this.accessToken) {
            return null;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/user/profile`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();

            if (data.success) {
                return data.profile;
            } else {
                return null;
            }
        } catch (error) {
            console.error('Get profile error:', error);
            return null;
        }
    }

    async updateProfile(updates) {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/user/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify(updates)
            });

            const data = await response.json();

            if (data.success) {
                return { success: true, profile: data.profile };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Update profile error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async signInWithGoogle() {
        try {
            // Import Supabase client dynamically
            const { createClient } = await import('https://cdn.skypack.dev/@supabase/supabase-js@2');
            
            // Create Supabase client with project credentials
            const supabase = createClient(
                'https://empxwjsdjszlvbplmtts.supabase.co',
                'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcHh3anNkanN6bHZicGxtdHRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk0NTExNTcsImV4cCI6MjA3NTAyNzE1N30.jXNKBJrapzqj2mEM1lhNdiC2ns2OoGvj3k43E9elSUE'
            );
            
            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback.html`
                }
            });

            if (error) {
                console.error('Google OAuth error:', error);
                return { success: false, error: error.message };
            }

            // Redirect to Google OAuth
            if (data.url) {
                window.location.href = data.url;
            } else {
                return { success: false, error: 'No OAuth URL received' };
            }
        } catch (error) {
            console.error('Google sign-in error:', error);
            return { success: false, error: 'Failed to initialize Google OAuth' };
        }
    }

    // 2FA Methods
    async enrollMFA() {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/mfa/enroll`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('MFA enrollment error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async verifyMFA(factorId, challengeId, code) {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/mfa/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify({
                    factorId,
                    challengeId,
                    code
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('MFA verification error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async getMFAFactors() {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/mfa/factors`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Get MFA factors error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async getAuthenticatorAssuranceLevel() {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/mfa/aal`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Get AAL error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async createPortfolio(name, description = null) {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/portfolios`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify({
                    name,
                    description
                })
            });

            const data = await response.json();

            if (data.success) {
                return { success: true, portfolio: data.portfolio };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Create portfolio error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    async getPortfolios() {
        if (!this.accessToken) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/portfolios`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            const data = await response.json();

            if (data.success) {
                return { success: true, portfolios: data.portfolios };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Get portfolios error:', error);
            return { success: false, error: 'Network error occurred' };
        }
    }

    isAuthenticated() {
        return this.accessToken !== null && this.currentUser !== null;
    }

    getAuthHeaders() {
        if (!this.accessToken) {
            return {};
        }
        return {
            'Authorization': `Bearer ${this.accessToken}`
        };
    }

    updateAuthState() {
        // Update UI based on authentication state
        const authElements = document.querySelectorAll('[data-auth]');
        authElements.forEach(element => {
            const authAction = element.dataset.auth;
            const isLoggedIn = this.isAuthenticated();
            
            switch (authAction) {
                case 'show-if-logged-in':
                    element.style.display = isLoggedIn ? '' : 'none';
                    break;
                case 'show-if-logged-out':
                    element.style.display = isLoggedIn ? 'none' : '';
                    break;
                case 'enable-if-logged-in':
                    element.disabled = !isLoggedIn;
                    break;
            }
        });

        // Update user info in UI
        const userEmailElements = document.querySelectorAll('[data-user-info="email"]');
        userEmailElements.forEach(element => {
            if (this.currentUser) {
                element.textContent = this.currentUser.email;
            }
        });

        // Trigger custom event for other components
        document.dispatchEvent(new CustomEvent('authStateChanged', {
            detail: {
                isAuthenticated: this.isAuthenticated(),
                user: this.currentUser
            }
        }));
    }
}

// Global auth service instance
const authService = new AuthService();

// Authentication UI components
class AuthUI {
    constructor() {
        this.authService = authService;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Sign up form
        const signUpForm = document.getElementById('signup-form');
        if (signUpForm) {
            signUpForm.addEventListener('submit', this.handleSignUp.bind(this));
        }

        // Sign in form
        const signInForm = document.getElementById('signin-form');
        if (signInForm) {
            signInForm.addEventListener('submit', this.handleSignIn.bind(this));
        }

        // Sign out button
        const signOutBtn = document.getElementById('signout-btn');
        if (signOutBtn) {
            signOutBtn.addEventListener('click', this.handleSignOut.bind(this));
        }

        // Google sign-in buttons
        const googleSignInBtn = document.getElementById('google-signin-btn');
        const googleSignUpBtn = document.getElementById('google-signup-btn');
        
        if (googleSignInBtn) {
            googleSignInBtn.addEventListener('click', this.handleGoogleSignIn.bind(this));
        }
        
        if (googleSignUpBtn) {
            googleSignUpBtn.addEventListener('click', this.handleGoogleSignIn.bind(this));
        }

        // Listen for auth state changes
        document.addEventListener('authStateChanged', this.handleAuthStateChange.bind(this));
    }

    async handleSignUp(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const email = formData.get('email');
        const password = formData.get('password');
        const fullName = formData.get('fullName');

        const result = await this.authService.signUp(email, password, fullName);

        if (result.success) {
            this.showMessage('Account created successfully!', 'success');
            this.hideAuthModal();
        } else {
            this.showMessage(result.error, 'error');
        }
    }

    async handleSignIn(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const email = formData.get('email');
        const password = formData.get('password');

        const result = await this.authService.signIn(email, password);

        if (result.success) {
            this.showMessage('Signed in successfully!', 'success');
            this.hideAuthModal();
        } else {
            this.showMessage(result.error, 'error');
        }
    }

    async handleSignOut() {
        await this.authService.signOut();
        this.showMessage('Signed out successfully!', 'success');
    }

    async handleGoogleSignIn() {
        const result = await this.authService.signInWithGoogle();
        if (!result.success) {
            this.showMessage(result.error, 'error');
        }
        // If successful, the user will be redirected to Google OAuth
    }

    handleAuthStateChange(event) {
        const { isAuthenticated, user } = event.detail;
        
        // Update navigation
        this.updateNavigation(isAuthenticated);
        
        // Update user info
        if (isAuthenticated && user) {
            this.updateUserInfo(user);
        }
    }

    updateNavigation(isAuthenticated) {
        const navItems = document.querySelectorAll('[data-nav-item]');
        navItems.forEach(item => {
            const requiresAuth = item.dataset.requiresAuth === 'true';
            if (requiresAuth) {
                item.style.display = isAuthenticated ? '' : 'none';
            }
        });
    }

    updateUserInfo(user) {
        const userElements = document.querySelectorAll('[data-user-info]');
        userElements.forEach(element => {
            const infoType = element.dataset.userInfo;
            switch (infoType) {
                case 'email':
                    element.textContent = user.email;
                    break;
                case 'name':
                    element.textContent = user.user_metadata?.full_name || user.email.split('@')[0];
                    break;
            }
        });
    }

    showAuthModal(type = 'signin') {
        // Toggle between sign in and sign up forms
        const signInForm = document.getElementById('signin-form');
        const signUpForm = document.getElementById('signup-form');
        const modal = document.getElementById('auth-modal');

        if (modal) {
            if (type === 'signin') {
                signInForm?.style.setProperty('display', 'block');
                signUpForm?.style.setProperty('display', 'none');
            } else {
                signInForm?.style.setProperty('display', 'none');
                signUpForm?.style.setProperty('display', 'block');
            }
            modal.style.display = 'block';
        }
    }

    hideAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showMessage(message, type = 'info') {
        // Create or update message element
        let messageEl = document.getElementById('auth-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'auth-message';
            messageEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 4px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                max-width: 300px;
                word-wrap: break-word;
            `;
            document.body.appendChild(messageEl);
        }

        messageEl.textContent = message;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                messageEl.style.backgroundColor = '#10b981';
                break;
            case 'error':
                messageEl.style.backgroundColor = '#ef4444';
                break;
            default:
                messageEl.style.backgroundColor = '#3b82f6';
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (messageEl && messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 5000);
    }
}

// Initialize auth UI when DOM is loaded
let authUI;
document.addEventListener('DOMContentLoaded', () => {
    authUI = new AuthUI();
    // Export after initialization
    window.authUI = authUI;
});

// Export for use in other modules
window.authService = authService;
