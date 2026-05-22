param(
    [string]$Version
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$distApp = Join-Path $root "dist\TrackHunter"
$releaseRoot = Join-Path $root "release"
$versionFile = Join-Path $root "RELEASE_VERSION.txt"

if ([string]::IsNullOrWhiteSpace($Version)) {
    if (-not (Test-Path -LiteralPath $versionFile)) {
        throw "Arquivo RELEASE_VERSION.txt nao encontrado. Crie o arquivo com a versao (ex: v2.1.0)."
    }
    $Version = (Get-Content -LiteralPath $versionFile -Raw).Trim()
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    throw "Versao invalida. Defina em RELEASE_VERSION.txt ou passe -Version."
}

if ($Version -notmatch "^[A-Za-z0-9._-]+$") {
    throw "Versao invalida '$Version'. Use apenas letras, numeros, ponto, underline e hifen."
}

$releaseName = "TrackHunter-$Version"
$releaseDir = Join-Path $releaseRoot $releaseName
$zipPath = Join-Path $releaseRoot "$releaseName.zip"

if (-not (Test-Path -LiteralPath (Join-Path $distApp "TrackHunter.exe"))) {
    throw "Executavel nao encontrado. Rode o build antes: pyinstaller --noconfirm --clean TrackHunterApp.spec"
}

if (Test-Path -LiteralPath $releaseDir) {
    $emptyDir = Join-Path $releaseRoot "_empty"
    New-Item -ItemType Directory -Force -Path $emptyDir | Out-Null
    & robocopy $emptyDir $releaseDir /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -gt 7) {
        throw "Falha ao limpar release antigo. Codigo robocopy: $LASTEXITCODE"
    }
    Remove-Item -LiteralPath $releaseDir -Recurse -Force
    Remove-Item -LiteralPath $emptyDir -Recurse -Force
}
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

& robocopy $distApp $releaseDir /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -gt 7) {
    throw "Falha ao copiar arquivos do executavel. Codigo robocopy: $LASTEXITCODE"
}

New-Item -ItemType Directory -Force -Path `
    (Join-Path $releaseDir "downloads"), `
    (Join-Path $releaseDir "logs"), `
    (Join-Path $releaseDir "state") | Out-Null

Copy-Item -Path (Join-Path $root "tracklist.txt") -Destination (Join-Path $releaseDir "state\tracklist.txt") -Force

@" 
TrackHunter $Version
================

Como abrir
----------
1. Extraia a pasta inteira do ZIP.
2. Clique duas vezes em "TrackHunter.exe".

Importante
----------
- Nao mova o arquivo TrackHunter.exe sozinho.
- Mantenha a pasta _internal junto dele.
- Use o botao Tracklist no programa para adicionar, editar e salvar suas musicas.

Pastas
------
- downloads: musicas baixadas.
- logs: logs da execucao.
- state: historico local e tracklist salva pelo programa.

Se o Windows mostrar alerta de seguranca
----------------------------------------
Clique em "Mais informacoes" e depois em "Executar assim mesmo", caso voce confie na origem do arquivo.
"@ | Set-Content -Path (Join-Path $releaseDir "LEIA-ME.txt") -Encoding UTF8

Push-Location $releaseRoot
try {
    & tar.exe -a -c -f $zipPath $releaseName
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao criar ZIP. Codigo tar: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "Versao da release: $Version"
Write-Host "Release pronta em: $releaseDir"
Write-Host "ZIP pronto em: $zipPath"
