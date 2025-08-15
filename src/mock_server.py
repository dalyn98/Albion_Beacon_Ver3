from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import time, random

app = FastAPI(title="ALbion_Beacon Local API (Mock)", version="0.1.0")

class Pos(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)

class LocationHeartbeat(BaseModel):
    nick: str
    region: str
    pos: Optional[Pos] = None
    party: Optional[int] = Field(default=None, ge=1, le=20)
    ts: int

class Nearby(BaseModel):
    nick: str
    dist: int = Field(ge=0)
    region: str
    pos: Optional[Pos] = None

@app.get("/v1/health")
def health():
    return {"ok": True, "ts": int(time.time())}

@app.post("/v1/auth/gate")
def auth_gate(payload: dict):
    nick = payload.get("nick") or "hyuna"
    gm = bool(payload.get("gm", False))
    return {"nick": nick, "gm": gm}

@app.post("/v1/heartbeat")
def heartbeat(hb: LocationHeartbeat):
    return {"ok": True, "echo": hb.model_dump()}

@app.get("/v1/events/nearby", response_model=List[Nearby])
def nearby(hop: int = 8):
    def rnd():
        return round(random.uniform(0.38, 0.62), 2)
    return [
        {"nick": "ally1", "dist": 120, "region": "ASIA/SGP", "pos": {"x": rnd(), "y": rnd()}},
        {"nick": "ally2", "dist": 180, "region": "ASIA/SGP", "pos": {"x": rnd(), "y": rnd()}}
    ]
