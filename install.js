const { virtual_env } = require("./constants");
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

    const basePath = path.join(__dirname, 'ComfyUI', 'models');
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
    const comfyCacheDir = path.join(__dirname, 'cache');
    
    return [
        `git clone --depth 1 -b main https://github.com/piyushK52/comfy_runner ${comfyCacheDir}/comfy_runner`,
        `git clone https://github.com/comfyanonymous/ComfyUI.git ${comfyCacheDir}/ComfyUI`,
        `xcopy /E /Y ${comfyCacheDir}/comfy_runner ${path.join(__dirname, 'comfy_runner')}`,
        `xcopy /E /Y ${comfyCacheDir}/ComfyUI ${path.join(__dirname, 'ComfyUI')}`
    ];
}

// Get installation commands based on the platform
function getInstallCommand(kernel) {
    const { platform } = kernel;
    
    const project_requirements = [
        `pip install -r ${path.join(__dirname, 'requirements.txt')}`,
        `pip install -r ${path.join(__dirname, 'runnerrequirements.txt')}`,  // runnerrequirements.txt added
        `pip install -r ${path.join(__dirname, 'groovyrequirements.txt')}`   // groovyrequirements.txt added
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
        `pip install -r ${path.join(__dirname, 'requirements.txt')}`
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
                    path: __dirname,
                    message: getInstallCommand(kernel)
                }
            },
            {
                method: "fs.copy",
                params: {
                    // Assuming .env.sample is located one level above the current __dirname
                    src: path.resolve(__dirname, '../.env.sample'),
                    dest: path.join(__dirname, '.env'),
                },
            },
            {
                method: "fs.link",
                params: {
                    drive: {
                        "checkpoints": path.join(__dirname, 'ComfyUI/models/checkpoints'),
                        "clip": path.join(__dirname, 'ComfyUI/models/clip'),
                        "clip_vision": path.join(__dirname, 'ComfyUI/models/clip_vision'),
                        "configs": path.join(__dirname, 'ComfyUI/models/configs'),
                        "controlnet": path.join(__dirname, 'ComfyUI/models/controlnet'),
                        "embeddings": path.join(__dirname, 'ComfyUI/models/embeddings'),
                        "loras": path.join(__dirname, 'ComfyUI/models/loras'),
                        "upscale_models": path.join(__dirname, 'ComfyUI/models/upscale_models'),
                        "vae": path.join(__dirname, 'ComfyUI/models/vae')
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
