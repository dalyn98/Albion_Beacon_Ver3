import time, threading, queue, json, os

DEFAULT_HEARTBEAT_SEC = 120
AUTO_OFF_NO_RX_SEC = 600
AUTO_OFF_STATIONARY_SEC = 1800

class ShareEngine:
    def __init__(self, outbox_path: str, hb_sec:int=DEFAULT_HEARTBEAT_SEC):
        self.enabled = False
        self.hb_sec = hb_sec
        self.outbox_path = outbox_path
        self._q = queue.Queue()
        self._t = None
        self._last_rx = time.time()
        self._last_pos = None
        os.makedirs(outbox_path, exist_ok=True)

    def set_enabled(self, on: bool):
        self.enabled = on

    def submit_local_state(self, nick:str, region:str, pos:dict, party:int|None):
        now = time.time()
        stationary = (self._last_pos == pos and pos is not None)
        self._last_pos = pos
        self._last_rx = now
        if stationary and (now - self._last_rx) > AUTO_OFF_STATIONARY_SEC:
            self.enabled = False
        payload = {"nick": nick, "region": region, "pos": pos, "party": party, "ts": int(now)}
        self._q.put(payload)

    def _loop(self):
        last = 0
        while self.enabled:
            if time.time() - self._last_rx > AUTO_OFF_NO_RX_SEC:
                self.enabled = False
                break
            if time.time() - last >= self.hb_sec:
                latest = None
                try:
                    while True:
                        latest = self._q.get_nowait()
                except queue.Empty:
                    pass
                if latest:
                    fn = os.path.join(self.outbox_path, f"hb-{int(time.time())}.json")
                    with open(fn, "w", encoding="utf-8") as f:
                        json.dump(latest, f, ensure_ascii=False)
                last = time.time()
            time.sleep(0.2)

    def start(self):
        if self._t and self._t.is_alive():
            return
        self.enabled = True
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()

    def stop(self):
        self.enabled = False
