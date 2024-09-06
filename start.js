const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');
const { project_dir } = require('./constants');

// Clone the Groovy repository if it doesn't already exist
function cloneGroovyRepo() {
    const groovyFolderPath = path.resolve(project_dir, 'Groovy');
    
    if (!fs.existsSync(groovyFolderPath)) {
        try {
            console.log("Cloning Groovy repository...");
            execSync(`git clone https://github.com/downlifted/Groovy-StyleSuite.git ${groovyFolderPath}`, { stdio: 'inherit' });
            console.log("Groovy repository cloned successfully.");
        } catch (error) {
            console.error("Failed to clone Groovy repository:", error.message || error);
        }
    } else {
        console.log("Groovy repository already exists. Skipping clone.");
    }
}

// Move Groovy folder if needed
function moveGroovyFolder(destinationDir) {
    const groovyFolderPath = path.resolve(project_dir, 'Groovy');
    const destinationPath = path.resolve(project_dir, destinationDir);

    try {
        if (!fs.existsSync(destinationPath)) {
            console.log(`Moving Groovy folder to ${destinationPath}...`);
            fs.renameSync(groovyFolderPath, destinationPath);
            console.log("Groovy folder moved successfully.");
        } else {
            console.log("Destination folder already exists. Skipping move.");
        }
    } catch (error) {
        console.error("Failed to move Groovy folder:", error.message || error);
    }
}

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

// Main function to handle the entire process
module.exports = async () => {
    try {
        console.log("Initializing setup...");

        // Clone the Groovy repo and move it to the correct location if necessary
        cloneGroovyRepo();
        moveGroovyFolder('correct_destination_directory');  // Specify your destination directory here

        // Start ComfyUI and then app.py
        startComfyUI();
        console.log("ComfyUI started successfully.");
        startApp();
        console.log("app.py started successfully.");
    } catch (error) {
        console.error("An error occurred during initialization:", error.message || error);
    }
};
