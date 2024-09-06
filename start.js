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
          message: "python app.py",
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
