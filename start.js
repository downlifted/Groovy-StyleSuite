const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const { virtual_env, project_dir } = require("./constants");

// Helper function to check if a directory exists
function directoryExists(directory) {
  return fs.existsSync(directory);
}

// Helper function to move directory contents
function moveContents(sourceDir, targetDir) {
  const files = fs.readdirSync(sourceDir);
  files.forEach(file => {
    const srcPath = path.join(sourceDir, file);
    const destPath = path.join(targetDir, file);
    fs.renameSync(srcPath, destPath);
  });
}

// Main function to clone and move repos
module.exports = () => {
  const comfyRunnerDir = path.resolve(__dirname, project_dir, 'comfy_runner');
  const comfyUIDir = path.resolve(__dirname, project_dir, 'ComfyUI');

  // Create a temp directory for cloning
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'clone-'));

  // Check if comfy_runner exists, if not clone it and move it
  if (!directoryExists(comfyRunnerDir)) {
    console.log('Cloning comfy_runner repository...');
    execSync(`git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner ${tempDir}/comfy_runner`);
    moveContents(`${tempDir}/comfy_runner`, comfyRunnerDir);
  } else {
    console.log('comfy_runner already exists. Skipping cloning.');
  }

  // Check if ComfyUI exists, if not clone it and move it
  if (!directoryExists(comfyUIDir)) {
    console.log('Cloning ComfyUI repository...');
    execSync(`git clone https://github.com/comfyanonymous/ComfyUI.git ${tempDir}/ComfyUI`);
    moveContents(`${tempDir}/ComfyUI`, comfyUIDir);
  } else {
    console.log('ComfyUI already exists. Skipping cloning.');
  }

  // Clean up the temp directory
  fs.rmdirSync(tempDir, { recursive: true });

  const config = {
    daemon: true,
    run: [
      {
        method: "shell.run",
        params: {
          venv: path.resolve(__dirname, project_dir, virtual_env),
          message: "python app.py",
          on: [{ event: "/http:\/\/[0-9.:]+/", done: true }],
        },
      },
    ],
  };

  return config;
};
