from PIL import Image
import os

def convert(input_path, target_format, temp_dir):
    img = Image.open(input_path)
    # Important Pillow rule: Always call .convert("RGB") before saving as JPG
    if target_format.lower() in ['jpg', 'jpeg']:
        img = img.convert("RGB")
    
    filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"{filename_without_ext}.{target_format}"
    output_path = os.path.join(temp_dir, output_filename)
    
    img.save(output_path)
    return output_path
