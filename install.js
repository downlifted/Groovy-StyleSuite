const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs-extra');  // fs-extra allows copying with merge
const { project_dir } = require('./constants');

// Check if the folder already exists and is not empty
function isFolderNonEmpty(folderPath) {
    try {
        const files = fs.readdirSync(folderPath);
        return files.length > 0;
    } catch (error) {
        return false;  // If folder doesn't exist or an error occurs, assume it's empty
    }
}

// Clone repository into a temporary folder if needed
function cloneRepoTemp(repoUrl, tempFolder) {
    const tempClonePath = path.resolve(project_dir, tempFolder);

    // Check if the destination already exists and is not empty
    if (!isFolderNonEmpty(tempClonePath)) {
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

// Copy contents from the temp folder to the Groovy folder
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

// Main execution function
module.exports = async (kernel) => {
    const config = {
        run: [
            {
                method: "shell.run",
                params: {
                    message: [
                        `Cloning repositories...`,
                    ],
                },
            },
            {
                method: "shell.run",
                params: {
                    // Only clone to temporary folders if the Groovy folder isn't non-empty
                    message: [
                        `Checking if Groovy folder exists...`,
                        `if [ ! "$(ls -A ${path.resolve(project_dir, 'Groovy')})" ]; then git clone --depth 1 -b main https://github.com/downlifted/Groovy-StyleSuite.git ${path.resolve(project_dir, 'temp_groovy_clone')}; fi`,
                        `git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner.git ${path.resolve(project_dir, 'temp_comfyrunner_clone')}`,
                        `git clone https://github.com/comfyanonymous/ComfyUI.git ${path.resolve(project_dir, 'temp_comfyui_clone')}`
                    ],
                },
            },
            {
                method: "shell.run",
                params: {
                    // Copy contents from temporary folders to Groovy
                    message: [
                        `Copying repositories to Groovy...`,
                        `fs.copySync('${path.resolve(project_dir, 'temp_groovy_clone')}', '${path.resolve(project_dir, 'Groovy')}', { overwrite: false, errorOnExist: false })`,
                        `fs.copySync('${path.resolve(project_dir, 'temp_comfyrunner_clone')}', '${path.resolve(project_dir, 'Groovy')}', { overwrite: false, errorOnExist: false })`,
                        `fs.copySync('${path.resolve(project_dir, 'temp_comfyui_clone')}', '${path.resolve(project_dir, 'Groovy')}', { overwrite: false, errorOnExist: false })`
                    ],
                },
            },
            {
                method: "shell.run",
                params: {
                    // Install dependencies
                    path: project_dir,
                    venv: virtual_env,
                    message: getInstallCommand(kernel),
                },
            },
            {
                method: "fs.copy",
                params: {
                    // Copy .env.sample to .env
                    src: `${project_dir}/.env.sample`,
                    dest: `${project_dir}/.env`,
                },
            },
        ],
    };

    return config;
};
