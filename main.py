import time
import os
import shutil
import re
import random
import torch
import gradio as gr
from PIL import Image, UnidentifiedImageError
import requests
from config import artists, modifiers, COMFYUI_DIR, OUTPUT_DIR, COMFYUI_PORT, username_global, user_lock, predefined_styles, API_KEYS, headers
from utilities import read_workflow, update_workflow, write_workflow, image_to_text, generate_prompt, send_workflow_to_comfyui, monitor_output_images, zip_images, blend_images, get_predefined_style_image, add_placeholder_image, generate_fallback_prompt

torch.cuda.empty_cache()

GROOVY_IMAGE_URL = "https://raw.githubusercontent.com/downlifted/Groovy-StyleSuite/main/groovy.png"

adjectives = ["Hungry", "Curious", "Brave", "Silly", "Gentle", "Swift"]
nouns = ["Tiger", "Mountain", "River", "Explorer", "Eagle", "Forest"]

def generate_random_username():
    return random.choice(adjectives) + random.choice(nouns)

def ensure_groovy_image(user_folder):
    groovy_image_path = os.path.join(user_folder, "groovy.png")
    if not os.path.exists(groovy_image_path):
        response = requests.get(GROOVY_IMAGE_URL, stream=True)
        if response.status_code == 200:
            with open(groovy_image_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response

def initialize_user():
    global username_global
    if not username_global:
        username_global = generate_random_username()
    
    user_folder = os.path.join(OUTPUT_DIR, username_global)
    os.makedirs(user_folder, exist_ok=True)
    ensure_groovy_image(user_folder)
    
    return username_global

def process_images(user_id, style_image, structure_image, custom_text, artist_dropdown, modifier_dropdown, negative_prompt, denoise_value, denoise_min, denoise_max, depth_processor, depth_strength, ksampler_steps, use_tilenet, model_name, randomize, randomize_denoise, randomize_depth_processor, blending_mode=False, progress=gr.Progress()):
    global username_global, headers

    def get_image_path(image):
        if isinstance(image, dict):
            return image["name"]
        elif isinstance(image, str):
            return image
        else:
            return image.name

    with user_lock:
        if not user_id:
            if not username_global:
                username_global = generate_random_username()
            user_id = username_global
        else:
            username_global = user_id

        user_folder = os.path.join(OUTPUT_DIR, user_id)
        blended_folder = os.path.join(user_folder, "BLENDED")
        os.makedirs(user_folder, exist_ok=True)
        os.makedirs(blended_folder, exist_ok=True)
        ensure_groovy_image(user_folder)

    style_image_path = get_image_path(style_image)
    structure_image_path = get_image_path(structure_image)

    # Check if the uploaded files are valid images
    try:
        Image.open(style_image_path).verify()
        Image.open(structure_image_path).verify()
    except UnidentifiedImageError:
        return "Invalid image file provided.", "", ""

    workflow_file = "yestile.json" if use_tilenet else "workflow.json"
    workflow_path = os.path.join(COMFYUI_DIR, workflow_file)
    workflow = read_workflow(workflow_path)

    if randomize or not artist_dropdown:
        selected_artists = [artist for category in artists for artist in artists[category]]
    else:
        selected_artists = artist_dropdown
    
    if randomize or not modifier_dropdown:
        selected_modifiers = [modifier for category in modifiers for modifier in modifiers[category]]
    else:
        selected_modifiers = modifier_dropdown

    output_images = []
    debug_logs = ""
    terminal_logs = ""
    generated_prompt = ""

    try:
        input_text = image_to_text(style_image_path)
        if input_text == "Image identification failed":
            debug_logs += f"Skipping image: {style_image_path} due to identification failure.\n"
            return "Image identification failed", debug_logs, "Image identification failed"
        
        prompt = generate_prompt(input_text, selected_artists, selected_modifiers, custom_text)
        if prompt == "There was an error processing the image. Please try again.":
            headers["Authorization"] = f"Bearer {API_KEYS[1]}"
            prompt = generate_prompt(input_text, selected_artists, selected_modifiers, custom_text)
            if prompt == "There was an error processing the image. Please try again.":
                headers["Authorization"] = f"Bearer {API_KEYS[2]}"
                prompt = generate_prompt(input_text, selected_artists, selected_modifiers, custom_text)
                if prompt == "There was an error processing the image. Please try again.":
                    prompt = generate_fallback_prompt(selected_artists, selected_modifiers, custom_text)

        generated_prompt = prompt

        denoise_values = [0.55, 0.75] if blending_mode else [random.uniform(denoise_min, denoise_max) if randomize_denoise else denoise_value]

        if randomize_depth_processor:
            depth_processors = ["MiDaS-DepthMapPreprocessor", "LeReS-DepthMapPreprocessor", "Zoe-DepthMapPreprocessor"]
            depth_processor = random.choice(depth_processors)

        for denoise_value in denoise_values:
            updated_workflow = update_workflow(workflow, style_image_path, structure_image_path, prompt, negative_prompt, denoise_value, depth_processor, depth_strength, ksampler_steps, use_tilenet, model_name, user_id)
            write_workflow(updated_workflow, workflow_path)

            try:
                payload = {
                    "client_id": "192e7dc710dc4e548fd4b539b925a62f",
                    "prompt": updated_workflow,
                    "extra_data": {}
                }
                send_workflow_to_comfyui(payload, COMFYUI_PORT)
                
                previous_images = os.listdir(OUTPUT_DIR)
                new_images = monitor_output_images(OUTPUT_DIR, previous_images)

                time.sleep(2)
                
                for img_path in new_images:
                    if user_id in img_path:  # Ensure the file belongs to the current user
                        shutil.copy(img_path, user_folder)
                
                output_images.extend(new_images)
                terminal_logs += f"Processed image: {structure_image_path}\n"
                terminal_logs += f"Using style: {style_image_path}\n"
                terminal_logs += f"Generated prompt: {prompt}\n"
                terminal_logs += f"Negative prompt: {negative_prompt if negative_prompt else 'bad quality, blurry, ugly'}\n"
                terminal_logs += f"Denoise value: {denoise_value}\n"
                terminal_logs += f"Depth processor: {depth_processor}\n"
                terminal_logs += f"Depth strength: {depth_strength}\n"
                terminal_logs += f"KSampler steps: {ksampler_steps}\n"
                terminal_logs += f"Using Tile Control Net: {use_tilenet}\n"
                terminal_logs += f"New image generated: {new_images}\n"
                
            except Exception as e:
                error_message = f"Error during processing: {str(e)}"
                print(error_message)
                debug_logs += error_message

        if blending_mode and len(output_images) >= 2:
            blended_image = blend_images(output_images[-1], output_images[-2], blend_ratio=0.4)
            blended_image_path = os.path.join(blended_folder, f"blended_{os.path.basename(output_images[-2])}")
            blended_image.save(blended_image_path)
            output_images.append(blended_image_path)

    except Exception as e:
        error_message = f"Error during processing image: {str(e)}"
        print(error_message)
        debug_logs += error_message

    if not output_images:
        placeholder_image_path = add_placeholder_image(user_folder)
        output_images.append(placeholder_image_path)
        debug_logs += "No images were processed, added a placeholder image.\n"

    if len(output_images) > 1:
        zip_filename = zip_images(output_images, 1, user_folder)
        return zip_filename, debug_logs, terminal_logs

    return os.path.join(user_folder, os.path.basename(output_images[0])) if output_images else "Error processing images", debug_logs, terminal_logs

def process_batch_images(user_id, style_images, structure_images, custom_text, artist_dropdown, modifier_dropdown, negative_prompt, denoise_value, denoise_min, denoise_max, depth_processor, depth_strength, ksampler_steps, randomize, use_tilenet, model_name, randomize_denoise, randomize_depth_processor, blending_mode, zip_interval):
    global username_global, headers

    def get_image_path(image):
        if isinstance(image, dict):
            return image["name"]
        elif isinstance(image, str):
            return image
        else:
            return image.name

    with user_lock:
        if not user_id:
            if not username_global:
                username_global = generate_random_username()
            user_id = username_global
        else:
            username_global = user_id

        user_folder = os.path.join(OUTPUT_DIR, user_id)
        blended_folder = os.path.join(user_folder, "BLENDED")
        os.makedirs(user_folder, exist_ok=True)
        os.makedirs(blended_folder, exist_ok=True)
        ensure_groovy_image(user_folder)

    def extract_number(filename):
        """Extracts the first number found in the filename or returns a large number if no number is found."""
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    style_image_paths = sorted([get_image_path(img) for img in style_images], key=lambda x: extract_number(os.path.splitext(os.path.basename(x))[0]))
    structure_image_paths = [get_image_path(img) for img in structure_images]

    workflow_file = "yestile.json" if use_tilenet else "workflow.json"
    workflow_path = os.path.join(COMFYUI_DIR, workflow_file)
    workflow = read_workflow(workflow_path)

    if randomize or not artist_dropdown:
        selected_artists = [artist for category in artists for artist in artists[category]]
    else:
        selected_artists = artist_dropdown

    if randomize or not modifier_dropdown:
        selected_modifiers = [modifier for category in modifiers for modifier in modifiers[category]]
    else:
        selected_modifiers = modifier_dropdown

    output_images = []
    zip_files = []
    debug_logs = ""
    terminal_logs = ""
    generated_prompt = ""

    total_images = len(style_image_paths)
    chunk_index = 1
    for i, style_image_path in enumerate(style_image_paths):
        structure_image_path = structure_image_paths[i % len(structure_image_paths)]
        
        try:
            input_text = image_to_text(style_image_path)
            if input_text == "Image identification failed":
                debug_logs += f"Skipping image: {style_image_path} due to identification failure.\n"
                continue
            
            retries = 3
            for attempt in range(retries):
                prompt = generate_prompt(input_text, selected_artists, selected_modifiers, custom_text)
                if not prompt.startswith("Error"):
                    break
                elif attempt == retries - 1:
                    prompt = generate_fallback_prompt(selected_artists, selected_modifiers, custom_text)

            generated_prompt = prompt

            denoise_values = [0.55, 0.75] if blending_mode else [random.uniform(denoise_min, denoise_max) if randomize_denoise else denoise_value]

            if randomize_depth_processor:
                depth_processors = ["MiDaS-DepthMapPreprocessor", "LeReS-DepthMapPreprocessor", "Zoe-DepthMapPreprocessor"]
                depth_processor = random.choice(depth_processors)

            for denoise_value in denoise_values:
                updated_workflow = update_workflow(workflow, style_image_path, structure_image_path, prompt, negative_prompt, denoise_value, depth_processor, depth_strength, ksampler_steps, use_tilenet, model_name, user_id)
                write_workflow(updated_workflow, workflow_path)

                try:
                    payload = {
                        "client_id": "192e7dc710dc4e548fd4b539b925a62f",
                        "prompt": updated_workflow,
                        "extra_data": {}
                    }
                    send_workflow_to_comfyui(payload, COMFYUI_PORT)
                    
                    previous_images = os.listdir(OUTPUT_DIR)
                    new_images = monitor_output_images(OUTPUT_DIR, previous_images)

                    time.sleep(2)
                    
                    for img_path in new_images:
                        if user_id in img_path:  # Ensure the file belongs to the current user
                            img_full_path = os.path.join(OUTPUT_DIR, img_path)
                            unique_filename = ensure_unique_filename(user_folder, os.path.basename(img_full_path))
                            destination_path = os.path.join(user_folder, unique_filename)
                            shutil.copy(img_full_path, destination_path)
                            output_images.append(destination_path)
                        
                    terminal_logs += f"Processed image {i+1}/{total_images}: {structure_image_path}\n"
                    terminal_logs += f"Using style: {style_image_path}\n"
                    terminal_logs += f"Generated prompt: {prompt}\n"
                    terminal_logs += f"Negative prompt: {negative_prompt if negative_prompt else 'bad quality, blurry, ugly'}\n"
                    terminal_logs += f"Denoise value: {denoise_value}\n"
                    terminal_logs += f"Depth processor: {depth_processor}\n"
                    terminal_logs += f"Depth strength: {depth_strength}\n"
                    terminal_logs += f"KSampler steps: {ksampler_steps}\n"
                    terminal_logs += f"Using Tile Control Net: {use_tilenet}\n"
                    terminal_logs += f"New image generated: {new_images}\n"

                    if blending_mode and len(output_images) >= 2:
                        blended_image = blend_images(output_images[-1], output_images[-2], blend_ratio=0.4)
                        blended_image_path = os.path.join(blended_folder, f"blended_{os.path.basename(output_images[-2])}")
                        blended_image.save(blended_image_path)
                        output_images.append(blended_image_path)
                    time.sleep(2)  # Add delay to ensure file operations complete
                except Exception as e:
                    error_message = f"Error during processing image {i+1}/{total_images}: {str(e)}"
                    print(error_message)
                    debug_logs += error_message

            progress_text = f"Processed {i + 1}/{total_images} - Done: {i + 1}, Left: {total_images - (i + 1)}"
            yield output_images, progress_text, terminal_logs, zip_files

            if (i + 1) % zip_interval == 0 or (i + 1) == total_images:
                try:
                    time.sleep(2)  # Add delay before zipping files
                    zip_filename = zip_images(output_images, chunk_index, user_folder)
                    zip_files.append(zip_filename)
                    output_images = []
                    chunk_index += 1
                    yield output_images, progress_text, terminal_logs, zip_files
                except Exception as e:
                    error_message = f"Error during zipping files: {str(e)}"
                    print(error_message)
                    debug_logs += error_message

        except Exception as e:
            error_message = f"Error during processing image {i+1}/{total_images}: {str(e)}"
            print(error_message)
            debug_logs += error_message

    if not output_images:
        placeholder_image_path = add_placeholder_image(user_folder)
        output_images.append(placeholder_image_path)
        debug_logs += "No images were processed, added a placeholder image.\n"

    return output_images, debug_logs, terminal_logs, zip_files

def gallery(images):
    """Function to create a gallery view of the images."""
    gallery_images = []
    for image in images:
        try:
            img = Image.open(image)
            img.thumbnail((150, 150))
            gallery_images.append(img)
        except UnidentifiedImageError:
            continue
    return gallery_images

def ensure_unique_filename(directory, filename):
    """Ensure a unique filename in the directory by appending numbers if necessary."""
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{extension}"
        counter += 1
    return new_filename

def process_predefined_style(user_id, structure_image, style_name, style_category):
    style_image_path = get_predefined_style_image(style_name, style_category)
    if not style_image_path:
        return "Error: Style image not found.", "", "Style image not found."

    # Use the existing process_images function for processing
    return process_images(
        user_id, style_image_path, structure_image, "", [], [], "", 0.7, 0.4, 1.0, "MiDaS-DepthMapPreprocessor", 1, 27, True, "MOBIUS.safetensors", False, False, False, False
    )

def update_artist_dropdown(category):
    return gr.update(choices=artists[category])

def update_modifier_dropdown(category):
    return gr.update(choices=modifiers[category])

def show_denoise_sliders(randomize_denoise):
    return gr.update(visible=randomize_denoise), gr.update(visible=randomize_denoise), gr.update(visible=randomize_denoise)

def load_user_gallery(user_id):
    global username_global
    user_folder = os.path.join(OUTPUT_DIR, username_global)
    ensure_groovy_image(user_folder)
    image_files = [os.path.join(user_folder, file) for file in os.listdir(user_folder) if file.endswith((".png", ".jpg", ".jpeg"))]
    return gr.update(value=image_files)

def main():
    global username_global
    
    with gr.Blocks(css="""
    .gradio-container {font-family: Arial, sans-serif;}
    .download-button {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Blue_download_arrow.svg/1200px-Blue_download_arrow.svg.png');
        background-size: cover;
        border: none;
        width: 50px;
        height: 50px;
        cursor: pointer.
    }
    .psychedelic-text span {
        animation: colorchange 10s infinite;
    }
    @keyframes colorchange {
         0% { color: #ff69b4; }
         10% { color: #ba55d3; }
         20% { color: #7b68ee; }
         30% { color: #00bfff; }
         40% { color: #3cb371; }
         50% { color: #ffff54; }
         60% { color: #ffa500; }
         70% { color: #ff4500; }
         80% { color: #ff1493; }
         90% { color: #da70d6; }
         100% { color: #ff69b4; }
    }
    """) as demo:
        gr.Markdown("""
        <h1 class="psychedelic-text">
            <span>G</span><span>r</span><span>o</span><span>o</span><span>v</span><span>y</span>-
            <span> </span>
            <span>S</span><span>t</span><span>y</span><span>l</span><span>S</span><span>u</span><span>i</span><span>t</span>;
            <span> </span>
            <span>G</span><span>r</span><span>o</span><span>o</span><span>v</span><span>y</span>-
            <span> </span>
            <span>L</span><span>i</span><span>k</span><span>e</span>
            <span>y</span><span>o</span><span>u</span>.
        </h1>
        """)

        gr.Markdown("ComfyUI Workflow Automation\nWelcome to the Groovy ComfyUI Workflow Automation tool. Follow the instructions below to upload your images and generate AI art. For batch processing, you can upload multiple images and the tool will process them sequentially or randomly as per your choice. <b>Imagine that the STRUCTURE item is the item you want to reflect the style on, the STYLE image is the image the structure will be Styled with, and the prompt will be based on the Style image respectfully. ~ 1")

        username_global = initialize_user()

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### beWiZ's GroOvy StyleSuite")
                gr.Image(value="https://raw.githubusercontent.com/downlifted/Groovy-StyleSuite/main/groovy.png", label="GroOvy- StyleSuite Logo")
                with gr.Accordion("Developer Information", open=False):
                    gr.Markdown("### Made by BeWiZ")
                    gr.Markdown("[![BeWiZ Logo](https://raw.githubusercontent.com/downlifted/pictoprompt/master/aia.png)](https://twitter.com/AiAnarchist)")
                    gr.Markdown("Contact: [downlifted@gmail.com](mailto:downlifted@gmail.com)")
                with gr.Accordion("About StyleSuite", open=False):
                    gr.Markdown("""
                    ### StyleSuite: AI Art Style Transfer
                    Style hundreds of images at once with no need for prompting due to the LLM that powers the image recognition.
                    - **ComfyUI**: For seamless integration and image processing.
                    - **Hugging Face**: For state-of-the-art language models.
                    - **Gradio**: For an intuitive user interface.
                    - **PicToPrompt**: For advanced image recognition and prompting.
                    """)

            with gr.Column(scale=3):
                with gr.Tab("Single Image Processing"):
                    with gr.Row():
                        with gr.Column():
                            user_id = gr.Textbox(label="Username", value=username_global, interactive=False)
                            style_image = gr.File(label="Upload Style Image", type="filepath")
                            structure_image = gr.File(label="Upload Structure Image", type="filepath")
                            custom_text = gr.Textbox(label="Add Custom Text (Optional)", placeholder="Enter custom text here...")
                            negative_prompt = gr.Textbox(label="Negative Prompt (Optional)", placeholder="Enter negative prompt here...")
                            denoise_value = gr.Slider(label="Denoise Value", minimum=0.4, maximum=1.0, step=0.01, value=0.6, visible=True)
                            denoise_min = gr.Slider(label="Denoise Min Value", minimum=0.4, maximum=1.0, step=0.01, value=0.6, visible=False)
                            denoise_max = gr.Slider(label="Denoise Max Value", minimum=0.4, maximum=1.0, step=0.01, value=0.7, visible=False)
                            randomize_denoise = gr.Checkbox(label="Randomize Denoise Value", value=False)
                            depth_processor = gr.Radio(label="Depth Processor", choices=["MiDaS-DepthMapPreprocessor", "LeReS-DepthMapPreprocessor", "Zoe-DepthMapPreprocessor"], value="MiDaS-DepthMapPreprocessor", info="Select depth map processor: MiDaS for more enforced control on the main subject, LeReS for less concentration on the main subject, Zoe for a balance.")
                            randomize_depth_processor = gr.Checkbox(label="Randomize Depth Processor", value=False)
                            depth_strength = gr.Slider(label="Depth Strength", minimum=0.0, maximum=1.0, step=0.01, value=1)
                            ksampler_steps = gr.Slider(label="KSampler Steps", minimum=1, maximum=100, step=1, value=27)
                            randomize = gr.Checkbox(label="Randomize Artists and Modifiers", value=False)
                            use_tilenet = gr.Checkbox(label="Use Tile Control Net", value=True)
                            model_name = gr.Dropdown(["MOBIUS.safetensors", "albedobaseXL_v21.safetensors"], label="Model Selection", value="albedobaseXL_v21.safetensors")
                            blending_mode = gr.Checkbox(label="Enable Blending Mode", value=False)

                            artist_category = gr.Dropdown(list(artists.keys()), label="Select Artist Category", interactive=True)
                            artist_dropdown = gr.Dropdown([], label="Select Artists", multiselect=True, interactive=True)
                            modifier_category = gr.Dropdown(list(modifiers.keys()), label="Select Modifier Category", interactive=True)
                            modifier_dropdown = gr.Dropdown([], label="Select Modifiers", multiselect=True, interactive=True)

                            process_btn = gr.Button("Start ComfyUI and Update Workflow")

                            artist_category.change(fn=update_artist_dropdown, inputs=artist_category, outputs=artist_dropdown)
                            modifier_category.change(fn=update_modifier_dropdown, inputs=modifier_category, outputs=modifier_dropdown)
                            randomize_denoise.change(fn=show_denoise_sliders, inputs=randomize_denoise, outputs=[denoise_value, denoise_min, denoise_max])

                        with gr.Column():
                            output = gr.Image(label="Transformed Image")
                            debug_output = gr.Textbox(label="Debug Logs", interactive=True)
                            terminal_output = gr.Textbox(label="Terminal Output", interactive=True)

                    process_btn.click(
                        fn=process_images,
                        inputs=[user_id, style_image, structure_image, custom_text, artist_dropdown, modifier_dropdown, negative_prompt, denoise_value, denoise_min, denoise_max, depth_processor, depth_strength, ksampler_steps, use_tilenet, model_name, randomize, randomize_denoise, randomize_depth_processor, blending_mode],
                        outputs=[output, debug_output, terminal_output]
                    )

                with gr.Tab("Predefined Styles"):
                    with gr.Row():
                        with gr.Column():
                            user_id_predefined = gr.Textbox(label="Username", value=username_global, interactive=False)
                            structure_image_predefined = gr.File(label="Upload Structure Image", type="filepath")
                            style_category_predefined = gr.Dropdown(list(predefined_styles.keys()), label="Select Style Category", interactive=True)
                            style_predefined = gr.Dropdown([], label="Select Style", interactive=True)
                            process_predefined_btn = gr.Button("Apply Predefined Style")

                            def update_style_dropdown(category):
                                styles = [style["name"] for style in predefined_styles[category]]
                                return gr.update(choices=styles)

                            style_category_predefined.change(fn=update_style_dropdown, inputs=style_category_predefined, outputs=style_predefined)

                        with gr.Column():
                            output_predefined = gr.Image(label="Transformed Image")
                            debug_output_predefined = gr.Textbox(label="Debug Logs", interactive=True)
                            terminal_output_predefined = gr.Textbox(label="Terminal Output", interactive=True)

                    process_predefined_btn.click(
                        fn=process_predefined_style,
                        inputs=[user_id_predefined, structure_image_predefined, style_predefined, style_category_predefined],
                        outputs=[output_predefined, debug_output_predefined, terminal_output_predefined]
                    )

                with gr.Tab("Batch Image Processing"):
                    with gr.Row():
                        with gr.Column():
                            user_id_batch = gr.Textbox(label="Username", value=username_global, interactive=False)
                            style_images = gr.File(label="Upload Style Images", file_count="multiple", type="filepath")
                            structure_images = gr.File(label="Upload Structure Images", file_count="multiple", type="filepath")
                            custom_text_batch = gr.Textbox(label="Add Custom Text (Optional)", placeholder="Enter custom text here...")
                            negative_prompt_batch = gr.Textbox(label="Negative Prompt (Optional)", placeholder="Enter negative prompt here...")
                            denoise_value_batch = gr.Slider(label="Denoise Value", minimum=0.4, maximum=1.0, step=0.01, value=0.6, visible=True)
                            denoise_min_batch = gr.Slider(label="Denoise Min Value", minimum=0.4, maximum=1.0, step=0.01, value=0.6, visible=False)
                            denoise_max_batch = gr.Slider(label="Denoise Max Value", minimum=0.4, maximum=1.0, step=0.01, value=0.7, visible=False)
                            randomize_denoise_batch = gr.Checkbox(label="Randomize Denoise Value", value=False)
                            depth_processor_batch = gr.Radio(label="Depth Processor", choices=["MiDaS-DepthMapPreprocessor", "LeReS-DepthMapPreprocessor", "Zoe-DepthMapPreprocessor"], value="MiDaS-DepthMapPreprocessor", info="Select depth map processor: MiDaS for more enforced control on the main subject, LeReS for less concentration on the main subject, Zoe for a balance.")
                            randomize_depth_processor_batch = gr.Checkbox(label="Randomize Depth Processor", value=False)
                            depth_strength_batch = gr.Slider(label="Depth Strength", minimum=0.0, maximum=1.0, step=0.01, value=1)
                            ksampler_steps_batch = gr.Slider(label="KSampler Steps", minimum=1, maximum=100, step=1, value=27)
                            randomize_batch = gr.Checkbox(label="Randomize Artists and Modifiers", value=False)
                            use_tilenet_batch = gr.Checkbox(label="Use Tile Control Net", value=True)
                            model_name_batch = gr.Dropdown(["MOBIUS.safetensors", "albedobaseXL_v21.safetensors"], label="Model Selection", value="albedobaseXL_v21.safetensors")
                            blending_mode_batch = gr.Checkbox(label="Enable Blending Mode", value=False)
                            zip_interval = gr.Slider(label="ZIP Interval", minimum=1, maximum=100, step=1, value=10)

                            artist_category_batch = gr.Dropdown(list(artists.keys()), label="Select Artist Category", interactive=True)
                            artist_dropdown_batch = gr.Dropdown([], label="Select Artists", multiselect=True, interactive=True)
                            modifier_category_batch = gr.Dropdown(list(modifiers.keys()), label="Select Modifier Category", interactive=True)
                            modifier_dropdown_batch = gr.Dropdown([], label="Select Modifiers", multiselect=True, interactive=True)

                            process_batch_btn = gr.Button("Start Batch Processing")

                            artist_category_batch.change(fn=update_artist_dropdown, inputs=artist_category_batch, outputs=artist_dropdown_batch)
                            modifier_category_batch.change(fn=update_modifier_dropdown, inputs=modifier_category_batch, outputs=modifier_dropdown_batch)
                            randomize_denoise_batch.change(fn=show_denoise_sliders, inputs=randomize_denoise_batch, outputs=[denoise_value_batch, denoise_min_batch, denoise_max_batch])

                        with gr.Column():
                            output_batch = gr.Gallery(label="Transformed Images")
                            debug_output_batch = gr.Textbox(label="Debug Logs", interactive=True)
                            terminal_output_batch = gr.Textbox(label="Terminal Output", interactive=True)

                    process_batch_btn.click(
                        fn=process_batch_images,
                        inputs=[user_id_batch, style_images, structure_images, custom_text_batch, artist_dropdown_batch, modifier_dropdown_batch, negative_prompt_batch, denoise_value_batch, denoise_min_batch, denoise_max_batch, depth_processor_batch, depth_strength_batch, ksampler_steps_batch, randomize_batch, use_tilenet_batch, model_name_batch, randomize_denoise_batch, randomize_depth_processor_batch, blending_mode_batch, zip_interval],
                        outputs=[output_batch, debug_output_batch, terminal_output_batch]
                    )

                with gr.Tab("Gallery"):
                    user_id_gallery = gr.Textbox(label="Username", value=username_global, interactive=False)
                    user_gallery = gr.Gallery(label="User Gallery")
                    refresh_gallery_btn = gr.Button("Refresh Gallery")

                    def refresh_gallery(user_id):
                        return load_user_gallery(user_id)

                    refresh_gallery_btn.click(fn=refresh_gallery, inputs=user_id_gallery, outputs=user_gallery)

    demo.launch(share=True)

if __name__ == "__main__":
    main()