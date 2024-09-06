const fs = require('fs');
const path = require('path');

module.exports = {
  run: [
    // Clone the main repository
    {
      method: "shell.run",
      params: {
        message: [
          "git clone https://github.com/downlifted/Groovy-StyleSuite app",
        ]
      }
    },
    // Step for torch, if your project uses torch
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",                // Customize the venv folder path if needed
          path: "app",                // Customize the path to start the shell from
          // xformers: true   // Uncomment if your project requires xformers
        }
      }
    },
    // Ensure directories comfy_runner and ComfyUI exist
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",  // Make sure this is the base app directory
        message: [
          // Ensure comfy_runner and ComfyUI directories are created
          `mkdir -p ${path.resolve('app', 'comfy_runner')}`,
          `mkdir -p ${path.resolve('app', 'ComfyUI')}`
        ]
      }
    },
    // Install requirements for the main project and subdirectories
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "pip install gradio devicetorch", // Install initial dependencies
          `pip install -r ${path.resolve('app', 'requirements.txt')}`, // Install main project requirements
          `pip install -r ${path.resolve('app', 'comfy_runner', 'requirements.txt')}`, // Install comfy_runner requirements
          `pip install -r ${path.resolve('app', 'ComfyUI', 'requirements.txt')}`, // Install ComfyUI requirements
        ]
      }
    },
    // Optional: Linking virtual environment or other resources
    {
      method: "fs.link",
      params: {
        venv: "app/env"
      }
    }
  ]
};
