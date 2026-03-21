document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // 1. VISUAL EFFECTS (Particles, Focus, Ripple)
    // ==========================================

    const container = document.getElementById('particles');
    const particleCount = 50;

    // --- Particle System ---
    if (container) {
        for (let i = 0; i < particleCount; i++) {
            createParticle();
        }

        function createParticle() {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            
            const size = Math.random() * 5 + 2;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            
            const duration = Math.random() * 10 + 10;
            particle.style.animationDuration = `${duration}s`;
            
            const delay = Math.random() * 5;
            particle.style.animationDelay = `${delay}s`;

            container.appendChild(particle);
        }
    }

    // --- Input Focus Animations ---
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        // Check initial state (browser autofill)
        if (input.value) {
            if (input.parentElement) input.parentElement.classList.add('focused');
        }

        input.addEventListener('focus', () => {
            if (input.parentElement) input.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                if (input.parentElement) input.parentElement.classList.remove('focused');
            }
        });
        
        // Listen for autofill events
        input.addEventListener('animationstart', (e) => {
             if (e.animationName === 'onAutoFillStart') {
                 if (input.parentElement) input.parentElement.classList.add('focused');
             }
        });
    });

    // --- Button Ripple Effect ---
    // Try to find .login-btn, fallback to generic submit button if class missing
    const btn = document.querySelector('.login-btn') || document.querySelector('button[type="submit"]');
    if (btn) {
        btn.addEventListener('click', function(e) {
            // Check form validity before playing animation
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                let ripple = document.createElement('div');
                ripple.style.position = 'absolute';
                ripple.style.background = 'rgba(255,255,255,0.3)';
                ripple.style.borderRadius = '50%';
                ripple.style.pointerEvents = 'none';
                ripple.style.transform = 'translate(-50%, -50%)';
                ripple.style.width = '0';
                ripple.style.height = '0';
                ripple.style.left = e.offsetX + 'px';
                ripple.style.top = e.offsetY + 'px';
                ripple.style.animation = 'ripple 0.6s linear';
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            }
        });
    }

    // ==========================================
    // 2. LOGIN LOGIC (AJAX Submission)
    // ==========================================
    
    const loginForm = document.querySelector('form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Login';
            
            if(submitBtn) {
                // Slight delay to allow ripple animation to start visible
                setTimeout(() => {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = 'Logging in...';
                }, 100);
            }

            // Collect form data
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());
            
            // Get CSRF Token if it exists (handles Flask-WTF)
            const csrfTokenInput = document.querySelector('input[name="csrf_token"]');
            const headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            };
            
            if (csrfTokenInput) {
                headers['X-CSRFToken'] = csrfTokenInput.value;
            }

            fetch('/auth/login', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            })
            .then(response => {
                // If the server returns a 400 or 401, this block still runs, 
                // but we need to check response.ok or handle the JSON body manually.
                return response.json().then(data => ({ status: response.status, body: data }));
            })
            .then(result => {
                if (result.body.success) {
                    window.location.href = result.body.redirect;
                } else {
                    // Show error
                    alert(result.body.message || 'Login failed');
                    if(submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalBtnText;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An unexpected error occurred.');
                if(submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            });
        });
    }
});