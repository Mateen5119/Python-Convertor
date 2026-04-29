# Deploying the Flask File Converter Online

This guide explains how to deploy your Flask-based File Converter application to the internet for free. 

## 1. Deployment Strategy & Reality Check

Deploying a standard Flask web application is usually straightforward, but this application has specific "heavy" requirements:
*   **Heavy Python Libraries:** Packages like `pandas` and `PyMuPDF` (fitz) are large and require significant memory to process files.
*   **System-Level Dependencies:** Crucially, document conversion relies on **LibreOffice**, which is a massive system-level application, not just a Python package.

### Serverless vs. Containerized Environments
*   **Serverless (e.g., Vercel, AWS Lambda):** These platforms are designed for lightweight, fast-booting functions. They have strict limits on deployment size (often 250MB uncompressed), memory, and execution time (often 10-60 seconds). Furthermore, they offer a **read-only file system** (except for the `/tmp` directory) and you **cannot install system packages** like LibreOffice. 
*   **Containerized (e.g., Render, Railway, Fly.io):** These platforms run your app inside a Docker container. You have full control over the environment, meaning you can install LibreOffice, manage disk space, and run background tasks without severe execution time limits.

**Conclusion:** For the full functionality of your file converter, a **Containerized** approach (Option 2) is highly recommended. The **Serverless** approach (Option 1) will only work as a lightweight version with limited capabilities.

---

## 2. Option 1: The Vercel Approach (Lightweight Version)

Deploying to Vercel is fast and free, but it comes with severe limitations for this specific app. 

**Limitations on Vercel:**
*   **No LibreOffice:** Any document conversion relying on LibreOffice (e.g., Word to PDF, Excel to PDF) **will fail**.
*   **Size Limits:** Large libraries like `pandas` might push you over the 250MB deployment limit.
*   **Timeout:** Large file conversions might hit the 10-second timeout limit on the free tier.
*   **File System:** You can only write to the `/tmp` directory.

### Step 1: Create `vercel.json`
Create a file named `vercel.json` in the root of your project:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Step 2: Update `app.py`
You must ensure your Flask app is properly exported and uses the correct temporary directory.

1.  **Expose the App Variable:** Vercel looks for a variable named `app`. Ensure your `app.py` has this at the global scope:
    ```python
    from flask import Flask
    app = Flask(__name__)
    ```
2.  **Use `/tmp` for Storage:** Ensure all temporary file uploads and conversions are routed to the `/tmp` directory, as the rest of the file system is read-only.
    ```python
    import os
    import tempfile

    # Correct way to handle temporary files on Vercel
    TEMP_DIR = tempfile.gettempdir() 
    # OR explicitly:
    # TEMP_DIR = "/tmp"
    ```

### Step 3: Deploy
1. Push your code to a GitHub repository.
2. Go to [Vercel.com](https://vercel.com) and link your GitHub account.
3. Click "Add New..." -> "Project" and import your repository.
4. Leave the framework preset as "Other" and click "Deploy".

---

## 3. Option 2: The Render.com / Docker Approach (Recommended)

Render offers a generous free tier that supports Docker containers. This is the **only way** to run the full application for free, as Docker allows us to install LibreOffice.

### Step 1: Create the `Dockerfile`
Create a file named `Dockerfile` (no extension) in your project root. This file instructs Render to install Python, LibreOffice, and your app's dependencies.

```dockerfile
# Use a lightweight Python base image
FROM python:3.10-slim

# Install system dependencies, including LibreOffice for document conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure the temporary conversions directory exists and has permissions
RUN mkdir -p /tmp/conversions && chmod 777 /tmp/conversions

# Expose the port Render uses
EXPOSE 10000

# Start the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "120", "app:app"]
```

*Note: We use `gunicorn` instead of Flask's built-in development server for better stability and performance. Ensure `gunicorn` is in your `requirements.txt`.*

### Step 2: Deployment Steps on Render
1. Push your complete code (including the `Dockerfile` and `requirements.txt`) to a GitHub repository.
2. Sign up at [Render.com](https://render.com) and link your GitHub account.
3. Click **"New +"** and select **"Web Service"**.
4. Connect the GitHub repository containing your app.
5. In the setup screen:
   *   **Name:** Give your app a name.
   *   **Region:** Choose the region closest to you.
   *   **Branch:** `main` (or your default branch).
   *   **Runtime:** Select **Docker**.
   *   **Instance Type:** Select **Free** ($0/month).
6. Click **"Create Web Service"**.

Render will now build your Docker container (this may take 5-10 minutes because downloading and installing LibreOffice takes time). Once deployed, your full converter will be live!

---

## 4. Security & Cleanup Best Practices for Web

Deploying to the public internet exposes your app to abuse. You must implement the following safeguards:

### 1. Secure File Uploads
*   **Limit File Size:** Prevent malicious users from uploading massive files that crash your server.
    ```python
    # Limit uploads to 16MB
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
    ```
*   **Sanitize Filenames:** Never trust user-provided filenames. Always use `werkzeug.utils.secure_filename`.
    ```python
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    ```

### 2. Configure CORS (Cross-Origin Resource Sharing)
If your frontend and backend are hosted separately, you need to allow them to communicate. If they are bundled together, this is less of a concern, but it's still good practice to restrict access.
```python
from flask_cors import CORS

# Only allow requests from your specific domain
CORS(app, resources={r"/*": {"origins": "https://your-frontend-domain.com"}})
```

### 3. Aggressive Resource Cleanup
Disk space is limited on free tiers. If you don't delete converted files, your server will eventually crash.
*   **Use `try...finally`:** Ensure temporary files are deleted immediately after they are sent to the user, even if the conversion fails. (Note: Using `after_this_request` or background tasks is often necessary in Flask to delete files *after* sending them).
    ```python
    import os
    from flask import send_file, after_this_request

    @app.route('/download')
    def download_file():
        file_path = '/tmp/converted_file.pdf'
        
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as error:
                app.logger.error(f"Error removing or closing downloaded file handle: {error}")
            return response

        return send_file(file_path, as_attachment=True)
    ```
*   **Background Cron Jobs:** For Docker/Render deployments, consider adding a lightweight background thread or entrypoint script that periodically wipes the `/tmp/conversions` directory to catch any orphaned files.