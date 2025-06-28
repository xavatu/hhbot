import asyncio

from hh_service.config import server


async def main():
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
