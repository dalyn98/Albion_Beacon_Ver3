Param(
    [string]$Nick,
    [Nullable[bool]]$UploadEnabled,
    [int]$HeartbeatSec,
    [string]$Interface,
    [string]$BPF,
    [Nullable[bool]]$NickValidated
)

$root = Split-Path -Parent $PSScriptRoot
$settingsPath = Join-Path $root "settings.json"

if (-not (Test-Path $settingsPath)) {
    Write-Error "settings.json not found at $settingsPath"
    exit 1
}

# Read JSON allowing BOM
$jsonText = Get-Content -LiteralPath $settingsPath -Raw -Encoding Byte
# Strip UTF-8 BOM if present
if ($jsonText.Length -ge 3 -and $jsonText[0] -eq 0xEF -and $jsonText[1] -eq 0xBB -and $jsonText[2] -eq 0xBF) {
    $jsonText = $jsonText[3..($jsonText.Length-1)]
}
$utf8 = [System.Text.Encoding]::UTF8.GetString($jsonText)
$cfg = $utf8 | ConvertFrom-Json

# Mutations
if ($PSBoundParameters.ContainsKey('Nick')) { $cfg.nick = $Nick }
if ($PSBoundParameters.ContainsKey('UploadEnabled')) {
    if (-not $cfg.upload) { $cfg.upload = @{} }
    $cfg.upload.enabled = [bool]$UploadEnabled
}
if ($PSBoundParameters.ContainsKey('HeartbeatSec')) {
    if (-not $cfg.heartbeat) { $cfg.heartbeat = @{} }
    $cfg.heartbeat.sec = [int]$HeartbeatSec
}
if ($PSBoundParameters.ContainsKey('Interface')) {
    if (-not $cfg.capture) { $cfg.capture = @{} }
    $cfg.capture.interface = $Interface
}
if ($PSBoundParameters.ContainsKey('BPF')) {
    if (-not $cfg.capture) { $cfg.capture = @{} }
    $cfg.capture.bpf = $BPF
}
if ($PSBoundParameters.ContainsKey('NickValidated')) {
    $cfg.NickValidated = [bool]$NickValidated
}

# Write without BOM
$enc = New-Object System.Text.UTF8Encoding($false)
$bytes = [System.Text.Encoding]::UTF8.GetBytes(($cfg | ConvertTo-Json -Depth 8))
[System.IO.File]::WriteAllBytes($settingsPath, $bytes)
Write-Host "Updated $settingsPath without BOM."
