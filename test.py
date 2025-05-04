from pathlib import Path
import requests

API_URL = "http://127.0.0.1:8081"
SESSION_ID = "test-session-123"
SVG_DIR = Path("test-files")
OUTPUT_PDF_A4 = Path("output_test_result_a4.pdf")
OUTPUT_PDF_INDIVIDUAL = Path("output_test_result_individual.pdf")
STAMP_WIDTH_MM = 40
STAMP_HEIGHT_MM = 15

# 1. Reset session
print("\U0001F504 Resetting session...")
requests.post(f"{API_URL}/reset-session/?session_id={SESSION_ID}")

# 2. Upload SVG files
print("\U0001F4E4 Uploading SVGs...")
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
            print(f"\u2705 Uploaded: {svg_file.name}")
        else:
            print(f"\u274C Failed: {svg_file.name}", res.text)

# 3. Generate A4 grid-style PDF
print("\U0001F9FE Generating A4 Grid PDF...")
pdf_response = requests.post(f"{API_URL}/generate-pdf?session_id={SESSION_ID}")
if pdf_response.status_code == 200:
    OUTPUT_PDF_A4.write_bytes(pdf_response.content)
    print(f"\u2705 A4 PDF saved as: {OUTPUT_PDF_A4}")
else:
    print(f"\u274C Failed to generate A4 PDF: {pdf_response.text}")

# 4. Generate one-stamp-per-page PDF
print("\U0001F9FE Generating Per-Stamp PDF...")
pdf_response = requests.post(f"{API_URL}/generate-individual-pdf/?session_id={SESSION_ID}")
if pdf_response.status_code == 200:
    OUTPUT_PDF_INDIVIDUAL.write_bytes(pdf_response.content)
    print(f"\u2705 Individual PDF saved as: {OUTPUT_PDF_INDIVIDUAL}")
else:
    print(f"\u274C Failed to generate Individual PDF: {pdf_response.text}")
