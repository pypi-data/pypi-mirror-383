import time
import redis
import numpy as np
from rich.console import Console
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

console = Console()


class TairReader:
    def __init__(self, ip:str, port:int, username:str, password:str, requests:int):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.requests = requests

    def _parse_timestamp_ms(self, val:str) -> int:
        if '-' in val:
            ts_part = val.rsplit('-', 1)[-1]
        else:
            ts_part = val
        return int(ts_part)

    def run(self):
        client = redis.Redis(host=self.ip, port=self.port, username=self.username, password=self.password, decode_responses=True)

        try:
            client.ping()
            console.print("Successfully connected to target Tair server.", style="green")
            console.print("Flushing all data...", style="green")
            client.flushall()
            # Ensure DB is empty before proceeding
            while True:
                try:
                    size = client.dbsize()
                    if size == 0:
                        break
                except Exception:
                    pass
                time.sleep(0.05)
        except Exception as e:
            console.print(f"Failed to connect to target Tair server: {e}", style="red")
            return

        console.print("start to Reading data from target Tair server", style="green")

        def server_now_ms() -> int:
            """Helper function to get server time in milliseconds."""
            sec, usec = client.time()
            return sec * 1000 + (usec // 1000)

        latencies_counts = {}

        idx = 0
        while idx < self.requests:
            db_size = client.dbsize()
            if db_size - idx > 10:
                val = client.get(str(idx))
                if val is None:
                    continue
                try:
                    send_ms = self._parse_timestamp_ms(val)
                except Exception:
                    console.print(f"error: invalid value for key {idx}: {val}", style="red")
                    continue
                now_ms = server_now_ms()
                latency = now_ms - send_ms
                num_keys_in_batch = db_size - idx
                latencies_counts[latency] = latencies_counts.get(latency, 0) + num_keys_in_batch
                idx = db_size

        latencies_ms = []
        for latency, num in latencies_counts.items():
            latencies_ms.extend([latency] * num)

        console.print(f"max latency: {max(latencies_ms)}ms", style="bold green")
        console.print(f"average latency: {sum(latencies_ms) / len(latencies_ms)}ms", style="bold green")

        if latencies_ms:
            p50 = np.percentile(latencies_ms, 50)
            p75 = np.percentile(latencies_ms, 75)
            p90 = np.percentile(latencies_ms, 90)
            p95 = np.percentile(latencies_ms, 95)
            p99 = np.percentile(latencies_ms, 99)
            console.print(f"P50 latency: {p50}ms", style="bold green")
            console.print(f"P75 latency: {p75}ms", style="bold green")
            console.print(f"P90 latency: {p90}ms", style="bold green")
            console.print(f"P95 latency: {p95}ms", style="bold green")
            console.print(f"P99 latency: {p99}ms", style="bold green")
            # Visualization: histogram and CDF saved as PNG files
            out_dir = Path.cwd()
            try:
                plt.figure(figsize=(8, 4.5))
                plt.hist(latencies_ms, bins=50, color="#4C78A8", edgecolor="green")
                plt.title("Latency Histogram (ms)")
                plt.xlabel("Latency (ms)")
                plt.ylabel("Count")
                hist_path = out_dir / "latency_hist.png"
                plt.tight_layout()
                plt.savefig(hist_path)
                plt.close()
                console.print(f"Saved histogram to {hist_path}", style="green")

                lats_sorted = np.sort(np.array(latencies_ms))
                y = np.arange(1, len(lats_sorted) + 1) / len(lats_sorted)
                plt.figure(figsize=(8, 4.5))
                plt.plot(lats_sorted, y, color="#F58518")
                plt.title("Latency CDF")
                plt.xlabel("Latency (ms)")
                plt.ylabel("CDF")
                cdf_path = out_dir / "latency_cdf.png"
                plt.tight_layout()
                plt.savefig(cdf_path)
                plt.close()
                console.print(f"Saved CDF to {cdf_path}", style="green")
            except Exception as viz_err:
                console.print(f"Failed to render plots: {viz_err}", style="red")
