# -*- coding: utf-8 -*-
"""
From logs (*.jsonl), extract top-N destination IPs and print /24 and /16 candidates.
Usage:
  python scripts/build_region_candidates.py ".\logs\log-20250816.jsonl" 30
"""
import sys, json, collections, ipaddress, re
from typing import Iterable

def iter_ips(path: str) -> Iterable[str]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            dst = obj.get("dst") or obj.get("dst_ip") or obj.get("ip_dst") or ""
            if isinstance(dst, str):
                yield dst

def is_public(ip: str) -> bool:
    try:
        ipobj = ipaddress.ip_address(ip)
        return not (ipobj.is_private or ipobj.is_loopback or ipobj.is_multicast or ipobj.is_reserved)
    except Exception:
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/build_region_candidates.py <log.jsonl> [TopN]")
        sys.exit(1)
    path = sys.argv[1]
    topn = int(sys.argv[2]) if len(sys.argv) >= 3 else 30

    ctr = collections.Counter(ip for ip in iter_ips(path) if is_public(ip))
    top = ctr.most_common(topn)

    # Aggregate into CIDRs
    cidr24 = collections.Counter()
    cidr16 = collections.Counter()
    for ip, c in top:
        try:
            ipobj = ipaddress.ip_address(ip)
            net24 = ipaddress.ip_network(f"{ipobj.exploded}/24", strict=False)
            net16 = ipaddress.ip_network(f"{ipobj.exploded}/16", strict=False)
            cidr24[str(net24)] += c
            cidr16[str(net16)] += c
        except Exception:
            continue

    print("# Top IPs")
    for ip, c in top:
        print(f"{ip}\t{c}")

    print("\n# /24 candidates (desc)")
    for cidr, c in cidr24.most_common():
        print(f"{cidr}\t{c}")

    print("\n# /16 candidates (desc)")
    for cidr, c in cidr16.most_common():
        print(f"{cidr}\t{c}")

if __name__ == "__main__":
    main()
