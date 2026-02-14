#!/usr/bin/env python3
"""
Upload to Cloudinary - Uploads videos and assets to cloud storage
"""
import os
import json
import argparse
from pathlib import Path
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

def configure_cloudinary():
    """Configure Cloudinary SDK"""
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

def upload_to_cloud(run_id, files_dir):
    """Upload files to Cloudinary"""
    
    print("☁️ Uploading files to Cloudinary...")
    
    configure_cloudinary()
    
    files_dir = Path(files_dir)
    
    uploaded_files = {}
    
    # Files to upload
    files_to_upload = {
        'long_video': 'long_video.mp4',
        'short_video': 'short_video.mp4',
        'thumbnail': 'thumbnail.jpg',
        'script': 'script.json',
        'hook': 'hook.json',
        'cta': 'cta.json'
    }
    
    for key, filename in files_to_upload.items():
        file_path = files_dir / filename
        
        if file_path.exists():
            print(f"⬆️ Uploading {filename}...")
            
            try:
                # Upload with metadata
                result = cloudinary.uploader.upload(
                    str(file_path),
                    public_id=f"yt_autopilot/{run_id}/{key}",
                    resource_type='auto',
                    context=f"run_id={run_id}|type={key}"
                )
                
                uploaded_files[key] = {
                    'url': result.get('secure_url'),
                    'public_id': result.get('public_id'),
                    'bytes': result.get('bytes')
                }
                
                print(f"✅ Uploaded: {result.get('secure_url')}")
                
            except Exception as e:
                print(f"❌ Upload failed for {filename}: {e}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    # Save upload manifest
    manifest = {
        'run_id': run_id,
        'uploaded_at': str(Path().stat().st_mtime),
        'files': uploaded_files
    }
    
    manifest_file = files_dir / 'upload_manifest.json'
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Upload complete: {len(uploaded_files)} files")
    
    # Print URLs for webhook
    if 'long_video' in uploaded_files:
        print(f"\n📹 Long Video URL: {uploaded_files['long_video']['url']}")
    if 'short_video' in uploaded_files:
        print(f"📱 Short Video URL: {uploaded_files['short_video']['url']}")
    if 'thumbnail' in uploaded_files:
        print(f"🎨 Thumbnail URL: {uploaded_files['thumbnail']['url']}")
    
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--files-dir', required=True)
    args = parser.parse_args()
    
    upload_to_cloud(args.run_id, args.files_dir)

if __name__ == '__main__':
    main()
