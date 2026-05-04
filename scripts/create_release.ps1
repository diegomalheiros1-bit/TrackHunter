$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$distApp = Join-Path $root "dist\TrackHunter"
$releaseRoot = Join-Path $root "release"
$releaseDir = Join-Path $releaseRoot "TrackHunter-v2.0"
$zipPath = Join-Path $releaseRoot "TrackHunter-v2.0.zip"

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

Copy-Item -Path (Join-Path $root "tracklist.txt") -Destination (Join-Path $releaseDir "tracklist.txt") -Force

@"
TrackHunter v2.0
================

Como abrir
----------
1. Extraia a pasta inteira do ZIP.
2. Clique duas vezes em "TrackHunter.exe".

Importante
----------
- Nao mova o arquivo TrackHunter.exe sozinho.
- Mantenha a pasta _internal junto dele.
- Edite o arquivo tracklist.txt antes de iniciar, se quiser trocar as musicas.

Pastas
------
- downloads: musicas baixadas.
- logs: logs da execucao.
- state: historico local do programa.

Se o Windows mostrar alerta de seguranca
----------------------------------------
Clique em "Mais informacoes" e depois em "Executar assim mesmo", caso voce confie na origem do arquivo.
"@ | Set-Content -Path (Join-Path $releaseDir "LEIA-ME.txt") -Encoding UTF8

Push-Location $releaseRoot
try {
    & tar.exe -a -c -f $zipPath "TrackHunter-v2.0"
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao criar ZIP. Codigo tar: $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

Write-Host "Release pronta em: $releaseDir"
Write-Host "ZIP pronto em: $zipPath"
