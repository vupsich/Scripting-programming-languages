import aiosqlite

class DataSaver:
    async def save_to_db(self, db_path, data):
        async with aiosqlite.connect(db_path) as db:
            await asyncio.sleep(2)  # Имитация задержки
            for item in data:
                await db.execute("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)",
                                 (item["userId"], item["title"], item["body"]))
            await db.commit()
