const { virtual_env, project_dir } = require("./constants");
const path = require('path');

// Install dependencies based on platform
function getInstallCommand(kernel) {
  const { platform, gpu } = kernel;

  function combineLists(list1, list2) {
    return [...list1, ...list2];
  }

  const project_requirements = [
    `pip install -r ${path.resolve(__dirname, project_dir, 'requirements.txt')}`,
    `pip install -r ${path.resolve(__dirname, project_dir, 'comfy_runner', 'requirements.txt')}`,
    `pip install -r ${path.resolve(__dirname, project_dir, 'ComfyUI', 'requirements.txt')}`,
  ];

  if (platform === "linux") {
    const cmd_list = []; // Defaults for Linux
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

  // Handle macOS
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
            `git clone --depth 1 -b main https://github.com/banodoco/Dough.git ${project_dir}`,
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          message: [
            // Clone the required repositories
            "git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner",
            "git clone https://github.com/comfyanonymous/ComfyUI.git",
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          venv: virtual_env,
          message: getInstallCommand(kernel), // Install dependencies
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          message: [
            // Create the environment file
            `cp ${project_dir}/.env.sample ${project_dir}/.env`,
          ],
        },
      },
    ],
  };

  return config;
};
