# utilities.py

import os
import json
import random
import requests
import time
import zipfile
import shutil
from PIL import Image
from config import API_KEYS, headers

def read_workflow(file_path):
    """Read the workflow.json file."""
    print(f"Reading workflow from {file_path}")
    with open(file_path, 'r') as file:
        workflow = json.load(file)
    return workflow

def update_workflow(workflow, style_image_path, structure_image_path, prompt, negative_prompt, denoise_value, depth_processor, depth_strength, ksampler_steps, use_tilenet, model_name):
    """Update the workflow with the new images, prompts, and denoising value."""
    print(f"Updating workflow with style image: {style_image_path}, structure image: {structure_image_path}, prompt: {prompt}, and denoise value: {denoise_value}")
    
    for node_key, node in workflow.items():
        if isinstance(node, dict) and 'inputs' in node:
            if node.get('_meta', {}).get('title') == 'Load Style':
                node['inputs']['image'] = style_image_path
            elif node.get('_meta', {}).get('title') == 'Load Structure':
                node['inputs']['image'] = structure_image_path
            elif node.get('_meta', {}).get('title') == 'CLIP Text Encode (Prompt)':
                node['inputs']['text'] = prompt
                print(f"Updated prompt in node {node_key}: {node['inputs']['text']}")
            elif node.get('_meta', {}).get('title') == 'CLIP Text Encode (Negative)':
                node['inputs']['text'] = negative_prompt if negative_prompt else "bad quality, blurry, ugly"
                print(f"Updated negative prompt in node {node_key}: {node['inputs']['text']}")
            elif node.get('_meta', {}).get('title') == 'Load Checkpoint':
                node['inputs']['ckpt_name'] = model_name
                print(f"Updated model path in node {node_key}: {node['inputs']['ckpt_name']}")
            elif node.get('_meta', {}).get('title') == 'KSampler':
                node['inputs']['denoise'] = denoise_value  # Set the denoising value
                node['inputs']['steps'] = ksampler_steps  # Set the steps for KSampler
                print(f"Updated denoise value in node {node_key}: {node['inputs']['denoise']}")
                print(f"Updated KSampler steps in node {node_key}: {node['inputs']['steps']}")
            elif node.get('_meta', {}).get('title') == 'AIO Aux Preprocessor':
                node['inputs']['preprocessor'] = depth_processor  # Set the depth map preprocessor
                node['inputs']['strength'] = depth_strength  # Set the depth map strength
                print(f"Updated depth map preprocessor in node {node_key}: {node['inputs']['preprocessor']}")
                print(f"Updated depth map strength in node {node_key}: {node['inputs']['strength']}")
            elif node.get('_meta', {}).get('title') == 'AIO Tile':
                node['inputs']['preprocessor'] = "TilePreprocessor"  # Always set to TilePreprocessor
                node['inputs']['strength'] = depth_strength  # Set the depth map strength for Tile
                print(f"Updated Tile depth map preprocessor in node {node_key}: {node['inputs']['preprocessor']}")
                print(f"Updated Tile depth map strength in node {node_key}: {node['inputs']['strength']}")
            elif node.get('_meta', {}).get('title') == 'Tile Control Net':
                node['inputs']['enabled'] = use_tilenet  # Enable or disable the tile control net
                print(f"Updated Tile Control Net in node {node_key} to {'enabled' if use_tilenet else 'disabled'}")
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

    retries = 3
    for attempt in range(retries):
        for key in API_KEYS:
            headers["Authorization"] = f"Bearer {key}"
            response = requests.post(API_URL, headers=headers, data=data)
            try:
                response_json = response.json()
                generated_text = response_json[0]["generated_text"]
                print(f"Generated text: {generated_text}")
                return generated_text
            except (requests.exceptions.JSONDecodeError, IndexError, KeyError) as e:
                print(f"Attempt {attempt + 1} failed with key {key}: {e}")
    return "Image identification failed"

def generate_prompt(input_text, selected_artists, selected_modifiers, custom_text, retries=5):
    if input_text.startswith("Error"):
        return generate_fallback_prompt(selected_artists, selected_modifiers, custom_text)

    falcon_7b = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    API_URL = falcon_7b

    for attempt in range(retries):
        prompt = f"Create a unique, highly detailed, and imaginative AI art prompt based on the context of the photo: {input_text}. Focus on landscapes and scenery, avoiding descriptions of humans or animals. Ensure the description is vivid, compelling, and evokes strong visual imagery."
        if custom_text:
            prompt += f" Theme: {custom_text}."

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "do_sample": True,
                "top_k": 10,
                "temperature": 1,
                "return_full_text": False,
            },
            "options": {
                "wait_for_model": True
            }
        }

        for key in API_KEYS:
            headers["Authorization"] = f"Bearer {key}"
            response = requests.post(API_URL, headers=headers, json=payload)
            try:
                response_json = response.json()
                generated_text = response_json[0]["generated_text"]
                if "As the AI language model" not in generated_text and "I am unable to render visual data" not in generated_text:
                    print(f"Generated prompt: {generated_text}")

                    artist_list = ', '.join(random.sample(selected_artists, min(2, len(selected_artists))))
                    modifier_list = ', '.join(random.sample(selected_modifiers, min(4, len(selected_modifiers))))
                    generated_text += f" Style inspired by {artist_list}. Modifiers: {modifier_list}."

                    return generated_text
            except (requests.exceptions.JSONDecodeError, IndexError, KeyError) as e:
                print(f"Attempt {attempt + 1} failed with key {key}: {e}")

    return generate_fallback_prompt(selected_artists, selected_modifiers, custom_text)

def generate_fallback_prompt(selected_artists, selected_modifiers, custom_text):
    fallback_prompt = "Create a unique, highly detailed, and imaginative landscape prompt."
    if custom_text:
        fallback_prompt += f" Theme: {custom_text}."
    if selected_artists:
        artist_list = ', '.join(random.sample(selected_artists, min(2, len(selected_artists))))
        fallback_prompt += f" Style inspired by {artist_list}."
    if selected_modifiers:
        modifier_list = ', '.join(random.sample(selected_modifiers, min(4, len(selected_modifiers))))
        fallback_prompt += f" Modifiers: {modifier_list}."
    print(f"Fallback prompt: {fallback_prompt}")
    return fallback_prompt

def send_workflow_to_comfyui(workflow, port):
    url = f"http://127.0.0.1:{port}/prompt"
    headers = {"Content-Type": "application/json"}
    print(f"Sending workflow to ComfyUI at {url}")
    response = requests.post(url, headers=headers, json=workflow)
    response.raise_for_status()

def get_predefined_style_image(style_name, category):
    for style in predefined_styles[category]:
        if style["name"] == style_name:
            return style["image"]
    return None

def get_latest_image(folder):
    files = os.listdir(folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
    latest_image = os.path.join(folder, image_files[-1]) if image_files else None
    return latest_image

def monitor_output_images(output_dir, previous_images):
    new_images = []
    while True:
        files = os.listdir(output_dir)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        new_image_files = [f for f in image_files if f not in previous_images]
        if new_image_files:
            new_images = [os.path.join(output_dir, f) for f in new_image_files]
            break
        time.sleep(1)
    return new_images

def zip_images(image_paths, index, user_folder):
    zip_filename = os.path.join(user_folder, f"output_images_{index}.zip")
    counter = 1
    while os.path.exists(zip_filename):
        counter += 1
        zip_filename = os.path.join(user_folder, f"output_images_{index}_{counter}.zip")
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for img_path in image_paths:
            zipf.write(img_path, os.path.basename(img_path))
    return zip_filename

def blend_images(image_path1, image_path2, blend_ratio=0.4):
    image1 = Image.open(image_path1).convert("RGBA")
    image2 = Image.open(image_path2).convert("RGBA")
    blended_image = Image.blend(image1, image2, blend_ratio)
    return blended_image
