
from __future__ import annotations
import numpy as np, pandas as pd
from dataclasses import dataclass
from typing import Sequence, Optional, Dict, Any
from patsy import dmatrices
from .design import SurveyDesign
from .replicate import make_delete_a_group_jk, make_replicates

@dataclass
class QuantRegResult:
    tau: np.ndarray
    coef: np.ndarray   # shape (T, p)
    se: np.ndarray     # shape (T, p)
    names: list[str]
    details: Dict[str, Any]
    def summary(self):
        out = []
        for i, t in enumerate(self.tau):
            out.append(f"tau = {t:.2f}")
            for name, b, s in zip(self.names, self.coef[i], self.se[i]):
                z = b/s if s>0 else np.nan
                out.append(f"  {name:15s} {b: .6g} (SE {s:.6g}) z={z:.3g}")
        return "\n".join(out)

class SurveyQuantileRegression:
    def __init__(self, formula: str, tau: Sequence[float]=(0.5,), variance: str="replicate", replicates: Optional[tuple]=None, max_iter: int=1000, lr: float=0.1, tol: float=1e-6, loss: str="pinball", alpha: float=0.1):
        assert variance in ("replicate",), "For now, SEs via replicate only."
        self.formula=formula; self.tau=np.array(tau, dtype=float)
        self.variance=variance; self.replicates=replicates
        self.max_iter=max_iter; self.lr=lr; self.tol=tol
        assert loss in ("pinball","sal")
        self.loss=loss; self.alpha=float(alpha)
        self._res=None

    def _pinball_grad(self, X, y, w, b, tau):
        r = y - X@b
        g = - X.T @ (w * (tau - (r < 0).astype(float)))
        return g

    def _sal_grad(self, X, y, w, b, tau, alpha):
        r = y - X@b
        s = 1/(1+np.exp(-r/alpha))  # sigmoid(r/alpha)
        # grad of smooth pinball approx: -(tau-1 + s) * X^T w
        return - X.T @ (w * ((tau-1) + s))

    def _fit_tau(self, X, y, w, tau):
        p = X.shape[1]
        b = np.zeros(p)
        lr = self.lr
        for it in range(self.max_iter):
            g = self._pinball_grad(X, y, w, b, tau) if self.loss=="pinball" else self._sal_grad(X, y, w, b, tau, self.alpha)
            b_new = b - lr * g / (np.linalg.norm(g) + 1e-12)
            if np.max(np.abs(b_new - b)) < self.tol:
                b = b_new; break
            b = b_new
        return b

    def fit(self, design: SurveyDesign):
        df = design.df.copy()
        y, X = dmatrices(self.formula, data=df, return_type="dataframe")
        y = y.values.flatten()
        X = X.values
        w = design.weights.values.astype(float)
        names = ["Intercept"] + [n for n in X.dtype.names] if isinstance(X, np.void) else list(dmatrices(self.formula, data=df, return_type="dataframe")[1].columns)
        coefs = []
        for t in self.tau:
            coefs.append(self._fit_tau(X, y, w, t))
        coefs = np.vstack(coefs)

        # replicate SEs
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
        reps = []
        for c in R.columns:
            wr = R[c].values.astype(float)
            rr = []
            for t in self.tau:
                rr.append(self._fit_tau(X, y, wr, t))
            reps.append(np.vstack(rr))
        reps = np.stack(reps)  # (B, T, p)
        rho = (self.replicates[1].get("fay_rho") if self.replicates else None)
        if rho is None:
            var = ((reps - coefs[None,:,:])**2).sum(axis=0)/reps.shape[0]
        else:
            var = ((reps - coefs[None,:,:])**2).sum(axis=0)/(reps.shape[0]*(1-rho)**2)
        se = np.sqrt(var)
        self._res = QuantRegResult(self.tau, coefs, se, names, {"replicates": R.shape[1]})
        return self

    def summary(self):
        return self._res.summary()
