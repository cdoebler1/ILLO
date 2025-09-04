# scheduler.py (add dynamic-safe mutation)
import time
try:
    import gc
except ImportError:
    gc = None

_MONO = time.monotonic

class Task:
    name        = "task"
    priority    = 5          # lower = higher priority
    period_ms   = 20
    budget_ms   = 2
    enabled     = True

    def __init__(self):
        self._next_due = 0.0
        self._last_start = 0.0
        self.overruns = 0
        self.jitter_max_ms = 0.0

    def start(self, now): pass
    def step(self, now):  raise NotImplementedError
    def stop(self, now):  pass

    def _due(self, now): return now >= self._next_due
    def _schedule_next(self, now): self._next_due = now + (self.period_ms / 1000.0)
    def _on_run_begin(self, now): self._last_start = now
    def _on_run_end(self, now):
        elapsed_ms = (now - self._last_start) * 1000.0
        if elapsed_ms > self.budget_ms: self.overruns += 1
    def _update_jitter(self, now):
        ideal_prev_due = self._next_due - (self.period_ms / 1000.0)
        lateness_ms = max(0.0, (now - ideal_prev_due) * 1000.0)
        if lateness_ms > self.jitter_max_ms: self.jitter_max_ms = lateness_ms

class Scheduler:
    def __init__(self, min_idle_sleep_ms=2, gc_interval_ms=1000):
        self.tasks = []
        self._pending_add = []
        self._pending_remove = []
        self.min_idle_sleep_ms = min_idle_sleep_ms
        self.gc_interval_ms = gc_interval_ms
        self._next_gc = 0.0
        self._running = False

    def add(self, task):
        # Safe during run: queue and apply post-iteration
        self._pending_add.append(task)
        return task

    def remove(self, task):
        self._pending_remove.append(task)

    def _apply_mutations(self):
        if self._pending_remove:
            for t in self._pending_remove:
                if t in self.tasks:
                    try: t.stop(_MONO())
                    except: pass
                    self.tasks.remove(t)
            self._pending_remove = []
        if self._pending_add:
            now = _MONO()
            for t in self._pending_add:
                t._schedule_next(now)
                try: t.start(now)
                except: pass
                self.tasks.append(t)
            self._pending_add = []
            # keep deterministic order
            self.tasks.sort(key=lambda t: (t.priority, getattr(t, "name", "zzz")))

    def start(self):
        self._running = True
        self._apply_mutations()
        if gc and self.gc_interval_ms:
            now = _MONO()
            self._next_gc = now + (self.gc_interval_ms / 1000.0)

    def stop(self):
        now = _MONO()
        for t in list(self.tasks):
            try: t.stop(now)
            except: pass
        self._running = False

    def run_forever(self):
        self.start()
        try:
            while self._running:
                now = _MONO()
                if gc and self.gc_interval_ms and now >= self._next_gc:
                    gc.collect()
                    self._next_gc = now + (self.gc_interval_ms / 1000.0)

                ran = False
                for t in self.tasks:
                    if not t.enabled: continue
                    if t._due(now):
                        t._update_jitter(now)
                        t._on_run_begin(now)
                        t.step(now)
                        now2 = _MONO()
                        t._on_run_end(now2)
                        t._schedule_next(now2)
                        ran = True

                # Apply adds/removes between frames
                self._apply_mutations()

                if not ran:
                    time.sleep(self.min_idle_sleep_ms / 1000.0)
        finally:
            self.stop()

    def stats(self):
        return [{
            "name": getattr(t, "name", "task"),
            "priority": t.priority,
            "period_ms": t.period_ms,
            "budget_ms": t.budget_ms,
            "enabled": t.enabled,
            "overruns": t.overruns,
            "jitter_max_ms": round(t.jitter_max_ms, 2),
        } for t in self.tasks]
