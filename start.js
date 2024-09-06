const path = require('path');

const { virtual_env, project_dir } = require("./constants");

module.exports = () => {
  const config = {
    daemon: true,
    run: [
      {
        method: "shell.run",
        params: {
          path: project_dir,
          venv: path.resolve(__dirname, project_dir, virtual_env),
          message: [
            "pip install torch", // Install PyTorch if not already installed
            "python ./ComfyUI/main.py", // Launch ComfyUI instead of app.py
          ],
          on: [{ event: "/http:\/\/[0-9.:]+/", done: true }],
        },
      },
      {
        method: "local.set",
        params: {
          url: "{{input.event[0]}}"
        }
      },
    ],
  };
  return config;
};
