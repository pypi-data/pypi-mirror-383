import time
import asyncio
import random
import string
import redis
from rich.console import Console

console = Console()


class TairWriter:
    def __init__(self, ip:str, port:int, username:str, password:str, requests:int, batch_size:int=1, value_length:int=0, connections:int=1):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.requests = requests
        self.batch_size = batch_size
        self.value_length = value_length
        self.connections = connections
        if self.value_length <= 0:
            self._value_prefix = ""
        elif self.value_length == 1:
            self._value_prefix = "-"
        else:
            alphabet = string.ascii_letters + string.digits
            padding = "".join(random.choice(alphabet) for _ in range(self.value_length - 1))
            self._value_prefix = f"{padding}-"

    def _build_value(self, send_time_ms:int) -> str:
        if self.value_length <= 0:
            return str(send_time_ms)
        return f"{self._value_prefix}{send_time_ms}"

    async def _writer_worker(self, worker_id:int, keys_queue:asyncio.Queue):
        client = redis.asyncio.Redis(host=self.ip, port=self.port, username=self.username, password=self.password, decode_responses=True)
        try:
            while True:
                first = await keys_queue.get()
                if first is None:
                    break

                batch_keys = [first]
                while len(batch_keys) < self.batch_size:
                    try:
                        next_item = keys_queue.get_nowait()
                        if next_item is None:
                            await keys_queue.put(None)
                            break
                        batch_keys.append(next_item)
                    except asyncio.QueueEmpty:
                        break

                sec, usec = await client.time()
                send_time_ms = sec * 1000 + (usec // 1000)

                pipe = client.pipeline(transaction=False)
                for key in batch_keys:
                    pipe.set(key, self._build_value(send_time_ms))
                await pipe.execute()
        finally:
            try:
                await client.close()
            except Exception:
                pass

    async def run(self):
        setup_client = redis.asyncio.Redis(host=self.ip, port=self.port, username=self.username, password=self.password, decode_responses=True)
        try:
            await setup_client.ping()
            console.print("Successfully connected to source Tair server.", style="green")
            console.print("Flushing all data...", style="green")
            await setup_client.flushall()
            # Ensure DB is empty before proceeding
            while True:
                try:
                    size = await setup_client.dbsize()
                    if size == 0:
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.05)
        except Exception as e:
            console.print(f"Failed to connect to source Tair server: {e}", style="red")
            return

        console.print("start to Writing data to source Tair server.", style="green")
        keys_queue: asyncio.Queue = asyncio.Queue(maxsize=0)
        for k in range(self.requests):
            await keys_queue.put(str(k))
        for _ in range(self.connections):
            await keys_queue.put(None)

        start_time = time.time()
        workers = [asyncio.create_task(self._writer_worker(i, keys_queue)) for i in range(self.connections)]
        try:
            await asyncio.gather(*workers)
        finally:
            pass

        end_time = time.time()
        run_time = end_time - start_time
        console.print(f"\nTotal keys written: {self.requests}", style="bold green")
        console.print(f"pipeline: {self.batch_size}", style="bold green")
        console.print(f"connections: {self.connections}", style="bold green")
        console.print(f"extra bytes per value (-l): {self.value_length}", style="bold green")
        console.print(f"Total run time: {run_time:.4f} seconds", style="bold green")
        if run_time > 0:
            qps = self.requests / run_time
            console.print(f"Write QPS: {qps:,.2f} ops/sec", style="bold green")
