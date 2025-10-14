
from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

def load_mini_nhanes(n: int = 2000, seed: int = 7) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 80, size=n)
    sex = rng.choice(["F","M"], size=n, p=[0.52,0.48])
    race = rng.choice(["W","B","H","O"], size=n, p=[0.62,0.12,0.19,0.07])
    income = np.exp(rng.normal(10, 0.6, size=n))
    bmi = rng.normal(27 + 0.03*(age-45) + (sex=="M")*1.0, 4.0, size=n).clip(15, 55)
    health = rng.choice(["Excellent","Good","Fair","Poor"], size=n, p=[0.3,0.45,0.2,0.05])
    strata = rng.choice(["NE","MW","S","W"], size=n, p=[.2,.22,.37,.21])
    psu = rng.integers(100, 300, size=n)
    base_w = rng.uniform(0.2, 3.5, size=n)
    p_age = 0.6 - (age-18)/200.0
    w = base_w * (1/np.clip(p_age, 0.1, 0.9))
    df = pd.DataFrame({
        "id": np.arange(1, n+1),
        "age": age,
        "sex": sex,
        "race": race,
        "income": income,
        "bmi": bmi,
        "health": health,
        "strata": strata,
        "psu": psu,
        "w": w
    })
    meta = {"name":"mini_nhanes","rows":n,"description":"Synthetic NHANES-like microdata"}
    return df, meta

def load_voter_sample(n: int = 500, seed: int = 11) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    sex = rng.choice(["F","M"], size=n, p=[0.52,0.48])
    region = rng.choice(["NE","MW","S","W"], size=n, p=[.2,.22,.37,.21])
    education = rng.choice(["HS","SomeCollege","BA","Grad"], size=n, p=[.3,.3,.25,.15])
    turnout_prob = 0.55 + (education=="BA")*0.08 + (education=="Grad")*0.12 + (region=="NE")*0.03 - (region=="S")*0.04
    turnout_prob = np.clip(turnout_prob, 0.05, 0.95)
    turnout = (rng.random(n) < turnout_prob).astype(int)
    weight = rng.uniform(0.5, 3.0, size=n)
    df = pd.DataFrame({"sex":sex,"region":region,"education":education,"turnout":turnout,"weight":weight})
    meta = {"name":"voter_sample","rows":n,"description":"Synthetic voter sample for post-strat demos"}
    return df, meta

def load_wellbeing_study(n: int = 800, seed: int = 21) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 80, size=n)
    stress = rng.normal(0,1,size=n)
    exercise = rng.integers(0,6,size=n)
    wellbeing = (50 + 0.2*(80-age) - 3*stress + 1.1*exercise + rng.normal(0,3,size=n)).clip(0,100)
    strata = rng.choice([1,2,3], size=n, p=[.4,.35,.25])
    psu = rng.integers(100, 160, size=n)
    weight = rng.uniform(0.7, 2.5, size=n)
    df = pd.DataFrame({"age":age,"stress":stress,"exercise":exercise,"wellbeing":wellbeing,"strata":strata,"psu":psu,"weight":weight})
    meta = {"name":"wellbeing_study","rows":n,"description":"Wellbeing study for GLM demos"}
    return df, meta
