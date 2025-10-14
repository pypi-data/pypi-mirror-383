
from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, Union, Literal, List
from .design import SurveyDesign

Strategy = Literal["rake", "bounded", "entropy", "entropy_bounded"]

@dataclass
class CalibrationResult:
    design: SurveyDesign
    g_weights: pd.Series
    converged: bool
    iters: int
    max_abs_moment_gap: float
    diagnostics: Dict[str, Any]

def _validate_margins(df: pd.DataFrame, categorical_margins, categorical_targets: str):
    if not categorical_margins: return
    for key, targets in categorical_margins.items():
        if categorical_targets == "share":
            s = sum(float(v) for v in targets.values())
            if not (abs(s-1.0) < 1e-6):
                raise ValueError(f"Shares for margin {key} must sum to 1. Got {s}.")
        # ensure categories exist (soft); missing are ignored

def _block_indicator(df: pd.DataFrame, cols: Tuple[str, ...]) -> pd.DataFrame:
    # Multiway: one-hot of cartesian cells that appear in data
    key = tuple(cols) if isinstance(cols, (list, tuple)) else (cols,)
    cats = df[list(key)].astype("object").apply(tuple, axis=1)
    dummies = pd.get_dummies(cats, drop_first=False)
    dummies.columns = [f"{'x'.join(map(str,k))}" for k in dummies.columns]
    return dummies

def _targets_vector(df: pd.DataFrame, w: np.ndarray, blocks: List[Tuple[Tuple[str,...], Dict]],
                    categorical_targets: str, numeric_totals: Dict[str,float]) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    X_blocks = []
    names = []
    for cols, targets in blocks:
        D = _block_indicator(df, cols)
        X_blocks.append(D.values)
        names += [f"m:{','.join(cols)}:{c}" for c in D.columns]
    X = np.concatenate(X_blocks, axis=1) if X_blocks else np.zeros((len(df),0))
    t_list = []
    # categorical targets
    for (cols, targets) in blocks:
        D = _block_indicator(df, cols)
        if categorical_targets == "share":
            totals = {}
            for k, s in targets.items():
                # find matching rows for that cell
                if isinstance(cols, tuple):
                    mask = (df[list(cols)].astype("object").apply(tuple, axis=1) == (k if isinstance(k, tuple) else (k,)))
                else:
                    mask = (df[cols]==k)
                totals[k] = s * np.sum(w)  # share of total weighted sum
        else:
            totals = targets
        # Ensure order matches D's columns
        for cname in D.columns:
            # cname is stringified tuple; reconstruct key by splitting (heuristic)
            t = 0.0
            # parse cname back to tuple by splitting on 'x'
            parts = tuple(cname.split("x"))
            # coerce numeric-looking to original types if present in df
            # Create mask to compute observed total as fallback if key missing
            mask = (df[list(cols)].astype("object").apply(tuple, axis=1) == parts)
            key = parts if len(cols)>1 else parts[0]
            t = float(totals.get(key, (w[mask]).sum()*0.0))  # default 0 if not in targets
            t_list.append(t)
    # numeric totals
    if numeric_totals:
        X_num = np.column_stack([df[k].astype(float).values for k in numeric_totals.keys()])
        X = np.concatenate([X, X_num], axis=1)
        names += [f"num:{k}" for k in numeric_totals.keys()]
        for k in numeric_totals.keys():
            t_list.append(float(numeric_totals[k]))
    return np.array(t_list, dtype=float), names, pd.DataFrame(X, columns=names, index=df.index)

def _ipf_cycle(df: pd.DataFrame, w0: pd.Series, margins, targets_mode: str, bounds=None):
    g = np.ones(len(df), dtype=float)
    history_gaps = []
    for _ in range(200):
        maxgap = 0.0
        for cols, targets in margins:
            D = _block_indicator(df, cols)
            cur_tot = (w0.values[:,None] * g[:,None] * D.values).sum(axis=0)
            if targets_mode == "share":
                targ = np.array([targets.get(c if len(cols)==1 else tuple(c.split("x")), 0.0) for c in D.columns]) * (w0.values*g).sum()
            else:
                targ = np.array([targets.get((c if len(cols)==1 else tuple(c.split("x"))), 0.0) for c in D.columns])
            # avoid division by zero
            adj = np.ones_like(cur_tot)
            nz = cur_tot > 0
            adj[nz] = targ[nz] / cur_tot[nz]
            # apply multiplicative factor per cell
            for j, cname in enumerate(D.columns):
                mask = D.iloc[:, j].values.astype(bool)
                g_new = g[mask] * adj[j]
                if bounds is not None:
                    L,U = bounds
                    g_new = np.clip(g_new, L, U)
                g[mask] = g_new
            maxgap = max(maxgap, float(np.max(np.abs(targ - cur_tot))))
        history_gaps.append(maxgap)
        if maxgap < 1e-7:
            return g, True, history_gaps
    return g, False, history_gaps

def calibrate(
    design: SurveyDesign,
    *,
    categorical_margins: Dict[Union[str, Tuple[str, ...]], Dict[Union[str, int, Tuple], float]] = None,
    numeric_totals: Dict[str, float] = None,
    strategy: Strategy = "rake",
    bounds: Tuple[float, float] = (0.3, 3.0),
    max_iter: int = 200,
    tol: float = 1e-7,
    ridge: float = 0.0,
    step_damping: float = 0.5,
    max_backtracks: int = 20,
    multiway_balancing: Literal["cyclic","joint"] = "cyclic",
    categorical_targets: Literal["share","total"] = "share",
    out_weight_col: Optional[str] = None,
    domain: str | None = None,
    zero_outside: bool = True,
) -> CalibrationResult:
    df = design.df.copy()
    w0 = design.weights.copy()
    # Domain handling
    if domain:
        mask = design.df.eval(domain).astype(bool)
        if zero_outside:
            df_work = df.loc[mask].copy()
            w0_work = w0.loc[mask].copy()
            outside_idx = (~mask).values
        else:
            df_work = df.loc[mask].copy()
            w0_work = w0.loc[mask].copy()
        df_used = df_work; w0_used = w0_work
    else:
        df_used = df; w0_used = w0
    if (not categorical_margins) and (not numeric_totals):
        raise ValueError("Provide categorical_margins and/or numeric_totals.")
    blocks = []
    if categorical_margins:
        for k,v in categorical_margins.items():
            if isinstance(k, (list, tuple)):
                blocks.append( (tuple(k), v) )
            else:
                blocks.append( ((k,), v) )
    _validate_margins(df, categorical_margins, categorical_targets)

    if strategy in ("rake","bounded"):
        bounds_val = (bounds if strategy=="bounded" else None)
        g, conv, history = _ipf_cycle(df_used, w0_used, blocks, categorical_targets, bounds=bounds_val)
        # If numeric_totals are specified, do a light GREG on top to hit totals
        if numeric_totals:
            X = np.column_stack([df_used[k].astype(float).values for k in numeric_totals.keys()])
            tX = np.array([v for v in numeric_totals.values()], dtype=float)
            w = w0_used.values * g
            WX = (w[:,None]*X)
            A = WX.T @ X + ridge*np.eye(X.shape[1])
            b = tX - (w @ X)
            try:
                a = np.linalg.solve(A, b)
                g_num = 1.0 + (X @ a)/np.maximum(w, 1e-12)
                g = g * g_num
            except Exception:
                pass
        w_new = w0.values * g
        out = design.copy()
        col = out_weight_col or design.weight or "__w__"
        if out_weight_col and (out_weight_col not in out.df.columns):
            out.df[out_weight_col] = w_new
            out.weight = out_weight_col
        else:
            out.df[col] = w_new
            out.weight = col
        maxgap = float(max(history)) if history else 0.0
    # assemble full-length weights
    if domain:
        g_full = np.ones(len(df), dtype=float)
        if zero_outside:
            # zero outside domain
            g_full[:] = 0.0
        g_full[df.index.get_indexer(df_used.index)] = (g if strategy in ("rake","bounded") else g_weights)
        w_new = w0.values * g_full
        g_series = pd.Series(g_full, index=df.index, name="g")
    else:
        if strategy in ("rake","bounded"):
            w_new = w0.values * g
            g_series = pd.Series(g, index=df.index, name="g")
        else:
            w_new = np.zeros(len(df)); w_new[df.index.get_indexer(df_used.index)] = w_new_sub
            g_series = pd.Series(np.ones(len(df)), index=df.index, name="g")

    out = design.copy()
    col = out_weight_col or design.weight or "__w__"
    if out_weight_col and (out_weight_col not in out.df.columns):
        out.df[out_weight_col] = w_new
        out.weight = out_weight_col
    else:
        out.df[col] = w_new
        out.weight = col

    return CalibrationResult(out, g_series,
                             converged if strategy not in ("rake","bounded") else conv,
                             it if strategy not in ("rake","bounded") else len(history),
                             float(max(history) if (strategy not in ("rake","bounded")) else (max(history) if history else 0.0)),
                             {"history_gaps": history})
