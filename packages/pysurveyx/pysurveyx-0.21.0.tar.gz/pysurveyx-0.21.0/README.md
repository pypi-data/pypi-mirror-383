
# pysurveyx (v0.21.0)

A unified Python framework for **complex surveys**, inspired by R's `survey`:
- Sampling designs (strata/PSU/SSU), FPCs, replicate-weight variance (BRR/Fay/JK/bootstrap)
- Calibration: raking, bounded, entropy, entropy_bounded (+ multiway)
- Estimators: totals, means, proportions, ratios, GLM, quantiles (+ Woodruff SEs)
- Quantile regression with replicate SEs (pinball & smoothed SAL)
- **Dynamic, self-contained HTML reports** with Plotly

## End-to-end
```bash
python examples/end_to_end.py --out report_out
# Produces: report_out.html (self-contained) and optional PDF
```

## Docs
Built via Sphinx and auto-published to GitHub Pages on tag pushes.
