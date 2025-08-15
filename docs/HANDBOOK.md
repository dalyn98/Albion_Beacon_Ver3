# 협업 핸드북 — ALbion_Beacon_ver2

- **우선순위**: Windows 데스크톱 **프로그램 본체(캡처/로그)** → (선택) 공유/대시보드
- **분업**: 백엔드/캡처/계약 — 이 리포. UI/대시보드 — 별도 (Replit)

## 브랜치
- main: 안정 릴리즈
- dev: 통합 개발
- feat/<area>-<slug>: 기능 브랜치 (예: feat/capture-nic-select)

## 커밋/PR
- 커밋: `feat(capture): ...`, `fix(decode): ...`, `docs: ...`
- PR 체크리스트: 빌드 통과, 계약 준수, 문서 동기화

## 문서 자동화
- `contracts/` 변경 → `scripts/sync-docs.ps1` 실행 → `docs/API_SUMMARY.md` 갱신
