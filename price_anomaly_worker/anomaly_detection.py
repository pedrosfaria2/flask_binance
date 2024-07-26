import numpy as np
from scipy.stats import zscore


def detect_anomalies(prices, threshold=3.0):
    z_scores = zscore(prices)
    anomalies = np.where(np.abs(z_scores) > threshold)
    return anomalies[0].size > 0
