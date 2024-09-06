const path = require('path');
const { virtual_env, project_dir } = require("./constants");

module.exports = () => {
  const config = {
    daemon: true,
    run: [
      {
        // First, start ComfyUI
        method: "shell.run",
        params: {
          path: project_dir,
          venv: path.resolve(__dirname, project_dir, virtual_env),
          message: [
            "pip install torch", // Ensure torch is installed
            "python ./ComfyUI/main.py", // Start ComfyUI
          ],
          on: [{ event: "/http:\/\/[0-9.:]+/", done: true }], // Wait for ComfyUI to start
        },
      },
      {
        // Then, run app.py once ComfyUI has started
        method: "shell.run",
        params: {
          path: project_dir,
          venv: path.resolve(__dirname, project_dir, virtual_env),
          message: "python app.py", // Run app.py after ComfyUI
          on: [{ event: "/http:\/\/[0-9.:]+/", done: true }], // Ensure this runs after ComfyUI
        },
      },
      {
        // Capture the local URL if needed
        method: "local.set",
        params: {
          url: "{{input.event[0]}}"
        }
      },
    ],
  };
  return config;
};
