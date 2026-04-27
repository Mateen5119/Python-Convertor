import os
import subprocess
import sys

def get_libreoffice_path():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    lo_path = os.path.join(base_path, 'libreoffice_portable', 'App', 'libreoffice', 'program', 'soffice.exe')
    
    # Check alternative portableapps path structure
    if not os.path.exists(lo_path):
        lo_path = os.path.join(base_path, 'libreoffice_portable', 'program', 'soffice.exe')
    
    return lo_path

def convert(input_path, target_format, temp_dir):
    if target_format.lower() != 'pdf':
        raise NotImplementedError("Only PDF target is supported for documents right now.")
        
    soffice = get_libreoffice_path()
    if not os.path.exists(soffice):
        raise FileNotFoundError(f"LibreOffice not found at {soffice}. Make sure Phase 4 is completed.")
        
    cmd = [
        soffice,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', temp_dir,
        input_path
    ]
    
    # Run libreoffice conversion
    subprocess.run(cmd, check=True, timeout=120)
    
    filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"{filename_without_ext}.pdf"
    output_path = os.path.join(temp_dir, output_filename)
    
    if not os.path.exists(output_path):
        raise FileNotFoundError("Conversion failed: LibreOffice did not create the output file.")
        
    return output_path
