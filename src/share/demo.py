# Demo: share engine usage
import time, os
from src.share.engine import ShareEngine

def main():
    eng = ShareEngine(outbox_path="outbox")
    eng.start()
    eng.submit_local_state(nick="hyuna", region="ASIA/SGP", pos={"x":0.42, "y":0.61}, party=2)
    for _ in range(3):
        time.sleep(60)  # 1분 간격으로 상태 갱신
        eng.submit_local_state(nick="hyuna", region="ASIA/SGP", pos={"x":0.43, "y":0.62}, party=2)
    eng.stop()

if __name__ == "__main__":
    main()
