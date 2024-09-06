const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs-extra');  // fs-extra allows copying with merge
const { project_dir } = require('./constants');

// Clone repository to a temporary location
function cloneRepoTemp(repoUrl, tempFolder) {
    const tempClonePath = path.resolve(project_dir, tempFolder);
    
    if (!fs.existsSync(tempClonePath)) {
        try {
            console.log(`Cloning ${repoUrl} to temp location...`);
            execSync(`git clone ${repoUrl} ${tempClonePath}`, { stdio: 'inherit' });
            console.log(`Repository ${repoUrl} cloned successfully to ${tempClonePath}.`);
        } catch (error) {
            console.error(`Failed to clone ${repoUrl}:`, error.message || error);
        }
    } else {
        console.log(`Temporary folder ${tempClonePath} already exists. Skipping clone.`);
    }
}

// Copy contents of the cloned repo to the existing Groovy folder
function copyToGroovyFolder(tempFolder) {
    const tempClonePath = path.resolve(project_dir, tempFolder);
    const groovyFolderPath = path.resolve(project_dir, 'Groovy');
    
    try {
        console.log(`Copying contents from ${tempClonePath} to ${groovyFolderPath}...`);
        fs.copySync(tempClonePath, groovyFolderPath, { overwrite: true });
        console.log(`Contents copied to ${groovyFolderPath} successfully.`);
    } catch (error) {
        console.error("Failed to copy to Groovy folder:", error.message || error);
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

        // Clone ComfyUI and Comfy_Runner to temporary locations
        cloneRepoTemp('https://github.com/comfyanonymous/ComfyUI.git', 'temp_comfyui_clone');
        cloneRepoTemp('https://github.com/piyushK52/comfy_runner.git', 'temp_comfyrunner_clone');

        // Copy both repositories' contents into the Groovy folder
        copyToGroovyFolder('temp_comfyui_clone');
        copyToGroovyFolder('temp_comfyrunner_clone');

        // Start ComfyUI and then app.py
        startComfyUI();
        console.log("ComfyUI started successfully.");
        startApp();
        console.log("app.py started successfully.");
    } catch (error) {
        console.error("An error occurred during initialization:", error.message || error);
    }
};
