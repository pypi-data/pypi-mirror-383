
from __future__ import annotations
import datetime
import numpy as np
from typing import Optional, Dict
from .poststrat import CalibrationResult
from .design import SurveyDesign

def calibration_report(result: CalibrationResult, design_before: SurveyDesign, outfile_base: str, title: Optional[str]=None, export_pdf: bool=False) -> Dict[str, Optional[str]]:
    title = title or "Calibration Diagnostics Report"
    g = result.g_weights
    stats = {
        "g_min": float(np.min(g)),
        "g_max": float(np.max(g)),
        "g_mean": float(np.mean(g)),
        "g_median": float(np.median(g)),
        "num_clipped": int(np.sum((g==g.min()) | (g==g.max()))),
        "converged": bool(result.converged),
        "iterations": int(result.iters),
        "max_abs_gap": float(result.max_abs_moment_gap),
    }
    hist = result.diagnostics.get("history_gaps", []) if hasattr(result, "diagnostics") and isinstance(result.diagnostics, dict) else []

    # Build Markdown
    md_lines = []
    md_lines.append(f"# {title}")
    md_lines.append("")
    md_lines.append(f"**Generated:** {datetime.datetime.utcnow().isoformat()}Z")
    md_lines.append("")
    md_lines.append("## Summary")
    for k,v in stats.items():
        md_lines.append(f"- **{k}**: {v}")
    md_lines.append("")
    if hist:
        md_lines.append("## Constraint gap over iterations")
        for i, val in enumerate(hist):
            md_lines.append(f"- iter {i+1}: {val:.6g}")
        md_lines.append("")

    w0 = design_before.weights
    w1 = result.design.weights
    md_lines.append("## Weight summary (before vs after)")
    md_lines.append(f"- Before: min={w0.min():.4g}, median={w0.median():.4g}, mean={w0.mean():.4g}, max={w0.max():.4g}")
    md_lines.append(f"- After:  min={w1.min():.4g}, median={w1.median():.4g}, mean={w1.mean():.4g}, max={w1.max():.4g}")
    md_text = "\n".join(md_lines)

    md_path = outfile_base + ".md"
    html_path = outfile_base + ".html"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    html = f"""<html><head><meta charset="utf-8"><title>{title}</title>
    <style>body{{font-family:Arial, sans-serif; max-width:800px; margin:2rem auto;}} h1{{border-bottom:1px solid #ddd}}</style>
    </head><body><h1>{title}</h1><pre>{md_text}</pre></body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_path = None
    if export_pdf:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            pdf_path = outfile_base + ".pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            y = height - 1*inch
            c.setFont("Helvetica-Bold", 14); c.drawString(1*inch, y, title); y -= 0.3*inch
            c.setFont("Helvetica", 10)
            for k,v in stats.items():
                c.drawString(1*inch, y, f"{k}: {v}"); y -= 0.2*inch
                if y < 1*inch: c.showPage(); y = height - 1*inch
            if hist:
                c.setFont("Helvetica-Bold", 12); c.drawString(1*inch, y, "Constraint gaps:"); y -= 0.25*inch
                c.setFont("Helvetica", 10)
                for i,val in enumerate(hist[:40]):
                    c.drawString(1.1*inch, y, f"iter {i+1}: {val:.6g}"); y -= 0.18*inch
                    if y < 1*inch: c.showPage(); y = height - 1*inch
            c.showPage(); c.save()
        except Exception:
            pdf_path = None

    return {"markdown": md_path, "html": html_path, "pdf": pdf_path}
