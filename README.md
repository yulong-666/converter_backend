# Universal File Converter Backend

> A high-performance, plugin-based file conversion microservice running on Python 3.11+ and FastAPI.

🚀 **Universal File Converter** is designed for scalability and extensibility. It features a robust plugin architecture, enterprise-grade logging, automated lifecycle management, and strict type safety.

---

## 🌟 Key Features

-   **🔌 Extensible Plugin Architecture**: Easily add support for new file formats (PDF, DOCX, Images, etc.) by implementing a simple configuration contract.
-   **⚡ High Performance**: Built on **FastAPI** and **Uvicorn**, utilizing full asynchronous I/O (`async`/`await`) for non-blocking file processing.
-   **🛡️ Enterprise Observability**:
    -   **Unified Logging**: Centralized logging logic (`app/core/logger.py`) handling all application, server, and error logs.
    -   **Contextual Sinks**: Logs are automatically routed to separate files: `application.log`, `access.log`, `error.log`, `security.log`, and `audit.log`.
    -   **Access Monitoring**: Automatic HTTP traffic capture via middleware.
-   **🧹 Self-Maintained System**:
    -   **Auto-Cleanup**: Background tasks (`BackgroundTasks`) automatically remove temporary files inside `temp/` after every conversion request to prevent disk bloat.
-   **🧪 Quality Assurance**:
    -   Comprehensive **Pytest** suite covering API endpoints, service logic, and edge cases.
-   **🎨 Modern Web Interface**: Includes a beautiful, dark-mode/glassmorphism web UI for user interaction.

---

## 📂 Project Structure

```bash
converter_backend/
├── app/
│   ├── api/            # API Route definitions
│   ├── core/           # Core config & Logging logic
│   ├── middlewares/    # HTTP Middlewares (Access Log)
│   ├── plugins/        # Converter Plugins (e.g., json_to_md)
│   ├── services/       # Business Logic Layer
│   └── static/         # Frontend Assets (HTML/CSS/JS)
├── logs/               # Log files (Auto-generated)
├── temp/               # Temporary file storage (Auto-cleaned)
├── tests/              # Pytest Suite
├── main.py             # Application Entry Point
├── .env                # Environment Variables
└── requirements.txt    # Dependencies
```

---

## 🚀 Quick Start

### 1. Requirements
-   **Python 3.11+**

### 2. Installation
It is strictly recommended to use a **virtual environment**.

```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Server
Start the development server with hot-reload enabled:

```bash
uvicorn main:app --reload
# OR
python main.py
```

The server will start at `http://localhost:8000`.

---

## 📖 Usage

### Web Interface
Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

You will see a drag-and-drop interface to upload files and download the converted result.

### API Documentation
FastAPI provides interactive API docs automatically.
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

#### Example: Convert File
**POST** `/api/v1/convert`

**Curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/convert" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.json"
```

**Response**: Returns the converted binary file (`application/octet-stream`).

---

## 🛠️ Development Guide

### Running Tests
Execute the full test suite using `pytest`:

```bash
pytest
```
*Ensure dependencies are installed before running tests.*

### Adding a New Plugin
To add a new converter (e.g., XML to JSON):

1.  Create a new file in `app/plugins/xml_to_json.py`.
2.  Inherit from `BaseConverter`.
3.  Define the `meta` property (source format `.xml`, target format `.json`).
4.  Implement the `async def convert(...)` method.
5.  The service layer will automatically discover and register your plugin at runtime!

---

## 📄 License
This project is proprietary software.
