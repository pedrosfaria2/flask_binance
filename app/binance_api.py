import aiohttp


async def fetch_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            symbols = [symbol['symbol'].lower() for symbol in data['symbols']]
            return symbols
