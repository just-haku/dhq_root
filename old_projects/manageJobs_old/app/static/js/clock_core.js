const ClockApp = {
    modules: [],
    
    register: function(moduleId, initFunction) {
        // Store the module to init later
        this.modules.push({ id: moduleId, init: initFunction });
    },

    start: function() {
        this.modules.forEach(mod => {
            // Find the div reserved for this module in HTML
            const container = document.getElementById(mod.id);
            if(container) {
                console.log("Starting Module:", mod.id);
                mod.init(container);
            } else {
                console.warn("Module container not found:", mod.id);
            }
        });
    }
};

// Auto-start when page loads
window.addEventListener('load', () => ClockApp.start());