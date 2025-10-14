
from __future__ import annotations
import os, io, base64, datetime
import numpy as np, pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot as plot_offline
from typing import List, Dict, Any, Optional
from .design import SurveyDesign
from .poststrat import CalibrationResult

def _gweight_histogram(res: CalibrationResult) -> go.Figure:
    g = res.g_weights.replace([np.inf, -np.inf], np.nan).dropna()
    fig = go.Figure(go.Histogram(x=g, nbinsx=40))
    fig.update_layout(title='g-weight distribution', xaxis_title='g', yaxis_title='count')
    return fig

def _design_effect_bar(design: SurveyDesign) -> go.Figure:
    if not design.strata:
        vals = [float(design.weights.var() / (design.weights.mean()**2))]
        names = ['overall']
    else:
        names, vals = [], []
        for s, g in design.df.groupby(design.strata):
            w = g[design.weight].astype(float)
            deff = float(w.var(ddof=1) / (w.mean()**2)) if len(w)>1 else 0.0
            names.append(str(s)); vals.append(deff)
    fig = go.Figure(go.Bar(x=names, y=vals))
    fig.update_layout(title='Design-effect proxy by stratum', xaxis_title='Stratum', yaxis_title='DEFF (proxy)')
    return fig

def _quantreg_curves(qreg_result) -> go.Figure:
    tau = qreg_result.tau
    names = qreg_result.names
    coef = qreg_result.coef  # (T,p)
    fig = go.Figure()
    for j, name in enumerate(names):
        fig.add_trace(go.Scatter(x=tau, y=coef[:,j], mode='lines+markers', name=name))
    fig.update_layout(title='Quantile Regression Coefficients vs τ', xaxis_title='τ', yaxis_title='Coefficient')
    return fig

def build_survey_report(design: SurveyDesign, results: List[Any], *, outfile: str, metadata: Optional[Dict[str, Any]]=None, export_pdf: bool=True) -> Dict[str, Optional[str]]:
    """Create a self-contained HTML dashboard with inline Plotly and an optional PDF.

    results may include CalibrationResult and QuantRegResult instances.

    Returns paths to {'html':..., 'pdf':...}

    """
    metadata = metadata or {}
    title = metadata.get('title', 'pysurveyx Survey Report')
    author = metadata.get('author', 'pysurveyx')
    generated = datetime.datetime.utcnow().isoformat() + 'Z'

    sections = []
    # Always include DEFF
    fig_deff = _design_effect_bar(design)
    div_deff = plot_offline(fig_deff, include_plotlyjs='inline', output_type='div')

    sections.append(f"<h2>Design Effect</h2>{div_deff}")

    # Include per-result sections
    calib = [r for r in results if hasattr(r, 'g_weights')]
    qregs = [r for r in results if hasattr(r, 'coef') and hasattr(r, 'tau')]
    if calib:
        fig_g = _gweight_histogram(calib[0])
        div_g = plot_offline(fig_g, include_plotlyjs=False, output_type='div')  # JS already inline in first figure
        sections.append(f"<h2>Calibration Diagnostics</h2>{div_g}")
    if qregs:
        fig_q = _quantreg_curves(qregs[0])
        div_q = plot_offline(fig_q, include_plotlyjs=False, output_type='div')
        sections.append(f"<h2>Quantile Regression</h2>{div_q}")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem; }}
header {{ margin-bottom: 2rem; }}
h1 {{ border-bottom: 1px solid #e5e5e5; padding-bottom: .3rem; }}
section {{ margin-top: 2rem; }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p><strong>Author:</strong> {author} &nbsp; | &nbsp; <strong>Generated:</strong> {generated}</p>
</header>
{''.join(f'<section>{s}</section>' for s in sections)}
</body>
</html>
"""
    html_path = outfile + '.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # PDF (static) using ReportLab; try snapshot via kaleido if available
    pdf_path = None
    if export_pdf:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            pdf_path = outfile + '.pdf'
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter
            y = height - 1*inch
            c.setFont('Helvetica-Bold', 14); c.drawString(1*inch, y, title); y -= 0.3*inch
            c.setFont('Helvetica', 10); c.drawString(1*inch, y, f'Author: {author}'); y -= 0.2*inch
            c.drawString(1*inch, y, f'Generated: {generated}'); y -= 0.3*inch
            c.setFont('Helvetica-Bold', 12); c.drawString(1*inch, y, 'Summary'); y -= 0.25*inch
            c.setFont('Helvetica', 10); c.drawString(1*inch, y, 'See HTML for interactive charts.'); y -= 0.25*inch
            c.showPage(); c.save()
        except Exception:
            pdf_path = None

    return {'html': html_path, 'pdf': pdf_path}
