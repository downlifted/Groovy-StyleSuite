const path = require('path');
const { execSync } = require('child_process');
const { project_dir } = require('./constants');

// Ensure ComfyUI is ready before starting the app
function startComfyUI() {
    try {
        console.log("Starting ComfyUI...");
        execSync(`python ${path.resolve(project_dir, 'ComfyUI', 'main.py')}`, { stdio: 'inherit' });
    } catch (error) {
        console.error("Failed to start ComfyUI:", error.message || error);
    }
}

// Run app.py after ComfyUI is started
function startApp() {
    try {
        console.log("Running app.py...");
        execSync(`python ${path.resolve(project_dir, 'app.py')}`, { stdio: 'inherit' });
    } catch (error) {
        console.error("Failed to run app.py:", error.message || error);
    }
}

// Main function to start everything in sequence
module.exports = async () => {
    try {
        console.log("Initializing setup...");
        startComfyUI();
        console.log("ComfyUI started successfully.");
        startApp();
        console.log("app.py started successfully.");
    } catch (error) {
        console.error("An error occurred during initialization:", error.message || error);
    }
};
