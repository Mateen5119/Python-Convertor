# 🗺️ FileConverter — Complete Build Roadmap
> A browser-based, privacy-first, standalone file conversion tool built with Python + HTML/CSS/JS

---

## 🧠 Architecture Philosophy (Read This First)

Before a single line of code, understand the two golden rules this project is built on:

1. **Client-First**: If the browser can do it natively (images, canvas, FileReader API), it WILL do it — zero server touch.
2. **Zero-Persistence Server**: For conversions that MUST hit the server (DOCX→PDF, PDF→DOCX etc.), the file lifecycle is: `receive → convert → return → wipe`. The server holds nothing.

This splits conversions into two lanes:

| Lane | Who Does It | Examples |
|---|---|---|
| **Browser Lane** | JavaScript + Canvas/FileReader API | PNG↔JPG, PNG↔WEBP, BMP→JPG, image resizing |
| **Server Lane** | Python (Flask) + bundled libs | DOCX→PDF, PDF→DOCX, CSV↔XLSX, PDF→PPTX, PDF→Images |

---

## 📦 Full Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Backend | Python + Flask (lightweight) | Minimal, easy to bundle |
| Document Conversion | LibreOffice Portable (bundled) | Best DOCX/XLSX/PPTX→PDF quality, free |
| PDF Tools | PyMuPDF (fitz) | Fast, accurate, pure Python wheel |
| PDF→DOCX | pdf2docx | Best free option for text-heavy PDFs |
| PDF→PPTX | PyMuPDF + python-pptx | Page-as-image approach |
| Spreadsheets | pandas + openpyxl | CSV↔XLSX, perfect accuracy |
| Image (server fallback) | Pillow | Reliable, well-maintained |
| Frontend | Vanilla HTML + CSS + JS | Zero framework overhead |
| Packaging | PyInstaller | Creates `.exe` / binary with everything inside |
| Security | Python `secrets`, `tempfile`, `shutil` | Secure temp dirs, no predictable paths |

---

## 🏗️ Phase 1 — Project Skeleton

**Goal**: Set up the folder structure and virtual environment before writing a single line of logic.

### Steps:

1. Create the root project folder: `fileconverter/`

2. Inside it, create this structure:
   ```
   fileconverter/
   ├── app.py                  ← Flask entry point
   ├── converters/             ← One Python file per conversion type
   │   ├── __init__.py
   │   ├── images.py
   │   ├── documents.py
   │   ├── spreadsheets.py
   │   └── pdf_tools.py
   ├── static/
   │   ├── index.html          ← The entire UI lives here
   │   ├── style.css
   │   └── app.js
   ├── libreoffice_portable/   ← Bundled LibreOffice (added in Phase 4)
   ├── requirements.txt
   └── build_spec.spec         ← PyInstaller config (added in Phase 8)
   ```

3. Create a Python virtual environment:
   ```
   python -m venv venv
   ```

4. Activate it (Windows: `venv\Scripts\activate` / Mac/Linux: `source venv/bin/activate`)

5. Create `requirements.txt` with these libraries:
   ```
   flask
   pillow
   pymupdf
   pdf2docx
   python-pptx
   pandas
   openpyxl
   ```

6. Run `pip install -r requirements.txt`

---

## 🐍 Phase 2 — Flask Backend Core

**Goal**: A minimal Flask server that opens the browser UI, receives files, routes them to the right converter, and sends back the result.

### Steps:

1. In `app.py`, configure Flask to:
   - Serve `static/index.html` on the root route `/`
   - Expose a single POST endpoint: `/convert`
   - Set a **MAX FILE SIZE** limit (e.g., 50MB) using Flask's `MAX_CONTENT_LENGTH`
   - On startup, automatically open the browser to `http://localhost:5000`

2. The `/convert` endpoint logic must follow this exact lifecycle:
   ```
   Step A: Receive uploaded file + conversion_type parameter
   Step B: Validate file type against an allowed-types whitelist
   Step C: Create a UNIQUE, RANDOM temp directory using Python's secrets module
   Step D: Save the uploaded file there
   Step E: Call the correct converter module
   Step F: Read the output file into memory (as bytes)
   Step G: IMMEDIATELY delete the entire temp directory (input + output both gone)
   Step H: Stream the bytes back to the browser as a download
   ```
   
   **Critical**: Step G must happen inside a `finally:` block so the cleanup runs even if the conversion crashes.

3. Add a `/health` endpoint that returns `{"status": "ok"}` — the frontend will ping this to confirm the local server is running before showing the UI.

---

## 🔄 Phase 3 — Conversion Modules

Build each converter as an isolated module. Each function receives an input path and output path, does the work, and returns nothing (errors raise exceptions).

### 3A — Image Conversions (`converters/images.py`)

**Note**: Most image conversions are better done in the browser (Phase 5). This module is a **server-side fallback** only.

1. Use **Pillow** (`PIL.Image`) to handle:
   - PNG → JPG (handle transparency: flatten to white background before saving as JPG)
   - JPG → PNG
   - Any image format → WEBP
   - WEBP → JPG or PNG
   - BMP → any format
2. Important Pillow rule: Always call `.convert("RGB")` before saving as JPG to avoid crashes on RGBA/palette images.

### 3B — Document Conversions (`converters/documents.py`)

This module wraps LibreOffice Portable as a **subprocess call**. It does NOT import LibreOffice as a Python library — it calls it as a command-line program.

1. Write a helper function `get_libreoffice_path()` that:
   - Detects the OS (Windows / Mac / Linux)
   - Returns the correct path to the `soffice` or `soffice.exe` binary inside your bundled `libreoffice_portable/` folder
   
2. For **DOCX/XLSX/PPTX → PDF**, the LibreOffice command pattern is:
   ```
   soffice --headless --convert-to pdf --outdir OUTPUT_DIR INPUT_FILE
   ```
   Run this using Python's `subprocess.run()` with a timeout.

3. For **PPTX → PDF**, same command — LibreOffice handles all Office formats.

4. Always capture `stdout` and `stderr` from the subprocess to log any errors.

### 3C — PDF Tools (`converters/pdf_tools.py`)

1. **PDF → DOCX**: Use `pdf2docx`. Call `Converter(pdf_path)` → `.convert(docx_path)` → `.close()`. Works best on text-heavy, single-column PDFs.

2. **PDF → Images (PNG/JPG)**: Use `PyMuPDF (fitz)`:
   - Open the PDF with `fitz.open()`
   - Loop through each page
   - Render each page as a `Pixmap` at 2x zoom (150-200 DPI is fine for screen)
   - Save each page as a numbered PNG/JPG
   - If the output is multiple images, zip them together before returning

3. **PDF → PPTX**: This is a "page-as-image" approach — not editable text output:
   - Use `fitz` to render each PDF page as a PNG image (same as step 2)
   - Use `python-pptx` to create a new presentation
   - Set slide dimensions to match PDF page size (use A4 or Letter as default)
   - For each page image, add a blank slide and place the image to fill the full slide
   - Save as `.pptx`

### 3D — Spreadsheet Conversions (`converters/spreadsheets.py`)

1. **CSV → XLSX**: Use `pandas`:
   - `pd.read_csv(input_path)` → `df.to_excel(output_path, index=False)`
   - Use `openpyxl` as the engine

2. **XLSX → CSV**: 
   - `pd.read_excel(input_path)` → `df.to_csv(output_path, index=False)`
   - Handle multi-sheet workbooks: either convert only the first sheet (simple) or loop and produce a zip of multiple CSVs (advanced)

---

## 📦 Phase 4 — Bundle LibreOffice (The Critical Step)

**Goal**: Ship LibreOffice inside your app so users never install anything.

### Steps:

1. Download **LibreOffice Portable** (not the installer version):
   - Windows: Download from `portableapps.com` — LibreOfficePortable
   - Mac: The standard `.app` bundle works; copy its `Contents/MacOS/` folder
   - Linux: Download the `.tar.gz` archive from libreoffice.org, extract it

2. You only need a subset of LibreOffice's files. To minimize size, keep only:
   - The `program/` folder (contains `soffice.exe` / `soffice`)
   - The `share/` folder (filters, fonts, config)
   - Remove: help files, Gallery, templates, extensions you don't need
   - This can reduce size from ~800MB to ~200-250MB

3. Place the stripped folder at `fileconverter/libreoffice_portable/`

4. In `get_libreoffice_path()` (from Phase 3B), if the app is packaged with PyInstaller, use `sys._MEIPASS` to locate the bundled path. If running as a raw Python script, use a path relative to `app.py`.

5. Test by running a DOCX→PDF conversion manually through your documents.py function before moving on.

---

## 🌐 Phase 5 — Browser Frontend

**Goal**: A clean drag-and-drop UI that handles image conversions entirely in JS and sends document conversions to the local Flask server.

### 5A — HTML Structure (`static/index.html`)

Build one single-page app with these sections:
1. **Drop Zone**: A large `<div>` with a dashed border that accepts file drag-and-drop
2. **File Input Button**: Standard `<input type="file">` as fallback for drag-and-drop
3. **Format Selector**: A `<select>` dropdown showing available target formats (dynamically populated based on what file is dropped)
4. **Convert Button**
5. **Progress Indicator**: A simple animated bar or spinner (shown during conversion)
6. **Status Message**: Shows "Converting…", "Done! Downloading…", or error messages

### 5B — JavaScript Logic (`static/app.js`)

Structure your JS with this decision tree:

```
User drops/selects a file
        ↓
Detect source format (from file.type or file.name extension)
        ↓
Populate the "Convert To" dropdown with valid options
        ↓
User clicks Convert
        ↓
Is this a BROWSER-LANE conversion? (image ↔ image)
  YES → Handle entirely in JS (no server call)
  NO  → Check /health endpoint first → POST to /convert
```

**Browser-side image conversion using Canvas API:**
- Use `FileReader.readAsDataURL()` to read the image
- Draw it on an invisible `<canvas>` element
- Use `canvas.toBlob(callback, 'image/jpeg', quality)` or `'image/png'` to export
- Create a temporary `<a>` tag with `download` attribute and `.click()` it to trigger download
- No server involved. No file ever leaves the user's machine.

**For server-lane conversions:**
- Create a `FormData` object with the file + `conversion_type`
- Use `fetch('/convert', { method: 'POST', body: formData })`
- On response, convert it to a `Blob`, create a download URL, trigger download
- Show the progress indicator during the fetch

### 5C — Format Routing Map

In your JS, define a mapping object that tells the UI which target formats are valid for each source type:

```
PNG  → [JPG, WEBP]           (browser-side)
JPG  → [PNG, WEBP]           (browser-side)
WEBP → [JPG, PNG]            (browser-side)
BMP  → [JPG, PNG]            (browser-side)
DOCX → [PDF]                 (server-side)
PPTX → [PDF]                 (server-side)
XLSX → [PDF, CSV]            (server-side)
PDF  → [DOCX, PNG, JPG, PPTX](server-side)
CSV  → [XLSX]                (server-side)
```

---

## 🔒 Phase 6 — Security Layer

**Goal**: Prevent abuse, protect user privacy, and ensure no file lingers on the server.

### Steps:

1. **Temp Directory Isolation**: Every upload gets its own unique random directory:
   - Use `tempfile.mkdtemp()` combined with a `secrets.token_hex(16)` prefix
   - Never use predictable paths like `/tmp/upload_1/`, `/tmp/upload_2/`

2. **Always-Delete Guarantee**: Wrap every conversion in a `try/finally` block:
   ```
   try:
       save file → convert → read output into memory
   finally:
       shutil.rmtree(temp_dir, ignore_errors=True)
   ```
   Output is in memory (bytes) before the disk is wiped. The response streams from memory.

3. **File Type Whitelist**: Before saving any uploaded file, check BOTH:
   - The file's MIME type (from the request headers)
   - The actual file extension
   - Cross-check them: a `.jpg` file that has a PDF MIME type should be rejected
   - Maintain a hardcoded `ALLOWED_CONVERSIONS` dictionary — nothing outside it is processed

4. **Magic Byte Validation**: The gold standard. Check the first few bytes of the file against known signatures:
   - PNG files start with `\x89PNG`
   - PDF files start with `%PDF`
   - ZIP-based formats (DOCX, XLSX, PPTX) start with `PK\x03\x04`
   - Use Python's `imghdr` module or a small manual check for this

5. **File Size Limit**: Set `app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024` (50MB). Flask will automatically reject larger files with a 413 error.

6. **No Logging of File Content**: Configure Flask's logger to NEVER log file names, sizes, or conversion types. Log only server errors (500-level).

7. **CORS Lockdown**: Restrict the Flask server to only accept requests from `localhost`. Reject any request with an `Origin` header that isn't `http://localhost:5000`. This prevents other websites from silently using your tool when it's running.

8. **Conversion Timeout**: Add a timeout to the LibreOffice subprocess call (e.g., 60 seconds). If it hangs, kill the process and clean up. This prevents a malformed file from freezing the server.

9. **Rate Limiting (Optional but Recommended for Web Deployment)**: If you ever deploy this as a public web service (not local), add `Flask-Limiter` to cap requests per IP per minute.

---

## 📁 Phase 7 — File Lifecycle Summary

This is the full lifecycle of a server-lane file. Document it clearly in your code as a comment block:

```
[1] ARRIVE    → File bytes received in Flask request (in RAM only so far)
[2] VALIDATE  → MIME type + extension + magic bytes checked against whitelist
[3] ISOLATE   → Written to a unique, randomly-named temp directory
[4] CONVERT   → Converter module processes it, output written to same temp dir
[5] RETRIEVE  → Output file read into Python bytes object (now in RAM)
[6] WIPE      → Entire temp directory deleted (shutil.rmtree) — input + output gone
[7] RESPOND   → Bytes sent back to browser as a file download response
```

Steps 5 and 6 must happen in this exact order. The bytes are in RAM, disk is clean, then the response is sent.

---

## 📦 Phase 8 — Standalone Packaging with PyInstaller

**Goal**: Package everything — Python, Flask, all libraries, AND LibreOffice — into a single folder or executable.

### Steps:

1. Install PyInstaller: `pip install pyinstaller`

2. Create a `.spec` file (PyInstaller config) — this is better than using command-line flags for complex projects.

3. In the spec file, configure:
   - `datas`: Include your `static/` folder and `libreoffice_portable/` folder in the package
   - `hiddenimports`: Manually add `fitz`, `pdf2docx`, `pptx`, `pandas`, `openpyxl` if PyInstaller misses them
   - `onedir` mode (not `onefile`) — creates a folder, not a single `.exe`. Much faster startup because LibreOffice is large.

4. Use `sys._MEIPASS` in your code to detect when running as a PyInstaller bundle and adjust all paths accordingly. Example:
   ```
   Base path when packaged:  sys._MEIPASS/
   Base path when scripting: os path of app.py
   ```

5. Build for each platform separately:
   - **Windows**: Run PyInstaller on Windows → produces `dist/fileconverter/` folder with `fileconverter.exe`
   - **Mac**: Run on Mac → produces `dist/fileconverter.app` or folder
   - **Linux**: Run on Linux → produces `dist/fileconverter/` folder with a binary

6. Test the packaged version by running from the `dist/` folder — NOT from the source. Many path issues only appear in packaged form.

7. Create a simple launcher:
   - Windows: A `.bat` file or the `.exe` directly
   - Mac/Linux: A shell script that runs `./fileconverter/fileconverter`
   - The launcher should open the browser to `http://localhost:5000` if the Python script doesn't do it automatically

---

## 🌍 Phase 9 — (Optional) Web Deployment Mode

If you also want to deploy this as a public website (not just local tool):

1. Add an environment variable flag: `DEPLOYMENT_MODE=web` vs `DEPLOYMENT_MODE=local`

2. In `web` mode:
   - Enforce stricter file size limits (10MB instead of 50MB)
   - Add `Flask-Limiter` rate limiting per IP
   - Use proper WSGI server (`gunicorn`) instead of Flask's dev server
   - Store temp files in `/tmp` on the server with guaranteed cleanup via `finally` block
   - Consider using `tmpfs` (RAM disk) on Linux for temp storage — files never touch persistent disk at all

3. In `local` mode:
   - Bind only to `127.0.0.1` (not `0.0.0.0`) — not reachable from other machines on the network
   - Allow larger file sizes
   - Use dev server (fine for local use)

4. For deployment, a cheap VPS (1GB RAM, 1 vCPU) is sufficient since:
   - You're not storing anything
   - LibreOffice conversions are CPU-heavy but brief
   - Stateless architecture — scales horizontally easily

---

## ✅ Phase 10 — Testing Checklist

Before calling it done, test every conversion path:

| Conversion | Test File | Expected Behavior |
|---|---|---|
| PNG → JPG | Image with transparency | White background, no alpha crash |
| JPG → PNG | Standard photo | Lossless output |
| WEBP → JPG | Modern format file | Correct colors |
| DOCX → PDF | Document with tables, images | Layout preserved |
| PPTX → PDF | Multi-slide deck | All slides included |
| XLSX → PDF | Spreadsheet with formulas | Values (not formulas) shown |
| PDF → DOCX | Simple text PDF | Editable text output |
| PDF → PNG | Multi-page PDF | One PNG per page, zipped |
| PDF → PPTX | Multi-page PDF | Each page as a slide |
| CSV → XLSX | Data with commas in fields | Columns correct |
| XLSX → CSV | Multi-sheet workbook | First sheet exported |
| Security | Upload an `.exe` renamed as `.pdf` | Rejected by magic bytes check |
| Security | Upload a 200MB file | Rejected with 413 error |
| Cleanup | Check temp folder during/after conversion | Folder appears briefly, then gone |

---

## 📐 Conversion Coverage Map

Based on your reference file, here is what each phase delivers:

| Conversion | Library | Quality | Lane |
|---|---|---|---|
| PNG/JPG/WEBP/BMP ↔ JPG/PNG/WEBP | Pillow (server) / Canvas API (browser) | Perfect | Browser-first |
| DOCX → PDF | LibreOffice (bundled) | High | Server |
| PPTX → PDF | LibreOffice (bundled) | High | Server |
| XLSX → PDF | LibreOffice (bundled) | High | Server |
| PDF → DOCX | pdf2docx | Good | Server |
| PDF → PNG/JPG | PyMuPDF | Perfect | Server |
| PDF → PPTX | PyMuPDF + python-pptx | Medium | Server |
| CSV → XLSX | pandas | Perfect | Server |
| XLSX → CSV | pandas | Perfect | Server |

---

## 🗂️ Final Deliverable Checklist

- [ ] Working Flask server with `/convert` and `/health` endpoints
- [ ] All 5 converter modules complete and tested individually
- [ ] LibreOffice Portable stripped and placed in `libreoffice_portable/`
- [ ] Browser UI with drag-and-drop, format selector, progress indicator
- [ ] Browser-side image conversion (no server call for PNG↔JPG↔WEBP)
- [ ] Security: magic bytes validation, whitelist, file size cap, no logging, CORS lock
- [ ] Guaranteed cleanup in `finally` blocks for every server-side conversion
- [ ] PyInstaller spec file configured with all `datas` entries
- [ ] Tested as a packaged binary on target OS
- [ ] All test cases in Phase 10 pass

---

*Total estimated lines of Python code: ~400–600 (excluding LibreOffice)*
*Total estimated lines of HTML/CSS/JS: ~300–500*
*Final packaged size: ~200–280MB (LibreOffice dominates)*