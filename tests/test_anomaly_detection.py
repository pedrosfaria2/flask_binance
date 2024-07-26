import pytest
from price_anomaly_worker.anomaly_detection import detect_anomalies


def test_no_anomalies():
    prices = [100] * 31
    assert detect_anomalies(prices) == False


def test_single_anomaly():
    prices = [100, 101, 102, 99, 100, 101, 102, 100, 100] * 3 + [150]
    assert detect_anomalies(prices) == True


def test_multiple_anomalies():
    prices = [100, 101, 102, 99, 100, 101, 102, 100] * 4 + [150, 50]
    assert detect_anomalies(prices) == True


def test_no_data():
    prices = []
    assert detect_anomalies(prices) == False


def test_constant_data():
    prices = [100] * 31
    assert detect_anomalies(prices) == False


def test_anomalies_negative_prices():
    prices = [-100, -101, -102, -99, -100, -101, -102, -100, -100] * 3 + [-150]
    assert detect_anomalies(prices) == True


def test_anomalies_mixed_prices():
    prices = [100, -100, 102, -99, 100, -101, 102, 100] * 4 + [600]
    assert detect_anomalies(prices) == True
