
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib.pyplot as plt

def plot_weight_distribution(design, by:str|None=None):
    w = design.weights
    if by is None:
        plt.hist(w, bins=30)
        plt.xlabel("Weight")
        plt.ylabel("Count")
        plt.title("Weight distribution")
        plt.show()
    else:
        for k, g in design.df.groupby(by):
            plt.hist(g[design.weight], bins=30, alpha=0.5, label=str(k))
        plt.xlabel("Weight")
        plt.ylabel("Count")
        plt.title(f"Weight distribution by {by}")
        plt.legend()
        plt.show()

def plot_strata_design_effects(design):
    # simple proxy: deff_h = var_w / mean_w^2 within stratum (illustrative)
    df = design.df
    out = []
    for s, g in df.groupby(design.strata) if design.strata else [(1, df)]:
        w = g[design.weight].astype(float)
        deff = (w.var(ddof=1) / (w.mean()**2)) if len(w)>1 else 0.0
        out.append((s, deff))
    s, d = zip(*out)
    plt.bar(range(len(d)), d)
    plt.xticks(range(len(d)), s)
    plt.ylabel("Design effect (proxy)")
    ttl = f"Design effects by {design.strata}" if design.strata else "Design effects"
    plt.title(ttl)
    plt.show()


from typing import Sequence
import plotly.graph_objs as go

def plot_quantile_curves(model) -> 'go.Figure':
    """Interactive Plotly figure: coefficients vs tau for a fitted SurveyQuantileRegression."""
    tau = model._res.tau
    names = model._res.names
    coef = model._res.coef  # (T,p)
    fig = go.Figure()
    for j, name in enumerate(names):
        fig.add_trace(go.Scatter(x=tau, y=coef[:,j], mode='lines+markers', name=name))
    fig.update_layout(title='Quantile Regression Coefficients vs τ', xaxis_title='τ', yaxis_title='Coefficient')
    return fig
