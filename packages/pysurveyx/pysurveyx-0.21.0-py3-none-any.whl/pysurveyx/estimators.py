
from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .design import SurveyDesign
from .variance import taylor_var_mean, taylor_var_mean_2stage, taylor_var_ratio
from .replicate import make_replicates, make_delete_a_group_jk

@dataclass
class _PointSE:
    estimate: float
    se: float
    n: int
    details: Dict[str, Any]
    def ci(self, level=0.95):
        from scipy.stats import norm
        z = norm.ppf(0.5 + level/2)
        return (self.estimate - z*self.se, self.estimate + z*self.se)
    def summary(self):
        lo, hi = self.ci()
        return f"Estimate={self.estimate:.6g} | SE={self.se:.6g} | 95% CI [{lo:.6g}, {hi:.6g}] | n={self.n}"

class _BaseEstimator:
    def __init__(self, variance: str="taylor", replicates: Optional[tuple]=None, domain: Optional[str]=None):
        assert variance in ("taylor","replicate")
        self.variance = variance; self.replicates = replicates; self.domain=domain
        self.results_: Optional[_PointSE] = None
    def _replicate_variance(self, point, pts):
        rho = (self.replicates[1].get("fay_rho") if self.replicates else None)
        diffs = pts - point
        if rho is None:
            return float((diffs**2).sum()/len(pts))
        return float((diffs**2).sum()/(len(pts)*(1-rho)**2))
    def _get_reps(self, design: SurveyDesign):
        if design.repweights is not None:
            return design.repweights
        if self.replicates is None:
            return make_delete_a_group_jk(design.df, design.weights, design._S(), design._P(), G=30)
        kind, params = self.replicates[0], (self.replicates[1] or {})
        if kind == "dagjk":
            return make_delete_a_group_jk(design.df, design.weights, design._S(), design._P(), **params)
        else:
            return make_replicates(design.df, design.weights, design._S(), design._P(), kind=kind, **params)

class SurveyMean(_BaseEstimator):
    def __init__(self, variable: str, **kwargs):
        super().__init__(**kwargs); self.variable=variable
    def fit(self, design: SurveyDesign):
        design.validate()
        y = design.df[self.variable]; w=design.weights
        dmask = design.domain_mask(self.domain)
        point = float((y[dmask]*w[dmask]).sum()/w[dmask].sum())
        if self.variance=="taylor":
            if design.ssu is not None:
                var = taylor_var_mean_2stage(y, w, design._S(), design._P(), design._Q(),
                                             domain=dmask,
                                             fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None),
                                             fpc_psu=(design.df[design.fpc_psu] if design.fpc_psu else None))
            else:
                var = taylor_var_mean(y, w, design._S(), design._P(), domain=dmask,
                                      fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None))
        else:
            R = self._get_reps(design)
            pts = np.array([(y[dmask]*R[c][dmask]).sum()/R[c][dmask].sum() for c in R.columns])
            var = self._replicate_variance(point, pts)
        self.results_ = _PointSE(point, float(np.sqrt(var)), int(dmask.sum()), {"variable": self.variable, "variance": self.variance})
        return self
    def summary(self): return self.results_.summary()

class SurveyTotal(SurveyMean):
    def fit(self, design: SurveyDesign):
        design.validate()
        y = design.df[self.variable]; w=design.weights
        dmask = design.domain_mask(self.domain)
        point = float((y[dmask]*w[dmask]).sum())
        if self.variance=="taylor":
            if design.ssu is not None:
                vm = taylor_var_mean_2stage(y, w, design._S(), design._P(), design._Q(),
                                            domain=dmask,
                                            fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None),
                                            fpc_psu=(design.df[design.fpc_psu] if design.fpc_psu else None))
            else:
                vm = taylor_var_mean(y, w, design._S(), design._P(), domain=dmask,
                                     fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None))
            var = vm * (w[dmask].sum()**2)
        else:
            R = self._get_reps(design)
            pts = np.array([(y[dmask]*R[c][dmask]).sum() for c in R.columns])
            var = self._replicate_variance(point, pts)
        self.results_ = _PointSE(point, float(np.sqrt(var)), int(dmask.sum()), {"variable": self.variable, "variance": self.variance})
        return self

class SurveyProportion(SurveyMean):
    def summary(self): return super().summary() + " (proportion)"

class SurveyRatio(_BaseEstimator):
    def __init__(self, y: str, x: str, **kwargs):
        super().__init__(**kwargs); self.y=y; self.x=x
    def fit(self, design: SurveyDesign):
        design.validate()
        y=design.df[self.y]; x=design.df[self.x]; w=design.weights
        dmask = design.domain_mask(self.domain)
        point = float((y[dmask]*w[dmask]).sum() / (x[dmask]*w[dmask]).sum())
        if self.variance=="taylor":
            z = (y - point*x)
            if design.ssu is not None:
                var_mean_z = taylor_var_mean_2stage(z, w, design._S(), design._P(), design._Q(),
                                                    domain=dmask,
                                                    fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None),
                                                    fpc_psu=(design.df[design.fpc_psu] if design.fpc_psu else None))
            else:
                var_mean_z = taylor_var_mean(z, w, design._S(), design._P(), domain=dmask,
                                             fpc_strata=(design.df[design.fpc_strata] if design.fpc_strata else None))
            denom = (x[dmask]*w[dmask]).sum()
            var = var_mean_z * ((w[dmask].sum()/denom)**2)
        else:
            R = self._get_reps(design)
            pts = []
            for c in R.columns:
                num = (y[dmask]*R[c][dmask]).sum()
                den = (x[dmask]*R[c][dmask]).sum()
                pts.append(num / (den if den!=0 else 1e-12))
            var = self._replicate_variance(point, np.array(pts))
        self.results_ = _PointSE(point, float(np.sqrt(var)), int(dmask.sum()), {"y":self.y,"x":self.x,"variance":self.variance})
        return self
    def summary(self): return self.results_.summary()
