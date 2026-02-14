#!/usr/bin/env python3
"""
Thumbnail Generation - Uses Stability AI to generate video thumbnails
"""
import os
import json
import argparse
import requests
from pathlib import Path
import base64

STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

def generate_thumbnail(script_file, run_id):
    """Generate thumbnail using Stability AI"""
    
    print("🎨 Generating thumbnail with Stability AI...")
    
    # Load script
    with open(script_file, 'r', encoding='utf-8') as f:
        script_data = json.load(f)
    
    # Get thumbnail prompt
    prompt = script_data.get('metadata', {}).get('stability_ai_prompt', '')
    
    if not prompt:
        # Fallback prompt
        title = script_data.get('metadata', {}).get('final_title', '')
        prompt = f"YouTube thumbnail, dramatic lighting, Indian person with shocked expression, bold text overlay, high contrast, cinematic, 4k, professional photography style, {title}"
    
    # Enhance prompt for better results
    enhanced_prompt = f"{prompt}, youtube thumbnail style, high contrast, dramatic lighting, eye-catching, vibrant colors, professional photography, 4k quality, centered composition"
    
    negative_prompt = "blurry, low quality, distorted face, multiple faces, text in image, watermark, logo, cropped, out of frame"
    
    try:
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "application/json"
        }
        
        files = {
            'prompt': (None, enhanced_prompt),
            'negative_prompt': (None, negative_prompt),
            'aspect_ratio': (None, '16:9'),
            'mode': (None, 'text-to-image'),
            'model': (None, 'sd3.5-large'),
            'output_format': (None, 'jpeg')
        }
        
        print(f"🎨 Sending request to Stability AI...")
        
        response = requests.post(
            STABILITY_API_URL,
            headers=headers,
            files=files
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Save image
        output_dir = Path('output')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if base64 image is in response
        if 'image' in data:
            image_data = base64.b64decode(data['image'])
            output_file = output_dir / 'thumbnail.jpg'
            
            with open(output_file, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ Thumbnail generated: {output_file}")
            return output_file
        elif 'images' in data and len(data['images']) > 0:
            image_data = base64.b64decode(data['images'][0])
            output_file = output_dir / 'thumbnail.jpg'
            
            with open(output_file, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ Thumbnail generated: {output_file}")
            return output_file
        else:
            print(f"⚠️ Unexpected response format: {data.keys()}")
            return None
            
    except Exception as e:
        print(f"⚠️ Thumbnail generation failed: {e}")
        # Create a placeholder or fallback
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--script-file', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    
    generate_thumbnail(args.script_file, args.run_id)

if __name__ == '__main__':
    main()
