import pytest
import aresponses
from app.binance_api import fetch_symbols


@pytest.mark.asyncio
async def test_fetch_symbols():
    async with aresponses.ResponsesMockServer() as server:
        response_payload = {
            "symbols": [
                {"symbol": "BTCUSDT"},
                {"symbol": "ETHUSDT"},
                {"symbol": "BNBUSDT"}
            ]
        }

        server.add("api.binance.com", "/api/v3/exchangeInfo", "GET", response_payload)

        symbols = await fetch_symbols()

        assert symbols == ["btcusdt", "ethusdt", "bnbusdt"]
