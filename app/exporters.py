"""Export the comic layout to PDF using FPDF."""
from pathlib import Path

from fpdf import FPDF

EXPORT_DIR = Path(__file__).resolve().parent / "static" / "exports"


def _safe(text: str) -> str:
    return (text or "").encode("latin-1", "replace").decode("latin-1")


def export_pdf(comic_id: str, title: str, pages: list[dict], story: str) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    margin, gap, cap_h = 10, 4, 12

    # Cover + story page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.multi_cell(0, 14, _safe(title), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _safe(story), new_x="LMARGIN", new_y="NEXT")

    usable_w, usable_h = 210 - 2 * margin, 297 - 2 * margin
    for page in pages:
        pdf.add_page()
        rows = page["rows"]
        row_h = (usable_h - gap * (len(rows) - 1)) / len(rows)
        y = margin
        for row in rows:
            cell_w = (usable_w - gap * (len(row) - 1)) / len(row)
            x = margin
            img_h = row_h - cap_h
            side = min(cell_w, img_h)
            for p in row:
                pdf.image(p["image_path"], x=x + (cell_w - side) / 2, y=y, w=side, h=side)
                pdf.rect(x + (cell_w - side) / 2, y, side, side)
                pdf.set_xy(x, y + side + 1)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(cell_w, 4, _safe(p.get("caption", "")), align="C")
                x += cell_w + gap
            y += row_h + gap

    out = EXPORT_DIR / f"{comic_id}.pdf"
    pdf.output(str(out))
    return out
