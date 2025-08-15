param(
  [string]$OpenApi = 'contracts/openapi.yaml',
  [string]$OutSummary = 'docs/API_SUMMARY.md'
)
Write-Host '==> Sync docs from OpenAPI...'
if (-Not (Test-Path $OpenApi)) { Write-Error 'openapi.yaml not found'; exit 1 }
'# API Summary (auto)`n`n- Source: contracts/openapi.yaml`n' | Out-File -Encoding utf8 $OutSummary
Write-Host 'OK -> ' $OutSummary
