
from __future__ import annotations
import numpy as np, pandas as pd
from typing import Optional
from .exceptions import SurveyError

def _fpc_factor(value, n_sample):
    try:
        v = float(value)
    except Exception:
        return 1.0
    if 0.0 <= v <= 1.0:
        f = v
    else:
        N = v if v>0 else np.inf
        f = min(1.0, n_sample / N)
    return max(0.0, 1.0 - f)

def taylor_var_mean(y: pd.Series, w: pd.Series, strata: pd.Series, psu: pd.Series,
                    domain: Optional[pd.Series]=None, fpc_strata: Optional[pd.Series]=None) -> float:
    if domain is not None:
        y=y[domain]; w=w[domain]; strata=strata[domain]; psu=psu[domain]
        if fpc_strata is not None: fpc_strata=fpc_strata[domain]
    df = pd.DataFrame({"y":y.astype(float), "w":w.astype(float), "H":strata, "P":psu})
    if fpc_strata is not None: df["FPC_H"] = fpc_strata
    var_sum = 0.0
    for h, d in df.groupby("H"):
        psu_stats = d.groupby("P").apply(lambda g: pd.Series({"ty": (g["y"]*g["w"]).sum(), "tw": g["w"].sum()}))
        m = len(psu_stats)
        if m < 2: raise SurveyError(f"Stratum {h} has <2 PSUs.")
        ybar_h = psu_stats["ty"].sum()/psu_stats["tw"].sum()
        u = psu_stats["ty"]/psu_stats["tw"] - ybar_h
        s2u = (u**2).sum()/(m-1)
        fpc = 1.0
        if fpc_strata is not None:
            fpc_vals = d["FPC_H"].dropna().unique()
            fpc = _fpc_factor(fpc_vals[0], m) if len(fpc_vals)>0 else 1.0
        var_sum += (s2u/m) * fpc
    return float(var_sum)

def taylor_var_mean_2stage(y: pd.Series, w: pd.Series, strata: pd.Series, psu: pd.Series, ssu: pd.Series,
                           domain: Optional[pd.Series]=None,
                           fpc_strata: Optional[pd.Series]=None, fpc_psu: Optional[pd.Series]=None) -> float:
    if domain is not None:
        y=y[domain]; w=w[domain]; strata=strata[domain]; psu=psu[domain]; ssu=ssu[domain]
        if fpc_strata is not None: fpc_strata=fpc_strata[domain]
        if fpc_psu is not None: fpc_psu=fpc_psu[domain]
    df = pd.DataFrame({"y":y.astype(float), "w":w.astype(float), "H":strata, "P":psu, "Q":ssu})
    if fpc_strata is not None: df["FPC_H"] = fpc_strata
    if fpc_psu is not None: df["FPC_P"] = fpc_psu
    var_sum = 0.0
    for h, dh in df.groupby("H"):
        psu_stats = dh.groupby("P").apply(lambda g: pd.Series({"ty": (g["y"]*g["w"]).sum(), "tw": g["w"].sum()}))
        m_h = len(psu_stats)
        if m_h < 2: raise SurveyError(f"Stratum {h} has <2 PSUs.")
        ybar_h = psu_stats["ty"].sum()/psu_stats["tw"].sum()
        u_hi = psu_stats["ty"]/psu_stats["tw"] - ybar_h
        S2_between = (u_hi**2).sum()/(m_h-1)
        fpc1 = 1.0
        if fpc_strata is not None:
            vals = dh["FPC_H"].dropna().unique()
            fpc1 = _fpc_factor(vals[0], m_h) if len(vals)>0 else 1.0
        W_h = psu_stats["tw"].sum()
        within_sum = 0.0
        for i, di in dh.groupby("P"):
            ss_stats = di.groupby("Q").apply(lambda g: pd.Series({"ty": (g["y"]*g["w"]).sum(), "tw": g["w"].sum()}))
            k_hi = len(ss_stats)
            if k_hi < 2: 
                continue
            yhat_hi = ss_stats["ty"].sum()/ss_stats["tw"].sum()
            u_hij = ss_stats["ty"]/ss_stats["tw"] - yhat_hi
            S2_within = (u_hij**2).sum()/(k_hi-1)
            fpc2 = 1.0
            if fpc_psu is not None:
                vals2 = di["FPC_P"].dropna().unique()
                fpc2 = _fpc_factor(vals2[0], k_hi) if len(vals2)>0 else 1.0
            W_hi = ss_stats["tw"].sum()
            within_sum += (S2_within / k_hi) * fpc2 * ((W_hi / W_h)**2)
        var_h = (S2_between / m_h) * fpc1 + (within_sum / m_h)
        var_sum += var_h
    return float(var_sum)

def taylor_var_ratio(y: pd.Series, x: pd.Series, w: pd.Series, strata: pd.Series, psu: pd.Series,
                     domain: Optional[pd.Series]=None, fpc_strata: Optional[pd.Series]=None) -> float:
    if domain is not None:
        y=y[domain]; x=x[domain]; w=w[domain]; strata=strata[domain]; psu=psu[domain]
        if fpc_strata is not None: fpc_strata=fpc_strata[domain]
    r = (y*w).sum() / (x*w).sum()
    z = (y - r*x)
    var_mean_z = taylor_var_mean(z, w, strata, psu, fpc_strata=fpc_strata)
    denom = (x*w).sum()
    return float(var_mean_z * ((w.sum()/denom)**2))
