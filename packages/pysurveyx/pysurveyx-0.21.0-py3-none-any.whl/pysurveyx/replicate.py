
from __future__ import annotations
import numpy as np, pandas as pd
from typing import Optional
from .exceptions import SurveyError

def _hadamard(n: int) -> np.ndarray:
    def H(m):
        if m==1: return np.array([[1]])
        Hm = H(m//2)
        return np.block([[Hm, Hm],[Hm, -Hm]])
    m = 1
    while m < n: m *= 2
    return H(m)

def make_replicates(df: pd.DataFrame, weight: pd.Series, strata: pd.Series, psu: pd.Series, 
                    kind: str="brr", B: int=80, fay_rho: Optional[float]=None, random_state: int=123) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    W = weight.astype(float).copy()
    reps = []
    names = []

    if kind == "jk1":
        for s, g in df.groupby(strata.name):
            psus = g[psu.name].unique()
            for p in psus:
                w = W.copy()
                w[(df[strata.name]==s) & (df[psu.name]==p)] = 0.0
                reps.append(w); names.append(f"jk1_{s}_{p}")
        R = pd.concat(reps, axis=1); R.columns = names
        return R

    if kind == "brr":
        c = df.groupby(strata.name)[psu.name].nunique()
        if (c != 2).any():
            raise SurveyError("BRR requires exactly 2 PSUs per stratum.")
        H = len(c)
        Hmat = _hadamard(H)
        rows = Hmat if Hmat.shape[0] >= B else np.tile(Hmat, (int(np.ceil(B/Hmat.shape[0])),1))
        rows = rows[:B,:H]
        strata_levels = list(c.index)
        for b in range(B):
            w = W.copy()
            for j, s in enumerate(strata_levels):
                sign = rows[b, j]
                g = df[df[strata.name]==s]
                psus = g[psu.name].unique()
                p1, p2 = psus[0], psus[1]
                if fay_rho is None:
                    factor_keep, factor_drop = 2.0, 0.0
                else:
                    factor_keep, factor_drop = (1+fay_rho), (1-fay_rho)
                keep = p1 if sign>0 else p2
                drop = p2 if sign>0 else p1
                w[(df[strata.name]==s) & (df[psu.name]==keep)] *= factor_keep
                w[(df[strata.name]==s) & (df[psu.name]==drop)] *= factor_drop
            reps.append(w); names.append(f"brr_{b}")
        R = pd.concat(reps, axis=1); R.columns = names
        return R

    if kind == "bootstrap":
        strata_levels = df[strata.name].unique()
        for b in range(B):
            w = W.copy()*0.0
            for s in strata_levels:
                g = df[df[strata.name]==s]
                psus = g[psu.name].nunique()
                draws = rng.choice(g[psu.name].unique(), size=psus, replace=True)
                for p in draws:
                    sel = (df[strata.name]==s) & (df[psu.name]==p)
                    w[sel] += W[sel]
            reps.append(w); names.append(f"boot_{b}")
        R = pd.concat(reps, axis=1); R.columns = names
        return R

    raise SurveyError(f"Unknown replicate kind: {kind}")

def make_delete_a_group_jk(df: pd.DataFrame, weight: pd.Series, strata: pd.Series, psu: pd.Series,
                           G: int=30, random_state: int=123) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    W = weight.astype(float).copy()
    psu_df = df[[strata.name, psu.name]].drop_duplicates().copy()
    psu_df["group"] = -1
    for s, g in psu_df.groupby(strata.name):
        m = len(g)
        Gs = min(G, m)
        groups = np.array(list(range(Gs)))
        assign = np.tile(groups, int(np.ceil(m/Gs)))[:m]
        rng.shuffle(assign)
        psu_df.loc[g.index, "group"] = assign
    reps = []
    names = []
    merged = df.merge(psu_df, on=[strata.name, psu.name], how="left")
    groups_all = sorted(psu_df["group"].unique().tolist())
    for g in groups_all:
        w = W.copy()
        mask_del = (merged["group"]==g)
        w[mask_del] = 0.0
        for s, block in merged.groupby(strata.name):
            m = block["group"].nunique()
            if m > 1:
                factor = m/(m-1)
                idx = (merged[strata.name]==s) & (merged["group"]!=g)
                w[idx] *= factor
        reps.append(w); names.append(f"dagjk_{int(g)}")
    R = pd.concat(reps, axis=1); R.columns = names
    return R
