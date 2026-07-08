#Requires -Version 5.1
param(
    [Parameter(Mandatory, Position = 0)]
    [string]$FeatureId,
    [Parameter(Mandatory, Position = 1)]
    [ValidateRange(1,4)]
    [int]$GateNumber
)
$ErrorActionPreference = 'Stop'
$ScriptDir      = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot       = (Resolve-Path (Join-Path $ScriptDir '..\..\')).Path
$SpecsDir       = Join-Path $RepoRoot '.specify\specs'
$MemoryDir      = Join-Path $RepoRoot '.specify\memory'
$CheckpointsDir = Join-Path $RepoRoot '.specify\checkpoints'
$ConfigFile     = Join-Path $RepoRoot '.specify\config.json'
function Write-Info  { param([string]$Msg) Write-Host "[INFO] $Msg" -ForegroundColor Blue }
function Write-Ok    { param([string]$Msg) Write-Host "[OK]   $Msg" -ForegroundColor Green }
function Write-Warn  { param([string]$Msg) Write-Host "[WARN] $Msg" -ForegroundColor Yellow }
function Write-Err   { param([string]$Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }
function Write-Check { param([string]$Msg) Write-Host "   -> $Msg" -ForegroundColor Cyan }
function Test-FileExists {
    param([string]$Path, [string]$Desc)
    if (Test-Path $Path) { Write-Ok "$Desc exists"; return $true }
    Write-Err "$Desc MISSING"; return $false
}
function Test-FileNotTemplate {
    param([string]$Path, [string]$Desc)
    if (-not (Test-Path $Path)) { return $false }
    $c = Get-Content $Path -Raw
    if ($c -match '\[FEATURE_NAME\]|\[NNN\]|\[DATE\]|<!-- INSTRUCTION -->') {
        Write-Warn "$Desc contains template placeholders"; return $false
    }
    if ($c -match '(?m)^\*\*Status:\*\*.*\|.*\|') {
        Write-Warn "$Desc is still a template (Status field not filled)"; return $false
    }
    if ($c -match '\[Story [Tt]itle\]|\[Describe |\[Add ') {
        Write-Warn "$Desc contains unfilled template placeholders"; return $false
    }
    $contentLines = ($c -split "`n" | Where-Object { $_ -notmatch '^\s*$|^#|^-' }).Count
    if ($contentLines -lt 5) { Write-Warn "$Desc appears to be mostly empty"; return $false }
    return $true
}
function Test-AcceptanceCriteria {
    param([string]$SpecFile)
    if (-not (Test-Path $SpecFile)) { return $false }
    $c = Get-Content $SpecFile -Raw
    $acCount = ([regex]::Matches($c, 'AC-\d+')).Count
    if ($acCount -lt 1) { Write-Err 'No acceptance criteria found in spec.md'; return $false }
    Write-Check "Found $acCount acceptance criteria"
    return $true
}
function Test-UserStories {
    param([string]$SpecFile)
    if (-not (Test-Path $SpecFile)) { return $false }
    $usCount = ([regex]::Matches((Get-Content $SpecFile -Raw), '(?m)^#{2,4}\s+US-\d+')).Count
    if ($usCount -lt 1) { Write-Err 'No user stories found in spec.md'; return $false }
    Write-Check "Found $usCount user stories"
    return $true
}
function Test-NeedsClarificationMarkers {
    param([string]$Dir, [int]$MaxPerFile = 3)
    $errors = 0; $total = 0
    Write-Info 'Checking [NEEDS CLARIFICATION] markers:'
    Get-ChildItem $Dir -Filter '*.md' | ForEach-Object {
        $count = ([regex]::Matches((Get-Content $_.FullName -Raw), '\[NEEDS CLARIFICATION:')).Count
        $total += $count
        if ($count -gt $MaxPerFile) {
            Write-Err "$($_.Name) has $count [NEEDS CLARIFICATION] markers (max $MaxPerFile)"
            $errors++
        } elseif ($count -gt 0) {
            Write-Warn "$($_.Name) has $count [NEEDS CLARIFICATION] marker(s)"
        }
    }
    if ($total -eq 0) { Write-Ok 'No unresolved [NEEDS CLARIFICATION] markers' }
    else              { Write-Check "Total markers: $total" }
    return ($errors -eq 0)
}
function Invoke-Gate1 {
    param([string]$Dir)
    $e = 0
    Write-Host ''
    Write-Host '--- Gate 1: Three Amigos Review ---'
    Write-Host ''
    Write-Host 'Checking: Do we all share the same understanding?'; Write-Host ''
    Write-Info 'Required artifacts:'
    if (-not (Test-FileExists (Join-Path $Dir 'business-context.md') 'business-context.md')) { $e++ }
    if (-not (Test-FileNotTemplate (Join-Path $Dir 'business-context.md') 'business-context.md')) { $e++ }
    if (-not (Test-FileExists (Join-Path $Dir 'spec.md') 'spec.md')) { $e++ }
    if (-not (Test-FileNotTemplate (Join-Path $Dir 'spec.md') 'spec.md')) { $e++ }
    if (-not (Test-UserStories (Join-Path $Dir 'spec.md'))) { $e++ }
    if (-not (Test-AcceptanceCriteria (Join-Path $Dir 'spec.md'))) { $e++ }
    if (-not (Test-FileExists (Join-Path $Dir 'clarifications.md') 'clarifications.md')) { $e++ }
    Write-Info 'Clarification markers:'
    if (-not (Test-NeedsClarificationMarkers $Dir)) { $e++ }
    Write-Host ''
    return $e
}
function Invoke-Gate2 {
    param([string]$Dir)
    $e = 0
    Write-Host '--- Gate 2: Technical Alignment Review ---'
    Write-Host ''
    Write-Info 'Required artifacts:'
    if (-not (Test-FileExists (Join-Path $Dir 'plan.md') 'plan.md')) { $e++ }
    if (-not (Test-FileNotTemplate (Join-Path $Dir 'plan.md') 'plan.md')) { $e++ }
    Write-Info 'Clarification markers:'
    if (-not (Test-NeedsClarificationMarkers $Dir)) { $e++ }
    Write-Host ''
    return $e
}
function Invoke-Gate3 {
    param([string]$Dir)
    $e = 0
    Write-Host '--- Gate 3: Implementation Gate ---'
    Write-Host ''
    Write-Info 'Required artifacts:'
    if (-not (Test-FileExists (Join-Path $Dir 'test-cases.md') 'test-cases.md')) { $e++ }
    if (-not (Test-FileNotTemplate (Join-Path $Dir 'test-cases.md') 'test-cases.md')) { $e++ }
    if (-not (Test-FileExists (Join-Path $Dir 'tasks.md') 'tasks.md')) { $e++ }
    if (-not (Test-FileNotTemplate (Join-Path $Dir 'tasks.md') 'tasks.md')) { $e++ }
    if (-not (Test-FileExists (Join-Path $Dir 'analysis-report.md') 'analysis-report.md')) { $e++ }
    Write-Info 'Clarification markers:'
    if (-not (Test-NeedsClarificationMarkers $Dir)) { $e++ }
    Write-Host ''
    return $e
}
# Main
$FeatureDir = Join-Path $SpecsDir $FeatureId
if (-not (Test-Path $FeatureDir)) {
    Write-Err "Feature directory not found: $FeatureDir"
    exit 1
}
Write-Info "Ceremony level: standard"
$ErrorCount = 0
switch ($GateNumber) {
    1 { $ErrorCount = Invoke-Gate1 $FeatureDir }
    2 { $ErrorCount = Invoke-Gate2 $FeatureDir }
    3 { $ErrorCount = Invoke-Gate3 $FeatureDir }
    4 { Write-Err 'Gate 4 not implemented in this simplified script'; $ErrorCount = 1 }
}
if ($ErrorCount -gt 0) {
    Write-Host ''
    Write-Err "GATE $GateNumber FAILED ($ErrorCount issues)"
    exit 2
} else {
    Write-Host ''
    Write-Ok "GATE $GateNumber PASSED"
    exit 0
}
