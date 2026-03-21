console.log("Script clockInterval.js starting...");

/********************************************
* GLOBAL STATE & CONSTANTS
********************************************/
let clockInterval = null;
let timerInterval = null;
let stopwatchInterval = null;
let currentMode = "clock";
let updateInterval = 50; // update every 50ms
let timezoneOffsetHours = 7;
let lastObjectURLs = { // Store object URLs to revoke them later
    background: null,
    'digits-global': null,
    'digits-hours': null,
    'digits-minutes': null,
    'digits-seconds': null,
    'digits-separators': null,
    font: null
};

// Timing state
let timerRemaining = 60;
let stopwatchTime = 0;
let stopwatchLastTimestamp = null;
let clockSpeed = 1;
let clockRealStart = null;
let clockVirtualStart = null;
let timerStartTime = null;

// UI State
let layoutIsVertical = false;
let isPanelOpen = false;
let currentFontName = "'Orbitron', sans-serif"; // Default font
let globalDigitSettings = { type: 'solid', value: '#FFFFFF' }; // Store global style
let chunkSpecificSettings = { hours: null, minutes: null, seconds: null, separators: null };

// Drag state
let currentDrag = null;
let dragOffsetX = 0;
let dragOffsetY = 0;
let isDraggingClockChunk = false;
let currentUiDrag = null;
let uiDragOffsetX = 0;
let uiDragOffsetY = 0;

//Shortcuts
const defaultShortcuts = {
    toggleStartPause: 's',
    resetTimerStopwatch: 'r',
    nextMode: 'm',
    toggleLayout: 'l',
    closeSettings: 'escape' // Use 'escape' for the Escape key
    // Add Spacebar? Might conflict. We handle space separately.
};
let currentShortcuts = { ...defaultShortcuts }; // Start with defaults
let activeShortcutInput = null; // Track which input is waiting for a key

//Audio
let soundToggle = null;
let soundSelect = null;
let soundFile = null;
let testSoundButton = null;
let tickVolumeSlider = null;
let tickVolumeValue = null;
let alarmVolumeSlider = null;
let alarmVolumeValue = null;
let userInteracted = false;

let soundEnabled = false;
let currentAudio = null; // For ticking
let lastSecond = -1;
let customAudioURL = null;
let tickVolume = 0.7; // <<< ENSURE DECLARED
let alarmEnabled = true; // Alarm defaults on?
let currentAlarmAudio = null;
let customAlarmAudioURL = null;
let alarmVolume = 0.8; // <<< ENSURE DECLARED

let showDate = false;
let applyGmtButton = null;

console.log("Global state declared.");

/********************************************
* DOM ELEMENT VARIABLES (Declared globally, assigned in DOMContentLoaded)
********************************************/
let backgroundLayer = null;
let clockContainer = null;
let hoursEl = null;
let sep1El = null;
let minutesEl = null;
let sep2El = null;
let secondsEl = null;
let allChunks = [];
let bodyElement = null;
let toggleLayoutButton = null;
let settingsButton = null;
let topStartButton = null;
let topPauseButton = null;
let topStopButton = null;
let settingsPanel = null;
let tabButtons = null;
let tabContents = null;
let digitTabButtons = null;
let digitTabContents = null;
let modeSelect = null;
let timerSettings = null;
let timerInput = null;
let tickSpeedInput = null;
let clockSizeInput = null;
let setButton = null;
let startButton = null;
let pauseButton = null;
let resetButton = null;
let bgSolidColorInput = null;
let bgGradientDegree = null;
let bgGradientStart = null;
let bgGradientEnd = null;
let bgImageUrlInput = null;
let bgImageFileInput = null;
let bgImagePreview = null;
let fontSelect = null;
let fontFileInput = null;
let applyBaseFontBtn = null;
let applyCustomFontBtn = null;
let bgOpacityInput = null;
let bgOpacityValue = null;
let bgBlurInput = null;
let bgBlurValue = null;
let applyBgStyleBtn = null;
let digitsOpacityInput = null;
let digitsOpacityValue = null;
let digitsBlurInput = null;
let digitsBlurValue = null;
let applyDigitsStyleBtn = null;
let glowToggle = null;
let glowColorInput = null;
let dateDisplay = null;
let dateDisplayToggle = null;
let shortcutSettingsList = null;
let saveShortcutsButton = null;
let resetShortcutsButton = null;
let alarmSelect = null;
let alarmFile = null;
let testAlarmButton = null;
let timezoneOffsetInput =null;

/******************************************
 * AUDIO DECLARATION
 *****************************************/
let sounds = {};
let alarmSounds = {}; // Object for preloaded alarm sounds


// Preload default tick sounds
try {
    sounds.click = new Audio('/static/audio/click.mp3'); // Added /static/
    sounds.analog = new Audio('/static/audio/tick.mp3'); // Added /static/
    sounds.beep = new Audio('/static/audio/beep.mp3'); // Added /static/
    Object.values(sounds).forEach(s => s.volume = tickVolume);
    console.log("Default tick sounds preloaded (attempted).");
} catch (e) { console.error("Error preloading tick sounds:", e);}

// Preload default alarm sounds
try {
    alarmSounds.alarmBeep = new Audio('/static/audio/lofi-alarm.mp3'); // Added /static/
    alarmSounds.chime = new Audio('/static/audio/oversimplified.mp3'); // Added /static/
    Object.values(alarmSounds).forEach(s => s.volume = alarmVolume);
    console.log("Default alarm sounds preloaded (attempted).");
} catch (e) { console.error("Error preloading alarm sounds:", e);}
console.log("DOM Element variables declared.");

/********************************************
* UTILITY FUNCTIONS
********************************************/
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
      const later = () => {
          clearTimeout(timeout);
          func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
  };
}

function getImageURL(fileInput, textInput, key) {
  if (lastObjectURLs[key]) {
      URL.revokeObjectURL(lastObjectURLs[key]);
      lastObjectURLs[key] = null;
  }
  if (fileInput && fileInput.files.length > 0) {
      const file = fileInput.files[0];
      if (file.type.startsWith('image/')) {
          const newUrl = URL.createObjectURL(file);
          lastObjectURLs[key] = newUrl;
          return newUrl;
      } else {
          console.warn("Invalid file type selected for key:", key);
          alert("Please select a valid image file.");
          return textInput ? textInput.value.trim() : null;
      }
  } else if (textInput) {
      return textInput.value.trim();
  }
  return null;
}

function getEventCoords(e) {
  if (e.touches && e.touches.length > 0) {
      return { x: e.touches[0].clientX, y: e.touches[0].clientY };
  } else if (e.changedTouches && e.changedTouches.length > 0) {
      return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
  } else {
      return { x: e.clientX, y: e.clientY };
  }
}

console.log("Utility functions defined.");

/********************************************
* TAB SWITCHING LOGIC
********************************************/
function showTab(tabId, isNested = false) {
  // Use optional chaining just in case elements aren't ready yet (shouldn't happen if called correctly)
  const buttons = isNested ? digitTabButtons : tabButtons;
  const contents = isNested ? digitTabContents : tabContents;

  if (!buttons || !contents) {
      console.warn(`showTab called but buttons or contents not available (tabId: ${tabId})`);
      return;
  }

  contents.forEach(content => {
      if (content) { // Check if content element exists
          if (content.id === tabId) {
              content.classList.add('active');
          } else {
              content.classList.remove('active');
          }
      }
  });

  buttons.forEach(button => {
      if (button) { // Check if button element exists
          if (button.dataset.tab === tabId) {
              button.classList.add('active');
          } else {
              button.classList.remove('active');
          }
      }
  });
}

console.log("Tab switching logic defined.");
/********************************************
* CLOCK/TIMER/STOPWATCH LOGIC (Mostly unchanged, check placement)
********************************************/
function stopAllIntervals() {
  clearInterval(clockInterval); clockInterval = null;
  clearInterval(timerInterval); timerInterval = null;
  clearInterval(stopwatchInterval); stopwatchInterval = null;
}

// --- CLOCK ---
function updateClockDisplay() {
    const nowMillis = Date.now(); // Get current real time once

    let displayTimeMillis; // The final timestamp we want to display

    if (currentMode === 'clock' && clockSpeed !== 1 && clockRealStart && clockVirtualStart) {
        // --- Apply Clock Speed (Only if speed is not 1 AND clock has started) ---
        const realElapsed = nowMillis - clockRealStart;
        const virtualElapsed = realElapsed * clockSpeed;

        // Calculate target time based on the VIRTUAL start time + VIRTUAL elapsed
        displayTimeMillis = clockVirtualStart.getTime() + virtualElapsed;
        // --- End Clock Speed ---

        // --- DEBUG LOG for Speed ---
        // console.log(`Speed Applied: RealElapsed=${realElapsed}, VirtualElapsed=${virtualElapsed}, TargetMillis=${displayTimeMillis}`);
        // ---

    } else {
        // --- Normal Speed or Not Clock Mode ---
        // Calculate display time directly using current real time and offset
        displayTimeMillis = nowMillis + (timezoneOffsetHours * 3600000); // 3600000ms in an hour
        // --- End Normal Speed ---

        // --- DEBUG LOG for Normal ---
        // console.log(`Normal Speed/Mode: TargetMillis=${displayTimeMillis}`);
        // ---
    }

    // --- Convert target milliseconds to Date object and extract UTC components ---
    const targetTime = new Date(displayTimeMillis);
    let hours = targetTime.getUTCHours();
    let minutes = targetTime.getUTCMinutes();
    let seconds = targetTime.getUTCSeconds();
    // let millis = targetTime.getUTCMilliseconds(); // Optional

    // --- Play Tick Sound ---
    if (soundEnabled && currentAudio && seconds !== lastSecond) {
        playSoundWithCheck(currentAudio, tickVolume);
    }
    lastSecond = seconds; // Update last second AFTER the check

    // --- Update DOM ---
    updateChunks(hours, minutes, seconds, 0);
}

function startClock() {
    console.log("Attempting to start clock..."); // Keep this log
    if (!hoursEl || !minutesEl || !secondsEl) { console.error("Cannot start clock: Digit elements not available."); return; }

    stopAllIntervals(); // Clear existing intervals

    clockRealStart = Date.now(); // Record the real start time NOW

    // === Explicitly use current offset ===
    const currentOffsetMillis = timezoneOffsetHours * 3600000; // Calculate offset in ms
    clockVirtualStart = new Date(clockRealStart + currentOffsetMillis); // Set virtual start based on current real time + CURRENT offset
    // === End explicit use ===

    console.log(`Clock started/restarted. Offset Used: ${timezoneOffsetHours}, RealStart: ${new Date(clockRealStart).toISOString()}, VirtualStart: ${clockVirtualStart.toISOString()}`); // Log the values used

    updateClockDisplay(); // Initial display based on new offset/speed logic
    clockInterval = setInterval(updateClockDisplay, updateInterval);

    console.log("Clock interval (re)set with ID:", clockInterval);
}

function handleFirstInteraction() {
    console.log("First user interaction detected. Audio context likely active.");
    userInteracted = true;
    // Remove the listeners after first interaction
    document.removeEventListener('click', handleFirstInteraction);
    document.removeEventListener('touchstart', handleFirstInteraction);
    document.removeEventListener('keydown', handleFirstInteraction);
}

function setTimer() {
  stopAllIntervals();
  timerRemaining = parseFloat(timerInput?.value) || 0; // Optional chaining
  timerStartTime = null;
  updateTimerDisplay();
}

function startTimer() {
  if (timerInterval || timerRemaining <= 0) return;
  stopAllIntervals();
  timerStartTime = Date.now();
  updateTimerDisplay();
  timerInterval = setInterval(updateTimerDisplay, updateInterval);
}

function updateTimerDisplay() {
  let remaining = timerRemaining;
  if (timerStartTime) {
      let elapsed = (Date.now() - timerStartTime) / 1000;
      let effectiveElapsed = elapsed * clockSpeed;
      remaining = Math.max(timerRemaining - effectiveElapsed, 0);
  }
  if (remaining <= 0 && timerInterval) {
      clearInterval(timerInterval); timerInterval = null;
      timerStartTime = null; remaining = 0;playAlarmSound();
  }
  const hrs = Math.floor(remaining / 3600);
  const mins = Math.floor((remaining % 3600) / 60);
  const secs = Math.floor(remaining % 60);
  const millis = Math.floor((remaining % 1) * 1000);
  updateChunks(hrs, mins, secs, millis);
}

function pauseTimer() {
  if (!timerInterval) return;
  clearInterval(timerInterval); timerInterval = null;
  let elapsed = (Date.now() - timerStartTime) / 1000 * clockSpeed;
  timerRemaining = Math.max(timerRemaining - elapsed, 0);
  timerStartTime = null;
  updateTimerDisplay();
}

function resetTimer() {
  stopAllIntervals();
  timerRemaining = parseFloat(timerInput?.value) || 0; // Optional chaining
  timerStartTime = null;
  updateTimerDisplay();
}

function setStopwatch() {
  stopAllIntervals();
  stopwatchTime = 0;
  stopwatchLastTimestamp = null;
  updateChunks(0, 0, 0, 0);
}

function startStopwatch() {
  if (stopwatchInterval) return;
  stopAllIntervals();
  if (!stopwatchLastTimestamp) {
      stopwatchLastTimestamp = Date.now();
  }
  stopwatchInterval = setInterval(updateStopwatchDisplay, updateInterval);
}

function updateStopwatchDisplay() {
  if (stopwatchLastTimestamp === null) return;
  const now = Date.now();
  const deltaSeconds = (now - stopwatchLastTimestamp) / 1000;
  stopwatchLastTimestamp = now;
  const effectiveDelta = deltaSeconds * clockSpeed;
  stopwatchTime += effectiveDelta;
  const hrs = Math.floor(stopwatchTime / 3600);
  const mins = Math.floor((stopwatchTime % 3600) / 60);
  const secs = Math.floor(stopwatchTime % 60);
  const millis = Math.floor((stopwatchTime % 1) * 1000);
  updateChunks(hrs, mins, secs, millis);
}

function pauseStopwatch() {
  if (!stopwatchInterval) return;
  clearInterval(stopwatchInterval); stopwatchInterval = null;
  stopwatchLastTimestamp = null;
}

function resetStopwatch() {
  stopAllIntervals();
  stopwatchTime = 0;
  stopwatchLastTimestamp = null;
  updateChunks(0, 0, 0, 0);
}

console.log("Time logic functions defined.");

/********************************************
* UI UPDATE FUNCTIONS
********************************************/

// Update clock digit elements
function updateChunks(hours, minutes, seconds, _millis = 0) {
  // Check if elements exist before updating text content
  if (hoursEl) hoursEl.textContent = hours.toString().padStart(2, "0");
  if (minutesEl) minutesEl.textContent = minutes.toString().padStart(2, "0");
  if (secondsEl) secondsEl.textContent = seconds.toString().padStart(2, "0");

  const sepText = layoutIsVertical ? "__" : ":";
  if (sep1El) sep1El.textContent = sepText;
  if (sep2El) sep2El.textContent = sepText;

  // Re-align mask if needed
  allChunks.forEach(chunk => {
      if (!chunk) return; // Skip if element was not found
      const chunkId = chunk.id || (chunk === sep1El || chunk === sep2El ? 'separators' : null);
      if (!chunkId) return;
      const setting = chunkSpecificSettings[chunkId] || globalDigitSettings;
      if (setting && setting.type === 'mask') {
          alignChunkBackground(chunk);
      }
  });
}

function toggleLayout() {
  if (!clockContainer) return;
  layoutIsVertical = !layoutIsVertical;
  clockContainer.style.flexDirection = layoutIsVertical ? "column" : "row";
  const margin = layoutIsVertical ? "0.1em 0" : "0 0.1em";
  allChunks.forEach(ch => { if (ch) ch.style.margin = margin; });
  triggerTimeUpdate();
}

function triggerTimeUpdate() {
  if (currentMode === "clock") { updateClockDisplay(); }
  else if (currentMode === "timer") { updateTimerDisplay(); }
  else if (currentMode === "stopwatch") {
      const hrs = Math.floor(stopwatchTime / 3600);
      const mins = Math.floor((stopwatchTime % 3600) / 60);
      const secs = Math.floor(stopwatchTime % 60);
      const millis = Math.floor((stopwatchTime % 1) * 1000);
      updateChunks(hrs, mins, secs, millis);
  }
}

function updateUIForMode(mode) {
  console.log(`Updating UI for mode: ${mode}`);
  if (timerSettings) timerSettings.style.display = (mode === "timer") ? "block" : "none";
  console.log("Stopping all intervals before mode switch...");
  stopAllIntervals();
  if (mode === "clock") { startClock(); }
  else if (mode === "timer") { updateTimerDisplay(); }
  else if (mode === "stopwatch") { triggerTimeUpdate(); }
}

// Defined globally or before DOMContentLoaded listener
function updateDateDisplay() {
    // Check if element exists before trying to update it
    if (!dateDisplay) {
        // console.log("updateDateDisplay called, but dateDisplay element is null."); // Debug
        return;
    }
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString(undefined, options);
    // console.log("Updating date display to:", dateString); // Debug
    dateDisplay.textContent = dateString; // Set the text content
}

function toggleDateDisplay(show) { // Ensure this function is defined up here
    if (dateDisplay) {
        dateDisplay.style.display = show ? 'block' : 'none';
    } else {console.warn("Cannot toggle date display: element not found.");}
    showDate = show; // Update state
    // Optional: Save state to localStorage
    // localStorage.setItem('showDateDisplay', show);
    console.log("Date display toggled:", show); // Add log
}

console.log("UI Update functions defined.");

/********************************************
* SETTINGS APPLICATION FUNCTIONS
********************************************/

// --- Background Settings ---
function applyBackgroundSettings(type) {
  if (!backgroundLayer) return;
  if (type === 'solid' && bgSolidColorInput) { backgroundLayer.style.background = bgSolidColorInput.value; }
  else if (type === 'gradient' && bgGradientDegree && bgGradientStart && bgGradientEnd) {
      const deg = parseInt(bgGradientDegree.value, 10) || 0;
      const start = bgGradientStart.value; const end = bgGradientEnd.value;
      backgroundLayer.style.background = `linear-gradient(${deg}deg, ${start}, ${end})`;
      backgroundLayer.style.backgroundSize = "cover";
  } else if (type === 'image' && bgImageFileInput && bgImageUrlInput && bgImagePreview) {
      const url = getImageURL(bgImageFileInput, bgImageUrlInput, 'background');
      if (url) {
           backgroundLayer.style.backgroundImage = `url("${url}")`;
           backgroundLayer.style.backgroundPosition = 'center center';
           backgroundLayer.style.backgroundSize = 'cover';
           backgroundLayer.style.backgroundRepeat = 'no-repeat';
           backgroundLayer.style.backgroundColor = '';
           bgImagePreview.src = url; bgImagePreview.style.display = 'block';
      } else { backgroundLayer.style.backgroundImage = 'none'; bgImagePreview.style.display = 'none'; alert("Provide valid image URL/file."); }
  }
  applyDigitStylesForAllChunks(); // Re-align masks
}

// --- Digits Settings ---
// Helper to get the DOM elements for a chunk key
function getChunkElements(chunkKey) {
    switch(chunkKey) {
        case 'hours': return [hoursEl];
        case 'minutes': return [minutesEl];
        case 'seconds': return [secondsEl];
        case 'separators': return [sep1El, sep2El];
        case 'global': return allChunks; // Applying global affects all
        default: return [];
    }
}

// Main function to apply style to a specific chunk (or all if global)
function applyDigitStyleForChunk(chunkKey, styleType, styleValue) {
     console.log(`Applying style ${styleType} to ${chunkKey} with value:`, styleValue);
     const elements = getChunkElements(chunkKey);
     if (!elements.length) return;

     // Store the setting
     const setting = { type: styleType, value: styleValue };
     if (chunkKey === 'global') {
         globalDigitSettings = setting;
         // Clear specific settings when global is applied? Or keep overrides?
         // Let's keep overrides for now. User can reset specifics to 'global'.
         // Apply to all chunks now, respecting overrides later
         applyDigitStylesForAllChunks();
     } else {
         chunkSpecificSettings[chunkKey] = setting;
         // Apply just to this chunk/these elements
         elements.forEach(el => applyStyleToElement(el, setting));
     }
}

// Applies the actual CSS to a single DOM element based on stored settings
function applyStyleToElement(element, setting) {
     if (!element || !setting) return;

     // Reset common styles first
     element.style.color = 'transparent'; // Base for masking
     element.style.backgroundImage = 'none';
     element.style.backgroundClip = 'text';
     element.style.webkitBackgroundClip = 'text';
     element.style.webkitTextFillColor = 'transparent'; // Needed for mask/gradient/image

     // Apply specific style
     switch (setting.type) {
         case 'solid':
             element.style.color = setting.value; // Direct color
             element.style.webkitTextFillColor = setting.value; // Override transparency
             element.style.backgroundClip = 'unset'; // Not needed for solid
             element.style.webkitBackgroundClip = 'unset';
             element.style.backgroundImage = 'none';
              // Special handling for separators if they shouldn't be masked
             if (element === sep1El || element === sep2El) {
                 // Keep non-masked style unless explicitly masked/imaged
             }
             break;
         case 'gradient':
             const { deg, start, end } = setting.value;
             element.style.backgroundImage = `linear-gradient(${deg}deg, ${start}, ${end})`;
             element.style.backgroundSize = '100%'; // Ensure gradient fills text area
              element.style.backgroundClip = 'text';
              element.style.webkitBackgroundClip = 'text';
              element.style.webkitTextFillColor = 'transparent';
             break;
         case 'image':
             element.style.backgroundImage = `url("${setting.value}")`;
             element.style.backgroundPosition = 'center';
             element.style.backgroundSize = 'cover';
              element.style.backgroundClip = 'text';
              element.style.webkitBackgroundClip = 'text';
              element.style.webkitTextFillColor = 'transparent';
             break;
         case 'mask':
              element.style.background = 'none'; // Remove chunk-specific background
              element.style.backgroundClip = 'text';
              element.style.webkitBackgroundClip = 'text';
              element.style.webkitTextFillColor = 'transparent';
             alignChunkBackground(element); // Align with main background
             break;
        case 'global': // This case occurs when resetting a specific chunk
            const globalSetting = globalDigitSettings;
            applyStyleToElement(element, globalSetting); // Apply the current global setting
            break;
     }
}


// Re-apply styles to all chunks based on stored global/specific settings
function applyDigitStylesForAllChunks() {
    allChunks.forEach(el => {
        let chunkId = null;
        if (el === hoursEl) chunkId = 'hours';
        else if (el === minutesEl) chunkId = 'minutes';
        else if (el === secondsEl) chunkId = 'seconds';
        else if (el === sep1El || el === sep2El) chunkId = 'separators';

        if (chunkId) {
            const specificSetting = chunkSpecificSettings[chunkId];
            applyStyleToElement(el, specificSetting || globalDigitSettings); // Use specific or fallback to global
        }
    });
}

// Align chunk background for 'mask' effect (Mostly unchanged)
function alignChunkBackground(chunk) {
    // Check if this chunk *should* be masked currently
    let chunkId = null;
    if (chunk === hoursEl) chunkId = 'hours';
    else if (chunk === minutesEl) chunkId = 'minutes';
    else if (chunk === secondsEl) chunkId = 'seconds';
    else if (chunk === sep1El || chunk === sep2El) chunkId = 'separators';

    const setting = chunkId ? (chunkSpecificSettings[chunkId] || globalDigitSettings) : globalDigitSettings;

    if (!setting || setting.type !== 'mask') {
         // Ensure background position is cleared if not masking
         chunk.style.backgroundPosition = '';
         return;
    }


    const rect = chunk.getBoundingClientRect();
    const bgRect = backgroundLayer.getBoundingClientRect();
    const bgStyle = window.getComputedStyle(backgroundLayer);

    // Calculate offset
    const left = rect.left - bgRect.left;
    const top = rect.top - bgRect.top;

    // Get computed background style from the main layer
    chunk.style.backgroundImage = bgStyle.backgroundImage;
    chunk.style.backgroundSize = bgStyle.backgroundSize;
    chunk.style.backgroundRepeat = bgStyle.backgroundRepeat;
    chunk.style.backgroundColor = 'transparent'; // Ensure no color block

    // Apply the offset position
    chunk.style.backgroundPosition = `-${left}px -${top}px`;
    chunk.style.webkitTextFillColor = 'transparent'; // Crucial for mask
    chunk.style.color = 'transparent';
}

// --- Font Settings ---
function applyFont(fontFamily, isCustom = false, blobURL = null) {
    currentFontName = fontFamily; // Store the name/stack

    if (isCustom && blobURL) {
        const styleId = "custom-font-style";
        let styleEl = document.getElementById(styleId);
        if (!styleEl) {
            styleEl = document.createElement("style");
            styleEl.id = styleId;
            document.head.appendChild(styleEl);
        }
        // Use a consistent custom font name
        const customFontInternalName = "UserCustomFont";
        styleEl.innerHTML = `
          @font-face {
            font-family: '${customFontInternalName}';
            src: url('${blobURL}');
          }
        `;
        // Apply using the internal name
         allChunks.forEach(ch => ch.style.fontFamily = `'${customFontInternalName}', ${currentFontName}`); // Fallback
    } else {
         // Apply directly from select or default
         allChunks.forEach(ch => ch.style.fontFamily = currentFontName);
    }

    // Re-align masks if needed, as font change affects geometry
    applyDigitStylesForAllChunks();
}

// --- Style Settings (Opacity/Blur) ---
function applyBackgroundStyle() {
  if (!bgOpacityInput || !bgBlurInput || !backgroundLayer || !bgOpacityValue || !bgBlurValue) return;
  const opacity = bgOpacityInput.value; const blur = bgBlurInput.value;
  backgroundLayer.style.opacity = opacity; backgroundLayer.style.filter = `blur(${blur}px)`;
  bgOpacityValue.textContent = parseFloat(opacity).toFixed(2); bgBlurValue.textContent = `${blur}px`;
  applyDigitStylesForAllChunks();
}

// === ADDED CHECK FOR NEW ELEMENT ===
function applyDigitsStyle() {
    // Check required elements
    if (!digitsOpacityInput || !digitsBlurInput || !clockContainer || !digitsOpacityValue || !digitsBlurValue) {
         console.warn("Cannot apply opacity/blur styles, elements missing.");
         return;
    }
    console.log("Applying digits opacity/blur...");

    // Apply opacity and blur ONLY
    const opacity = digitsOpacityInput.value;
    const blur = digitsBlurInput.value || 0;
    clockContainer.style.opacity = opacity;
    clockContainer.style.filter = `blur(${blur}px)`;

    // Update displays
    digitsOpacityValue.textContent = parseFloat(opacity).toFixed(2);
    digitsBlurValue.textContent = `${blur}px`;

    // --- REMOVE GLOW LOGIC FROM HERE ---
    // clockContainer.style.setProperty('--glow-color', previewGlowColor); // DELETE
    // clockContainer.classList.toggle('glow-enabled', previewGlowEnabled); // DELETE
    // --- END REMOVE ---

    // Optional: Realign masks if blur affects layout significantly
    // alignChunkBackgroundIfMasked();
}
console.log("Settings application functions defined.");

/********************************************
* DRAG & DROP (Merged Logic)
********************************************/
function handleDragStart(e) {
    const target = e.target;
    // Check if target is clock chunk OR draggable UI
    const isChunk = target.classList.contains("chunk") && target.id;
    const isDraggableUI = target.classList.contains("draggable-ui");

    if (!isChunk && !isDraggableUI) return; // Not draggable
    if (isPanelOpen && settingsPanel?.contains(target)) return; // Don't drag if click starts inside open panel

    const coords = getEventCoords(e);
    const rect = target.getBoundingClientRect();

    if (isChunk) {
        currentDrag = target;
        isDraggingClockChunk = true;
        const containerRect = clockContainer.getBoundingClientRect();
        dragOffsetX = coords.x - rect.left; dragOffsetY = coords.y - rect.top;
        currentDrag.style.position = "absolute";
        currentDrag.style.left = (rect.left - containerRect.left) + "px";
        currentDrag.style.top = (rect.top - containerRect.top) + "px";
        currentDrag.style.zIndex = 9999; currentDrag.style.cursor = 'grabbing';
    } else { // isDraggableUI
        currentUiDrag = target;
        uiDragOffsetX = coords.x - rect.left; uiDragOffsetY = coords.y - rect.top;
        if (window.getComputedStyle(currentUiDrag).position === 'static') {
            currentUiDrag.style.position = 'absolute'; // Ensure position allows top/left
        }
        currentUiDrag.classList.add('dragging'); currentUiDrag.style.cursor = 'grabbing';
    }
    document.body.style.cursor = 'grabbing';
}

function handleDragMove(e) { // Combined move logic
    const coords = getEventCoords(e);
    if (currentDrag) { // Dragging a clock chunk
        e.preventDefault(); // Prevent scroll only when dragging chunk
        const containerRect = clockContainer.getBoundingClientRect();
        const mouseXRelative = coords.x - containerRect.left;
        const mouseYRelative = coords.y - containerRect.top;
        const newLeft = mouseXRelative - dragOffsetX;
        const newTop = mouseYRelative - dragOffsetY;
        currentDrag.style.left = newLeft + "px"; currentDrag.style.top = newTop + "px";
        // Mask alignment check...
        const chunkId = currentDrag.id;
        if (chunkId) { const setting = chunkSpecificSettings[chunkId] || globalDigitSettings; if (setting && setting.type === 'mask') alignChunkBackground(currentDrag); }
    } else if (currentUiDrag) { // Dragging a generic UI element
        e.preventDefault(); // Prevent scroll when dragging UI
        const newTop = coords.y - uiDragOffsetY; const newLeft = coords.x - uiDragOffsetX;
        // Keep within viewport bounds (optional but recommended)
        const vpWidth = document.documentElement.clientWidth;
        const vpHeight = document.documentElement.clientHeight;
        const elRect = currentUiDrag.getBoundingClientRect(); // Get width/height for bounds check
        const constrainedLeft = Math.max(0, Math.min(newLeft, vpWidth - elRect.width));
        const constrainedTop = Math.max(0, Math.min(newTop, vpHeight - elRect.height));
        currentUiDrag.style.left = constrainedLeft + 'px';
        currentUiDrag.style.top = constrainedTop + 'px';
    }
}

function handleDragEnd(e) { // Combined end logic
    if (currentDrag) { currentDrag.style.zIndex = 1; currentDrag.style.cursor = 'move'; }
    if (currentUiDrag) { currentUiDrag.classList.remove('dragging'); currentUiDrag.style.cursor = 'grab'; }
    document.body.style.cursor = 'default';
    setTimeout(() => { isDraggingClockChunk = false; currentDrag = null; currentUiDrag = null; }, 0);
}

console.log("Drag & Drop functions defined/merged.");

/********************************************
 * SHORTCUTS 
********************************************/
// Function to format key event data into a display string
function formatShortcutKey(e) {
    if (!e || !e.key) return '';
    let parts = [];
    if (e.ctrlKey) parts.push('Ctrl');
    if (e.altKey) parts.push('Alt');
    if (e.shiftKey) parts.push('Shift');

    // Handle specific key names
    let keyName = e.key;
    if (keyName === ' ') keyName = 'Space';
    else if (keyName.length > 1) keyName = keyName; // Keep Escape, ArrowUp etc.
    else keyName = keyName.toLowerCase(); // Lowercase single chars

    // Avoid adding modifier if it's the only part (e.g., just pressing Ctrl)
    if (!(parts.length > 0 && e.key.toLowerCase().includes(parts[parts.length-1].toLowerCase()))) {
         parts.push(keyName);
    }

    return parts.join('+');
}

// Function to populate the shortcut input fields
function displayShortcuts() {
    if (!shortcutSettingsList) return;
    const inputs = shortcutSettingsList.querySelectorAll('.shortcut-input');
    inputs.forEach(input => {
        const action = input.dataset.action;
        input.value = currentShortcuts[action] || ''; // Display current or empty
    });
}

// Function to save shortcuts (e.g., to localStorage)
function saveShortcuts() {
    try {
        localStorage.setItem('clockShortcuts', JSON.stringify(currentShortcuts));
        console.log("Shortcuts saved to localStorage.");
        alert("Shortcuts saved!");
    } catch (e) {
        console.error("Failed to save shortcuts to localStorage:", e);
        alert("Failed to save shortcuts.");
    }
}

// Function to load shortcuts
function loadShortcuts() {
    try {
        const saved = localStorage.getItem('clockShortcuts');
        if (saved) {
            currentShortcuts = JSON.parse(saved);
            console.log("Shortcuts loaded from localStorage.");
        } else {
            currentShortcuts = { ...defaultShortcuts }; // Use defaults if nothing saved
            console.log("No saved shortcuts found, using defaults.");
        }
    } catch (e) {
        console.error("Failed to load or parse shortcuts from localStorage:", e);
        currentShortcuts = { ...defaultShortcuts }; // Fallback to defaults
    }
    displayShortcuts(); // Update the inputs visually
}

// Function to handle key capture for shortcut input
function captureShortcut(e) {
    if (!activeShortcutInput) return;

    e.preventDefault(); // Prevent typing the key in the box
    e.stopPropagation();

    const shortcutString = formatShortcutKey(e);
    const action = activeShortcutInput.dataset.action;

    // Check for conflicts (optional but recommended)
    for (const act in currentShortcuts) {
         if (currentShortcuts[act] === shortcutString && act !== action) {
             alert(`Shortcut "${shortcutString}" is already assigned to "${act.replace(/([A-Z])/g, ' $1').trim()}". Please choose another.`); // Nicer action name
             return; // Don't assign conflict
         }
    }


    activeShortcutInput.value = shortcutString; // Display the captured key(s)
    currentShortcuts[action] = shortcutString; // Update the state *temporarily*

    console.log(`Captured shortcut for ${action}: ${shortcutString}`);

    // Remove focus styling and listener
    activeShortcutInput.blur(); // Remove focus
}

// Function to clear the shortcut listener when focus is lost
function endShortcutCapture() {
    if (activeShortcutInput) {
         activeShortcutInput.removeEventListener('keydown', captureShortcut);
         activeShortcutInput.removeEventListener('blur', endShortcutCapture); // Remove self
         activeShortcutInput.style.backgroundColor = '#f0f0f0'; // Reset background
         activeShortcutInput = null;
         console.log("Ended shortcut capture.");
    }
}

/********************************************
* AUDIO HANDLER FUNCTIONS
********************************************/

function playSoundWithCheck(audioObject, volume) {
    if (!audioObject) {
        console.warn("Attempted to play null audio object.");
        return;
    }
    if (!userInteracted) {
        console.warn("Audio play skipped: User interaction required first.");
        // Optionally queue the sound to play after first interaction? More complex.
        return;
    }

    try {
        audioObject.pause(); // Stop previous playback just in case
        audioObject.currentTime = 0; // Rewind
        audioObject.volume = volume; // Set desired volume
        // Play returns a Promise
        audioObject.playbackRate = Math.max(0.5, Math.min(4, clockSpeed || 1.0));
        const playPromise = audioObject.play();

        if (playPromise !== undefined) {
            playPromise.then(_ => {
                // Playback started successfully
                // console.log("Audio playback started.");
            }).catch(error => {
                console.error("Audio playback failed:", error);
                // Example: Browser might throw NotAllowedError if interaction still needed
                // Or NotSupportedError for unsupported format/encoding
            });
        }
    } catch (e) {
        console.error("Error attempting to play audio:", e);
    }
}

function handleSoundSelection() {
    if (!soundSelect) return;
    const selectedValue = soundSelect.value;
    console.log("Tick sound selected:", selectedValue);
    if (selectedValue !== 'custom' && customAudioURL) { URL.revokeObjectURL(customAudioURL); customAudioURL = null; lastObjectURLs['customSound'] = null; if(soundFile) soundFile.value = ''; }
    if (selectedValue === 'custom') {
         if (customAudioURL) { currentAudio = new Audio(customAudioURL); currentAudio.volume = tickVolume; console.log("Using existing custom tick sound."); }
         else { currentAudio = null; console.log("Custom selected, waiting for upload."); }
    } else if (sounds[selectedValue]) {
        currentAudio = sounds[selectedValue]; // Already preloaded with volume set
    } else {
        currentAudio = null; // 'none'
    }
}

function handleSoundUpload(event) {
     const file = event.target.files[0]; if (!file) return;
     if (customAudioURL) { URL.revokeObjectURL(customAudioURL); customAudioURL = null; lastObjectURLs['customSound'] = null; }
     if (!file.type.startsWith('audio/')) { alert('Please select a valid audio file.'); if(soundFile) soundFile.value = ''; return; }
     customAudioURL = URL.createObjectURL(file); lastObjectURLs['customSound'] = customAudioURL;
     const tempAudio = new Audio();
     tempAudio.addEventListener('loadedmetadata', () => {
         console.log("Custom tick duration:", tempAudio.duration);
         if (tempAudio.duration > 2.1) { // Allow slightly over 2s
             alert(`Tick sound too long (${tempAudio.duration.toFixed(2)}s). Max 2 seconds.`);
             URL.revokeObjectURL(customAudioURL); customAudioURL = null; lastObjectURLs['customSound'] = null;
             if(soundFile) soundFile.value = ''; if(soundSelect) soundSelect.value = 'none'; currentAudio = null;
         } else {
             currentAudio = new Audio(customAudioURL); currentAudio.volume = tickVolume;
             if(soundSelect) soundSelect.value = 'custom'; console.log("Custom tick sound loaded.");
         }
     });
     tempAudio.addEventListener('error', (e) => { alert('Error loading audio metadata.'); console.error("Audio metadata error:", e); URL.revokeObjectURL(customAudioURL); customAudioURL = null; lastObjectURLs['customSound'] = null; if(soundFile) soundFile.value = ''; if(soundSelect) soundSelect.value = 'none'; currentAudio = null; });
     tempAudio.src = customAudioURL;
}

function handleAlarmSoundSelection() {
    if (!alarmSelect) return;
    const selectedValue = alarmSelect.value;
    console.log("Alarm selected:", selectedValue);
    if (selectedValue !== 'customAlarm' && customAlarmAudioURL) { URL.revokeObjectURL(customAlarmAudioURL); customAlarmAudioURL = null; lastObjectURLs['customAlarmSound'] = null; if(alarmFile) alarmFile.value = ''; }
    if (selectedValue === 'customAlarm') {
         if (customAlarmAudioURL) { currentAlarmAudio = new Audio(customAlarmAudioURL); currentAlarmAudio.volume = alarmVolume; }
         else { currentAlarmAudio = null; }
    } else if (alarmSounds[selectedValue]) {
        currentAlarmAudio = alarmSounds[selectedValue]; // Already preloaded with volume set
    } else {
        currentAlarmAudio = null; // 'none'
    }
}

function handleAlarmUpload(event) {
     const file = event.target.files[0]; if (!file) return;
     if (customAlarmAudioURL) { URL.revokeObjectURL(customAlarmAudioURL); customAlarmAudioURL = null; lastObjectURLs['customAlarmSound'] = null; }
     if (!file.type.startsWith('audio/')) { alert('Please select valid audio.'); if(alarmFile) alarmFile.value = ''; return; }
     customAlarmAudioURL = URL.createObjectURL(file); lastObjectURLs['customAlarmSound'] = customAlarmAudioURL;
     // Optional duration check for alarm can go here
     currentAlarmAudio = new Audio(customAlarmAudioURL); currentAlarmAudio.volume = alarmVolume;
     if(alarmSelect) alarmSelect.value = 'customAlarm'; console.log("Custom alarm sound loaded.");
}

function playAlarmSound() {
    console.log("Attempting to play alarm sound...");
    playSoundWithCheck(currentAlarmAudio, alarmVolume);
}

console.log("Audio handlers defined.");

/********************************************
* GLOBAL KEYDOWN HANDLER (for shortcuts)
********************************************/
// The actual handler function (defined outside setupEventListeners)
function globalKeydownHandler(e) {
  // Ignore if typing in inputs/selects OR if capturing a shortcut
  if (activeShortcutInput || (document.activeElement && ['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName))) {
      return;
  }
  const pressedShortcut = formatShortcutKey(e);
  let actionToPerform = null;
  let handled = false;
  // Find which action matches the pressed shortcut
  for (const action in currentShortcuts) {
      if (currentShortcuts[action] === pressedShortcut) {
          actionToPerform = action;
          break;
      }
  }
  // Handle Space separately if not assigned explicitly
  if (!actionToPerform && pressedShortcut === 'Space') {
      actionToPerform = 'toggleStartPause'; // Default Space action
  }
  if (actionToPerform) {
      console.log(`Shortcut detected: ${pressedShortcut} -> Action: ${actionToPerform}`);
      handled = true; // Assume handled if action found
      switch(actionToPerform) {
          case 'toggleStartPause':
              if (currentMode === 'timer' || currentMode === 'stopwatch') {
                  if (timerInterval || stopwatchInterval) {
                      if (pauseButton) pauseButton.click(); else console.warn("Pause button missing");
                  } else {
                      if (startButton) startButton.click(); else console.warn("Start button missing");
                  }
              } else handled = false;
              break;
          case 'resetTimerStopwatch':
              if (currentMode === 'timer' || currentMode === 'stopwatch') {
                  if (resetButton) resetButton.click(); else console.warn("Reset button missing");
              } else handled = false;
              break;
          case 'nextMode':
              if (modeSelect) {
                  const currentIndex = modeSelect.selectedIndex;
                  const nextIndex = (currentIndex + 1) % modeSelect.options.length;
                  modeSelect.selectedIndex = nextIndex;
                  modeSelect.dispatchEvent(new Event('change'));
              } else handled = false;
              break;
          case 'toggleLayout':
              if (toggleLayoutButton) toggleLayoutButton.click(); else handled = false;
              break;
          case 'closeSettings':
              if (isPanelOpen && settingsPanel && bodyElement) {
                  isPanelOpen = false;
                  settingsPanel.classList.remove('open');
                  bodyElement.classList.remove('settings-panel-open');
              } else handled = false;
              break;
          // Add cases for any other actions you define
          default:
              handled = false;
              console.warn(`Unhandled action mapped: ${actionToPerform}`);
              break;
      }
  }
  if (handled) {
      e.preventDefault(); // Prevent default browser action
  }
}

/********************************************
* EVENT LISTENERS SETUP
********************************************/
function setupEventListeners() {
  console.log("Attempting to setup event listeners..."); // Debug start

  try { // Wrap in try...catch to catch errors during setup

      // === MOVED TAB BUTTON LISTENERS HERE ===
        // Main Tabs
        if (tabButtons && tabButtons.length > 0) { // Check if elements exist
          tabButtons.forEach(button => {
              button.addEventListener('click', () => {
                  showTab(button.dataset.tab, false);
              });
          });
          console.log("Main tab button listeners attached."); // Debug
      } else {
          console.warn("tabButtons NodeList not found or empty.");
      }

      // Nested Digit Tabs
      if (digitTabButtons && digitTabButtons.length > 0) { // Check if elements exist
          digitTabButtons.forEach(button => {
              button.addEventListener('click', () => {
                  showTab(button.dataset.tab, true);
              });
          });
          console.log("Nested digit tab button listeners attached."); // Debug
      } else {
          console.warn("digitTabButtons NodeList not found or empty.");
      }
      // === END MOVED BLOCK ===

      // Layout toggle
      if (toggleLayoutButton) {
          toggleLayoutButton.addEventListener("click", toggleLayout);
      } else {
          console.warn("toggleLayoutButton not found for listener.");
      }

      // Settings panel show/hide
      if (settingsButton) {
          settingsButton.addEventListener("click", (e) => {
              console.log("Settings Button Click Handler Fired!"); // DEBUG
              e.stopPropagation(); // IMPORTANT: Prevent click from reaching document listener immediately
              isPanelOpen = !isPanelOpen;
              settingsPanel.classList.toggle('open', isPanelOpen);
              bodyElement.classList.toggle('settings-panel-open', isPanelOpen); // Toggle body class for hover controls CSS
          });
          console.log("Settings button listener attached."); // Debug
      } else {
          // This is critical, script might not function correctly without it.
          console.error("CRITICAL: Cannot attach listener - settingsButton element not found!");
      }

      // Close settings panel on click outside
      document.addEventListener('click', (e) => {
           // Basic check first: console.log("Document Clicked");
           if ( isPanelOpen &&
                settingsPanel && // Ensure panel exists
                settingsButton && // Ensure button exists
                !settingsPanel.contains(e.target) && // Click NOT inside panel
                e.target !== settingsButton && // Click NOT on button itself
                !settingsButton.contains(e.target) && // Click NOT inside button (e.g., icon)
                !isDraggingClockChunk // Click NOT part of a finished drag
              ) {
                  // console.log("Click outside detected, closing panel."); // Debug
                  isPanelOpen = false;
                  settingsPanel.classList.remove('open');
                  bodyElement.classList.remove('settings-panel-open');
          }
          // isDraggingClockChunk reset happens in handleDragEnd timeout
      });
      console.log("Document click listener (for closing panel) attached."); // Debug

      // --- Mode, Sliders, Background, Digits, Font, Style Listeners ---

      // Mode selection
      if (modeSelect) {
          modeSelect.addEventListener("change", e => { currentMode = e.target.value; updateUIForMode(currentMode); });
      } else {
          console.warn("modeSelect not found for listener.");
      }

      // Tick speed & Clock size
      if (tickSpeedInput) {
          tickSpeedInput.addEventListener("change", e => {
               const val = parseFloat(e.target.value);
               if (!isNaN(val) && val > 0) {
                   clockSpeed = val;
                   if (currentMode === 'clock') startClock(); // Restart clock if speed changes
               }
           });
      } else {
          console.warn("tickSpeedInput not found for listener.");
      }

      if (clockSizeInput) {
          clockSizeInput.addEventListener("input", debounce(e => {
              const val = e.target.value;
              allChunks.forEach(ch => { ch.style.fontSize = val + "vw"; });
              applyDigitStylesForAllChunks(); // Realign masks after size change
           }, 50));
      } else {
          console.warn("clockSizeInput not found for listener.");
      }

      // --- Shortcut Settings Listeners ---
      if (shortcutSettingsList) {
          shortcutSettingsList.addEventListener('focusin', (e) => {
              if (e.target.classList.contains('shortcut-input')) {
                  // If another input was active, end its capture first
                  if (activeShortcutInput && activeShortcutInput !== e.target) {
                      endShortcutCapture();
                  }
                  // Start capture for the new input
                  activeShortcutInput = e.target;
                  activeShortcutInput.value = 'Press key(s)...'; // Prompt user
                  activeShortcutInput.style.backgroundColor = '#e0e0ff'; // Highlight
                  // Add listeners specific to this input instance
                  activeShortcutInput.addEventListener('keydown', captureShortcut);
                  activeShortcutInput.addEventListener('blur', endShortcutCapture); // End capture on blur
                  console.log(`Started shortcut capture for: ${activeShortcutInput.dataset.action}`);
              }
          });
          // Initial population
          loadShortcuts(); // Load saved/defaults and display them
      } else { console.warn("shortcutSettingsList not found."); }


      if (saveShortcutsButton) {
          saveShortcutsButton.addEventListener('click', saveShortcuts);
      } else { console.warn("saveShortcutsButton not found."); }

      if (resetShortcutsButton) {
          resetShortcutsButton.addEventListener('click', () => {
              if (confirm("Reset all shortcuts to default?")) {
                  currentShortcuts = { ...defaultShortcuts };
                  displayShortcuts();
                  // Optionally save defaults immediately
                  // saveShortcuts();
                  console.log("Shortcuts reset to defaults.");
              }
          });
      } else { console.warn("resetShortcutsButton not found."); }

      // --- Modify Existing Main Keydown Listener ---
      document.removeEventListener('keydown', globalKeydownHandler); // Remove old one if exists
      document.addEventListener('keydown', globalKeydownHandler); // Add the new handler
      console.log("Global keyboard shortcut listener attached/updated.");

      // Event delegations for dynamic content (safer if parent exists)
      const backgroundTab = document.getElementById('background-tab');
      if (backgroundTab) {
          backgroundTab.addEventListener('click', e => {
               if (e.target.matches('button[data-apply^="bg-"]')) {
                   const type = e.target.dataset.apply.split('-')[1];
                   applyBackgroundSettings(type);
               }
           });
      } else {
           console.warn("background-tab not found for delegation listener.");
      }

      if (bgImageFileInput) {
           bgImageFileInput.addEventListener('change', () => {
               const url = getImageURL(bgImageFileInput, null, 'background-preview');
               if (url) { bgImagePreview.src = url; bgImagePreview.style.display = 'block'; }
               else { bgImagePreview.style.display = 'none'; }
           });
      } else {
           console.warn("bgImageFileInput not found for listener.");
      }

      const digitsTab = document.getElementById('digits-tab');
      if (digitsTab) {
           // Listener for Apply buttons within digits tab
           digitsTab.addEventListener('click', e => {
               if (e.target.matches('.apply-digit-style')) {
                  // Find closest parent container for this style group
                  const optionsDiv = e.target.closest('.digit-style-options');
                  if (!optionsDiv) return; // Should not happen

                  const chunkKey = optionsDiv.dataset.chunk;
                  const styleType = e.target.dataset.style;
                  let styleValue = null;

                  // Determine style value based on type
                  switch(styleType) {
                      case 'solid': styleValue = optionsDiv.querySelector('.digit-solid-color').value; break;
                      case 'gradient': styleValue = { deg: parseInt(optionsDiv.querySelector('.digit-gradient-degree').value, 10) || 0, start: optionsDiv.querySelector('.digit-gradient-start').value, end: optionsDiv.querySelector('.digit-gradient-end').value }; break;
                      case 'image':
                          const fileInput = optionsDiv.querySelector('.digit-image-file');
                          const urlInput = optionsDiv.querySelector('.digit-image-url');
                          const objectURLKey = `digits-${chunkKey}`;
                          styleValue = getImageURL(fileInput, urlInput, objectURLKey);
                          if (!styleValue) { alert(`Provide URL or upload image for ${chunkKey}.`); return; }
                          const preview = optionsDiv.querySelector('.digit-image-preview');
                          if(preview) { preview.src = styleValue; preview.style.display = 'block'; }
                          break;
                      case 'mask': styleValue = true; break; // Type is sufficient value
                      case 'global':
                          chunkSpecificSettings[chunkKey] = null; // Clear specific setting
                          applyDigitStylesForAllChunks(); // Re-apply everything
                          return; // Exit early
                  }
                  // Apply the determined style
                  applyDigitStyleForChunk(chunkKey, styleType, styleValue);
               }
           });
           // Listener for Image file previews within digits tab
           digitsTab.addEventListener('change', e => {
               if (e.target.matches('.digit-image-file')) {
                  const fileInput = e.target;
                  const optionsDiv = fileInput.closest('.digit-style-options');
                  if (!optionsDiv) return;
                  const preview = optionsDiv.querySelector('.digit-image-preview');
                  const chunkKey = optionsDiv.dataset.chunk;
                  const url = getImageURL(fileInput, null, `preview-digits-${chunkKey}`); // Preview-only key
                  if (url && preview) { preview.src = url; preview.style.display = 'block'; }
                  else if (preview) { preview.style.display = 'none'; }
               }
           });
      } else {
          console.warn("digits-tab not found for delegation listeners.");
      }

      // Font Settings
      if (applyBaseFontBtn) {
          applyBaseFontBtn.addEventListener('click', () => {
               const selectedFont = fontSelect.value;
               if (selectedFont !== 'custom') applyFont(selectedFont);
               else alert("Use 'Upload Custom Font'.");
          });
      } else {
           console.warn("applyBaseFontBtn not found for listener.");
      }

      if (applyCustomFontBtn) {
          applyCustomFontBtn.addEventListener('click', () => {
               const file = fontFileInput.files[0];
               if (!file) { alert("Select font file."); return; }
               if (lastObjectURLs.font) URL.revokeObjectURL(lastObjectURLs.font);
               const blobURL = URL.createObjectURL(file);
               lastObjectURLs.font = blobURL;
               applyFont(`'UserCustomFont', ${fontSelect.value || currentFontName}`, true, blobURL);
           });
      } else {
           console.warn("applyCustomFontBtn not found for listener.");
      }

      // Style Settings
      if (bgOpacityInput) bgOpacityInput.addEventListener('input', debounce(applyBackgroundStyle, 50)); else console.warn("bgOpacityInput not found");
      if (bgBlurInput) bgBlurInput.addEventListener('input', debounce(applyBackgroundStyle, 50)); else console.warn("bgBlurInput not found");
      if (applyBgStyleBtn) applyBgStyleBtn.addEventListener('click', applyBackgroundStyle); else console.warn("applyBgStyleBtn not found");

      if (digitsOpacityInput) digitsOpacityInput.addEventListener('input', debounce(applyDigitsStyle, 50)); else console.warn("digitsOpacityInput not found");
      if (digitsBlurInput) digitsBlurInput.addEventListener('input', debounce(applyDigitsStyle, 50)); else console.warn("digitsBlurInput not found for listener");
      if (applyDigitsStyleBtn) applyDigitsStyleBtn.addEventListener('click', applyDigitsStyle); else console.warn("applyDigitsStyleBtn not found");
      //Glow effect
      if (glowToggle && clockContainer) {
        glowToggle.addEventListener('change', (e) => {
            const isEnabled = e.target.checked;
            clockContainer.classList.toggle('glow-enabled', isEnabled);
            console.log("Glow effect toggled:", isEnabled);
            // alignChunkBackgroundIfMasked(); // <<< DELETE OR COMMENT OUT THIS LINE
        });
        // Optional: Set initial checkbox state
        // glowToggle.checked = clockContainer.classList.contains('glow-enabled');
        console.log("Glow toggle listener attached.");
    } else {
        console.warn("Glow toggle or clock container missing.");
    }

    // Glow Color Listener (Should be okay as is)
    if (glowColorInput && clockContainer) {
        glowColorInput.addEventListener('input', debounce((e) => {
            const color = e.target.value;
            console.log("Glow color changed:", color);
            clockContainer.style.setProperty('--glow-color', color);
        }, 50));
        console.log("Glow color listener attached.");
    } else {
        console.warn("Glow color input or clock container missing.");
    }

      // Timer/Stopwatch Controls (Panel)
      if (setButton) setButton.addEventListener("click", () => { if (currentMode === "timer") setTimer(); else if (currentMode === "stopwatch") setStopwatch(); else alert("Set only applies to Timer or Stopwatch mode."); }); else console.warn("setButton not found");
      if (startButton) startButton.addEventListener("click", () => { if (currentMode === "timer") startTimer(); else if (currentMode === "stopwatch") startStopwatch(); else alert("Clock runs automatically. Use Timer or Stopwatch mode to Start."); }); else console.warn("startButton not found");
      if (pauseButton) pauseButton.addEventListener("click", () => { if (currentMode === "timer") pauseTimer(); else if (currentMode === "stopwatch") pauseStopwatch(); }); else console.warn("pauseButton not found");
      if (resetButton) resetButton.addEventListener("click", () => { if (currentMode === "timer") resetTimer(); else if (currentMode === "stopwatch") resetStopwatch(); }); else console.warn("resetButton not found");

      // Top Controls (Hover Buttons)
      if (topStartButton) topStartButton.addEventListener("click", () => { if (currentMode === "timer") startTimer(); else if (currentMode === "stopwatch") startStopwatch(); }); else console.warn("topStartButton not found");
      if (topPauseButton) topPauseButton.addEventListener("click", () => { if (currentMode === "timer") pauseTimer(); else if (currentMode === "stopwatch") pauseStopwatch(); }); else console.warn("topPauseButton not found");
      if (topStopButton) topStopButton.addEventListener("click", () => { if (currentMode === "timer") resetTimer(); else if (currentMode === "stopwatch") resetStopwatch(); }); else console.warn("topStopButton not found");

      // Drag events (Now handles BOTH chunk and UI drags)
      // We attach to document to catch events even if mouse leaves element quickly
      document.addEventListener("mousedown", handleDragStart); // Checks target inside
      document.addEventListener("mousemove", handleDragMove);
      document.addEventListener("mouseup", handleDragEnd);
      document.addEventListener("touchstart", handleDragStart, { passive: true }); // Checks target inside
      document.addEventListener("touchmove", handleDragMove, { passive: false });
      document.addEventListener("touchend", handleDragEnd);
      console.log("Unified drag listeners attached to document.");
      document.addEventListener('click', handleFirstInteraction, { once: true }); // Run only once
      document.addEventListener('touchstart', handleFirstInteraction, { once: true });
      document.addEventListener('keydown', handleFirstInteraction, { once: true });
      console.log("First interaction listeners attached.");

      // --- Audio Tab Listeners ---
      // Audio Tab Listeners...
      if (soundToggle) {
        soundToggle.addEventListener('change', (e) => { soundEnabled = e.target.checked; console.log(`Sound enabled toggled: ${soundEnabled}`); if(soundEnabled) handleSoundSelection(); });
        console.log("Sound toggle listener attached.");
        } else {
            console.warn("soundToggle missing, cannot attach listener.");}
      if (soundSelect) { soundSelect.addEventListener('change', handleSoundSelection); } else { console.warn("soundSelect missing"); }
      if (soundFile) soundFile.addEventListener('change', handleSoundUpload); else console.warn("soundFile missing");
      if (testSoundButton) {
        testSoundButton.addEventListener('click', () => {
            console.log("Test Tick Button Clicked.");
            playSoundWithCheck(currentAudio, tickVolume); // Use helper
        });
    } else { console.warn("testSoundButton missing"); }
      if (alarmSelect) { alarmSelect.addEventListener('change', handleAlarmSoundSelection); handleAlarmSoundSelection(); } else console.warn("alarmSelect missing");
      if (alarmFile) alarmFile.addEventListener('change', handleAlarmUpload); else console.warn("alarmFile missing");
      if (testAlarmButton) {
        testAlarmButton.addEventListener('click', () => {
            console.log("Test Alarm Button Clicked.");
            playSoundWithCheck(currentAlarmAudio, alarmVolume); // Use helper
        });
    } else { console.warn("testAlarmButton missing"); }
      // Tick Volume Listener
      if (tickVolumeSlider && tickVolumeValue) {
          tickVolumeSlider.addEventListener('input', (e) => {
              tickVolume = parseFloat(e.target.value);
              tickVolumeValue.textContent = Math.round(tickVolume * 100) + '%';
              // Update volume on CURRENTLY selected/loaded audio
              if (currentAudio) currentAudio.volume = tickVolume;
              // Update volume on preloaded sounds too (so they have correct volume when selected later)
              Object.values(sounds).forEach(s => s.volume = tickVolume);
              console.log("Tick Volume set to:", tickVolume);
          });
          // Set initial display
          tickVolumeSlider.value = tickVolume;
          tickVolumeValue.textContent = Math.round(tickVolume * 100) + '%';
      } else { console.warn("tickVolumeSlider/Value missing"); }

      // Alarm Volume Listener
      if (alarmVolumeSlider && alarmVolumeValue) {
          alarmVolumeSlider.addEventListener('input', (e) => {
              alarmVolume = parseFloat(e.target.value);
              alarmVolumeValue.textContent = Math.round(alarmVolume * 100) + '%';
              // Update volume on CURRENTLY selected/loaded alarm
              if (currentAlarmAudio) currentAlarmAudio.volume = alarmVolume;
              // Update volume on preloaded alarms
              Object.values(alarmSounds).forEach(s => s.volume = alarmVolume);
              console.log("Alarm Volume set to:", alarmVolume);
          });
          // Set initial display
          alarmVolumeSlider.value = alarmVolume;
          alarmVolumeValue.textContent = Math.round(alarmVolume * 100) + '%';
      } else { console.warn("alarmVolumeSlider/Value missing"); }
      
      // Date Toggle Listener
      if (dateDisplayToggle && dateDisplay) { // Check BOTH elements exist
          dateDisplayToggle.addEventListener('change', (e) => toggleDateDisplay(e.target.checked));
          console.log("Date display toggle listener attached.");
          // Initial state is set during DOMContentLoaded now, no need to set checked here
      } else {
          console.warn("dateDisplayToggle or dateDisplay missing, cannot attach listener.");
      }
      // Move and End listeners on the document capture events better if mouse leaves the original element

      if (timezoneOffsetInput) {
        // Set initial value from state if loaded from storage (optional)
         timezoneOffsetInput.value = timezoneOffsetHours;
         // Add listener
         timezoneOffsetInput.addEventListener('change', (e) => {
             const newOffset = parseFloat(e.target.value);
             if (!isNaN(newOffset)) {
                 timezoneOffsetHours = newOffset;
                 console.log("Timezone offset changed to:", timezoneOffsetHours);
                 // If in clock mode, update the display immediately
                 if (currentMode === 'clock') {
                     updateClockDisplay(); // Force update
                 }
             } else {
                 e.target.value = timezoneOffsetHours; // Revert invalid input visually
             }
         });
         console.log("Timezone offset listener attached."); // Add log
    } else {
         console.warn("timezoneOffsetInput missing, cannot attach listener.");
    }
    if (applyGmtButton && timezoneOffsetInput) {
        timezoneOffsetInput.value = timezoneOffsetHours; // Set initial value
        applyGmtButton.addEventListener('click', () => {
            console.log("Apply GMT Button Clicked"); // Add log
            const newOffset = parseFloat(timezoneOffsetInput.value);
            if (!isNaN(newOffset)) {
                if (newOffset !== timezoneOffsetHours) {
                    timezoneOffsetHours = newOffset; // Update the global variable
                    console.log("Global timezoneOffsetHours updated to:", timezoneOffsetHours);
                    if (currentMode === 'clock') {
                        console.log("Mode is clock - Calling startClock() to apply new offset...");
                        startClock(); // <<< This restart is key
                    } else {
                         console.log(`Mode is ${currentMode} - Offset variable updated, but clock not restarted.`);
                         // Optionally force a single update for timer/stopwatch if needed? Usually not.
                    }
                } else {
                    console.log("Timezone offset value unchanged.");
                }
            } else {
                alert("Invalid timezone offset value.");
                timezoneOffsetInput.value = timezoneOffsetHours;
            }
        });
        console.log("Apply GMT Button listener attached.");
    } else {
        console.warn("Cannot attach Apply GMT listener: applyGmtButton or timezoneOffsetInput missing.");
    }

      // Window resize listener
      window.addEventListener('resize', debounce(() => {
          applyDigitStylesForAllChunks(); // Realign masks on resize
      }, 100));
      console.log("Resize listener attached."); // Debug

  } catch (error) {
      console.error("Error during event listener setup:", error);
      // Depending on the error, you might want to alert the user or stop further script execution
      // alert("A critical error occurred while setting up interactions. Please refresh the page.");
  }

  console.log("Event listeners setup function finished."); // Debug end
}

/********************************************
* INITIALIZATION
********************************************/
window.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded and parsed"); // Debug Log 1

  // --- Assign DOM Elements ---
  let criticalElementMissing = false;
  try {
      // Assign all variables declared globally
      backgroundLayer = document.getElementById("background-layer");
      clockContainer = document.getElementById("clock-container");
      hoursEl = document.getElementById("hours");
      sep1El = document.getElementById("sep1");
      minutesEl = document.getElementById("minutes");
      sep2El = document.getElementById("sep2");
      secondsEl = document.getElementById("seconds");
      allChunks = [hoursEl, minutesEl, secondsEl, sep1El, sep2El].filter(el => el != null);
      bodyElement = document.body;
      toggleLayoutButton = document.getElementById("toggle-layout-button");
      settingsButton = document.getElementById("settings-button");
      topStartButton = document.getElementById("topStart");
      topPauseButton = document.getElementById("topPause");
      topStopButton = document.getElementById("topStop");
      settingsPanel = document.getElementById("settings-panel");
      tabButtons = document.querySelectorAll(".settings-tabs .tab-button:not(.nested)");
      tabContents = document.querySelectorAll(".tab-content:not(.nested)");
      digitTabButtons = document.querySelectorAll(".nested-tabs .tab-button.nested");
      digitTabContents = document.querySelectorAll(".tab-content.nested");
      modeSelect = document.getElementById("mode-select");
      timerSettings = document.getElementById("timer-settings");
      timerInput = document.getElementById("timer-input");
      tickSpeedInput = document.getElementById("tick-speed");
      clockSizeInput = document.getElementById("clock-size");
      setButton = document.getElementById("set-button");
      startButton = document.getElementById("start-button");
      pauseButton = document.getElementById("pause-button");
      resetButton = document.getElementById("reset-button");
      bgSolidColorInput = document.getElementById("bg-solid-color");
      bgGradientDegree = document.getElementById("bg-gradient-degree");
      bgGradientStart = document.getElementById("bg-gradient-start");
      bgGradientEnd = document.getElementById("bg-gradient-end");
      bgImageUrlInput = document.getElementById("bg-image-url");
      bgImageFileInput = document.getElementById("bg-image-file");
      bgImagePreview = document.getElementById("bg-image-preview");
      fontSelect = document.getElementById("font-select");
      fontFileInput = document.getElementById("font-file");
      applyBaseFontBtn = document.getElementById("apply-base-font-btn");
      applyCustomFontBtn = document.getElementById("apply-custom-font-btn");
      bgOpacityInput = document.getElementById("bg-opacity");
      bgOpacityValue = document.getElementById("bg-opacity-value");
      bgBlurInput = document.getElementById("bg-blur");
      bgBlurValue = document.getElementById("bg-blur-value");
      applyBgStyleBtn = document.getElementById("apply-bg-style-btn");
      digitsOpacityInput = document.getElementById("digits-opacity");
      digitsOpacityValue = document.getElementById("digits-opacity-value");
      digitsBlurInput = document.getElementById("digits-blur");
      digitsBlurValue = document.getElementById("digits-blur-value");
      applyDigitsStyleBtn = document.getElementById("apply-digits-style-btn");
      glowToggle = document.getElementById("glow-toggle");
      dateDisplay = document.getElementById("date-display");
      dateDisplayToggle = document.getElementById("date-display-toggle");
      shortcutSettingsList = document.getElementById("shortcut-settings-list");
      saveShortcutsButton = document.getElementById("save-shortcuts-button");
      resetShortcutsButton = document.getElementById("reset-shortcuts-button");
      soundToggle = document.getElementById("sound-toggle");
      timezoneOffsetInput = document.getElementById("timezone-offset");
      tickVolumeSlider = document.getElementById("tick-volume-slider");
      tickVolumeValue = document.getElementById("tick-volume-value");
      alarmVolumeSlider = document.getElementById("alarm-volume-slider");
      alarmVolumeValue = document.getElementById("alarm-volume-value");
      soundSelect = document.getElementById("sound-select");
      soundFile = document.getElementById("sound-file");
      testSoundButton = document.getElementById("test-sound-button");
      alarmSelect = document.getElementById("alarm-select");
      alarmFile = document.getElementById("alarm-file");
      testAlarmButton = document.getElementById("test-alarm-button");
      glowColorInput = document.getElementById("glow-color");
      applyGmtButton = document.getElementById("apply-gmt-button");



      // --- Perform critical checks AFTER assignment attempt ---
      if (!settingsPanel) { console.error("CRITICAL INIT: settingsPanel assignment failed!"); criticalElementMissing = true; }
      if (!bodyElement) { console.error("CRITICAL INIT: bodyElement assignment failed!"); criticalElementMissing = true; } // Should always exist
      if (!modeSelect) { console.error("CRITICAL INIT: modeSelect assignment failed!"); criticalElementMissing = true; }
      if (!hoursEl || !minutesEl || !secondsEl) { console.error("CRITICAL INIT: Clock digit elements assignment failed!"); criticalElementMissing = true;}
      if (!settingsButton) { console.error("CRITICAL INIT: settingsButton assignment failed!"); criticalElementMissing = true;} // Check settings button needed for setup
      if (!dateDisplay) { console.warn("INIT WARNING: dateDisplay element not found!"); }
      if (!dateDisplayToggle) { console.warn("INIT WARNING: dateDisplayToggle element not found!"); }
      if (!timezoneOffsetInput) { console.error("CRITICAL INIT: timezoneOffsetInput assignment failed!"); criticalElementMissing = true; }
      if (!soundToggle) { console.warn("INIT WARNING: soundToggle missing!"); }
      if (!soundSelect) { console.warn("INIT WARNING: soundSelect missing!"); }
      if (!soundFile) { console.warn("INIT WARNING: soundFile missing!"); }
      if (!testSoundButton) { console.warn("INIT WARNING: testSoundButton missing!"); }
      if (!tickVolumeSlider) { console.warn("INIT WARNING: tickVolumeSlider missing!"); }
      if (!tickVolumeValue) { console.warn("INIT WARNING: tickVolumeValue missing!"); }
      if (!alarmSelect) { console.warn("INIT WARNING: alarmSelect missing!"); }
      if (!alarmFile) { console.warn("INIT WARNING: alarmFile missing!"); }
      if (!testAlarmButton) { console.warn("INIT WARNING: testAlarmButton missing!"); }
      if (!alarmVolumeSlider) { console.warn("INIT WARNING: alarmVolumeSlider missing!"); }
      if (!alarmVolumeValue) { console.warn("INIT WARNING: alarmVolumeValue missing!"); }
      if (!glowToggle) { console.warn("INIT WARNING: glowToggle missing!"); }
      if (!glowColorInput) { console.warn("INIT WARNING: glowColorInput missing!"); }
      if(glowToggle && clockContainer) glowToggle.checked = clockContainer.classList.contains('glow-enabled'); // Sync checkbox to initial state
      if(glowColorInput && clockContainer) glowColorInput.value = clockContainer.style.getPropertyValue('--glow-color').trim() || '#FFFFFF'; // Sync color picker
      if (!applyGmtButton) { console.warn("INIT WARNING: applyGmtButton missing!"); }


      console.log("Initial UI state set.");
      // Add more checks as needed (e.g., clockContainer)

      console.log("DOM Elements assigned/checked within DOMContentLoaded.");

  } catch(error) {
       console.error("Error during DOM Element assignment:", error);
       criticalElementMissing = true;
  }

  // Stop initialization if critical elements are missing
  if (criticalElementMissing) {
       alert("Error initializing: Critical elements missing/failed assignment. See console (F12).");
       return;
  }

  // --- Initial UI State Setup ---
  settingsPanel.classList.remove('open');
  bodyElement.classList.remove('settings-panel-open');
  isPanelOpen = false;
  showTab('mode-tab', false);
  showTab('digits-global-tab', true);
  console.log("Initial UI state set.");

  // --- Apply Default Visual Styles ---
  try {
      applyFont(currentFontName);
      applyBackgroundSettings('solid');
      applyDigitStyleForChunk('global', 'solid', '#FFFFFF');
      applyBackgroundStyle();
      applyDigitsStyle();
      const initialSize = clockSizeInput?.value || '15';
      allChunks.forEach(ch => { if (ch) ch.style.fontSize = initialSize + "vw"; });
      console.log("Default visual styles applied.");
  } catch (error) { console.error("Error applying default styles:", error); }

  if (dateDisplay) { // Only run if element exists
    updateDateDisplay(); // <<< CALL to set initial date
    setInterval(updateDateDisplay, 60 * 1000); // Update every minute
    console.log("Initial date display updated and interval set.");
    } else {
    console.log("Skipping initial date update and interval (element not found).");
    }

  // --- Set Initial Mode & Start Clock ---
  try {
      modeSelect.value = "clock";
      currentMode = "clock";
      updateUIForMode("clock"); // Calls startClock
      console.log("Initial mode set and updateUIForMode called.");
  } catch (error) { console.error("Error setting initial mode or starting clock:", error); }

  // --- Attach All Event Listeners ---
  if (typeof setupEventListeners === 'function') {
      setupEventListeners();
      console.log("setupEventListeners function called.");
  } else { console.error("CRITICAL: setupEventListeners function is not defined!"); }

  // Load and apply date visibility state
  //showDate = localStorage.getItem('showDateDisplay') === 'true'; // Optional: Load saved state
  toggleDateDisplay(showDate); // Apply initial state (default is off 'false')
  if (dateDisplayToggle) { // Check if toggle exists before setting its state
      dateDisplayToggle.checked = showDate; // Sync checkbox to match state
  }

  if(tickVolumeSlider && tickVolumeValue) {
      tickVolumeSlider.value = tickVolume;
      tickVolumeValue.textContent = Math.round(tickVolume * 100) + '%';
  }
  if(alarmVolumeSlider && alarmVolumeValue) {
      alarmVolumeSlider.value = alarmVolume;
      alarmVolumeValue.textContent = Math.round(alarmVolume * 100) + '%';
  }

  console.log("Initialization complete.");
}); // End of DOMContentLoaded Listener

/********************************************
* CLEANUP
********************************************/
window.addEventListener('beforeunload', () => {
  console.log("Cleaning up Object URLs before unload...");
  let revokedCount = 0;
  Object.keys(lastObjectURLs).forEach(key => {
      const url = lastObjectURLs[key];
      if (url) {
          try {
              URL.revokeObjectURL(url);
              lastObjectURLs[key] = null;
              revokedCount++;
          } catch (error) {
              console.error(`Error revoking Object URL for key ${key}:`, error);
          }
      }
  });
  console.log(`Revoked ${revokedCount} Object URLs.`);
});