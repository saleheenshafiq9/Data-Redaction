### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/saleheenshafiq9/Data-Redaction.git
cd pdf-redactor-api
```

#### 2. Set Up and Run the Backend API

The backend API is implemented using Python FAST API. Follow these steps to set it up:

1. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Required Dependencies**

   Ensure you have the necessary Python packages installed. If a `requirements.txt` file is present, run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend Server**

   ```uvicorn main:app --reload
   ```

   By default, Fast API runs on `http://127.0.0.1:8000/`.

#### 3. Load the Chrome Extension

1. **Open Chrome and Navigate to Extensions**

   Go to `chrome://extensions/`.

2. **Enable Developer Mode**

   Toggle the **Developer mode** switch in the top right corner.

3. **Load Unpacked Extension**

   Click on **Load unpacked** and select the `Data-Redaction` directory.

4. **Activate the Extension**

   The extension icon should now appear in the Chrome toolbar. Click on it to access the popup interface.

## 🛠️ Project Structure

```plaintext
Data-Redaction/
├── background.js        # Background script managing extension lifecycle
├── content.js           # Content script for scanning and redacting data
├── popup.html           # HTML for the popup interface
├── popup.js             # JavaScript for popup interactions
├── manifest.json        # Extension manifest file
├── pdf-redactor-api     # Python backend API for redaction
    ├── requirements.txt # Python dependencies (if present)
├── icons/               # Directory containing icon images
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── .gitignore           # Git ignore file
```
