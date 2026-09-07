<#
    Cities: Skylines II - Turkce Yama / kaldirma betigi

        irm https://raw.githubusercontent.com/KaanBahaSever/cs2-turkce-yama/main/uninstall.ps1 | iex
#>
#Requires -Version 5.1
[CmdletBinding()]
param([switch]$Force)

$ErrorActionPreference = 'Stop'
$ModName = 'TurkishLang'

function Say  ($m) { Write-Host "  $m" }
function Good ($m) { Write-Host "  [+] $m" -ForegroundColor Green }
function Warn ($m) { Write-Host "  [!] $m" -ForegroundColor Yellow }

Write-Host ""
Write-Host "  Cities: Skylines II - Turkce Yama kaldiriliyor" -ForegroundColor White
Write-Host ""

$gameData = Join-Path $env:USERPROFILE 'AppData\LocalLow\Colossal Order\Cities Skylines II'
$modDir   = Join-Path $gameData (Join-Path 'Mods' $ModName)

if (-not (Test-Path -LiteralPath $modDir)) {
    Warn "Yama zaten kurulu degil."
} else {
    $go = $true
    if (-not $Force) {
        $ans = Read-Host "  $modDir silinecek. Onayliyor musunuz? [E/h]"
        if ($ans -and $ans -notmatch '^(e|E|y|Y)$') { $go = $false }
    }
    if ($go) {
        Remove-Item -LiteralPath $modDir -Recurse -Force
        Good "Kaldirildi: $modDir"
    } else {
        Warn "Iptal edildi."
    }
}

$backupRoot = Join-Path $gameData 'TurkishLang-Yedek'
if (Test-Path -LiteralPath $backupRoot) {
    Write-Host ""
    Say "Kurulum sirasinda kaldirilan eski ceviri modlari burada duruyor:"
    Say "  $backupRoot"
    Say "Geri istiyorsaniz klasorleri Mods icine tasiyin."
}
Write-Host ""
