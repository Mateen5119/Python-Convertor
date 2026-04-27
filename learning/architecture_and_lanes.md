# FileConverter: Architecture and Lanes

FileConverter operates on a two-lane architecture designed to maximize privacy and efficiency.

## 1. The Browser Lane (Client-Side)
For image conversions (e.g., PNG to JPG, WEBP to PNG), the file **never leaves your computer**. 
The browser's built-in `Canvas API` and `FileReader` are used to:
1. Read the image into the browser's memory.
2. Draw the image onto an invisible HTML5 `<canvas>`.
3. Export the canvas data into the new format using `canvas.toBlob()`.

**Why?** It's instantaneous, uses zero server resources, and is 100% private.

## 2. The Server Lane (Backend)
For complex document formats like DOCX, XLSX, and PDF, browsers lack native conversion tools. These files are sent to the local Flask server.

The server uses:
- **LibreOffice Portable** for Office-to-PDF conversions.
- **PyMuPDF / pdf2docx** for PDF-to-Image/DOCX conversions.
- **Pandas** for spreadsheet conversions.

Even in the Server Lane, privacy is guaranteed by our strict Security Lifecycle.
