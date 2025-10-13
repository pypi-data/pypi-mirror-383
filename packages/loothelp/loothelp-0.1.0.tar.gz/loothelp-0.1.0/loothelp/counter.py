import time
import json
from pathlib import Path
import atexit


CURRENT = Path("lootdata.json")
HISTORY = Path("loot_history.txt")


class LootCounter:
    """Tracks runs, drops, and timing."""

    def __init__(self, save_path: Path | None = None):
        self.save_path = save_path or CURRENT
        self.init()
        self.load()

        atexit.register(self.save)

    def init(self):
        self.total_runs = 0
        self.total_drops = 0
        self.last_run_start = time.time()
        self.avg_run_time = 0.0
        self.title = "Loot Overlay"

    def reset(self):
        if self.total_runs > 0:
            self.save_history()
        self.init()
        

    # ------------------- Core Logic -------------------

    def start_run(self):
        self.last_run_start = time.time()

    def finish_run(self, drop=False):
        now = time.time()
        duration = now - self.last_run_start

        self.total_runs += 1
        if drop:
            self.total_drops += 1

        # Moving average for smoother display
        if self.total_runs >= 2:
            if self.avg_run_time == 0:
                self.avg_run_time = duration
            else:
                self.avg_run_time = (
                    self.avg_run_time * (self.total_runs - 1) + duration
                ) / self.total_runs

        self.last_run_start = now
        return duration

    # ------------------- Derived Values -------------------

    def drop_rate(self):
        if self.total_runs == 0:
            return 0.0
        return (self.total_drops / self.total_runs) * 100

    # ------------------- Persistence -------------------

    def save(self):
        data = {
            "title": self.title,
            "total_runs": self.total_runs,
            "total_drops": self.total_drops,
            "avg_run_time": self.avg_run_time,
        }
        try:
            self.save_path.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Failed to save data: {e}")

    def load(self):
        if not self.save_path.exists():
            return
        try:
            data = json.loads(self.save_path.read_text())
            self.title = data.get("title", "Loot Overlay")
            self.total_runs = data.get("total_runs", 0)
            self.total_drops = data.get("total_drops", 0)
            self.avg_run_time = data.get("avg_run_time", 0.0)
        except Exception as e:
            print(f"Failed to load data: {e}")
    
    def save_history(self):
        with HISTORY.open("a") as f:
            f.write(f"{self.title}: {self.total_runs} runs, {self.total_drops} drops, {self.drop_rate():.1f}% drop rate, avg time {self.avg_run_time:.1f}s\n")
