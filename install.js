const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs-extra');  // fs-extra allows copying with merge
const { project_dir } = require('./constants');

// Function to check if the folder already has files (meaning it's cloned)
function isRepoCloned(folderPath) {
    try {
        const files = fs.readdirSync(folderPath);
        return files.length > 0;
    } catch (error) {
        return false; // If folder doesn't exist or an error occurs, assume it's not cloned
    }
}

// Clone repository to a separate temporary folder
function cloneRepoTemp(repoUrl, tempFolder) {
    const tempClonePath = path.resolve(project_dir, tempFolder);
    
    if (!isRepoCloned(tempClonePath)) {
        try {
            console.log(`Cloning ${repoUrl} to temp location...`);
            execSync(`git clone ${repoUrl} ${tempClonePath}`, { stdio: 'inherit' });
            console.log(`Repository ${repoUrl} cloned successfully to ${tempClonePath}.`);
        } catch (error) {
            console.error(`Failed to clone ${repoUrl}:`, error.message || error);
        }
    } else {
        console.log(`Temporary folder ${tempClonePath} already contains files. Skipping clone.`);
    }
}

// Copy contents of the cloned repo to the existing Groovy folder
function copyToGroovyFolder(tempFolder) {
    const tempClonePath = path.resolve(project_dir, tempFolder);
    const groovyFolderPath = path.resolve(project_dir, 'Groovy');
    
    try {
        console.log(`Copying contents from ${tempClonePath} to ${groovyFolderPath}...`);
        fs.copySync(tempClonePath, groovyFolderPath, { overwrite: false, errorOnExist: false });
        console.log(`Contents copied to ${groovyFolderPath} successfully.`);
    } catch (error) {
        console.error("Failed to copy to Groovy folder:", error.message || error);
    }
}

// Ensure ComfyUI is ready before starting the app
function startComfyUI() {
    try {
        console.log("Starting ComfyUI
