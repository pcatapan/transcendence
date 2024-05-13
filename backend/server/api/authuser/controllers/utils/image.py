import os
import magic
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from urllib import request as urllib_request

def is_valid_image(avatar):
    # Check MIME type
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(avatar.read(1024))
    if not mime_type.startswith('image'):
        return False, 'Invalid file format. Please upload a valid image.'

    # Check file extension
    if not avatar.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        return False, 'Invalid file extension. Please upload a valid image.'
    
    # Check file size
    if avatar.size > 10 * 1024 * 1024:  # 10 MB
        return False, 'File size exceeds the limit. Please upload a smaller image.'

    return True, None

def get_unique_filename(filename):
    base_name, extension = os.path.splitext(filename)
    count = 1
    while default_storage.exists(os.path.join('avatars', f'{base_name}_{count}{extension}')):
        count += 1
    return f'{base_name}_{count}{extension}'

def save_avatar_from_url(url):
    # Download and validate image from URL
    with urllib_request.urlopen(url) as response:
        image_data = response.read()
        content_type = response.getheader('Content-Type').lower()
        if 'image' not in content_type:
            return None, 'Invalid content type. Please provide a valid image URL.'

        filename = slugify(os.path.basename(url))
        unique_filename = get_unique_filename(filename)
        default_storage.save(os.path.join('avatars', unique_filename), ContentFile(image_data))
        return unique_filename, None

