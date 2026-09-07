<#
    Cities: Skylines II - Turkce Yama / Turkish Localization
    Kurulum betigi. Tek satirla calistirmak icin:

        irm https://raw.githubusercontent.com/KaanBahaSever/cs2-turkce-yama/main/install.ps1 | iex

    Parametreler (yerelden calistirirken):
        -Source <yol|url>  Yama dosyasinin konumu
        -Force             Onay sormadan devam et
        -KeepOthers        Diger ceviri modlarini oldugu gibi birak
#>
#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Source,
    [switch]$Force,
    [switch]$KeepOthers
)

$ErrorActionPreference = 'Stop'

# ---- Depo adresi: kendi deponuza gore guncelleyin -------------------------
$RepoRaw = 'https://raw.githubusercontent.com/KaanBahaSever/cs2-turkce-yama/main'
# --------------------------------------------------------------------------

$ModName  = 'TurkishLang'
$FileName = 'en-US.json'

function Say  ($m) { Write-Host "  $m" }
function Step ($m) { Write-Host "  $m" -ForegroundColor Cyan }
function Good ($m) { Write-Host "  [+] $m" -ForegroundColor Green }
function Warn ($m) { Write-Host "  [!] $m" -ForegroundColor Yellow }
function Fail ($m) { Write-Host "  [x] $m" -ForegroundColor Red }

Write-Host ""
Write-Host "  Cities: Skylines II - Turkce Yama" -ForegroundColor White
Write-Host "  ---------------------------------" -ForegroundColor DarkGray
Write-Host ""

# 1) Oyun klasoru -----------------------------------------------------------
Step "Oyun klasoru araniyor..."
$gameData = Join-Path $env:USERPROFILE 'AppData\LocalLow\Colossal Order\Cities Skylines II'
if (-not (Test-Path -LiteralPath $gameData)) {
    Fail "Cities: Skylines II veri klasoru bulunamadi:"
    Say  "$gameData"
    Say  "Oyunu en az bir kez calistirip tekrar deneyin."
    return
}
Good "Bulundu: $gameData"

$modsDir = Join-Path $gameData 'Mods'
if (-not (Test-Path -LiteralPath $modsDir)) {
    New-Item -ItemType Directory -Force -Path $modsDir | Out-Null
    Say "Mods klasoru olusturuldu."
}

# 2) Yama dosyasini bul veya indir ------------------------------------------
Step "Yama dosyasi hazirlaniyor..."
$patch = $null
$temp  = $null

if ($Source -and $Source -notmatch '^https?://') {
    if (Test-Path -LiteralPath $Source -ErrorAction SilentlyContinue) {
        $patch = (Resolve-Path -LiteralPath $Source).Path
    } else {
        Fail "Belirtilen dosya bulunamadi: $Source"
        return
    }
}
if (-not $patch) {
    $candidates = @()
    if ($PSScriptRoot) { $candidates += (Join-Path $PSScriptRoot $FileName) }
    $candidates += (Join-Path (Get-Location).Path $FileName)
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) { $patch = (Resolve-Path -LiteralPath $c).Path; break }
    }
}
if (-not $patch) {
    $url = $Source
    if (-not $url) { $url = "$RepoRaw/$FileName" }
    if ($url -notmatch '^https?://') {
        Fail "Yama dosyasi bulunamadi ve gecerli bir indirme adresi yok."
        return
    }
    Say "Indiriliyor: $url"
    try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
    $temp = Join-Path $env:TEMP ("cs2-tr-" + [guid]::NewGuid().ToString('N') + ".json")
    try {
        Invoke-WebRequest -Uri $url -OutFile $temp -UseBasicParsing
    } catch {
        Fail "Indirme basarisiz: $($_.Exception.Message)"
        return
    }
    $patch = $temp
}

# 3) Dosyayi dogrula --------------------------------------------------------
$size = (Get-Item -LiteralPath $patch).Length
if ($size -lt 500000) {
    Fail "Yama dosyasi beklenenden kucuk ($size bayt). Dosya bozuk olabilir."
    if ($temp) { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }
    return
}
$head = Get-Content -LiteralPath $patch -TotalCount 40 | Out-String
if ($head.TrimStart()[0] -ne '{' -or $head -notmatch '"Assets\.') {
    Fail "Yama dosyasi gecerli bir yerellestirme JSON'u gibi gorunmuyor."
    if ($temp) { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }
    return
}
Good ("Yama dogrulandi (" + [math]::Round($size/1MB,2) + " MB)")

# 4) Onceki ceviri modlarini yedekle ----------------------------------------
$others = @()
foreach ($d in @(Get-ChildItem -LiteralPath $modsDir -Directory -ErrorAction SilentlyContinue)) {
    if ($d.Name -eq $ModName) { continue }
    $langDir = Join-Path $d.FullName 'lang'
    if (-not (Test-Path -LiteralPath $langDir)) { continue }
    $jsons = @(Get-ChildItem -LiteralPath $langDir -Filter *.json -File -ErrorAction SilentlyContinue)
    if ($jsons.Count -eq 0) { continue }
    # icinde .dll olan klasorler kod modudur, dokunma (orn. I18N Everywhere)
    $dlls = @(Get-ChildItem -LiteralPath $d.FullName -Filter *.dll -File -Recurse -ErrorAction SilentlyContinue)
    if ($dlls.Count -gt 0) { continue }
    $others += $d
}

if ($others.Count -gt 0 -and -not $KeepOthers) {
    Warn "Baska ceviri modlari bulundu. Bunlar bu yama ile CAKISIR:"
    foreach ($o in $others) { Say "    - $($o.Name)" }
    $go = $true
    if (-not $Force) {
        $ans = Read-Host "  Bunlari yedekleyip kaldiralim mi? [E/h]"
        if ($ans -and $ans -notmatch '^(e|E|y|Y)$') { $go = $false }
    }
    if ($go) {
        $stamp   = Get-Date -Format 'yyyyMMdd-HHmmss'
        $backup  = Join-Path $gameData ("TurkishLang-Yedek\" + $stamp)
        New-Item -ItemType Directory -Force -Path $backup | Out-Null
        foreach ($o in $others) {
            Move-Item -LiteralPath $o.FullName -Destination $backup -Force
            Good "Yedeklendi ve kaldirildi: $($o.Name)"
        }
        Say "Yedek konumu: $backup"
    } else {
        Warn "Atlandi. Cakisma yasarsaniz bu modlari elle kaldirin."
    }
} elseif ($others.Count -gt 0) {
    Warn "Diger ceviri modlari birakildi (-KeepOthers)."
}

# 5) Kur --------------------------------------------------------------------
Step "Yama kuruluyor..."
$target = Join-Path $modsDir (Join-Path $ModName 'lang')
New-Item -ItemType Directory -Force -Path $target | Out-Null
$dest = Join-Path $target $FileName
Copy-Item -LiteralPath $patch -Destination $dest -Force
if ($temp) { Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue }

if (-not (Test-Path -LiteralPath $dest)) { Fail "Kurulum basarisiz."; return }
Good "Kuruldu: $dest"

Write-Host ""
Write-Host "  Kurulum tamamlandi." -ForegroundColor Green
Write-Host ""
Say "Simdi sirasiyla:"
Say "  1. Oyunu acin (acikken kurduysaniz yeniden baslatin)."
Say "  2. I18N Everywhere modunun etkin oldugundan emin olun."
Say "  3. Options / Secenekler ekranina girip cikin - ceviri o an devreye girer."
Write-Host ""
