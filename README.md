Ran command: `git pull origin main`
Listed directory fileconverter
Listed directory converters
Viewed app.py:1-112
Viewed spreadsheets.py:1-21
Viewed images.py:1-16
Viewed pdf_tools.py:1-71
Viewed documents.py:1-42

# File Converter Pro

File Converter Pro is a robust, production-ready desktop application designed to streamline all your document, image, and spreadsheet conversion needs. Built with an intuitive web-based interface and packaged as a standalone Windows installer, it allows anyone to securely convert files locally without uploading sensitive data to the cloud.

## ✨ Key Features

- **Standalone Windows Execution:** Packaged into a standalone executable, requiring absolutely zero Python environment setup for end-users.
- **Chunked Streaming for Memory Optimization:** Engineered to handle incredibly large files without crashing or hogging system memory.
- **Strict Input Sanitization & Secure File Handling:** Utilizes unique, randomized temporary directories for each conversion task and immediately destroys data post-conversion to ensure absolute privacy.
- **Intelligent Format Detection:** Seamlessly decouples input formats from target formats, routing files to the exact right conversion engine behind the scenes.
  
## ⚠️ CRITICAL SETUP STEP: LibreOffice Extraction
Because of GitHub's strict file size limits, the heavy LibreOffice dependency required for Word-to-PDF conversions has been split into multi-part `.rar` archives. 

**The program will crash on Word-to-PDF conversions if you do not complete this step first:**

1. Navigate to the `fileconverter/libreoffice_portable/` directory.
2. Ensure you have an extraction tool like [WinRAR](https://www.rarlab.com/download.htm) or [7-Zip](https://www.7-zip.org/) installed on your computer.
3. Locate the first part of the archive (it will end in `.part01.rar` or `.part1.rar`).
4. Right-click that specific file and select **"Extract Here"**.
5. The software will automatically read all the other `.rar` parts in the folder and seamlessly stitch together the massive LibreOffice file required by the backend.

*(Note: You only need to extract the first part; the extractor handles the rest automatically).*

## 🔀 Supported Conversions (The Matrix)

| Category | Input Format(s) | Output Format(s) | Special Notes |
| :--- | :--- | :--- | :--- |
| **Image** | `PNG`, `JPG`, `JPEG`, `WEBP`, `BMP` | `JPG`, `JPEG`, `PNG`, `WEBP`, `BMP` | Automatically converts to the RGB color space when saving as JPG to prevent format errors. |
| **Spreadsheet** | `CSV`, `XLSX` | `XLSX`, `CSV` | Fast and accurate tabular data conversion. |
| **PDF Tools** | `PDF` | `DOCX` | Converts PDF text and layouts into editable Word documents. |
| **PDF Tools** | `PDF` | `PNG`, `JPG` | Renders each PDF page as an image. Automatically zips multiple pages into a single archive. |
| **PDF Tools** | `PDF` | `PPTX` | Converts each PDF page into a 10x7.5 inch presentation slide while maintaining aspect ratio. |
| **Document** | `DOCX`, `PPTX`, `XLSX`, `CSV` | `PDF` | High-fidelity conversion to PDF utilizing LibreOffice headless mode. |

## 📥 Installation Guide

1. Navigate to the **Releases** tab of this repository.
2. Download the latest `FileConverter_Installer.exe`.
3. Run the installer and follow the standard on-screen prompts.
4. **Important Note:** LibreOffice must be installed on your host machine for Word/PDF and other document conversions to function properly.

## 💻 Usage

1. Launch the application from your Start Menu or Desktop shortcut.
2. The application will automatically spin up a local server and open a new tab in your default web browser (`http://localhost:5000`).
3. Upload your desired file using the clean web interface.
4. Select your desired target conversion format from the dropdown menu.
5. Click **Convert**. Your file is processed securely on your local machine and the result will download automatically.

## 🛠️ Built With

- **[Flask](https://flask.palletsprojects.com/)** - Backend framework handling API routes and secure file transport.
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** - High-performance PDF manipulation and rendering.
- **[Pandas](https://pandas.pydata.org/)** - Robust spreadsheet data parsing.
- **[Pillow](https://python-pillow.org/)** - Powerful image processing library.
- **[pdf2docx](https://pypi.org/project/pdf2docx/)** - Seamless PDF to editable Word document conversion.
- **[python-pptx](https://python-pptx.readthedocs.io/)** - Dynamic creation of presentation slides.
- **[PyInstaller](https://pyinstaller.org/)** - Bundling the Python application into a distributable executable.
- **[Inno Setup](https://jrsoftware.org/isinfo.php)** - Packaging the executable into a professional Windows installer.