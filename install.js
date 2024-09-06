const { virtual_env, project_dir } = require("./constants");
const path = require('path');
const { execSync } = require('child_process');

function getInstallCommand(kernel) {
  const { platform, gpu } = kernel;

  function combineLists(list1, list2) {
    return [...list1, ...list2];
  }

  project_requirements = [
    `pip install -r ${path.resolve(__dirname, project_dir, 'comfy_runner', 'requirements.txt')}`,
  ];

  if (platform === "linux") {
    cmd_list = [];
    return combineLists(cmd_list, project_requirements);
  }

  if (platform === "win32") {
    cmd_list = [
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

module.exports = async (kernel) => {
  const config = {
    run: [
      {
        method: "shell.run",
        params: {
          message: [
            `git clone --depth 1 -b main https://github.com/downlifted/Groovy-StyleSuite.git ${project_dir}`,
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          message: [
            "git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner",
            "git clone https://github.com/comfyanonymous/ComfyUI.git",  // Ensuring ComfyUI is downloaded
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          venv: virtual_env,
          message: getInstallCommand(kernel), // Ensuring dependencies are installed
        },
      },
      {
        method: "fs.copy",
        params: {
          src: `${project_dir}/.env.sample`,
          dest: `${project_dir}/.env`,
        },
      },
    ],
  };
  return config;
