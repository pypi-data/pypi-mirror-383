
from __future__ import annotations
import numpy as np, pandas as pd
from typing import Optional, List, Dict, Literal
from .design import SurveyDesign
from .estimators import SurveyMean, SurveyTotal, SurveyProportion

def make_domain(design: SurveyDesign, expr: str, *, zero_outside: bool=True, out_weight_col: Optional[str]=None) -> SurveyDesign:
    """
    Create a domain (subpopulation) design. By default, keeps full sample but sets weights=0 outside domain,
    preserving correct variance structure across strata/PSUs.
    """
    d = design.copy()
    mask = d.df.eval(expr).astype(bool)
    if zero_outside:
        col = out_weight_col or (d.weight or "__w__")
        w = d.weights.copy()
        w[~mask] = 0.0
        d.df[col] = w
        d.weight = col
    else:
        d.df = d.df.loc[mask].copy()
    return d

def survey_tabulate(design: SurveyDesign, by: List[str], stat: Literal["mean","total","proportion"], var: Optional[str]=None) -> pd.DataFrame:
    """
    Convenience tabulation over groups using survey estimators.
    """
    rows = []
    for keys, g in design.df.groupby(by):
        sub = design.copy()
        sub.df = g.copy()
        if stat=="mean":
            est = SurveyMean(var).fit(sub)
            rows.append((*((keys,) if not isinstance(keys, tuple) else keys), "mean", est.results_.estimate, est.results_.se, est.results_.n))
        elif stat=="total":
            est = SurveyTotal(var).fit(sub)
            rows.append((*((keys,) if not isinstance(keys, tuple) else keys), "total", est.results_.estimate, est.results_.se, est.results_.n))
        elif stat=="proportion":
            if var is None:
                raise ValueError("var must be provided for proportion")
            est = SurveyProportion(var).fit(sub)
            rows.append((*((keys,) if not isinstance(keys, tuple) else keys), "prop", est.results_.estimate, est.results_.se, est.results_.n))
        else:
            raise ValueError("Unknown stat")
    cols = by + ["stat","estimate","se","n"]
    return pd.DataFrame(rows, columns=cols)


def domain_calibrate(design: SurveyDesign, domain: str, population_totals: dict, *, strategy: str="entropy_bounded", normalize: bool=True, bounds=(0.3,3.0), **kwargs):
    """Calibrate within a subpopulation using external totals (shares or counts).
    If normalize=True and totals look like shares (sum≈1), convert to totals using domain weight sum.
    """
    from .poststrat import calibrate
    mask = design.df.eval(domain).astype(bool)
    dsum = float(design.weights[mask].sum())
    cat_targets = {}
    for k, v in population_totals.items():
        total_sum = sum(v.values())
        if normalize and 0.99 <= total_sum <= 1.01:
            cat_targets[k] = {kk: dsum*vv for kk,vv in v.items()}
            target_mode = 'total'
        else:
            cat_targets[k] = v
            target_mode = 'total'
    res = calibrate(design, categorical_margins=cat_targets, categorical_targets=target_mode, strategy=strategy, bounds=bounds, domain=domain, zero_outside=True, **kwargs)
    return res
