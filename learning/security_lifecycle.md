# FileConverter: Security Lifecycle

When a file enters the Server Lane for conversion, it undergoes a strict, ephemeral lifecycle to ensure that no data is permanently stored.

## The 7-Step Lifecycle

1. **Arrive**: File bytes are received by the Flask `/convert` endpoint (stored in RAM).
2. **Validate**: The application checks the file extension against a strict whitelist (e.g., `['docx', 'pdf', 'xlsx']`).
3. **Isolate**: A unique, randomized temporary directory is created using Python's cryptographic `secrets.token_hex()` combined with `tempfile.mkdtemp()`. This prevents path-traversal attacks and isolates simultaneous conversions.
4. **Convert**: The specific converter module (e.g., LibreOffice subprocess) processes the file inside the isolated directory.
5. **Retrieve**: The converted output file is read back into Python's memory as bytes.
6. **Wipe**: The entire temporary directory (containing both the original upload and the converted result) is **immediately deleted** using `shutil.rmtree()`.
7. **Respond**: The bytes held in memory are streamed back to the browser as a downloaded file.

> **Crucial Guarantee**: Steps 6 and 7 are enforced using a `try...finally` block. This means that even if the conversion crashes or fails halfway, the temporary directory is guaranteed to be securely wiped.
