# config.py

import os
from threading import Lock

# HuggingFace API tokens
API_KEYS = [
    "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",
    "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",
    "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"
]
headers = {"Authorization": f"Bearer {API_KEYS[0]}"}

# Define the ComfyUI directory and port
COMFYUI_DIR = r"C:\Users\bewiz\OneDrive\Desktop\AI\ComfyUI_windows_portable\ComfyUI"
OUTPUT_DIR = r"C:\Users\bewiz\OneDrive\Desktop\AI\ComfyUI_windows_portable\ComfyUI\output"
COMFYUI_PORT = 8188  # Define a port for the ComfyUI instance
default_model_path = r"albedobaseXL_v21.safetensors"  # Default model path

# Global variable to store the username
username_global = None
user_lock = Lock()  # To prevent race conditions

# Artist categories
artists = {
    "Contemporary Artists": ["Takashi Murakami", "Tyler Edlin", "Greg Rutkowski", "Beeple", "Banksy"],
    "Classical Artists": ["Michelangelo", "Tom Thomson", "Thomas Kinkade"],
    "Photographers": ["David LaChapelle", "Annie Leibovitz", "Tim Walker", "Nick Knight", "Steven Meisel", "Mario Testino", "Peter Lindbergh", "Cindy Sherman"],
    "Fantasy Artists": ["James Gurney", "Alan Lee", "Brothers Hildebrandt", "Justin Gerard", "Michael Whelan", "Simon Stålenhag"],
    "Surreal Artists": ["Olafur Eliasson", "Zdzisław Beksiński", "Jean Delville", "Jakub Różalski"],
    "Digital Artists": ["Alex Ross", "Mike Winkelmann", "Noah Bradley", "Anton Fadeev", "Dan Mumford"]
}

# Modifier categories
modifiers = {
    "Rendering Techniques": ['4K', 'unreal engine', 'octane render', '8k octane render', 'ray tracing', 'volumetric lighting', 'cinematic', 'realistic lighting', 'high resolution render', 'hyper realism', 'rendered in cinema4d', 'imax', 'daz3d', 'zbrush', 'redshift'],
    "Art Styles": ['photorealistic', 'mandelbulb fractal', 'Highly detailed carvings', 'illustration', 'evocative', 'mysterious', 'Pop Surrealism', 'sharp photography', 'hyper realistic', 'Epic composition', 'incomparable reality', 'smooth', 'sharp focus', 'intricate details', 'figurative art', 'detailed painting', 'neo-fauvism', 'fauvism', 'synchromism', 'cubism', 'collage art', 'bioluminescent', 'glitch art', 'data moshing', 'procedural generation', 'generative design'],
    "Lighting and Effects": ['Dramatic lighting', 'volumetric light', 'light rays', 'soft mist', 'Atmosphere', 'Dramatic lighting', 'light painting', 'motion blur', 'tilt-shift'],
    "Themes and Atmospheres": ['Sakura blossoms', 'magical atmosphere', 'muted colors', 'dystopian art', 'fantasy art', 'matte drawing', 'speed painting', 'darksynth', 'color field', 'panfuturism', 'futuristic', 'pixiv', 'auto-destructive art', 'apocalypse art', 'afrofuturism', 'metaphysical painting', 'wiccan', 'grotesque', 'whimsical', 'psychedelic art', 'digital art', 'fractalism', 'anime aesthetic', 'chiaroscuro', 'mystical', 'majestic', 'synthwave', 'cosmic horror', 'lovecraftian', 'vanitas', 'macabre', 'toonami', 'hologram', 'magic realism', 'impressionism', 'metaverse', 'cyberpunk', 'retrofuturism', 'steam punk', 'solar punk', 'art nouveau', 'gothic', 'baroque', 'minimalism']
}

predefined_styles = {
    "Scene Design": [
        {"name": "I'm in love with my car!", "image": "/mnt/data/chrome_OejyMZx1EZ.png"},
        {"name": "Structured Serenity", "image": "/mnt/data/chrome_X1sUULAcHT.png"},
        {"name": "Ethereal Vistas", "image": "/mnt/data/chrome_LEnBGlmqOU.png"},
        {"name": "Arcane Elegance", "image": "/mnt/data/chrome_kwxfoIVhdO.png"},
        {"name": "Impasto Realms", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Mystic Ethereal", "image": "/mnt/data/chrome_A0bLZmNEwN.png"},
        {"name": "Vibrant Tranquility", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Warm Fables", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Storybook Charm", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Mystical Escape", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Twilight Frontier", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Retro Sci-Fi", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Eerie Realm", "image": "/mnt/data/chrome_sR6TtQdtmp.png"}
    ],
    "Illustration Design": [
        {"name": "Delicate Aquarelle", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Simple Playful", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Coloring Book", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Manga Sketch", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Neo-Tokyo Noir", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Aquarelle Life", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Cheerful Storybook", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Vivid Tableaux", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Digital Ukiyo-e", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Narrative Film", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Narrative Chromatism", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Skyborne Realm", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Simplified Scenic", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Enchanted Elegance", "image": "/mnt/data/chrome_sR6TtQdtmp.png"}
    ],
    "LOGO Design": [
        {"name": "Negative Space", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Neo-Digitalism", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Pastel 3D", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Spellcraft Curio", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Lore Symbol", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Stylized Fauna", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Pure Easiness", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Playful Seaside", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Joyful Playthings", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Felted Charm", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Pastel Heart", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Miniatures", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Battlecraft", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Halloween Cutie", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"}
    ],
    "Abstract Art": [
        {"name": "Colorful Felt", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Ceramic Lifelike", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Paper Cutout", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Yarn Realism", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Tiny World", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Inflatable Balloon", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Surreal Iridescence", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Mysterious Night", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Glass World", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Bold Collage", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Metallic Fluid", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Whispering Lines", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Classic Memphis", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Fantasy Home", "image": "/mnt/data/chrome_lnMdVwJ29U.png"}
    ],
    "Portrait": [
        {"name": "Realistic", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Modern Professional", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "I'm in love with my car!", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Warm Portrait", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Bold Linework", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Playful Enamel", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "3D Avatars", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Luminous Grace", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Joyful Clay", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Inked Realism", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Color Block Chic", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Hyperbolic Portraiture", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Shimmering Glow", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Golden Hour", "image": "/mnt/data/chrome_lnMdVwJ29U.png"}
    ],
    "Interior Design": [
        {"name": "Modern Glamorous", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Interior Design Insight", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Wood Tone", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Minimalist", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Transitional", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Coastal", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Mid-Century", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Boho", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Scandi", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Industrial", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Creamy", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Modern Hotel", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"}
    ],
    "Character Design": [
        {"name": "Dynamic Figures", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Whimsical Beings", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Stylized Creatures", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Expressive Personas", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Mythical Characters", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Fantasy Avatars", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Heroic Archetypes", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Sci-Fi Figures", "image": "/mnt/data/chrome_lnMdVwJ29U.png"}
    ],
    "Tattoo Design": [
        {"name": "B&W Tattoo", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Apocalyptic Horror", "image": "/mnt/data/chrome_sR6TtQdtmp.png"},
        {"name": "Floral Tattoo", "image": "/mnt/data/chrome_lnMdVwJ29U.png"},
        {"name": "Watercolor Tattoo", "image": "/mnt/data/chrome_RC0T2Xe6Th.png"},
        {"name": "Classic Dotwork", "image": "/mnt/data/chrome_sR6TtQdtmp.png"}
    ]
}

