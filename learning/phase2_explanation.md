# Phase 2 — Flask Backend Core

This document explains the changes made for Phase 2 of the Flask backend core.

## What was added in `fileconverter/app.py`

### 1. Flask app configuration
- Created a `Flask` app instance with `static_folder` pointing to `fileconverter/static`.
- Set `static_url_path=''` so the root route can serve static files directly.
- Configured `app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024` to limit uploads to 50MB.

### 2. Root route `/`
- Added a route handler for `/`.
- Returns `index.html` from the `static` folder using `app.send_static_file('index.html')`.
- This ensures the browser UI is served from the backend.

### 3. `POST /convert` endpoint
- Added a POST route at `/convert`.
- Validates that a file is included in `request.files`.
- Reads `converter_type` from `request.form`.
- Uses a dispatch table `CONVERTER_MODULES` to map converter types to module objects:
  - `image` → `converters.images`
  - `document` → `converters.documents`
  - `spreadsheet` → `converters.spreadsheets`
  - `pdf` → `converters.pdf_tools`
- If the converter type is missing or unsupported, returns a `400` error with a JSON message.
- Calls the selected module’s `convert(uploaded_file)` function.
- Returns a JSON response with `success: true` and the conversion result.
- Catches general exceptions and returns a `500` error if something goes wrong.

### 4. File size error handling
- Added a custom error handler for HTTP status `413`.
- Returns JSON with a clear message when an uploaded file exceeds 50MB.

### 5. Auto-open browser at startup
- Added `open_browser()` to launch `http://localhost:5000` in the default browser.
- Used `threading.Timer(1.0, open_browser).start()` in `start_browser()` so the browser opens shortly after the server starts.
- The app runs with `host='127.0.0.1'`, `port=5000`, `debug=False`, and `use_reloader=False`.

## What was added in converter stubs

Each converter module was created with a minimal `convert()` function that accepts the uploaded file and returns a placeholder JSON object. The current modules are:

- `fileconverter/converters/images.py`
- `fileconverter/converters/documents.py`
- `fileconverter/converters/spreadsheets.py`
- `fileconverter/converters/pdf_tools.py`

Each stub currently returns:
- `filename`: the name of the uploaded file
- `converter`: the converter type
- `message`: a note saying the conversion is not implemented yet

These stubs allow the backend to route requests correctly and return a valid response while actual conversion logic is still pending.

## Summary

The Phase 2 implementation provides a minimal working backend that:
- serves the browser UI,
- receives file uploads,
- routes uploads to the correct converter module,
- enforces a 50MB upload limit,
- and opens the app automatically in the browser on startup.

This is the core server foundation for later phases where actual file conversion logic will be implemented.
