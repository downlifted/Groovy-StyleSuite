// Import constants
const { project_dir, virtual_env } = require('./constants');

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
            "git clone https://github.com/comfyanonymous/ComfyUI.git",
          ],
        },
      },
      {
        method: "shell.run",
        params: {
          path: project_dir,
          venv: virtual_env,
          message: getInstallCommand(kernel) // Make sure this function is defined
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

  // Installing project requirements
  const project_requirements = [
    `pip install -r ${path.resolve(__dirname, project_dir, 'requirements.txt')}`,
    `pip install -r ${path.resolve(__dirname, project_dir, 'comfy_runner', 'requirements.txt')}`,
    `pip install -r ${path.resolve(__dirname, project_dir, 'ComfyUI', 'requirements.txt')}`,
  ];

  // Execute each installation command
  for (const command of project_requirements) {
    await kernel.runCommand(command, { venv: virtual_env });
  }

  return config;
};
