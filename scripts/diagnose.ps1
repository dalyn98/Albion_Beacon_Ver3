Write-Host '==> Diagnose (Npcap/Permissions/NIC)'
# TODO: 실제 진단 로직을 추가하세요. placeholder
Get-NetAdapter | Sort-Object -Property Status -Descending | Select-Object Name, Status, MacAddress
