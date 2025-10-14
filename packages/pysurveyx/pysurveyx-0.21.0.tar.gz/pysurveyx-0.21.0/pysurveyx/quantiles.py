
from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import Sequence, Optional, Dict, Any
from .design import SurveyDesign
from .variance import taylor_var_mean, taylor_var_mean_2stage
from .replicate import make_delete_a_group_jk, make_replicates

def _weighted_quantile(y: np.ndarray, w: np.ndarray, p: float) -> float:
    idx = np.argsort(y)
    y_s = y[idx]; w_s = w[idx]
    cw = np.cumsum(w_s)
    cutoff = p * w_s.sum()
    j = np.searchsorted(cw, cutoff, side="left")
    j = min(max(j, 0), len(y_s)-1)
    return float(y_s[j])

@dataclass
class _QResult:
    probs: np.ndarray
    quantiles: np.ndarray
    se: np.ndarray
    details: Dict[str, Any]
    def summary(self):
        out = []
        for p, q, s in zip(self.probs, self.quantiles, self.se):
            out.append(f"p={p:.3f} | q={q:.6g} | SE={s:.6g}")
        return "\n".join(out)

class SurveyQuantile:
    """
    Weighted quantiles with variance via Woodruff linearization or replicate methods.
    """
    def __init__(self, variable: str, probs: Sequence[float]=(0.5,), variance: str="taylor", replicates: Optional[tuple]=None, domain: Optional[str]=None, bandwidth: Optional[float]=None):
        assert variance in ("taylor","replicate")
        self.variable=variable; self.probs=np.array(probs, dtype=float)
        self.variance=variance; self.replicates=replicates; self.domain=domain
        self.bandwidth = bandwidth
        self.results_: Optional[_QResult] = None

    def fit(self, design: SurveyDesign):
        design.validate()
        y = design.df[self.variable].astype(float)
        w = design.weights.astype(float)
        mask = design.domain_mask(self.domain)
        y = y[mask].values; w = w[mask].values
        qs = np.array([_weighted_quantile(y, w, p) for p in self.probs])

        if self.variance=="replicate":
            if design.repweights is not None:
                R = design.repweights
            elif self.replicates is None:
                R = make_delete_a_group_jk(design.df, design.weights, design._S(), design._P(), G=30)
            else:
                kind, params = self.replicates[0], (self.replicates[1] or {})
                if kind=="dagjk":
                    R = make_delete_a_group_jk(design.df, design.weights, design._S(), design._P(), **params)
                else:
                    R = make_replicates(design.df, design.weights, design._S(), design._P(), kind=kind, **params)
            # replicate quantiles
            Qr = []
            for c in R.columns:
                wr = R[c][mask].values.astype(float)
                Qr.append([_weighted_quantile(y, wr, p) for p in self.probs])
            Qr = np.array(Qr)
            diffs = Qr - qs
            rho = (self.replicates[1].get("fay_rho") if self.replicates else None)
            if rho is None:
                var = (diffs**2).sum(axis=0)/Qr.shape[0]
            else:
                var = (diffs**2).sum(axis=0)/(Qr.shape[0]*(1-rho)**2)
            se = np.sqrt(var)
        else:
            # Woodruff linearization: Var(q_p) ≈ Var( I[Y<=q_p] ) / f(q_p)^2
            # where Var( I[Y<=q_p] ) computed via Taylor var of mean of indicator under design
            from pandas import Series
            # estimate f(q) via weighted finite difference
            se = []
            for q in qs:
                # small window h
                if self.bandwidth is None:
                    # Silverman-ish rule of thumb scaled to weighted IQR proxy
                    iqr = np.subtract(*np.percentile(y, [75,25]))
                    sigma = np.std(y)
                    s = min(sigma, iqr/1.349) if (sigma>0 and iqr>0) else (sigma if sigma>0 else 1.0)
                    h = 1.06*s*(len(y)**(-1/5)) if s>0 else max(1e-3, np.std(y)*0.1)
                else:
                    h = float(self.bandwidth)
                z = Series((y <= q).astype(float), index=np.arange(len(y)))
                # compute Taylor var of mean for indicator using design's structure
                if design.ssu is not None:
                    vF = taylor_var_mean_2stage(z, Series(w), design._S()[mask], design._P()[mask], design._Q()[mask] if design._Q() is not None else None)
                else:
                    vF = taylor_var_mean(z, Series(w), design._S()[mask], design._P()[mask])
                # density estimate at q (weighted kernel)
                denom = np.sum(w) * h
                fk = ( (w * (1/np.sqrt(2*np.pi)) * np.exp(-0.5*((y - q)/h)**2)).sum() / denom ) if denom>0 else 1e-9
                var_q = (vF / max(fk**2, 1e-18))
                se.append(np.sqrt(max(var_q, 0.0)))
            se = np.array(se)

        # cache sample & bandwidth for CI
        self._cache_ = {'y': y, 'w': w, 'h': (h if 'h' in locals() else self.bandwidth)}
        self.results_ = _QResult(self.probs, qs, se, {"method": self.variance})
        return self

    def summary(self): return self.results_.summary()

    def confint(self, level: float = 0.95) -> np.ndarray:
        """
        Woodruff inversion CIs for each requested quantile.
        Returns array shape (len(probs), 2) with [lower, upper].
        Method:
            1) compute variance of F(q) using Taylor (already done during fit)
            2) p_L = clip(p - z * sqrt(Var(F(q))), 0, 1), p_U analogously
            3) q_L = Q_w(p_L), q_U = Q_w(p_U)
        """
        from scipy.stats import norm
        if self.results_ is None:
            raise RuntimeError("Call .fit() before confint().")
        z = norm.ppf(0.5 + level/2)
        # recompute vF for each q using design passed to fit by closure is not stored;
        # we approximate using stored SE via delta: se_q ~ sqrt(vF)/f(q)  => sqrt(vF) ~ se_q * f(q)
        # To avoid re-access to design, we approximate f(q) using local kernel on the sample kept during fit.
        # Store lightweight cache during fit:
        y = self._cache_['y']; w = self._cache_['w']
        qs = self.results_.quantiles
        se_q = self.results_.se
        # Re-estimate density at q with bandwidth used in fit (cached as _h)
        h = self._cache_.get('h', None)
        ci = []
        for p, q, se in zip(self.probs, qs, se_q):
            if h is None or h <= 0:
                # fallback bandwidth
                iqr = np.subtract(*np.percentile(y, [75,25]))
                sigma = np.std(y)
                s = min(sigma, iqr/1.349) if (sigma>0 and iqr>0) else (sigma if sigma>0 else 1.0)
                hh = 1.06*s*(len(y)**(-1/5)) if s>0 else max(1e-3, np.std(y)*0.1)
            else:
                hh = h
            denom = np.sum(w) * hh
            fk = ( (w * (1/np.sqrt(2*np.pi)) * np.exp(-0.5*((y - q)/hh)**2)).sum() / denom ) if denom>0 else 1e-9
            # Var(F(q)) ≈ (se_q * f(q))^2
            vF = (se * max(fk,1e-9))**2
            pL = float(np.clip(p - z*np.sqrt(vF), 0.0, 1.0))
            pU = float(np.clip(p + z*np.sqrt(vF), 0.0, 1.0))
            qL = _weighted_quantile(y, w, pL)
            qU = _weighted_quantile(y, w, pU)
            ci.append((qL, qU))
        return np.array(ci)
