import time
from dataclasses import dataclass

@dataclass
class IdentityState:
    nick: str = ""
    verified: bool = False
    method: str = ""  # manual|ocr|server

class NickLinker:
    def __init__(self):
        self.state = IdentityState()

    def set_nick(self, nick: str):
        self.state.nick = nick
        self.state.verified = False
        self.state.method = ""

    def verify_manual(self, confirm: bool):
        if confirm and self.state.nick:
            self.state.verified = True
            self.state.method = "manual"
        return self.snapshot()

    def verify_ocr(self, ocr_text: str):
        if self.state.nick and (ocr_text or "").lower().find(self.state.nick.lower()) >= 0:
            self.state.verified = True
            self.state.method = "ocr"
        return self.snapshot()

    def verify_server(self, ok: bool):
        if ok and self.state.nick:
            self.state.verified = True
            self.state.method = "server"
        return self.snapshot()

    def snapshot(self):
        return dict(nick=self.state.nick, verified=self.state.verified, method=self.state.method, ts=int(time.time()))
