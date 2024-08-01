from client import main
import asyncio
from tqdm import tqdm
import time

# chunk_ids = range(1, 10, 2)
chunk_ids = [3]

async def mass():
    for chunk_id in chunk_ids:
        client_counts = [1, 8, 16, 50, 100, 150, 200]
        for client_count in tqdm(client_counts):
            print(f"Testing with {client_count} clients and chunk {chunk_id}")
            # TODO: change this below when you want to test sse/sr/ws
            await main("ws", client_count, chunk_id)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(mass())
