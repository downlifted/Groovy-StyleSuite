const { virtual_env, project_dir } = require("./constants");
const path = require('path');

function getInstallCommand(kernel) {
  const { platform } = kernel; // Removed 'gpu' since it's unused

  function combineLists(list1, list2) {
    return [...list1, ...list2];
  }

  let project_requirements = [
    `pip install -r ${path.resolve('requirements.txt')}`,
    `pip install -r ${path.resolve('comfy_runner', 'requirements.txt')}`,
    `pip install -r ${path.resolve('ComfyUI', 'requirements.txt')}`,
  ];

  if (platform === "linux") {
    let cmd_list = []; // Assuming py3.10 is set by default in Pinokio
    return combineLists(cmd_list, project_requirements);
  }

  if (platform === "win32") {
    let cmd_list = [
      "python.exe -m pip install --upgrade pip",
      "pip install websocket",
      "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    ];
    return combineLists(cmd_list, project_requirements);
  }

  // For macOS
  return [
    `pip install -r requirements.txt`,
  ];
}

module.exports = async (kernel) => {
  const config = {
    run: [
      {
        method: "shell.run",
        params: {
          message: [
            `git clone https://github.com/downlifted/Groovy-StyleSuite app`,
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
          message: getInstallCommand(kernel),
        },
      },
      {
        method: "fs.copy",
        params: {
          src: `${project_dir}/.env.sample`,
          dest: `${project_dir}/.env`,
        },
      },
      {
        method: "fs.link",
        params: {
          drive: {
            "checkpoints": `${project_dir}/ComfyUI/models/checkpoints`,
            "clip": `${project_dir}/ComfyUI/models/clip`,
            "clip_vision": `${project_dir}/ComfyUI/models/clip_vision`,
            "configs": `${project_dir}/ComfyUI/models/configs`,
            "controlnet": `${project_dir}/ComfyUI/models/controlnet`,
            "embeddings": `${project_dir}/ComfyUI/models/embeddings`,
            "loras": `${project_dir}/ComfyUI/models/loras`,
            "upscale_models": `${project_dir}/ComfyUI/models/upscale_models`,
            "vae": `${project_dir}/ComfyUI/models/vae`,
          },
          peers: [
            "https://github.com/cocktailpeanutlabs/automatic1111.git",
            "https://github.com/cocktailpeanutlabs/fooocus.git",
            "https://github.com/cocktailpeanutlabs/forge.git",
          ],
        },
      },
    ],
  };
  return config;
};
