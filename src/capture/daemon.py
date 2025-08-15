# Placeholder capture daemon (structure only)
import json, time, pathlib
from src.decode.locator import Locator, LocationHint
import socket

def iter_fake_packets():
    # 데모: 서버 IP 대역을 샘플로 흘림
    dsts = ["52.76.10.1:30200", "18.140.1.1:30200", "52.74.1.1:30200"]
    while True:
        yield {"src": "192.168.0.5:50123", "dst": dsts[int(time.time()) % len(dsts)], "len": 300}
        time.sleep(1)

def main():
    logs = pathlib.Path("logs"); logs.mkdir(exist_ok=True)
    # 지역 매핑
    import json as _j, pathlib as _p
    region_map = _j.loads(_p.Path("src/decode/region_map.json").read_text(encoding="utf-8"))
    locator = Locator(region_map)
    fn = logs / f"log-{time.strftime('%Y%m%d')}.jsonl"
    with fn.open("a", encoding="utf-8") as f:
        for pkt in iter_fake_packets():
            dst_ip = pkt["dst"].split(":")[0]
            hint: LocationHint = locator.infer({"dst": pkt["dst"]})
            rec = {
                "ts": int(time.time()),
                "dir": "out",
                "src": pkt["src"],
                "dst": pkt["dst"],
                "len": pkt["len"],
                "proto": "udp",
                "decoded": {"region": hint.region, "pos": None, "rules": (["region_hit"] if hint.region else [])}
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
