const { virtual_env, project_dir } = require("./constants");
const path = require('path');
const fs = require('fs');

// Ensure necessary directories exist
function ensureDirectories() {
    const modelDirectories = [
        'checkpoints',
        'clip',
        'clip_vision',
        'configs',
        'controlnet',
        'embeddings',
        'loras',
        'upscale_models',
        'vae'
    ];

    const basePath = path.join(project_dir, 'ComfyUI', 'models');
    modelDirectories.forEach(dir => {
        const fullPath = path.join(basePath, dir);
        if (!fs.existsSync(fullPath)) {
            fs.mkdirSync(fullPath, { recursive: true });
            console.log(`Created directory: ${fullPath}`);
        } else {
            console.log(`Directory already exists: ${fullPath}`);
        }
    });
}

// Clone repositories to a cache directory and move them
function getGitCommands() {
    // Use the project directory dynamically instead of hardcoding paths
    const comfyCacheDir = path.join(project_dir, 'cache');
    
    return [
        `git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner ${comfyCacheDir}/comfy_runner`,
        `git clone https://github.com/comfyanonymous/ComfyUI.git ${comfyCacheDir}/ComfyUI`,
        `xcopy /E /Y ${comfyCacheDir}/comfy_runner ${path.resolve(__dirname, project_dir, 'comfy_runner')}`,
        `xcopy /E /Y ${comfyCacheDir}/ComfyUI ${path.resolve(__dirname, project_dir, 'ComfyUI')}`
    ];
}

// Get installation commands based on the platform
function getInstallCommand(kernel) {
    const { platform, gpu } = kernel;
    
    project_requirements = [
        `pip install -r ${path.resolve(__dirname, 'requirements.txt')}`,
        `pip install -r ${path.resolve(__dirname, 'runnerrequirements.txt')}`,
        `pip install -r ${path.resolve(__dirname, 'groovyrequirements.txt')}`
    ];

    if (platform === "win32") {
        return [
            "python.exe -m pip install --upgrade pip",
            "pip install websocket",
            "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            ...project_requirements
        ];
    } else if (platform === "linux") {
        return project_requirements;
    }

    return [
        `pip install -r ${path.resolve(__dirname, 'requirements.txt')}`
    ];
}

// Main installation process
module.exports = async (kernel) => {
    const config = {
        run: [
            {
                method: "shell.run",
                params: {
                    message: getGitCommands()
                },
            },
            {
                method: "shell.run",
                params: {
                    venv: virtual_env,
                    path: project_dir,
                    message: getInstallCommand(kernel)
                }
            },
            {
                method: "fs.copy",
                params: {
                    src: `/.env.sample`,
                    dest: `/.env`,
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
                        "vae": `${project_dir}/ComfyUI/models/vae`
                    },
                    peers: [
                        "https://github.com/cocktailpeanutlabs/automatic1111.git",
                        "https://github.com/cocktailpeanutlabs/fooocus.git",
                        "https://github.com/cocktailpeanutlabs/forge.git"
                    ]
                }
            }
        ]
    };
    
    ensureDirectories();  // Ensure the necessary directories are created first
    return config;
};
