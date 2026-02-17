def classify_regime(z_score):
    """
    Classifies the market volatility regime based on VIX Z-score.
    """
    if z_score < -1:
        return "SUPPRESSED"
    elif -1 <= z_score <= 1:
        return "NORMAL"
    elif 1 < z_score <= 2:
        return "ELEVATED"
    else:
        return "CRISIS"
