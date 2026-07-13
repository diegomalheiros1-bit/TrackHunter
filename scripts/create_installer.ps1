param(
    [string]$Version
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$versionFile = Join-Path $root "RELEASE_VERSION.txt"

if ([string]::IsNullOrWhiteSpace($Version)) {
    if (-not (Test-Path -LiteralPath $versionFile)) {
        throw "Arquivo RELEASE_VERSION.txt nao encontrado."
    }
    $Version = (Get-Content -LiteralPath $versionFile -Raw).Trim()
}

if ([string]::IsNullOrWhiteSpace($Version)) {
    throw "Versao invalida."
}

if ($Version -notmatch "^[A-Za-z0-9._-]+$") {
    throw "Versao invalida '$Version'. Use apenas letras, numeros, ponto, underline e hifen."
}

$oneFileExe = Join-Path $root "dist-onefile\TrackHunter.exe"
$releaseRoot = Join-Path $root "release"
$installerPath = Join-Path $releaseRoot "TrackHunter-$Version-Setup.exe"
$workRoot = Join-Path $env:TEMP "TrackHunterInstaller-$Version"
$packageDir = Join-Path $workRoot "package"
$sedPath = Join-Path $workRoot "TrackHunterInstaller.sed"
$installScriptPath = Join-Path $packageDir "install.ps1"
$uninstallScriptPath = Join-Path $packageDir "uninstall.ps1"
$tempInstallerPath = Join-Path $workRoot "TrackHunter-$Version-Setup.exe"

if (-not (Test-Path -LiteralPath $oneFileExe)) {
    throw "Executavel unico nao encontrado. Gere antes: python -m PyInstaller --onefile ..."
}

$iexpress = (Get-Command iexpress.exe -ErrorAction SilentlyContinue).Source
if ([string]::IsNullOrWhiteSpace($iexpress)) {
    throw "IExpress nao encontrado neste Windows."
}

if (Test-Path -LiteralPath $workRoot) {
    Remove-Item -LiteralPath $workRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $packageDir, $releaseRoot | Out-Null
Copy-Item -LiteralPath $oneFileExe -Destination (Join-Path $packageDir "TrackHunter.exe") -Force
Copy-Item -LiteralPath (Join-Path $root "tracklist.txt") -Destination (Join-Path $packageDir "tracklist.txt") -Force

@'
$ErrorActionPreference = "Stop"

$defaultInstallDir = Join-Path $env:LOCALAPPDATA "Programs\TrackHunter"
$installDir = $defaultInstallDir
$exePath = ""
$uninstallerPath = ""
$stateDir = ""
$downloadsDir = ""
$logsDir = ""
$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TrackHunter"

function Set-InstallDir {
    param(
        [string]$SelectedInstallDir
    )

    if ([string]::IsNullOrWhiteSpace($SelectedInstallDir)) {
        throw "Selecione uma pasta de instalacao."
    }

    $script:installDir = [System.IO.Path]::GetFullPath($SelectedInstallDir.Trim())
    $script:exePath = Join-Path $script:installDir "TrackHunter.exe"
    $script:uninstallerPath = Join-Path $script:installDir "uninstall.ps1"
    $script:stateDir = Join-Path $script:installDir "state"
    $script:downloadsDir = Join-Path $script:installDir "downloads"
    $script:logsDir = Join-Path $script:installDir "logs"
}

Set-InstallDir $defaultInstallDir

function Install-TrackHunter {
    New-Item -ItemType Directory -Force -Path $installDir, $stateDir, $downloadsDir, $logsDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "TrackHunter.exe") -Destination $exePath -Force
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "uninstall.ps1") -Destination $uninstallerPath -Force

    $tracklistTarget = Join-Path $stateDir "tracklist.txt"
    if (-not (Test-Path -LiteralPath $tracklistTarget)) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot "tracklist.txt") -Destination $tracklistTarget -Force
    }

    $shell = New-Object -ComObject WScript.Shell
    $desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "TrackHunter.lnk"
    $startMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) "TrackHunter"
    $startMenuShortcut = Join-Path $startMenuDir "TrackHunter.lnk"
    New-Item -ItemType Directory -Force -Path $startMenuDir | Out-Null

    foreach ($shortcutPath in @($desktopShortcut, $startMenuShortcut)) {
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $exePath
        $shortcut.WorkingDirectory = $installDir
        $shortcut.IconLocation = "$exePath,0"
        $shortcut.Description = "TrackHunter"
        $shortcut.Save()
    }

    New-Item -Path $uninstallKey -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "DisplayName" -Value "TrackHunter" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "DisplayVersion" -Value "__TRACKHUNTER_VERSION__" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "Publisher" -Value "TrackHunter" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "InstallLocation" -Value $installDir -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "DisplayIcon" -Value $exePath -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "UninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$uninstallerPath`"" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "QuietUninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$uninstallerPath`" -Quiet" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "NoModify" -Value 1 -PropertyType DWord -Force | Out-Null
    New-ItemProperty -Path $uninstallKey -Name "NoRepair" -Value 1 -PropertyType DWord -Force | Out-Null
}

function Show-InstallerWindow {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    [System.Windows.Forms.Application]::EnableVisualStyles()

    $fontRegular = New-Object System.Drawing.Font("Segoe UI", 9)
    $fontSmall = New-Object System.Drawing.Font("Segoe UI", 8)
    $fontTitle = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
    $fontSubtitle = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
    $colorBackground = [System.Drawing.Color]::FromArgb(245, 247, 250)
    $colorHeader = [System.Drawing.Color]::FromArgb(16, 24, 39)
    $colorPanel = [System.Drawing.Color]::White
    $colorBorder = [System.Drawing.Color]::FromArgb(226, 232, 240)
    $colorText = [System.Drawing.Color]::FromArgb(15, 23, 42)
    $colorMuted = [System.Drawing.Color]::FromArgb(71, 85, 105)
    $colorPrimary = [System.Drawing.Color]::FromArgb(37, 99, 235)
    $colorPrimaryHover = [System.Drawing.Color]::FromArgb(29, 78, 216)
    $colorSuccess = [System.Drawing.Color]::FromArgb(22, 101, 52)

    $termsText = @"
Termo de Uso - TrackHunter

Ultima atualizacao: Julho de 2026

1. Sobre o TrackHunter

O TrackHunter e um software independente desenvolvido como um projeto pessoal com o objetivo de auxiliar na pesquisa e organizacao do processo de busca e download de arquivos disponiveis na plataforma Muzpa.

O TrackHunter nao e um software oficial, nao possui qualquer vinculo, parceria, autorizacao comercial ou afiliacao com o Muzpa ou seus proprietarios.

Este projeto foi criado para automatizar tarefas repetitivas realizadas pelo proprio usuario, proporcionando maior agilidade e praticidade durante a utilizacao da plataforma.

2. Natureza do projeto

O TrackHunter e um projeto em constante evolucao.

Embora sejam realizados testes para melhorar sua estabilidade, o software pode conter erros, limitacoes ou comportamentos inesperados.

Novas versoes poderao alterar funcionalidades, corrigir problemas ou modificar o funcionamento da aplicacao sem aviso previo.

3. Responsabilidade do usuario

Ao utilizar o TrackHunter, o usuario declara que:

- Possui uma conta valida e legitima na plataforma utilizada.
- Esta autorizado a acessar e baixar o conteudo disponivel em sua conta.
- E responsavel pelo uso do software e pelas acoes realizadas durante sua execucao.
- Concorda em utilizar o programa em conformidade com os termos de uso da plataforma utilizada.

O desenvolvedor nao se responsabiliza pelo uso inadequado do software.

4. Ausencia de garantias

O TrackHunter e fornecido "no estado em que se encontra" ("as is"), sem garantias de qualquer natureza.

Nao ha garantia de:

- funcionamento ininterrupto;
- compatibilidade permanente com alteracoes realizadas pelo Muzpa;
- disponibilidade continua da automacao;
- sucesso em todas as buscas;
- sucesso em todos os downloads;
- compatibilidade com futuras versoes do Windows ou de softwares de terceiros.

5. Alteracoes na plataforma

O funcionamento do TrackHunter depende da estrutura da plataforma Muzpa.

Caso o site seja alterado, determinadas funcionalidades poderao deixar de funcionar temporaria ou permanentemente ate que uma nova atualizacao do software seja disponibilizada.

6. Credenciais

As credenciais informadas pelo usuario sao utilizadas exclusivamente para autenticacao na plataforma durante a execucao do software.

O TrackHunter nao possui servidores proprios para armazenamento de contas, senhas ou informacoes pessoais.

O usuario e responsavel por manter suas credenciais em seguranca.

7. Limitacao de responsabilidade

Em nenhuma hipotese o desenvolvedor sera responsavel por:

- perda de arquivos;
- interrupcao de downloads;
- indisponibilidade do servico do Muzpa;
- alteracoes na plataforma que impecam o funcionamento da automacao;
- suspensao ou restricao de contas decorrentes do uso da ferramenta;
- danos diretos ou indiretos relacionados a utilizacao do software.

A utilizacao do TrackHunter ocorre por conta e risco do usuario.

8. Direitos autorais

O TrackHunter nao distribui musicas, midias ou conteudos proprios.

O software apenas automatiza determinadas acoes executadas pelo proprio usuario na plataforma em que ele possui acesso.

Todos os direitos sobre musicas, arquivos, marcas, logotipos e demais conteudos pertencem aos seus respectivos titulares.

9. Atualizacoes

O desenvolvedor podera disponibilizar novas versoes contendo:

- correcoes;
- melhorias de desempenho;
- novas funcionalidades;
- alteracoes na interface;
- adaptacoes decorrentes de mudancas na plataforma utilizada.

Nao ha obrigacao de fornecer atualizacoes continuas.

10. Aceitacao

Ao instalar ou utilizar o TrackHunter, o usuario declara ter lido, compreendido e aceitado integralmente este Termo de Uso.

Caso nao concorde com qualquer uma das disposicoes acima, recomenda-se nao utilizar o software.

☐ Li e concordo com o Termo de Uso do TrackHunter.
"@

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Instalar TrackHunter"
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.ClientSize = New-Object System.Drawing.Size(640, 430)
    $form.BackColor = $colorBackground

    $sourceExe = Join-Path $PSScriptRoot "TrackHunter.exe"
    if (Test-Path -LiteralPath $sourceExe) {
        $form.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($sourceExe)
    }

    $headerPanel = New-Object System.Windows.Forms.Panel
    $headerPanel.Location = New-Object System.Drawing.Point(0, 0)
    $headerPanel.Size = New-Object System.Drawing.Size(640, 122)
    $headerPanel.BackColor = $colorHeader
    $form.Controls.Add($headerPanel)

    $title = New-Object System.Windows.Forms.Label
    $title.Text = "TrackHunter __TRACKHUNTER_VERSION__"
    $title.Font = $fontTitle
    $title.ForeColor = [System.Drawing.Color]::White
    $title.Location = New-Object System.Drawing.Point(32, 24)
    $title.Size = New-Object System.Drawing.Size(560, 36)
    $headerPanel.Controls.Add($title)

    $versionLabel = New-Object System.Windows.Forms.Label
    $versionLabel.Text = "Versao a instalar: __TRACKHUNTER_VERSION__"
    $versionLabel.Font = $fontSubtitle
    $versionLabel.ForeColor = [System.Drawing.Color]::FromArgb(191, 219, 254)
    $versionLabel.Location = New-Object System.Drawing.Point(34, 62)
    $versionLabel.Size = New-Object System.Drawing.Size(560, 22)
    $headerPanel.Controls.Add($versionLabel)

    $description = New-Object System.Windows.Forms.Label
    $description.Text = "Leia e aceite o Termo de Uso para continuar com a instalacao."
    $description.Font = $fontRegular
    $description.ForeColor = [System.Drawing.Color]::FromArgb(226, 232, 240)
    $description.Location = New-Object System.Drawing.Point(34, 86)
    $description.Size = New-Object System.Drawing.Size(560, 28)
    $headerPanel.Controls.Add($description)

    $termsPanel = New-Object System.Windows.Forms.Panel
    $termsPanel.Location = New-Object System.Drawing.Point(32, 146)
    $termsPanel.Size = New-Object System.Drawing.Size(576, 184)
    $termsPanel.BackColor = $colorPanel
    $termsPanel.BorderStyle = "FixedSingle"
    $form.Controls.Add($termsPanel)

    $termsTitle = New-Object System.Windows.Forms.Label
    $termsTitle.Text = "Termo de Uso"
    $termsTitle.Font = $fontSubtitle
    $termsTitle.ForeColor = $colorText
    $termsTitle.Location = New-Object System.Drawing.Point(22, 14)
    $termsTitle.Size = New-Object System.Drawing.Size(520, 20)
    $termsPanel.Controls.Add($termsTitle)

    $termsBox = New-Object System.Windows.Forms.TextBox
    $termsBox.Multiline = $true
    $termsBox.ReadOnly = $true
    $termsBox.ScrollBars = "Vertical"
    $termsBox.Text = $termsText
    $termsBox.Font = $fontSmall
    $termsBox.ForeColor = $colorText
    $termsBox.BackColor = [System.Drawing.Color]::White
    $termsBox.Location = New-Object System.Drawing.Point(25, 40)
    $termsBox.Size = New-Object System.Drawing.Size(524, 94)
    $termsPanel.Controls.Add($termsBox)

    $acceptCheckbox = New-Object System.Windows.Forms.CheckBox
    $acceptCheckbox.Text = "Li e concordo com o Termo de Uso do TrackHunter."
    $acceptCheckbox.Font = $fontRegular
    $acceptCheckbox.ForeColor = $colorText
    $acceptCheckbox.Location = New-Object System.Drawing.Point(25, 145)
    $acceptCheckbox.Size = New-Object System.Drawing.Size(524, 24)
    $termsPanel.Controls.Add($acceptCheckbox)

    $contentPanel = New-Object System.Windows.Forms.Panel
    $contentPanel.Location = New-Object System.Drawing.Point(32, 146)
    $contentPanel.Size = New-Object System.Drawing.Size(576, 184)
    $contentPanel.BackColor = $colorPanel
    $contentPanel.BorderStyle = "FixedSingle"
    $contentPanel.Visible = $false
    $form.Controls.Add($contentPanel)

    $destinationLabel = New-Object System.Windows.Forms.Label
    $destinationLabel.Text = "Destino da instalacao:"
    $destinationLabel.Font = $fontSubtitle
    $destinationLabel.ForeColor = $colorText
    $destinationLabel.Location = New-Object System.Drawing.Point(22, 22)
    $destinationLabel.Size = New-Object System.Drawing.Size(520, 22)
    $contentPanel.Controls.Add($destinationLabel)

    $destinationInput = New-Object System.Windows.Forms.TextBox
    $destinationInput.Text = $installDir
    $destinationInput.Font = $fontRegular
    $destinationInput.Location = New-Object System.Drawing.Point(25, 54)
    $destinationInput.Size = New-Object System.Drawing.Size(405, 24)
    $contentPanel.Controls.Add($destinationInput)

    $browseButton = New-Object System.Windows.Forms.Button
    $browseButton.Text = "Procurar..."
    $browseButton.Font = $fontRegular
    $browseButton.FlatStyle = "Flat"
    $browseButton.BackColor = [System.Drawing.Color]::FromArgb(241, 245, 249)
    $browseButton.ForeColor = $colorText
    $browseButton.FlatAppearance.BorderColor = $colorBorder
    $browseButton.Location = New-Object System.Drawing.Point(444, 52)
    $browseButton.Size = New-Object System.Drawing.Size(105, 30)
    $browseButton.Add_Click({
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description = "Escolha onde instalar o TrackHunter"
        $dialog.SelectedPath = $destinationInput.Text
        $dialog.ShowNewFolderButton = $true
        if ($dialog.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) {
            if ((Split-Path -Path $dialog.SelectedPath -Leaf) -eq "TrackHunter") {
                $destinationInput.Text = $dialog.SelectedPath
            }
            else {
                $destinationInput.Text = Join-Path $dialog.SelectedPath "TrackHunter"
            }
        }
    })
    $contentPanel.Controls.Add($browseButton)

    $destinationHint = New-Object System.Windows.Forms.Label
    $destinationHint.Text = "Dica: se escolher uma pasta existente, o TrackHunter sera instalado dentro dela."
    $destinationHint.Font = $fontSmall
    $destinationHint.ForeColor = $colorMuted
    $destinationHint.Location = New-Object System.Drawing.Point(26, 90)
    $destinationHint.Size = New-Object System.Drawing.Size(520, 20)
    $contentPanel.Controls.Add($destinationHint)

    $status = New-Object System.Windows.Forms.Label
    $status.Text = "Pronto para instalar."
    $status.Font = $fontRegular
    $status.ForeColor = $colorMuted
    $status.Location = New-Object System.Drawing.Point(25, 128)
    $status.Size = New-Object System.Drawing.Size(524, 22)
    $contentPanel.Controls.Add($status)

    $progress = New-Object System.Windows.Forms.ProgressBar
    $progress.Style = "Marquee"
    $progress.MarqueeAnimationSpeed = 35
    $progress.Location = New-Object System.Drawing.Point(25, 153)
    $progress.Size = New-Object System.Drawing.Size(524, 14)
    $progress.Visible = $false
    $contentPanel.Controls.Add($progress)

    $footerLine = New-Object System.Windows.Forms.Panel
    $footerLine.Location = New-Object System.Drawing.Point(0, 360)
    $footerLine.Size = New-Object System.Drawing.Size(640, 1)
    $footerLine.BackColor = $colorBorder
    $form.Controls.Add($footerLine)

    $installButton = New-Object System.Windows.Forms.Button
    $installButton.Text = "Continuar"
    $installButton.Font = $fontSubtitle
    $installButton.FlatStyle = "Flat"
    $installButton.BackColor = $colorPrimary
    $installButton.ForeColor = [System.Drawing.Color]::White
    $installButton.FlatAppearance.BorderColor = $colorPrimary
    $installButton.Location = New-Object System.Drawing.Point(344, 378)
    $installButton.Size = New-Object System.Drawing.Size(124, 36)
    $installButton.Enabled = $false
    $installButton.Add_MouseEnter({ if ($installButton.Enabled) { $installButton.BackColor = $colorPrimaryHover } })
    $installButton.Add_MouseLeave({ if ($installButton.Enabled) { $installButton.BackColor = $colorPrimary } })
    $form.Controls.Add($installButton)

    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Text = "Cancelar"
    $cancelButton.Font = $fontRegular
    $cancelButton.FlatStyle = "Flat"
    $cancelButton.BackColor = [System.Drawing.Color]::White
    $cancelButton.ForeColor = $colorText
    $cancelButton.FlatAppearance.BorderColor = $colorBorder
    $cancelButton.Location = New-Object System.Drawing.Point(484, 378)
    $cancelButton.Size = New-Object System.Drawing.Size(124, 36)
    $cancelButton.Add_Click({ $form.Close() })
    $form.Controls.Add($cancelButton)

    $acceptCheckbox.Add_CheckedChanged({
        $installButton.Enabled = $acceptCheckbox.Checked
        if ($installButton.Enabled) {
            $installButton.BackColor = $colorPrimary
        }
        else {
            $installButton.BackColor = [System.Drawing.Color]::FromArgb(148, 163, 184)
        }
    })
    $installButton.BackColor = [System.Drawing.Color]::FromArgb(148, 163, 184)

    $script:installDone = $false
    $script:termsAccepted = $false
    $installButton.Add_Click({
        if (-not $script:termsAccepted) {
            if (-not $acceptCheckbox.Checked) {
                [System.Windows.Forms.MessageBox]::Show("Voce precisa aceitar o Termo de Uso para continuar.", "TrackHunter", "OK", "Warning") | Out-Null
                return
            }

            $script:termsAccepted = $true
            $termsPanel.Visible = $false
            $contentPanel.Visible = $true
            $description.Text = "Escolha a pasta de instalacao. O instalador cria atalhos e registra o TrackHunter para desinstalacao pelo Windows."
            $installButton.Text = "Instalar"
            $installButton.Enabled = $true
            $installButton.BackColor = $colorPrimary
            return
        }

        if ($script:installDone) {
            Start-Process -FilePath $exePath -WorkingDirectory $installDir
            $form.Close()
            return
        }

        try {
            Set-InstallDir $destinationInput.Text
            $installButton.Enabled = $false
            $cancelButton.Enabled = $false
            $destinationInput.Enabled = $false
            $browseButton.Enabled = $false
            $progress.Visible = $true
            $status.Text = "Instalando arquivos..."
            [System.Windows.Forms.Application]::DoEvents()

            Install-TrackHunter

            $script:installDone = $true
            $progress.Visible = $false
            $status.ForeColor = $colorSuccess
            $status.Text = "Instalacao concluida com sucesso."
            $installButton.Text = "Abrir TrackHunter"
            $installButton.Size = New-Object System.Drawing.Size(150, 36)
            $installButton.Location = New-Object System.Drawing.Point(318, 378)
            $installButton.Enabled = $true
            $cancelButton.Text = "Fechar"
            $cancelButton.Enabled = $true
        }
        catch {
            $progress.Visible = $false
            $installButton.Enabled = $true
            $cancelButton.Enabled = $true
            $destinationInput.Enabled = $true
            $browseButton.Enabled = $true
            $status.ForeColor = [System.Drawing.Color]::FromArgb(185, 28, 28)
            $status.Text = "Falha na instalacao."
            [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, "TrackHunter", "OK", "Error") | Out-Null
        }
    })

    [void]$form.ShowDialog()
}

try {
    Show-InstallerWindow
}
catch {
    Install-TrackHunter
    Start-Process -FilePath $exePath -WorkingDirectory $installDir
}
'@.Replace("__TRACKHUNTER_VERSION__", $Version) | Set-Content -LiteralPath $installScriptPath -Encoding UTF8

@'
param(
    [switch]$Quiet
)

$ErrorActionPreference = "SilentlyContinue"

$installDir = $PSScriptRoot
$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TrackHunter"
$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "TrackHunter.lnk"
$startMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) "TrackHunter"

Get-Process -Name "TrackHunter" | Stop-Process -Force
Remove-Item -LiteralPath $desktopShortcut -Force
Remove-Item -LiteralPath $startMenuDir -Recurse -Force
Remove-Item -LiteralPath $uninstallKey -Recurse -Force
Remove-Item -LiteralPath $installDir -Recurse -Force

if (-not $Quiet) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("TrackHunter foi desinstalado.", "TrackHunter") | Out-Null
}
'@ | Set-Content -LiteralPath $uninstallScriptPath -Encoding UTF8

$packageDirForSed = $packageDir.TrimEnd("\") + "\"

@"
[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=
DisplayLicense=
FinishMessage=TrackHunter instalado com sucesso.
TargetName=$tempInstallerPath
FriendlyName=TrackHunter $Version Setup
AppLaunched=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1
UserQuietInstCmd=powershell.exe -NoProfile -ExecutionPolicy Bypass -File install.ps1
SourceFiles=SourceFiles

[Strings]
FILE0="install.ps1"
FILE1="TrackHunter.exe"
FILE2="tracklist.txt"
FILE3="uninstall.ps1"

[SourceFiles]
SourceFiles0=$packageDirForSed

[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
%FILE3%=
"@ | Set-Content -LiteralPath $sedPath -Encoding ASCII

if (Test-Path -LiteralPath $tempInstallerPath) {
    Remove-Item -LiteralPath $tempInstallerPath -Force
}

& $iexpress /N /Q $sedPath
if (($null -ne $LASTEXITCODE) -and ($LASTEXITCODE -ne 0)) {
    throw "Falha ao criar instalador. Codigo IExpress: $LASTEXITCODE"
}

$deadline = (Get-Date).AddMinutes(8)
while ((Get-Date) -lt $deadline) {
    if (Test-Path -LiteralPath $tempInstallerPath) {
        $tempInstaller = Get-Item -LiteralPath $tempInstallerPath
        if ($tempInstaller.Length -gt 0) {
            break
        }
    }
    Start-Sleep -Seconds 1
}

if (-not (Test-Path -LiteralPath $tempInstallerPath)) {
    throw "Instalador nao foi criado em: $tempInstallerPath"
}

if (Test-Path -LiteralPath $installerPath) {
    Remove-Item -LiteralPath $installerPath -Force
}

$copyDeadline = (Get-Date).AddMinutes(3)
$copied = $false
while ((Get-Date) -lt $copyDeadline) {
    try {
        Copy-Item -LiteralPath $tempInstallerPath -Destination $installerPath -Force
        $copied = $true
        break
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $copied) {
    throw "Nao foi possivel copiar o instalador para: $installerPath"
}

Write-Host "Instalador pronto em: $installerPath"
