from dataclasses import dataclass
from typing import Optional, Dict, Any
import ipaddress

@dataclass
class LocationHint:
    region: Optional[str] = None
    pos: Optional[dict] = None

class Locator:
    def __init__(self, region_map: Dict[str, Any]):
        self.region_map = region_map

    def guess_region(self, dst_ip: str):
        for prefix, region in self.region_map.get("ip_prefixes", {}).items():
            try:
                if ipaddress.ip_address(dst_ip) in ipaddress.ip_network(prefix):
                    return region
            except Exception:
                pass
        return None

    def infer(self, packet_meta: dict) -> LocationHint:
        dst = packet_meta.get("dst","").split(":")[0]
        reg = self.guess_region(dst) if dst else None
        return LocationHint(region=reg, pos=None)
