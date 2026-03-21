ClockApp.register('module-time', function(element) {
    // 1. Create Content
    element.innerHTML = `<h1 id="main-time">Loading...</h1>`;
    const timeNode = document.getElementById('main-time');

    // 2. Update Logic
    function update() {
        const now = new Date();
        // Format: HH:MM:SS
        const timeString = now.toLocaleTimeString('en-GB', {hour12: false});
        timeNode.innerText = timeString;
    }
    
    // 3. Start Loop
    setInterval(update, 1000);
    update();
});