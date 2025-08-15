# ALbion_Beacon_ver2

> **초기화 버전** — 2025-08-15

이 리포지토리는 **Windows 데스크톱 프로그램**으로서 Albion Online의 **UDP 패킷을 로컬에서 수집/로그화**하고,
사용자 동의 시 **위치(지역/좌표)만** 최소한으로 공유하는 도구입니다. 중앙 대시보드는 **부가 모듈**입니다.

## 빠른 시작 (개발자)

```powershell
# 0) 의존성
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1) Mock API (선택) — 프론트 개발/헬스체크용
uvicorn src.mock_server:app --host 127.0.0.1 --port 8787 --reload

# 2) 캡처 데몬 (Placeholder: 구조 확인용)
python -m src.capture.daemon

# 3) 공유 엔진 DEMO (로컬 파일 outbox/ 에 하트비트 드랍)
python -m src.share.demo
```

## 폴더 구조
```
src/
  capture/        # Npcap/Scapy 기반 캡처 (daemon, utils)
  decode/         # 지역/좌표 추론(룰 기반; region_map.json)
  identity/       # 닉 일치 검증(입력/OCR/서버)
  share/          # 업링크 토글/주변공유(ON일 때만)
  mock_server.py  # 로컬 개발용 FastAPI
contracts/        # OpenAPI, JSON Schemas (단일 진실 소스)
docs/             # 핸드북/계획/프론트 가이드(자동생성 포함)
scripts/          # PowerShell 유틸 (sync-docs, bump-version, diagnose)
.github/          # CI 워크플로우/이슈 템플릿
logs/             # JSONL 일자별 로그 (런타임 생성)
```

## 정책 요약
- 하트비트 120s / 10분 미수신 자동 OFF / 30분 정체 자동 OFF
- 원본 패킷·이미지 **보관 금지**
- 업로드 **OFF 기본** (사용자 동의 시에만 최소 필드 전송)
