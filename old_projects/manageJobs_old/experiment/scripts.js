lucide.createIcons();

const loginStage = document.getElementById('loginStage');
const loginForm = document.getElementById('loginForm');
const animationLayer = document.getElementById('animationLayer');
const rocket = document.getElementById('rocket');
const smokeContainer = document.getElementById('smokeContainer');
const dashboardStage = document.getElementById('dashboardStage');
const dashContent = document.getElementById('dashContent');
const submitBtn = document.getElementById('submitBtn');
const btnContent = document.getElementById('btnContent');
const btnLoader = document.getElementById('btnLoader');
const errorNotif = document.getElementById('errorNotif');

// 1. Initial Reveal
window.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('loginCard');
    setTimeout(() => {
        card.classList.remove('initial-load');
        card.classList.add('ready');
    }, 100);
});

// 2. Smoke Generation
const generateSmoke = (count = 40) => {
    smokeContainer.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'smoke-particle';
        
        // Random placement near the center path
        const x = 30 + Math.random() * 40; 
        const y = 30 + Math.random() * 40;
        const size = 150 + Math.random() * 200;
        
        particle.style.left = `${x}%`;
        particle.style.top = `${y}%`;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.animationDelay = `${Math.random() * 0.5}s`;
        
        particle.classList.add('smoke-fill');
        smokeContainer.appendChild(particle);
    }
};

// 3. The Sequence Logic
const runLaunchSequence = () => {
    // Stage 1: Hide Login
    loginStage.style.opacity = '0';
    loginStage.style.transform = 'scale(0.9) translateY(-20px)';
    
    setTimeout(() => {
        loginStage.classList.add('hidden');
        animationLayer.classList.remove('hidden');
        
        // Stage 2: Rocket Launch
        rocket.classList.add('launching');
        
        // Stage 3: Smoke Splash
        setTimeout(() => {
            generateSmoke();
        }, 500);

        // Stage 4: Loading (Transition to Dash)
        setTimeout(() => {
            // Setup Dashboard in background
            dashboardStage.style.display = 'flex';
            
            // Stage 5: Dissolve Smoke
            const particles = document.querySelectorAll('.smoke-particle');
            particles.forEach(p => {
                p.classList.remove('smoke-fill');
                p.classList.add('smoke-dissolve');
            });
            
            // Final Reveal
            setTimeout(() => {
                animationLayer.classList.add('hidden');
                dashContent.classList.remove('opacity-0', 'translate-y-10');
            }, 1000);

        }, 2200);

    }, 700);
};

// 4. Form Handling
loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Check for "demo" access or any input
    const inputs = loginForm.querySelectorAll('input');
    const user = inputs[0].value;
    const pass = inputs[1].value;

    // Simulate Auth
    btnContent.style.opacity = '0';
    btnLoader.classList.remove('hidden');
    submitBtn.disabled = true;

    setTimeout(() => {
        // If "admin" / "admin", launch! Otherwise show the error note you wanted.
        if (user.toLowerCase() === 'admin' && pass === '1234') {
            runLaunchSequence();
        } else {
            // Standard Error Logic
            btnContent.style.opacity = '1';
            btnLoader.classList.add('hidden');
            submitBtn.disabled = false;
            
            errorNotif.classList.add('show');
            setTimeout(() => errorNotif.classList.remove('show'), 5000);
        }
    }, 1500);
});

// Logout Handling
document.getElementById('logoutBtn').addEventListener('click', () => {
    window.location.reload();
});

// Password Toggle
document.getElementById('togglePassword').addEventListener('click', () => {
    const input = document.getElementById('passwordInput');
    const type = input.type === 'password' ? 'text' : 'password';
    input.type = type;
    lucide.createIcons();
});