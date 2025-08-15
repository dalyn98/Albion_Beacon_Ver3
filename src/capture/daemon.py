# -*- coding: utf-8 -*-
"""
Capture Daemon (patched 2025-08-16)
- settings.json UTF-8-SIG safe reader (BOM tolerant)
- Interface resolver: Wi-Fi/Ethernet/GUID -> \\Device\\NPF_{GUID}
- Region fallback order: hint.region -> last_region -> settings.region
- ShareEngine: send only if Nick validated (temporary manual pass ok)
- Only send latest state periodically (debounced heartbeat)
"""
from __future__ import annotations

import json
import os
import sys
import time
import uuid
import queue
import threading
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.json")
OUTBOX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outbox")

def read_settings_utf8_sig(path: str) -> Dict[str, Any]:
    """Read JSON allowing UTF-8 BOM (utf-8-sig)."""
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def write_json_no_bom(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def resolve_iface(hint: Optional[str]) -> Optional[str]:
    """
    Try to resolve common interface hints to Npcap device form.
    Accepts:
      - Raw Npcap device: \\\\Device\\\\NPF_{GUID}
      - GUID only: {GUID}
      - Friendly names containing 'Wi-Fi' / 'Ethernet' / '무선' / '이더넷'
    Returns normalized device string or None.
    """
    if not hint:
        return None
    h = hint.strip()
    # Already a device path
    if h.startswith("\\\\Device\\\\NPF_"):
        return h
    # GUID-only
    if h.startswith("{") and h.endswith("}") and len(h) > 20:
        return "\\\\Device\\\\NPF_" + h.strip("{}")
    # Heuristics for friendly names → leave as-is; Npcap accepts names like "Wi-Fi" too (WinPcapCompat)
    # If user gives 'Wi-Fi' or 'Ethernet', keep it. For partial 'wifi', normalize to 'Wi-Fi'.
    low = h.lower()
    if "wi-fi" in low or "wifi" in low or "무선" in low:
        return "Wi-Fi"
    if "ethernet" in low or "이더넷" in low or "lan" in low:
        return "Ethernet"
    # If user pasted GUID without braces
    if len(h) >= 32 and all(c in "0123456789abcdef-{}" for c in low):
        guid = h.strip("{}")
        return "\\\\Device\\\\NPF_" + guid
    # As a last resort, return original string
    return h

@dataclass
class Heartbeat:
    nick: str
    region: str
    iface: Optional[str]
    ts: int
    type: str = "heartbeat"
    version: str = "v0.5.0-patch-2025-08-16"

class ShareEngine:
    """
    Minimal 'upload' engine:
    - Writes JSON files to ./outbox
    - Debounces by only writing the latest state each interval
    - Sends nothing if Nick validation not passed
    """
    def __init__(self, upload_enabled: bool, nick_valid: bool, interval_sec: int) -> None:
        self.upload_enabled = upload_enabled
        self.nick_valid = nick_valid
        self.interval_sec = max(5, int(interval_sec or 60))
        self._q: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=1)
        self._stop = threading.Event()
        os.makedirs(OUTBOX_DIR, exist_ok=True)

    def update_latest(self, payload: Dict[str, Any]) -> None:
        # Keep only the most recent payload in the queue
        try:
            while True:
                self._q.get_nowait()
        except Exception:
            pass
        try:
            self._q.put_nowait(payload)
        except Exception:
            pass

    def run(self) -> None:
        next_tick = time.time()
        while not self._stop.is_set():
            now = time.time()
            if now < next_tick:
                time.sleep(min(0.25, next_tick - now))
                continue
            next_tick = now + self.interval_sec
            if not (self.upload_enabled and self.nick_valid):
                continue
            try:
                latest = self._q.get_nowait()
            except Exception:
                latest = None
            if latest:
                fname = f"hb-{int(now)}-{uuid.uuid4().hex[:6]}.json"
                path = os.path.join(OUTBOX_DIR, fname)
                write_json_no_bom(path, latest)

    def stop(self) -> None:
        self._stop.set()

def pick_region(hint_region: Optional[str], last_region: Optional[str], settings_region: str) -> str:
    return hint_region or last_region or settings_region

def main():
    try:
        settings = read_settings_utf8_sig(SETTINGS_PATH)
    except FileNotFoundError:
        print("settings.json not found. Exiting.", file=sys.stderr)
        sys.exit(1)

    nick = settings.get("nick") or settings.get("Nick") or ""
    upload_enabled = bool(settings.get("upload", {}).get("enabled", False) or settings.get("UploadEnabled"))
    hb_sec = int(settings.get("heartbeat", {}).get("sec", settings.get("HeartbeatSec", 120)) or 120)
    iface_hint = settings.get("capture", {}).get("interface") or settings.get("Interface")
    bpf = settings.get("capture", {}).get("bpf", settings.get("BPF"))
    settings_region = settings.get("region") or settings.get("Region") or "UNKNOWN"

    # Temporary manual pass; user can toggle this in settings via helper script
    nick_valid = bool(settings.get("NickValidated", True))

    # In-memory state that a real decoder would keep
    last_region = settings.get("last_region")
    hint = settings.get("hint", {})
    hint_region = (hint or {}).get("region")

    region = pick_region(hint_region, last_region, settings_region)
    iface = resolve_iface(iface_hint)

    se = ShareEngine(upload_enabled=upload_enabled, nick_valid=nick_valid, interval_sec=hb_sec)
    t = threading.Thread(target=se.run, daemon=True)
    t.start()

    print("[daemon] started")
    print(f"  nick={nick!r}, nick_valid={nick_valid}, upload_enabled={upload_enabled}, hb_sec={hb_sec}")
    print(f"  iface_hint={iface_hint!r} -> resolved={iface!r}")
    print(f"  bpf={bpf!r}")
    print(f"  region(hint->last->settings)={hint_region!r}->{last_region!r}->{settings_region!r} => {region!r}")

    try:
        while True:
            hb = Heartbeat(nick=nick, region=region, iface=iface, ts=int(time.time()))
            se.update_latest(asdict(hb))
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        se.stop()
        print("[daemon] stopped")

if __name__ == "__main__":
    main()
