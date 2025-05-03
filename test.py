from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8081"
SESSION_ID = "test-session-123"
SVG_DIR = Path("test-files-square")
OUTPUT_PDF = Path("output_test_result.pdf")
STAMP_WIDTH_MM = 20
STAMP_HEIGHT_MM = 20

# 1. Reset session (send as query param)
print("🔄 Resetting session...")
requests.post(f"{API_URL}/reset-session/?session_id={SESSION_ID}")

# 2. Upload all SVG files
print("📤 Uploading SVGs...")
for svg_file in SVG_DIR.glob("*.svg"):
    with open(svg_file, "rb") as f:
        files = {"file": (svg_file.name, f, "image/svg+xml")}
        data = {
            "session_id": SESSION_ID,
            "width_mm": str(STAMP_WIDTH_MM),
            "height_mm": str(STAMP_HEIGHT_MM),
        }
        res = requests.post(f"{API_URL}/upload-svg/", data=data, files=files)
        if res.ok:
            print(f"✅ Uploaded: {svg_file.name}")
        else:
            print(f"❌ Failed: {svg_file.name}", res.text)

# 3. Generate PDF
print("🧾 Generating PDF...")
pdf_response = requests.post(f"{API_URL}/generate-pdf?session_id={SESSION_ID}")

if pdf_response.status_code == 200:
    OUTPUT_PDF.write_bytes(pdf_response.content)
    print(f"✅ PDF saved as: {OUTPUT_PDF}")
else:
    print(f"❌ Failed to generate PDF: {pdf_response.text}")
