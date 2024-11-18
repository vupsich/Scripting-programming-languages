import asyncio
import aiohttp

class DataLoader:
    async def fetch_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                await asyncio.sleep(2)  # Имитация задержки
                return await response.json()