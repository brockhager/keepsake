param(
  [ValidateSet('personal', 'demo')]
  [string]$RuntimeMode = 'personal',

  [string]$DataRoot = "$HOME/.keepsake",

  [switch]$Reset
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-SqliteReadFile {
  param(
    [Parameter(Mandatory = $true)]
    [string]$DatabasePath,
    [Parameter(Mandatory = $true)]
    [string]$SqlFilePath
  )

  if (-not (Test-Path -LiteralPath $SqlFilePath)) {
    throw "SQL file not found: $SqlFilePath"
  }

  $normalizedDatabasePath = $DatabasePath -replace '\\', '/'
  $normalizedSqlFilePath = $SqlFilePath -replace '\\', '/'

  & sqlite3 $normalizedDatabasePath ".read '$normalizedSqlFilePath'"
  if ($LASTEXITCODE -ne 0) {
    throw "sqlite3 failed while reading: $SqlFilePath"
  }
}

if (-not (Get-Command sqlite3 -ErrorAction SilentlyContinue)) {
  throw 'sqlite3 is required but was not found in PATH.'
}

$repoRoot = Split-Path -Path $PSScriptRoot -Parent
$profileRoot = Join-Path $DataRoot $RuntimeMode
$dbPath = Join-Path $profileRoot 'keepsake.db'
$attachmentsRoot = Join-Path $profileRoot 'attachments'
$exportsRoot = Join-Path $profileRoot 'exports'
$profileMetadataPath = Join-Path $profileRoot 'profile.json'

if ($Reset) {
  Remove-Item -LiteralPath $dbPath -Force -ErrorAction SilentlyContinue
}

$null = New-Item -ItemType Directory -Path $profileRoot -Force
$null = New-Item -ItemType Directory -Path $attachmentsRoot -Force
$null = New-Item -ItemType Directory -Path $exportsRoot -Force

$isNewDatabase = -not (Test-Path -LiteralPath $dbPath)

if (-not $isNewDatabase -and -not $Reset) {
  Write-Host "Database already exists: $dbPath"
  Write-Host 'No changes were applied. Use -Reset to recreate profile data.'
  exit 0
}

$migration1 = Join-Path $repoRoot 'db/migrations/0001_initial_schema.up.sql'
$migration2 = Join-Path $repoRoot 'db/migrations/0002_invariants_and_views.up.sql'
$migration3 = Join-Path $repoRoot 'db/migrations/0003_vault_foundation.up.sql'
$demoSeed = Join-Path $repoRoot 'db/seeds/demo_seed_v0.sql'

Invoke-SqliteReadFile -DatabasePath $dbPath -SqlFilePath $migration1
Invoke-SqliteReadFile -DatabasePath $dbPath -SqlFilePath $migration2
Invoke-SqliteReadFile -DatabasePath $dbPath -SqlFilePath $migration3

if ($RuntimeMode -eq 'demo') {
  Invoke-SqliteReadFile -DatabasePath $dbPath -SqlFilePath $demoSeed
}

$runtimeConfig = [ordered]@{
  runtimeMode = $RuntimeMode
  profileRoot = $profileRoot
  databasePath = $dbPath
  attachmentsPath = $attachmentsRoot
  exportsPath = $exportsRoot
  networkEnabledByDefault = ($RuntimeMode -eq 'demo')
  telemetryEnabledByDefault = $false
  syntheticData = ($RuntimeMode -eq 'demo')
}

$runtimeConfig | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $profileMetadataPath -Encoding UTF8

Write-Host "Initialized $RuntimeMode profile at: $profileRoot"
Write-Host "Database: $dbPath"
if ($RuntimeMode -eq 'demo') {
  Write-Host 'Synthetic demo seed applied.'
} else {
  Write-Host 'No seed data applied (personal mode).'
}
