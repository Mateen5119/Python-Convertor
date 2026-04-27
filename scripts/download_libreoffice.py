import os
import urllib.request
import re
import subprocess
import time
import sys

def download_and_install():
    print("Fetching LibreOffice Portable download page...")
    download_page_url = 'https://sourceforge.net/projects/portableapps/files/LibreOffice%20Portable/LibreOfficePortableLegacyWin7_25.2.7_MultilingualStandard.paf.exe/download'
    
    req = urllib.request.Request(download_page_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    
    match = re.search(r'url=(https://[^"]+)', html)
    if not match:
        print("Could not find direct download link.")
        return
        
    direct_link = match.group(1).replace('&amp;', '&')
    print(f"Downloading from direct link: {direct_link}")
    
    installer_path = "libreoffice_installer.paf.exe"
    
    req = urllib.request.Request(direct_link, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(installer_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
        
    print(f"Downloaded successfully. Size: {os.path.getsize(installer_path) / (1024*1024):.2f} MB")
    
    target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fileconverter', 'libreoffice_portable'))
    print(f"Installing silently to: {target_dir}")
    
    try:
        cmd = [os.path.abspath(installer_path), '/S', f'/D={target_dir}']
        print(f"Running: {' '.join(cmd)}")
        process = subprocess.Popen(cmd)
        process.wait()
        
        print("Waiting 15 seconds for extraction to complete...")
        time.sleep(15)
        print("Installation complete.")
        
    finally:
        if os.path.exists(installer_path):
            os.remove(installer_path)
            print("Cleaned up installer.")

if __name__ == '__main__':
    download_and_install()
