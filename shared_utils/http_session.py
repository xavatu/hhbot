from aiohttp import ClientSession


async def get_http_session():
    async with ClientSession() as session:
        yield session
