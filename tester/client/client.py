import time
import aiohttp
import sys
import aiohttp.client_exceptions
import websockets
import json
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
import os

c2c_full = {}
s_full = {}
between_reqs = {}
server_mem = {}

async def sse(url: str, client_num: int, title: str, mem: bool):
    # Set the start time and make a request to the server
    start_time = time.time()
    last_server_time = 0
    chunk_times = []

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(100*60)) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return

                async for line in response.content:
                    client_time = time.time()
                    line = line.decode('utf-8').replace("data: ", "").strip()
                    if line:
                        try:
                            line = json.loads(line)

                            if mem:
                                # Recording memory usage
                                mem = line['memory_usage'] / 1024 / 1024
                                server_mem[title] = server_mem.get(title, []) + [mem]

                            else:
                                last_server_time = float(line['server_time'])

                                # Add client time to chunk_times used for between_reqs
                                chunk_times.append(client_time)
                        except json.JSONDecodeError:
                            print("JSON ERROR!")
                            print(line)
                            pass
        # print(f"Connection closed {client_num}")

        if not mem:
            end_time = time.time()
            c2c_full[title] = c2c_full.get(title, []) + [end_time - start_time]

            s_full[title] = s_full.get(title, []) + [float(last_server_time)]

            # Using the chunk_times list, calculate the time between requests
            between_reqs[title] = between_reqs.get(title, []) + [(chunk_times[i+1] - chunk_times[i]) for i in range(len(chunk_times) - 1)]
    except aiohttp.client_exceptions.ClientPayloadError as e:
        print(e)
        return

async def ws(url: str, client_num: int, title: str, mem: bool, chunk_id: int):
    start_time = 0.0
    end_time = 0.0
    try:
        async with websockets.connect(url, ping_interval=None, ping_timeout=None, open_timeout=None, close_timeout=None, max_queue=None, max_size=None) as ws:
            chunk_times = []
            await ws.send(str(chunk_id))
            start_time = time.time()
            async for line in ws:
                try:
                    line = json.loads(line)
                    client_time = time.time()
                    if line.get("msg") == "\\END":
                        if not mem:
                            end_time = time.time()
                            s_full[title] = s_full.get(title, []) + [line.get("server_time")]
                        break
                    if line:
                        if mem:
                            # Recording memory usage
                            mem = line['memory_usage'] / 1024 / 1024
                            server_mem[title] = server_mem.get(title, []) + [mem]
                        
                        else:
                            # Add client time to chunk_times used for between_reqs
                            chunk_times.append(client_time)

                except Exception as e:
                    print(e)
                    break
            await ws.close()
        
        if not mem:
            c2c_full[title] = c2c_full.get(title, []) + [end_time - start_time]

            # Using the chunk_times list, calculate the time between requests
            between_reqs[title] = between_reqs.get(title, []) + [(chunk_times[i+1] - chunk_times[i]) for i in range(len(chunk_times) - 1)]
    except Exception as e:
        print(type(e))
        return

async def main(method: str, client_count, chunk_id):
    CLIENT_COUNT = client_count
    CHUNK_ID = chunk_id

    c2c_full.clear()
    s_full.clear()
    between_reqs.clear()
    server_mem.clear()


    # if method == "all":
    #     print("Testing with all methods")
    #     # open a pd dataframe to store the latencies

    #     print("StreamingResponse")
    #     clients = [sse(f"http://10.1.160.77:8000?id={CHUNK_ID}", client_id, "StreamingResponse", False) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*clients)
    #     clients = [sse(f"http://10.1.160.77:8001?id={CHUNK_ID}", client_id, "StreamingResponse", True) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*clients)

    #     print("SSE")
    #     clients = [sse(f"http://localhost:8000?id={CHUNK_ID}", client_id, "SSE", False) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*clients)
    #     clients = [sse(f"http://localhost:8001?id={CHUNK_ID}", client_id, "SSE", True) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*clients)

    #     print("WS")
    #     wsclients = [ws("ws://10.1.160.81:8000", client_id, "WebSocket", False, CHUNK_ID) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*wsclients)
    #     wsclients = [ws("ws://10.1.160.81:8001", client_id, "WebSocket", True, CHUNK_ID) for client_id in range(CLIENT_COUNT)]
    #     await asyncio.gather(*wsclients)

    if method == "sr":
        print("Testing with StreamingResponse")
        
        clients = [sse(f"http://10.1.203.175:8000?id={CHUNK_ID}", client_id, "StreamingResponse", False) for client_id in range(CLIENT_COUNT)]
        await asyncio.gather(*clients)
        # clients = [sse(f"http://10.1.203.175:8001?id={CHUNK_ID}", client_id, "StreamingResponse", True) for client_id in range(CLIENT_COUNT)]
        # await asyncio.gather(*clients)

    elif method == "sse":
        print("Testing with Server-Sent Events")
        
        clients = [sse(f"http://10.1.203.175:8000?id={CHUNK_ID}", client_id, "SSE", False) for client_id in range(CLIENT_COUNT)]
        await asyncio.gather(*clients)
        # clients = [sse(f"http://10.1.203.175:8001?id={CHUNK_ID}", client_id, "SSE", True) for client_id in range(CLIENT_COUNT)]
        # await asyncio.gather(*clients)

    elif method == "ws":
        print("Testing with WebSockets")
        wsclients = [ws("ws://10.1.203.175:8000", client_id, "WebSocket", False, CHUNK_ID) for client_id in range(CLIENT_COUNT)]
        await asyncio.gather(*wsclients)
        # wsclients = [ws("ws://10.1.203.175:8001", client_id, "WebSocket", True, CHUNK_ID) for client_id in range(CLIENT_COUNT)]
        # await asyncio.gather(*wsclients)
    else:
        print("Invalid test type")
        sys.exit()
    
    test_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    os.makedirs(f"results/{test_time}", exist_ok=True)

    c2c = pd.DataFrame(c2c_full)
    c2c.to_csv(f"results/{test_time}/client_to_client_full_time.csv")

    server_time = pd.DataFrame(s_full)
    server_time.to_csv(f"results/{test_time}/server_full_time.csv")

    between = pd.DataFrame(between_reqs)
    between.to_csv(f"results/{test_time}/between_chunks.csv")

    # mem = pd.DataFrame(server_mem)
    # mem.to_csv(f"results/{test_time}/server_memory_usage.csv")

    with open(f"results/{test_time}/metadata.json", "w") as f:
        f.write(json.dumps({
            "client_count": CLIENT_COUNT,
            "chunk_id": CHUNK_ID,
            "method": method,
            "test_time": test_time,
            "no_memory": False
        }))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], 200, 3))