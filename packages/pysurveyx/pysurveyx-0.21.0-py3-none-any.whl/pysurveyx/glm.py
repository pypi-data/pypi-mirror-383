
from __future__ import annotations
import numpy as np, pandas as pd
from patsy import dmatrices, dmatrix
from typing import Optional
from .design import SurveyDesign
from .replicate import make_replicates, make_delete_a_group_jk

class SurveyGLM:
    def __init__(self, formula: str, family: str="gaussian", max_iter: int=100, tol: float=1e-8,
                 variance: str="taylor", replicates: Optional[tuple]=None, domain: Optional[str]=None):
        assert family in ("gaussian","binomial")
        assert variance in ("taylor","replicate")
        self.formula=formula; self.family=family; self.max_iter=max_iter; self.tol=tol
        self.variance=variance; self.replicates=replicates; self.domain=domain
        self._res=None

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

    def fit(self, design: SurveyDesign):
        design.validate()
        df = design.df.copy()
        mask = design.domain_mask(self.domain)
        y, X = dmatrices(self.formula, data=df, return_type="dataframe")
        y = y.iloc[mask.values,:].values
        X = X.iloc[mask.values,:].values
        w = design.weights.iloc[mask.values].values.reshape(-1,1)
        b = np.zeros((X.shape[1],1))
        for _ in range(self.max_iter):
            eta = X @ b
            if self.family=="gaussian":
                mu = eta; var = np.ones_like(mu); gprime = np.ones_like(mu)
            else:
                mu = 1/(1+np.exp(-eta)); var = mu*(1-mu); gprime = 1/(mu*(1-mu))
            z = eta + (y-mu)*gprime
            W = (w.flatten()*var.flatten()).clip(min=1e-12)
            WX = X * W[:,None]
            XtWX = X.T @ WX
            XtWz = X.T @ (W[:,None]*z)
            b_new = np.linalg.solve(XtWX, XtWz)
            if np.max(np.abs(b_new-b)) < self.tol:
                b = b_new; break
            b = b_new

        if self.variance=="taylor":
            mu = (X @ b) if self.family=="gaussian" else 1/(1+np.exp(-(X@b)))
            if self.family=="gaussian":
                W = w.flatten()
            else:
                W = (w.flatten() * (mu*(1-mu)).flatten()).clip(min=1e-12)
            WX = X * W[:,None]
            bread = np.linalg.inv(X.T @ WX)
            scores = []
            psu_ids = design._P()[mask].values
            for uid in np.unique(psu_ids):
                idx = (psu_ids==uid)
                Xi = X[idx,:]; ri = (y[idx,:] - ( (Xi @ b) if self.family=="gaussian" else 1/(1+np.exp(-(Xi@b))) ))
                Wi = W[idx]
                Si = Xi.T @ (Wi[:,None] * ri)
                scores.append(Si)
            meat = sum([S @ S.T for S in scores])
            cov = bread @ meat @ bread
            se = np.sqrt(np.diag(cov))
        else:
            R = self._get_reps(design)
            def coef_from_w(wrep):
                yR, XR = dmatrices(self.formula, data=design.df, return_type="dataframe")
                yR = yR.iloc[mask.values,:].values
                XR = XR.iloc[mask.values,:].values
                wr = wrep[mask].values.reshape(-1,1)
                b = np.zeros((XR.shape[1],1))
                for _ in range(self.max_iter):
                    eta = XR @ b
                    if self.family=="gaussian":
                        mu = eta; var = np.ones_like(mu); gprime = np.ones_like(mu)
                    else:
                        mu = 1/(1+np.exp(-eta)); var = mu*(1-mu); gprime = 1/(mu*(1-mu))
                    z = eta + (yR-mu)*gprime
                    W = (wr.flatten()*var.flatten()).clip(min=1e-12)
                    WX = XR * W[:,None]
                    XtWX = XR.T @ WX
                    XtWz = XR.T @ (W[:,None]*z)
                    b_new = np.linalg.solve(XtWX, XtWz)
                    if np.max(np.abs(b_new-b)) < self.tol:
                        b = b_new; break
                    b = b_new
                return b.flatten()
            reps = np.vstack([coef_from_w(R[c]) for c in R.columns])
            point = b.flatten()
            rho = (self.replicates[1].get("fay_rho") if self.replicates else None)
            var = np.zeros_like(point)
            for j in range(len(point)):
                diffs = reps[:,j] - point[j]
                var[j] = (diffs**2).sum()/len(reps) if rho is None else (diffs**2).sum()/(len(reps)*(1-rho)**2)
            se = np.sqrt(var)

        names = ["Intercept"] + [n for n in dmatrix(self.formula.split("~")[1], data=df, return_type="dataframe").design_info.column_names if n!="Intercept"]
        self._res = {"coef": b.flatten(), "se": se, "names": names}
        return self

    def summary(self):
        out = ["Coef	SE	z	p"]
        from scipy.stats import norm
        for name, b, se in zip(self._res["names"], self._res["coef"], self._res["se"]):
            z = b/se if se>0 else np.nan
            p = 2*(1-norm.cdf(abs(z))) if np.isfinite(z) else np.nan
            out.append(f"{name}	{b:.6g}	{se:.6g}	{z:.3g}	{p:.3g}")
        return "\n".join(out)
