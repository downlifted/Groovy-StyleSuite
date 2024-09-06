const { virtual_env, project_dir } = require("./constants");
const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs-extra');

// Function to get installation command based on platform
function getInstallCommand(kernel) {
  const { platform } = kernel;

  function combineLists(list1, list2) {
    return [...list1, ...list2];
  }

  const project_requirements = [
    `pip install -r ${path.resolve(__dirname, project_dir, 'comfy_runner', 'requirements.txt')}`,
  ];

  if (platform === "linux") {
    const cmd_list = [];
    return combineLists(cmd_list, project_requirements);
  }

  if (platform === "win32") {
    const cmd_list = [
      "python.exe -m pip install --upgrade pip",
      "pip install websocket",
      "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    ];
    return combineLists(cmd_list, project_requirements);
  }

  return [
    `pip install -r ${path.resolve(__dirname, project_dir, 'requirements.txt')}`,
  ];
}

// Function to clone repositories into a temporary folder
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

// Function to copy contents from the temporary clone folder to Groovy folder
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
          // Clone repositories to temporary folders
          message: [
            `git clone --depth 1 -b main https://github.com/downlifted/Groovy-StyleSuite.git ${path.resolve(project_dir, 'temp_groovy_clone')}`,
            `git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner.git ${path.resolve(project_dir, 'temp_comfyrunner_clone')}`,
            `git clone https://github.com/comfyanonymous/ComfyUI.git ${path.resolve(project_dir, 'temp_comfyui_clone')}`
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          // Copy contents from temporary folders to Groovy folder
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
