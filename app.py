import os
import json
import random
import requests
import gradio as gr
from PIL import Image
import time
import zipfile

# HuggingFace API token
API_KEY = "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"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Define the ComfyUI directory and port
COMFYUI_DIR = r"C:\Users\bewiz\OneDrive\Desktop\AI\ComfyUI_windows_portable\ComfyUI"
OUTPUT_DIR = r"C:\Users\bewiz\OneDrive\Desktop\AI\ComfyUI_windows_portable\ComfyUI\output"
COMFYUI_PORT = 8188  # Define a port for the ComfyUI instance

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

def read_workflow(file_path):
    """Read the workflow.json file."""
    print(f"Reading workflow from {file_path}")
    with open(file_path, 'r') as file:
        workflow = json.load(file)
    return workflow

def update_workflow(workflow, style_image_path, structure_image_path, prompt, negative_prompt, denoise_value, model_path="albedobaseXL_v21.safetensors", depth_map_type=None, depth_map_strength=None, ksampler_steps=None):
    """Update the workflow with the new images, prompts, and other parameters."""
    print(f"Updating workflow with style image: {style_image_path}, structure image: {structure_image_path}, prompt: {prompt}, and denoise value: {denoise_value}")
    
    for node_key, node in workflow.items():
        if isinstance(node, dict) and 'inputs' in node:
            if node.get('_meta', {}).get('title') == 'Style':
                node['inputs']['image'] = style_image_path
            elif node.get('_meta', {}).get('title') == 'Structure':
                node['inputs']['image'] = structure_image_path
            elif node.get('_meta', {}).get('title') == 'CLIP Text Encode (Prompt)':
                node['inputs']['text'] = prompt
                print(f"Updated prompt in node {node_key}: {node['inputs']['text']}")
            elif node.get('_meta', {}).get('title') == 'CLIP Text Encode (Negative Prompt)':
                node['inputs']['text'] = negative_prompt
                print(f"Updated negative prompt in node {node_key}: {node['inputs']['text']}")
            elif node.get('_meta', {}).get('title') == 'Load Checkpoint':
                node['inputs']['ckpt_name'] = model_path
                print(f"Updated model path in node {node_key}: {node['inputs']['ckpt_name']}")
            elif node.get('_meta', {}).get('title') == 'KSampler':
                node['inputs']['denoise'] = denoise_value  # Set the denoising value
                if ksampler_steps:
                    node['inputs']['steps'] = ksampler_steps
                print(f"Updated denoise value in node {node_key}: {node['inputs']['denoise']}")
                print(f"Updated KSampler steps in node {node_key}: {node['inputs']['steps']}")
            elif depth_map_type and depth_map_type in node.get('_meta', {}).get('title', ''):
                node['inputs']['strength'] = depth_map_strength
                print(f"Updated depth map strength in node {node_key}: {node['inputs']['strength']}")
    return workflow

def write_workflow(workflow, file_path):
    """Write the updated workflow back to workflow.json."""
    print(f"Writing updated workflow to {file_path}")
    with open(file_path, 'w') as file:
        json.dump(workflow, file, indent=4)

def image_to_text(image_path):
    print(f"Generating text from image: {image_path}")
    salesforce_blip = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    API_URL = salesforce_blip

    with open(image_path, "rb") as f:
        data = f.read()

    response = requests.post(API_URL, headers=headers, data=data)
    try:
        response = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return "Error decoding JSON response."

    try:
        generated_text = response[0]["generated_text"]
        print(f"Generated text: {generated_text}")
        return generated_text
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        return error_message

def generate_prompt(input_text, selected_artists, selected_modifiers, custom_text, retries=5):
    if input_text.startswith("Error"):
        return "There was an error processing the image. Please try again."

    falcon_7b = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    API_URL = falcon_7b

    for attempt in range(retries):
        prompt = f"Create a unique, highly detailed, and imaginative AI art prompt based on the context of the photo: {input_text}. Ensure the description is vivid, compelling, and evokes strong visual imagery."
        if custom_text:
            prompt += f" Theme: {custom_text}."
        if selected_artists:
            artist_list = ', '.join(random.sample(selected_artists, min(3, len(selected_artists))))
            prompt += f" Style inspired by {artist_list}."
        if selected_modifiers:
            modifier_list = ', '.join(random.sample(selected_modifiers, min(3, len(selected_modifiers))))
            prompt += f" Modifiers: {modifier_list}."

        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100}}
        response = requests.post(API_URL, headers=headers, json=payload)

        try:
            response_json = response.json()
            generated_text = response_json.get("generated_text", None)
            if generated_text:
                return generated_text.strip()
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(2)  # Wait for a bit before retrying

    return "Unable to generate a prompt after multiple attempts. Please try again."

def start_comfyui_and_update_workflow(style_image, structure_image, custom_text, selected_artists, selected_modifiers, negative_prompt, denoise_value, randomize, depth_map_type, depth_map_strength, ksampler_steps):
    style_image_path = style_image.name
    structure_image_path = structure_image.name

    print(f"Starting ComfyUI with style image: {style_image_path} and structure image: {structure_image_path}")

    workflow_file = os.path.join(COMFYUI_DIR, 'workflow.json')
    workflow = read_workflow(workflow_file)

    input_text = image_to_text(structure_image_path)

    generated_prompt = generate_prompt(input_text, selected_artists, selected_modifiers, custom_text)
    
    updated_workflow = update_workflow(
        workflow,
        style_image_path,
        structure_image_path,
        generated_prompt,
        negative_prompt,
        denoise_value,
        model_path="albedobaseXL_v21.safetensors",
        depth_map_type=depth_map_type,
        depth_map_strength=depth_map_strength,
        ksampler_steps=ksampler_steps
    )
    write_workflow(updated_workflow, workflow_file)

    output_image_path = os.path.join(OUTPUT_DIR, 'output_image.png')
    debug_logs = "Debug logs placeholder"
    terminal_output = "Terminal output placeholder"

    # Implement the logic to run ComfyUI and get the output image
    # Here we should call the actual ComfyUI processing script or API
    # For now, we return placeholders

    return output_image_path, debug_logs, terminal_output

def process_images(style_image, structure_image, custom_text, selected_artists, selected_modifiers, negative_prompt, denoise_value, randomize, depth_map_type, depth_map_strength, ksampler_steps):
    return start_comfyui_and_update_workflow(
        style_image, 
        structure_image, 
        custom_text, 
        selected_artists, 
        selected_modifiers, 
        negative_prompt, 
        denoise_value, 
        randomize, 
        depth_map_type, 
        depth_map_strength, 
        ksampler_steps
    )

def process_batch_images(style_images, structure_images, custom_text, selected_artists, selected_modifiers, negative_prompt, denoise_value, randomize, depth_map_type, depth_map_strength, ksampler_steps):
    output_paths = []
    debug_logs = "Batch processing debug logs placeholder"
    terminal_output = "Batch processing terminal output placeholder"
    
    for style_image, structure_image in zip(style_images, structure_images):
        output_path, debug_log, terminal_out = process_images(
            style_image, structure_image, custom_text, selected_artists, selected_modifiers, negative_prompt, denoise_value, randomize, depth_map_type, depth_map_strength, ksampler_steps
        )
        output_paths.append(output_path)
    
    zip_filename = "batch_output.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in output_paths:
            zipf.write(file_path, os.path.basename(file_path))
    
    return zip_filename, debug_logs, terminal_output

def main():
    with gr.Blocks(css=".gradio-container {font-family: Arial, sans-serif;} .gradio-container .gr-button {background-color: #4CAF50; color: white;}") as demo:
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Accordion("Developer Info", open=True):
                    gr.Markdown("### Developed by [Ai Anarchist](https://twitter.com/AiAnarchist)")
                    gr.Markdown("Contact: [downlifted@gmail.com](mailto:downlifted@gmail.com)")
                    gr.Markdown("[![Twitter](https://upload.wikimedia.org/wikipedia/commons/4/4f/Twitter-logo.svg)](https://twitter.com/AiAnarchist)")

                with gr.Accordion("About StyleSuite", open=True):
                    gr.Markdown("""
                        ### StyleSuite: AI Art Style Transfer
                        Style hundreds of images at once with no need for prompting due to the LLM that powers the image recognition.
                        - **ComfyUI**: For seamless integration and image processing.
                        - **Hugging Face**: For state-of-the-art language models.
                        - **Gradio**: For an intuitive user interface.
                        - **PicToPrompt**: For advanced image recognition and prompting.
                    """)

            with gr.Column(scale=3):
                gr.Markdown("# StyleSuite for AI Art Style Transfer")

                with gr.Tab("Single Image Processing"):
                    with gr.Row():
                        with gr.Column():
                            style_image = gr.File(label="Upload Style Image", type="filepath")
                            structure_image = gr.File(label="Upload Structure Image", type="filepath")
                            custom_text = gr.Textbox(label="Add Custom Text (Optional)", placeholder="Enter custom text here...")
                            negative_prompt = gr.Textbox(label="Negative Prompt (Optional)", placeholder="Enter negative prompt here...")
                            denoise_value = gr.Slider(label="Denoise Value", minimum=0.0, maximum=1.0, step=0.01, value=0.69)
                            randomize = gr.Checkbox(label="Randomize Artists and Modifiers", value=False)
                            
                            artist_category = gr.Dropdown(list(artists.keys()), label="Select Artist Category", interactive=True)
                            artist_dropdown = gr.Dropdown([], label="Select Artists", multiselect=True, interactive=True)
                            modifier_category = gr.Dropdown(list(modifiers.keys()), label="Select Modifier Category", interactive=True)
                            modifier_dropdown = gr.Dropdown([], label="Select Modifiers", multiselect=True, interactive=True)

                            # Add depth map selection and strength slider
                            depth_map_type = gr.Radio(label="Depth Map Type", choices=["None", "LeReS", "Zoe"], value="None", interactive=True, 
                                                    info="Choose 'LeReS' for less concentration on the main subject, giving more background freedom. Choose 'Zoe' for more enforced control on the main subject.")
                            depth_map_strength = gr.Slider(label="Depth Map Strength", minimum=0.0, maximum=1.0, step=0.01, value=0.5)
                            
                            # Add KSampler steps slider
                            ksampler_steps = gr.Slider(label="KSampler Steps", minimum=10, maximum=100, step=1, value=50)

                            process_btn = gr.Button("Start ComfyUI and Update Workflow")

                            def update_artist_dropdown(category):
                                return gr.update(choices=artists[category])

                            def update_modifier_dropdown(category):
                                return gr.update(choices=modifiers[category])

                            artist_category.change(fn=update_artist_dropdown, inputs=artist_category, outputs=artist_dropdown)
                            modifier_category.change(fn=update_modifier_dropdown, inputs=modifier_category, outputs=modifier_dropdown)

                        with gr.Column():
                            output = gr.Image(label="Transformed Image")
                            debug_output = gr.Textbox(label="Debug Logs", interactive=True)
                            terminal_output = gr.Textbox(label="Terminal Output", interactive=True)

                    process_btn.click(
                        fn=process_images,
                        inputs=[style_image, structure_image, custom_text, artist_dropdown, modifier_dropdown, negative_prompt, denoise_value, randomize, depth_map_type, depth_map_strength, ksampler_steps],
                        outputs=[output, debug_output, terminal_output]
                    )

                with gr.Tab("Batch Image Processing"):
                    with gr.Row():
                        with gr.Column():
                            style_images = gr.File(label="Upload Style Images", file_count="multiple", type="filepath")
                            structure_images = gr.File(label="Upload Structure Images", file_count="multiple", type="filepath")
                            custom_text_batch = gr.Textbox(label="Add Custom Text (Optional)", placeholder="Enter custom text here...")
                            negative_prompt_batch = gr.Textbox(label="Negative Prompt (Optional)", placeholder="Enter negative prompt here...")
                            denoise_value_batch = gr.Slider(label="Denoise Value", minimum=0.0, maximum=1.0, step=0.01, value=0.69)
                            randomize_batch = gr.Checkbox(label="Randomize Artists and Modifiers", value=False)
                            
                            artist_category_batch = gr.Dropdown(list(artists.keys()), label="Select Artist Category", interactive=True)
                            artist_dropdown_batch = gr.Dropdown([], label="Select Artists", multiselect=True, interactive=True)
                            modifier_category_batch = gr.Dropdown(list(modifiers.keys()), label="Select Modifier Category", interactive=True)
                            modifier_dropdown_batch = gr.Dropdown([], label="Select Modifiers", multiselect=True, interactive=True)

                            # Add depth map selection and strength slider
                            depth_map_type_batch = gr.Radio(label="Depth Map Type", choices=["None", "LeReS", "Zoe"], value="None", interactive=True, 
                                                    info="Choose 'LeReS' for less concentration on the main subject, giving more background freedom. Choose 'Zoe' for more enforced control on the main subject.")
                            depth_map_strength_batch = gr.Slider(label="Depth Map Strength", minimum=0.0, maximum=1.0, step=0.01, value=0.5)
                            
                            # Add KSampler steps slider
                            ksampler_steps_batch = gr.Slider(label="KSampler Steps", minimum=10, maximum=100, step=1, value=50)

                            process_batch_btn = gr.Button("Start Batch Processing")

                            artist_category_batch.change(fn=update_artist_dropdown, inputs=artist_category_batch, outputs=artist_dropdown_batch)
                            modifier_category_batch.change(fn=update_modifier_dropdown, inputs=modifier_category_batch, outputs=modifier_dropdown_batch)

                        with gr.Column():
                            output_batch = gr.File(label="Download Transformed Image(s)")
                            debug_output_batch = gr.Textbox(label="Debug Logs", interactive=True)
                            terminal_output_batch = gr.Textbox(label="Terminal Output", interactive=True)

                    def process_and_enable_zip(*args):
                        output, debug, terminal, zip_filename = process_batch_images(*args)
                        return zip_filename, debug, terminal, zip_filename

                    process_batch_btn.click(
                        fn=process_and_enable_zip,
                        inputs=[style_images, structure_images, custom_text_batch, artist_dropdown_batch, modifier_dropdown_batch, negative_prompt_batch, denoise_value_batch, randomize_batch, depth_map_type_batch, depth_map_strength_batch, ksampler_steps_batch],
                        outputs=[output_batch, debug_output_batch, terminal_output_batch, output_batch]
                    )

    demo.launch(share=True)

if __name__ == "__main__":
    main()
