# NEXT STEPS — Patch (2025-08-16)

## Apply
```powershell
# 1) Extract at repo root
Expand-Archive -Path .\ALbion_Beacon_ver3_patch_2025-08-16.zip -DestinationPath . -Force

# 2) Stage & commit
git add src\capture\daemon.py scripts\build_region_candidates.py scripts\settings_helper.ps1 docs\NEXT_STEPS.md
git commit -m "feat: capture daemon fallback/iface-resolver; scripts for region candidates & settings"
git push
```

## Quick Heartbeat Test (10s)
```powershell
pwsh .\scripts\settings_helper.ps1 -Nick "hyuna" -UploadEnabled $true -HeartbeatSec 10
python -m src.capture.daemon

# 1~2분 후 outbox 생성 확인
Get-ChildItem .\outbox\hb-*.json | Select-Object -First 3

# 정상 확인 후 120초로 복구
pwsh .\scripts\settings_helper.ps1 -HeartbeatSec 120
```

## Improve Region Mapping
```powershell
$today = (Get-Date).ToString('yyyyMMdd')
python .\scripts\build_region_candidates.py ".\logs\log-$today.jsonl" 30
# -> 출력된 /24 또는 /16을 src\decode\region_map.json에 추가
# 데몬 재시작 후 region-hit 비율 체크
```
