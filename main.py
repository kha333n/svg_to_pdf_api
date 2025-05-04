import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

app = FastAPI()

# === CONFIGURABLE PARAMETERS ===
# Default outer margin on all sides of A4 in mm
PAGE_MARGIN_MM = 0
# Margin between each SVG stamp cell (horizontal & vertical) in mm
CELL_MARGIN_MM = 0
# Unit conversion
MM_TO_PT = 2.83465

# Temporary directory for storing session-based SVGs
SESSION_DIR = Path("svg_to_pdf_sessions")
SESSION_DIR.mkdir(exist_ok=True)

# Store session data in memory for simplicity (you can persist this in DB/cache)
session_svgs = {}

@app.post("/upload-svg/")
def upload_svg(
        session_id: str = Form(...),
        width_mm: float = Form(...),
        height_mm: float = Form(...),
        file: UploadFile = File(...)
):
    """Upload SVG file with intended stamp dimensions."""
    session_path = SESSION_DIR / session_id
    session_path.mkdir(parents=True, exist_ok=True)

    stamp_id = uuid.uuid4().hex
    file_path = session_path / f"{stamp_id}.svg"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Store stamp metadata
    metadata_path = session_path / f"{stamp_id}.meta"
    with open(metadata_path, "w") as f:
        f.write(f"{width_mm},{height_mm}")

    return {"message": "SVG uploaded", "stamp_id": stamp_id}

@app.post("/generate-pdf/")
def generate_pdf(session_id: str):
    session_path = SESSION_DIR / session_id
    if not session_path.exists():
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    svg_files = sorted([f for f in session_path.glob("*.svg")])
    if not svg_files:
        return JSONResponse(status_code=400, content={"error": "No SVGs to process"})

    # Group SVGs by dimension
    grouped = {}
    for svg_file in svg_files:
        meta_file = svg_file.with_suffix(".meta")
        if not meta_file.exists():
            continue
        with open(meta_file) as f:
            width_mm, height_mm = map(float, f.read().strip().split(","))
        key = (width_mm, height_mm)
        grouped.setdefault(key, []).append(svg_file)

    pdf_dir = session_path / "output"
    pdf_dir.mkdir(exist_ok=True)

    generated_pdfs = []
    for (w, h), files in grouped.items():
        # Page usable area after margin
        usable_width_mm = 297 - 2 * PAGE_MARGIN_MM
        usable_height_mm = 210 - 2 * PAGE_MARGIN_MM

        # Full cell size = stamp + margin between
        cell_w = w + CELL_MARGIN_MM * 2
        cell_h = h + CELL_MARGIN_MM * 2
        cols = int(usable_width_mm // cell_w)
        rows = int(usable_height_mm // cell_h)

        pdf_path = pdf_dir / f"stamps_{int(w)}x{int(h)}.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))

        for i, svg_file in enumerate(files):
            col = i % cols
            row = (i // cols) % rows
            if i != 0 and i % (cols * rows) == 0:
                c.showPage()

            x = PAGE_MARGIN_MM * MM_TO_PT + col * cell_w * MM_TO_PT + CELL_MARGIN_MM * MM_TO_PT
            y = PAGE_MARGIN_MM * MM_TO_PT + (rows - row - 1) * cell_h * MM_TO_PT + CELL_MARGIN_MM * MM_TO_PT

            drawing = svg2rlg(str(svg_file))
            drawing.width = w * MM_TO_PT
            drawing.height = h * MM_TO_PT
            renderPDF.draw(drawing, c, x, y)

        c.showPage()
        c.save()
        generated_pdfs.append(pdf_path)

    # Return first PDF for now
    if generated_pdfs:
        return FileResponse(generated_pdfs[0], filename=generated_pdfs[0].name)
    return JSONResponse(status_code=500, content={"error": "PDF generation failed"})

@app.post("/generate-individual-pdf/")
def generate_individual_pdf(session_id: str):
    session_path = SESSION_DIR / session_id
    if not session_path.exists():
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    svg_files = sorted([f for f in session_path.glob("*.svg")])
    if not svg_files:
        return JSONResponse(status_code=400, content={"error": "No SVGs to process"})

    pdf_dir = session_path / "output_individual"
    pdf_dir.mkdir(exist_ok=True)

    # Assume all SVGs are same size as defined by their metadata
    output_pdf = pdf_dir / "stamps_individual_pages.pdf"
    c = None

    for svg_file in svg_files:
        meta_file = svg_file.with_suffix(".meta")
        if not meta_file.exists():
            continue
        with open(meta_file) as f:
            width_mm, height_mm = map(float, f.read().strip().split(","))

        page_size = (width_mm * MM_TO_PT, height_mm * MM_TO_PT)

        if c is None:
            c = canvas.Canvas(str(output_pdf), pagesize=page_size)
        else:
            c.setPageSize(page_size)
            c.showPage()

        drawing = svg2rlg(str(svg_file))
        drawing.width = width_mm * MM_TO_PT
        drawing.height = height_mm * MM_TO_PT
        renderPDF.draw(drawing, c, 0, 0)

    if c:
        c.save()
        return FileResponse(output_pdf, filename=output_pdf.name)

    return JSONResponse(status_code=500, content={"error": "PDF generation failed"})

@app.post("/reset-session/")
def reset_session(session_id: str):
    session_path = SESSION_DIR / session_id
    if session_path.exists():
        shutil.rmtree(session_path)
    return {"message": "Session reset"}
