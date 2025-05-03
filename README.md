# SVG to PDF Stamp Grid API

This project provides a FastAPI-based microservice that accepts stamp SVG files, arranges them in a grid on A4 PDF
pages, and returns the generated PDF. Each SVG is sized precisely and optionally grouped by stamp dimensions.

## 📦 Features

- Upload SVGs with stamp dimensions
- Arrange stamps with margin and padding in a grid
- Group stamps by size to avoid layout distortion
- Convert stamps to precise A4-sized PDFs
- Return generated PDFs via API

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.12

1. **Clone the Repository**

```bash
git clone https://github.com/kha333n/svg_to_pdf_api.git
cd svg_to_pdf_api
```

2. **Create a Virtual Environment**

```bash
python3 -m venv venv
# Activate the virtual environment on Linux/Mac
source venv/bin/activate

# Activate the virtual environment on Windows
venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the Server**

```bash
uvicorn main:app --reload --port 8081
```

---

## 🔌 API Endpoints

### 1. `POST /upload-svg/`

Upload a single SVG file with size and session info.

#### Form Data:

- `session_id` (string, required): Session key to group files.
- `width_mm` (float, required): Width of the stamp in mm.
- `height_mm` (float, required): Height of the stamp in mm.
- `file` (file, required): SVG file upload.

#### Response:

```json
{
  "message": "SVG uploaded",
  "stamp_id": "abc123..."
}
```

---

### 2. `POST /generate-pdf?session_id=<your-session>`

Generate a PDF from previously uploaded SVGs grouped by stamp size.

#### Query Params:

- `session_id` (string, required)

#### Returns:

- A4-sized PDF file as direct download.

---

### 3. `POST /reset-session/?session_id=<your-session>`

Remove all uploaded SVGs from the session (including outputs).

#### Query Params:

- `session_id` (string, required)

#### Response:

```json
{
  "message": "Session reset"
}
```

---

## 📁 File Structure

```
svg_to_pdf_sessions/
└── <session_id>/
    ├── abc123.svg
    ├── abc123.meta
    └── output/
        └── stamps_40x15.pdf
```

---

## 📏 Configuration

File `main.py`

You can customize margins and spacing directly in the code:

- `PAGE_MARGIN_MM`: Outer margin on A4 page
- `CELL_MARGIN_MM`: Space between each stamp

---

## 🧪 Testing

You can use the included script to test by pointing it to a directory of SVGs:

```bash
python test.py
```