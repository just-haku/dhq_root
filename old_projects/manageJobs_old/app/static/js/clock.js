/**
 * LUCKFOX ULTIMATE CLOCK ENGINE v3.1 (Complete)
 * Features: 
 * - Virtual Time Engine (Variable Speed)
 * - Robust Drag & Drop with Snapping & Guidelines
 * - Advanced Styling (Gradients, Image Textures, Masks)
 * - Audio Engine (Ticks, Alarms)
 * - Persistent Settings (Optional Layout Persistence)
 * - Custom Modal System
 */

class ClockApp {
    constructor() {
        // --- CORE STATE ---
        this.mode = 'clock'; // 'clock', 'timer', 'stopwatch'
        this.rafId = null;
        this.lastFrameTime = performance.now();
        
        // Virtual Time System
        this.virtualTime = Date.now();
        this.speedAnchorTime = Date.now(); // Real world reference
        this.virtualAnchorTime = this.virtualTime; // Virtual world reference
        
        // Timing Counters
        this.timerDuration = 60;
        this.currentTimeVal = 0;
        this.running = true;
        
        // Audio
        this.audioCtx = null;
        this.lastTickSec = -1;
        this.alarmPlaying = false;

        // Resource Management
        this.objectURLs = {
            background: null,
            font: null,
            digitImages: {} 
        };

        // Drag & Snap System
        this.drag = {
            active: false,
            item: null,
            startX: 0, 
            startY: 0, 
            initialLeft: 0, 
            initialTop: 0,
            snapThreshold: 15,
            guidelines: []
        };

        // Layout Storage (Loaded separately to allow easy reset)
        this.layoutPositions = JSON.parse(localStorage.getItem('luckfox_layout_positions')) || {};

        // Settings (Defaults)
        const savedSettings = JSON.parse(localStorage.getItem('luckfox_clock_settings'));
        this.settings = savedSettings || {
            timezoneOffset: 7,
            speedMultiplier: 1.0,
            showDate: false,
            soundEnabled: false,
            soundType: 'click', 
            soundVol: 0.7,
            alarmEnabled: true,
            separatorFlash: false, 
            showGrid: false,
            shortcuts: {
                toggleStartPause: ' ',
                resetTimerStopwatch: 'r',
                toggleLayout: 'l',
                closeSettings: 'Escape'
            }
        };

        // DOM Cache (Populated in init)
        this.dom = {};

        // Start Initialization
        this.init();
    }

    init() {
        // 1. Cache DOM Elements
        this.cacheDOM();
        
        if (!this.dom.container) {
            console.error("Critical: Clock Container not found. Retrying...");
            setTimeout(() => this.init(), 200);
            return;
        }

        // 2. Restore State & Layout
        this.restoreState(); 
        this.applySavedPositions(); 

        // 3. Setup Logic
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupTabs();
        this.setupShortcuts();
        
        // 4. Initialize Time Anchors
        this.speedAnchorTime = Date.now();
        this.virtualAnchorTime = Date.now();

        // 5. Start Engine
        this.startLoop();
        
        // 6. Resize Observer for Mask Alignment
        const resizeObserver = new ResizeObserver(() => {
             requestAnimationFrame(() => this.alignMasks());
        });
        resizeObserver.observe(document.body);
        
        console.log("Luckfox Engine v3.1 Fully Loaded & Robust.");
    }

    cacheDOM() {
        this.dom = {
            // Layout
            container: document.getElementById('clock-container'),
            bg: document.getElementById('background-layer'),
            grid: document.getElementById('alignment-grid'),
            
            // Digits
            chunks: {
                h: document.getElementById('hours'),
                m: document.getElementById('minutes'),
                s: document.getElementById('seconds'),
                sep1: document.getElementById('sep1'),
                sep2: document.getElementById('sep2')
            },
            date: document.getElementById('date-display'),
            
            // Panels
            settingsPanel: document.getElementById('settings-panel'),
            modal: document.getElementById('custom-modal'),
            modalTitle: document.getElementById('modal-title'),
            modalMsg: document.getElementById('modal-msg'),
            modalYes: document.getElementById('modal-yes'),
            modalNo: document.getElementById('modal-no'),
            
            // Inputs
            inputs: {
                mode: document.getElementById('mode-select'),
                speed: document.getElementById('tick-speed'),
                timer: document.getElementById('timer-input'),
                timezone: document.getElementById('timezone-offset'),
                dateToggle: document.getElementById('date-display-toggle'),
                soundToggle: document.getElementById('sound-toggle'),
                soundSelect: document.getElementById('sound-select'),
                soundVol: document.getElementById('tick-volume-slider'),
                font: document.getElementById('font-select'),
                fontFile: document.getElementById('font-file')
            }
        };
    }

    // --- MAIN RENDER LOOP ---
    startLoop() {
        const loop = (timestamp) => {
            const dt = (timestamp - this.lastFrameTime) / 1000; // Seconds
            this.lastFrameTime = timestamp;

            // Calculate Virtual Time
            const now = Date.now();
            const realElapsed = now - this.speedAnchorTime;
            this.virtualTime = this.virtualAnchorTime + (realElapsed * this.settings.speedMultiplier);

            // Update Logic based on Mode
            if (this.mode === 'clock') {
                this.updateClock();
            } else if (this.running) {
                // Apply speed multiplier to timer/stopwatch delta as well
                this.updateTimerStopwatch(dt * this.settings.speedMultiplier);
            }
            
            this.rafId = requestAnimationFrame(loop);
        };
        this.rafId = requestAnimationFrame(loop);
    }

    updateClock() {
        // Calculate Target Date object based on Virtual Time + Offset
        const localOffsetMs = new Date().getTimezoneOffset() * 60000;
        const utcTime = this.virtualTime + localOffsetMs; 
        const targetTimeMs = utcTime + (3600000 * this.settings.timezoneOffset);
        const targetDate = new Date(targetTimeMs);

        const h = targetDate.getHours();
        const m = targetDate.getMinutes();
        const s = targetDate.getSeconds();

        this.renderDigits(h, m, s);
        
        // Tick Logic (Only once per second)
        if (s !== this.lastTickSec) {
            this.lastTickSec = s;
            this.playTick();
            this.updateDate(targetDate);
        }
    }

    updateTimerStopwatch(adjustedDt) {
        if (this.mode === 'timer') {
            this.currentTimeVal -= adjustedDt;
            if (this.currentTimeVal <= 0) {
                this.currentTimeVal = 0;
                this.running = false;
                this.playAlarm(); // Trigger Alarm
            }
        } else if (this.mode === 'stopwatch') {
            this.currentTimeVal += adjustedDt;
        }

        // Format
        let val = Math.floor(this.currentTimeVal);
        let h = Math.floor(val / 3600);
        let m = Math.floor((val % 3600) / 60);
        let s = val % 60;
        this.renderDigits(h, m, s);
    }

    renderDigits(h, m, s) {
        const pad = (n) => n.toString().padStart(2, '0');
        
        // Safety checks before accessing DOM properties
        if (this.dom.chunks.h) this.dom.chunks.h.innerText = pad(h);
        if (this.dom.chunks.m) this.dom.chunks.m.innerText = pad(m);
        if (this.dom.chunks.s) this.dom.chunks.s.innerText = pad(s);
        
        // Optional Separator Flash
        const opacity = this.settings.separatorFlash ? ((Date.now() % 1000 < 500) ? 1 : 0.5) : 1;
        if (this.dom.chunks.sep1) this.dom.chunks.sep1.style.opacity = opacity;
        if (this.dom.chunks.sep2) this.dom.chunks.sep2.style.opacity = opacity;
    }

    updateDate(dateObj) {
        if (!this.settings.showDate || !this.dom.date) return;
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        this.dom.date.innerText = dateObj.toLocaleDateString(undefined, options);
    }

    // --- TIME & MODE CONTROLS ---
    toggleStartPause() {
        if (this.mode === 'clock') return;
        this.running = !this.running;
    }

    reset() {
        if (this.mode === 'clock') return;
        this.running = false;
        this.alarmPlaying = false; // Stop alarm if resetting
        
        // Re-read timer input or reset stopwatch
        const timerInp = this.dom.inputs.timer;
        this.currentTimeVal = (this.mode === 'timer') ? parseFloat(timerInp ? timerInp.value : 60) : 0;
        
        // Immediate Render
        let val = Math.floor(this.currentTimeVal);
        this.renderDigits(Math.floor(val/3600), Math.floor((val%3600)/60), val%60);
    }

    setMode(mode) {
        this.mode = mode;
        const timerSettings = document.getElementById('timer-settings');
        if (timerSettings) timerSettings.style.display = (mode === 'timer') ? 'block' : 'none';
        
        if (mode === 'clock') this.running = true;
        else this.reset();
    }

    updateSpeed(newSpeed) {
        // 1. Calculate current state before changing speed
        const now = Date.now();
        const currentRealElapsed = now - this.speedAnchorTime;
        // 2. Lock virtual time at this exact moment
        const currentVirtualTime = this.virtualAnchorTime + (currentRealElapsed * this.settings.speedMultiplier);
        
        // 3. Set new anchors for the new speed
        this.virtualAnchorTime = currentVirtualTime;
        this.speedAnchorTime = now;
        
        // 4. Update speed setting
        this.settings.speedMultiplier = newSpeed;
        this.saveSettings();
    }

    // --- EVENT LISTENERS (Centralized) ---
    setupEventListeners() {
        // --- BUTTONS ---
        const click = (id, fn) => { 
            const el = document.getElementById(id); 
            if(el) el.onclick = (e) => { e.preventDefault(); fn(e); }; 
        };
        
        // Panel Toggles
        click('settings-button', (e) => { 
            e.stopPropagation(); 
            this.dom.settingsPanel.classList.toggle('active'); 
        });
        
        // Global Close Panel
        document.addEventListener('click', (e) => {
            const panel = this.dom.settingsPanel;
            if (panel && panel.classList.contains('active') && 
                !panel.contains(e.target) && e.target.id !== 'settings-button') {
                panel.classList.remove('active');
            }
        });

        // Layout Controls
        click('toggle-layout-button', () => this.toggleLayout());
        click('toggle-grid-btn', () => this.toggleGrid());
        
        click('reset-positions-btn', () => {
            this.confirmAction("Reset Position", "Reset all element positions to default?", () => {
                localStorage.removeItem('luckfox_layout_positions');
                location.reload(); 
            });
        });
        
        click('reload-nosave-btn', () => {
            this.confirmAction("Factory Reset", "Clear ALL settings and reload?", () => {
                localStorage.clear();
                location.reload();
            });
        });

        // Playback Controls
        click('start-button', () => { this.running = true; });
        click('topStart', () => { this.running = true; });
        
        click('pause-button', () => { this.running = false; });
        click('topPause', () => { this.running = false; });
        
        click('reset-button', () => this.reset());
        click('topStop', () => this.reset());
        click('set-button', () => this.reset()); // Set timer value

        // --- INPUTS ---
        const change = (id, fn) => { const el = document.getElementById(id); if(el) el.onchange = fn; };
        const input = (id, fn) => { const el = document.getElementById(id); if(el) el.oninput = fn; };

        // Mode & Settings
        change('mode-select', (e) => this.setMode(e.target.value));
        change('timezone-offset', (e) => { this.settings.timezoneOffset = parseFloat(e.target.value); this.saveSettings(); });
        input('tick-speed', (e) => { 
            const val = parseFloat(e.target.value); 
            if(val > 0) this.updateSpeed(val); 
        });
        
        // Date Toggle
        change('date-display-toggle', (e) => {
            this.settings.showDate = e.target.checked;
            if(this.dom.date) this.dom.date.style.display = e.target.checked ? 'block' : 'none';
            this.saveSettings();
        });

        // Font
        click('apply-base-font-btn', () => {
            const font = this.dom.inputs.font.value;
            if (font !== 'custom') {
                document.documentElement.style.setProperty('--clock-font', font);
            }
        });
        
        const fileIn = document.getElementById('font-file');
        if(fileIn) fileIn.onchange = (e) => {
             const file = e.target.files[0];
             if(!file) return;
             const url = this.createObjectURL(file, 'font');
             const fontFace = new FontFace('CustomUserFont', `url(${url})`);
             fontFace.load().then(loadedFace => {
                 document.fonts.add(loadedFace);
                 document.documentElement.style.setProperty('--clock-font', 'CustomUserFont');
             });
        };

        // --- STYLE DELEGATION ---
        document.body.addEventListener('click', (e) => {
            // Apply Digit Style Buttons
            if (e.target.classList.contains('apply-digit-style')) {
                const container = e.target.closest('.digit-style-options');
                const chunkKey = container.dataset.chunk;
                const styleType = e.target.dataset.style;
                this.applyDigitStyle(chunkKey, styleType, container);
            }
            // Background Buttons
            if (e.target.dataset.apply === 'bg-solid') {
                const col = document.getElementById('bg-solid-color').value;
                if(this.dom.bg) {
                    this.dom.bg.style.background = col;
                    this.alignMasks();
                }
            }
            if (e.target.dataset.apply === 'bg-gradient') {
                const deg = document.getElementById('bg-gradient-degree').value;
                const start = document.getElementById('bg-gradient-start').value;
                const end = document.getElementById('bg-gradient-end').value;
                if(this.dom.bg) {
                    this.dom.bg.style.background = `linear-gradient(${deg}deg, ${start}, ${end})`;
                    this.alignMasks();
                }
            }
            if (e.target.dataset.apply === 'bg-image') {
                const urlIn = document.getElementById('bg-image-url');
                const fileIn = document.getElementById('bg-image-file');
                let src = urlIn.value;
                if (fileIn.files[0]) src = this.createObjectURL(fileIn.files[0], 'background');
                
                if (src && this.dom.bg) {
                    this.dom.bg.style.background = `url(${src}) center/cover no-repeat`;
                    setTimeout(() => this.alignMasks(), 100);
                }
            }
        });

        // --- VISUAL SLIDERS (Debounced) ---
        const vizUpdate = this.debounce(() => {
            const bgOp = document.getElementById('bg-opacity');
            if(bgOp && this.dom.bg) this.dom.bg.style.opacity = bgOp.value;
            
            const bgBl = document.getElementById('bg-blur');
            if(bgBl && this.dom.bg) this.dom.bg.style.filter = `blur(${bgBl.value}px)`;
            
            const digOp = document.getElementById('digits-opacity');
            if(digOp && this.dom.container) this.dom.container.style.opacity = digOp.value;
            
            const digBl = document.getElementById('digits-blur');
            let filter = digBl ? `blur(${digBl.value}px)` : '';
            
            const glowToggle = document.getElementById('glow-toggle');
            if(glowToggle && glowToggle.checked) {
                const col = document.getElementById('glow-color').value;
                filter += ` drop-shadow(0 0 10px ${col}) drop-shadow(0 0 20px ${col})`;
            }
            if(this.dom.container) this.dom.container.style.filter = filter;
            this.alignMasks();
        }, 20);

        ['bg-opacity', 'bg-blur', 'digits-opacity', 'digits-blur', 'glow-toggle', 'glow-color']
            .forEach(id => {
                const el = document.getElementById(id);
                if(el) el.addEventListener('input', vizUpdate);
            });
            
        this.setupAudioHandlers();
    }

    // --- ADVANCED STYLING LOGIC ---
    applyDigitStyle(chunkKey, type, container) {
        let targets = (chunkKey === 'global') ? ['.chunk'] : [`#${chunkKey}`];
        if(chunkKey === 'hours') targets = ['#hours'];
        if(chunkKey === 'minutes') targets = ['#minutes'];
        if(chunkKey === 'seconds') targets = ['#seconds'];

        document.querySelectorAll(targets.join(',')).forEach(el => {
            // Reset base styles
            el.style.backgroundImage = 'none';
            el.style.color = 'inherit';
            el.style.webkitTextFillColor = 'initial';
            el.classList.remove('masked-chunk'); 

            if (type === 'solid') {
                const col = container.querySelector('.digit-solid-color')?.value;
                if(col) el.style.color = col;
            } 
            else if (type === 'gradient') {
                const s = container.querySelector('.digit-gradient-start')?.value;
                const e = container.querySelector('.digit-gradient-end')?.value;
                const deg = container.querySelector('.digit-gradient-degree')?.value || 90;
                
                if(s && e) {
                    el.style.backgroundImage = `linear-gradient(${deg}deg, ${s}, ${e})`;
                    el.style.webkitBackgroundClip = 'text';
                    el.style.webkitTextFillColor = 'transparent';
                    el.style.backgroundAttachment = 'fixed'; // Static texture effect
                }
            } 
            else if (type === 'image') {
                const urlIn = container.querySelector('.digit-image-url-input');
                const fileIn = container.querySelector('.digit-image-file');
                let src = urlIn ? urlIn.value : null;
                
                if (fileIn && fileIn.files[0]) {
                    src = this.createObjectURL(fileIn.files[0], 'digitImages', chunkKey);
                }

                if (src) {
                    el.style.backgroundImage = `url(${src})`;
                    el.style.backgroundSize = 'cover';
                    el.style.backgroundPosition = 'center';
                    el.style.webkitBackgroundClip = 'text';
                    el.style.webkitTextFillColor = 'transparent';
                    el.style.backgroundAttachment = 'fixed'; // Static texture effect
                }
            } 
            else if (type === 'mask') {
                el.classList.add('masked-chunk');
                this.alignSingleMask(el);
            }
        });
    }

    alignMasks() { 
        document.querySelectorAll('.masked-chunk').forEach(el => this.alignSingleMask(el)); 
    }

    alignSingleMask(el) {
        if (!this.dom.bg) return;
        const bgStyle = window.getComputedStyle(this.dom.bg);
        
        // If no background set, fallback
        if(!bgStyle.backgroundImage || bgStyle.backgroundImage === 'none') {
            el.style.color = 'rgba(255,255,255,0.1)'; 
            return;
        }
        
        // Copy background properties for seamless mask
        el.style.backgroundImage = bgStyle.backgroundImage;
        el.style.backgroundSize = bgStyle.backgroundSize;
        el.style.backgroundPosition = bgStyle.backgroundPosition;
        el.style.backgroundRepeat = bgStyle.backgroundRepeat;
        el.style.backgroundAttachment = 'fixed'; // Crucial for seamless align with fixed BG
        
        el.style.webkitBackgroundClip = 'text';
        el.style.webkitTextFillColor = 'transparent';
    }

    // --- DRAG, DROP & SNAP LOGIC ---
    setupDragAndDrop() {
        this.onDragStart = this.onDragStart.bind(this);
        this.onDragMove = this.onDragMove.bind(this);
        this.onDragEnd = this.onDragEnd.bind(this);

        document.addEventListener('mousedown', this.onDragStart);
        document.addEventListener('touchstart', this.onDragStart, { passive: false });
        
        // Global Listeners for End (Catch sticking issues)
        window.addEventListener('mouseup', this.onDragEnd);
        window.addEventListener('touchend', this.onDragEnd);
        window.addEventListener('blur', this.onDragEnd);
    }

    onDragStart(e) {
        const target = e.target.closest('.chunk') || e.target.closest('.draggable-ui');
        if (!target) return;
        if (this.dom.settingsPanel && this.dom.settingsPanel.classList.contains('active') && this.dom.settingsPanel.contains(target)) return;
        if (e.type === 'touchstart') e.preventDefault(); 

        this.drag.active = true;
        this.drag.item = target;
        this.drag.item.style.zIndex = 1000;
        this.drag.item.style.cursor = 'grabbing';

        // 1. Force Absolute Position if not set, preventing jump
        const style = window.getComputedStyle(target);
        if (style.position !== 'absolute') {
            const rect = target.getBoundingClientRect();
            target.style.position = 'absolute';
            target.style.left = rect.left + 'px';
            target.style.top = rect.top + 'px';
            target.style.margin = '0';
        }

        const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;

        this.drag.startX = clientX;
        this.drag.startY = clientY;
        this.drag.initialLeft = parseFloat(target.style.left) || 0;
        this.drag.initialTop = parseFloat(target.style.top) || 0;

        this.calculateSnapLines(target);

        document.addEventListener('mousemove', this.onDragMove);
        document.addEventListener('touchmove', this.onDragMove, { passive: false });
    }

    calculateSnapLines(currentItem) {
        this.drag.guidelines = [];
        const w = window.innerWidth, h = window.innerHeight;
        
        // Grid Fractions
        [0.25, 0.33, 0.5, 0.66, 0.75].forEach(f => {
            this.drag.guidelines.push({ v: w * f, type: 'v' });
            this.drag.guidelines.push({ v: h * f, type: 'h' });
        });

        // Other Elements
        const others = [...document.querySelectorAll('.chunk, .draggable-ui')].filter(el => el !== currentItem && el.style.display !== 'none');
        others.forEach(el => {
            const r = el.getBoundingClientRect();
            this.drag.guidelines.push(
                { v: r.left, type: 'v' }, { v: r.right, type: 'v' }, { v: r.left + r.width/2, type: 'v' },
                { v: r.top, type: 'h' }, { v: r.bottom, type: 'h' }, { v: r.top + r.height/2, type: 'h' }
            );
        });
    }

    onDragMove(e) {
        if (!this.drag.active || !this.drag.item) return;
        e.preventDefault(); 

        const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        const clientY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;

        let dx = clientX - this.drag.startX;
        let dy = clientY - this.drag.startY;
        
        let newLeft = this.drag.initialLeft + dx;
        let newTop = this.drag.initialTop + dy;

        // Snapping Logic
        const rect = this.drag.item.getBoundingClientRect();
        const cx = newLeft + rect.width / 2;
        const cy = newTop + rect.height / 2;
        const thresh = this.drag.snapThreshold;

        // X Snap
        for (let l of this.drag.guidelines.filter(g => g.type === 'v')) {
            if (Math.abs(newLeft - l.v) < thresh) newLeft = l.v;
            else if (Math.abs((newLeft + rect.width) - l.v) < thresh) newLeft = l.v - rect.width;
            else if (Math.abs(cx - l.v) < thresh) newLeft = l.v - rect.width/2;
        }
        // Y Snap
        for (let l of this.drag.guidelines.filter(g => g.type === 'h')) {
            if (Math.abs(newTop - l.v) < thresh) newTop = l.v;
            else if (Math.abs((newTop + rect.height) - l.v) < thresh) newTop = l.v - rect.height;
            else if (Math.abs(cy - l.v) < thresh) newTop = l.v - rect.height/2;
        }

        this.drag.item.style.left = `${newLeft}px`;
        this.drag.item.style.top = `${newTop}px`;
        
        // Update mask if needed
        if (this.drag.item.classList.contains('masked-chunk')) {
            this.alignSingleMask(this.drag.item);
        }
    }

    onDragEnd() {
        if (!this.drag.active) return;
        
        // Save Position
        const id = this.drag.item.id;
        if(id) {
            this.layoutPositions[id] = {
                left: this.drag.item.style.left,
                top: this.drag.item.style.top,
                position: 'absolute'
            };
            this.savePositions(); // Persist drag changes
        }

        if (this.drag.item) {
            this.drag.item.style.cursor = ''; 
            this.drag.item.style.zIndex = '';
        }
        this.drag.active = false;
        this.drag.item = null;

        document.removeEventListener('mousemove', this.onDragMove);
        document.removeEventListener('touchmove', this.onDragMove);
    }

    // --- AUDIO & MODAL ---
    setupAudioHandlers() {
        const soundToggle = this.dom.inputs.soundToggle;
        if(soundToggle) soundToggle.onchange = (e) => this.settings.soundEnabled = e.target.checked;
        const volSlider = this.dom.inputs.soundVol;
        if(volSlider) volSlider.oninput = (e) => this.settings.soundVol = parseFloat(e.target.value);
    }
    
    playTick() {
        if (!this.settings.soundEnabled) return;
        if (!this.audioCtx) this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        this.playSynth('click'); 
    }
    
    playAlarm() {
        if (!this.settings.alarmEnabled) return;
        if (!this.audioCtx) this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        this.playSynth('alarm');
    }
    
    playSynth(type) {
        try {
            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();
            osc.connect(gain); gain.connect(this.audioCtx.destination);
            
            if (type === 'alarm') {
                osc.frequency.setValueAtTime(600, this.audioCtx.currentTime);
                osc.type = 'sawtooth';
                gain.gain.setValueAtTime(0.5, this.audioCtx.currentTime);
                osc.start();
                osc.stop(this.audioCtx.currentTime + 2.0); // 2s Alarm
            } else {
                osc.frequency.setValueAtTime(800, this.audioCtx.currentTime);
                osc.type = 'square';
                gain.gain.setValueAtTime(this.settings.soundVol * 0.1, this.audioCtx.currentTime);
                osc.start();
                osc.stop(this.audioCtx.currentTime + 0.05);
            }
        } catch(e) {}
    }

    // Custom Modal Logic
    confirmAction(title, msg, onYes) {
        if(!this.dom.modal) {
            if(confirm(msg)) onYes(); return;
        }
        this.dom.modalTitle.innerText = title;
        this.dom.modalMsg.innerText = msg;
        this.dom.modal.style.display = 'flex';
        
        const close = () => { this.dom.modal.style.display = 'none'; };
        this.dom.modalYes.onclick = () => { onYes(); close(); };
        this.dom.modalNo.onclick = () => { close(); };
    }

    // --- PERSISTENCE & UTILS ---
    saveSettings() {
        localStorage.setItem('luckfox_clock_settings', JSON.stringify(this.settings));
    }
    savePositions() {
        localStorage.setItem('luckfox_layout_positions', JSON.stringify(this.layoutPositions));
    }
    
    applySavedPositions() {
        Object.keys(this.layoutPositions).forEach(id => {
            const el = document.getElementById(id);
            const pos = this.layoutPositions[id];
            if(el && pos) {
                el.style.position = pos.position || 'absolute';
                el.style.left = pos.left;
                el.style.top = pos.top;
                el.style.margin = '0';
            }
        });
    }

    toggleLayout() {
        const current = this.dom.container.style.flexDirection;
        const isCol = current === 'column';
        this.dom.container.style.flexDirection = isCol ? 'row' : 'column';
        const display = isCol ? 'block' : 'none';
        if(this.dom.chunks.sep1) this.dom.chunks.sep1.style.display = display;
        if(this.dom.chunks.sep2) this.dom.chunks.sep2.style.display = display;
    }

    toggleGrid() {
        this.settings.showGrid = !this.settings.showGrid;
        if(this.dom.grid) this.dom.grid.style.display = this.settings.showGrid ? 'block' : 'none';
    }

    createObjectURL(file, key, subKey = null) {
        if (subKey) {
            if (this.objectURLs[key][subKey]) URL.revokeObjectURL(this.objectURLs[key][subKey]);
        } else {
            if (this.objectURLs[key]) URL.revokeObjectURL(this.objectURLs[key]);
        }
        const url = URL.createObjectURL(file);
        if (subKey) this.objectURLs[key][subKey] = url;
        else this.objectURLs[key] = url;
        return url;
    }

    debounce(func, wait) {
        let timeout;
        return (...args) => { clearTimeout(timeout); timeout = setTimeout(() => func.apply(this, args), wait); };
    }

    restoreState() {
        const s = this.settings;
        const setVal = (id, v) => { const el = document.getElementById(id); if(el) el.value = v; };
        const setCheck = (id, v) => { const el = document.getElementById(id); if(el) el.checked = v; };
        
        setVal('timezone-offset', s.timezoneOffset);
        setVal('tick-speed', s.speedMultiplier);
        setCheck('date-display-toggle', s.showDate);
        setCheck('sound-toggle', s.soundEnabled);
        
        if (s.showDate && this.dom.date) this.dom.date.style.display = 'block';
        if (s.showGrid && this.dom.grid) this.dom.grid.style.display = 'block';
    }

    setupTabs() {
        const handle = (btns, contents, activeBtn) => {
            btns.forEach(b => b.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            activeBtn.classList.add('active');
            document.getElementById(activeBtn.dataset.tab).classList.add('active');
        };
        document.querySelectorAll('.main-tabs .tab-button').forEach(b => 
            b.onclick = () => handle(document.querySelectorAll('.main-tabs .tab-button'), document.querySelectorAll('#settings-panel > .tab-content'), b));
        document.querySelectorAll('.nested-tabs .tab-button').forEach(b => 
            b.onclick = () => handle(document.querySelectorAll('.nested-tabs .tab-button'), document.querySelectorAll('#digits-tab .tab-content'), b));
    }

    setupShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT') return;
            const action = Object.keys(this.settings.shortcuts).find(key => this.settings.shortcuts[key] === e.key);
            if (action) {
                if (action === 'toggleStartPause') this.toggleStartPause();
                if (action === 'resetTimerStopwatch') this.reset();
                if (action === 'toggleLayout') this.toggleLayout();
                if (action === 'closeSettings') this.dom.settingsPanel.classList.remove('active');
            }
        });
    }
}

window.addEventListener('DOMContentLoaded', () => { window.clockApp = new ClockApp(); });