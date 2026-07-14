# TrackHunter Executavel

Use o instalador `.exe` para uma experiencia mais convencional no Windows. O ZIP continua disponivel como pacote portatil em pasta.

Versao em desenvolvimento definida: `v2.2`.

Proxima release preparada: `v2.2`.

A versao `v2.2` esta configurada no codigo, no instalador e na documentacao. Gere os artefatos finais depois da validacao local da interface.

Artefatos esperados apos build:

- `dist/TrackHunter/TrackHunter.exe`
- `dist-onefile/TrackHunter.exe`
- `release/TrackHunter-v2.2.zip`
- `release/TrackHunter-v2.2-Setup.exe`

## Opcoes

- `release/TrackHunter-<versao>.zip`
  - Pacote portatil em pasta para enviar ao usuario.

- `release/TrackHunter-<versao>-Setup.exe`
  - Instalador Windows com Termo de Uso, selecao de pasta, atalhos, registro no Windows e desinstalador.

- `release/TrackHunter-<versao>/TrackHunter.exe`
  - Executavel principal. O usuario deve clicar duas vezes nele para abrir o programa.

- `release/TrackHunter-v2.2.zip`
  - ZIP atual gerado para distribuicao.

- `dist/TrackHunter/TrackHunter.exe`
  - Executavel local de desenvolvimento da versao `v2.2`.

- `dist-onefile/TrackHunter.exe`
  - Executavel unico usado como entrada do instalador.

- `scripts/`
  - Contem scripts auxiliares para desenvolvimento, build e execucao via Python.

## Importante

- Na interface, use o botao `Tracklist` para adicionar, editar e salvar as musicas.
- Use os toggles `Download MP3` e `Download AIFF` em `Opcoes` para escolher o formato antes de iniciar.
- Em internet lenta, aumente `Timeout Busca` para o app aguardar mais pelos resultados antes de marcar uma musica como nao encontrada.
- O indicador de conexao mostra uma leitura simples da resposta do Muzpa.
- O historico respeita o formato escolhido, entao uma faixa ja baixada em `MP3` ainda pode ser baixada em `AIFF`.
- O modo `Somente nao encontradas` tambem respeita o formato escolhido.
- O download automatico nao usa `ZIP`/`Download` como fallback.
- A tela principal usa layout responsivo com quatro quadros alinhados para diferentes resolucoes.
- Downloads vao para `downloads/`.
- Logs vao para `logs/`.
- Log tecnico de diagnostico fica em `logs/trackhunter-runtime.log`.
- Historico fica em `state/track_history.json`.
- A lista salva fica em `state/tracklist.txt`.
- O historico usa escrita atomica para reduzir risco de corrupcao.
- Se o historico estiver corrompido, um backup `track_history.corrupted_YYYYMMDD_HHMMSS.json` e criado.

## Estrutura esperada

Para usuarios finais, prefira enviar:

```text
release/TrackHunter-v2.2-Setup.exe
```

O instalador:

- mostra o Termo de Uso antes da instalacao;
- exige aceite para continuar;
- permite escolher a pasta de instalacao;
- cria atalhos;
- registra o app em Aplicativos instalados;
- inclui desinstalador.

Se usar o ZIP, nao mova o executavel sozinho. Depois de extrair a pasta inteira, o usuario deve abrir `TrackHunter.exe`.

## Gerar um novo pacote

1. Atualize `RELEASE_VERSION.txt` para uma nova versao (exemplo: `v2.2.0`, `v2.2.1-hotfix`).
2. Rode os testes.
3. Recompile o executavel em pasta.
4. Recompile o executavel unico.
5. Rode o script de release.
6. Rode o script do instalador.

Testes:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Antes de recriar uma release ja existente, feche qualquer `TrackHunter.exe` aberto dentro da pasta `release/`, pois o Windows pode bloquear arquivos internos do pacote.

Depois de recompilar o executavel, rode:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

Para gerar o executavel unico usado no instalador:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH='0'
python -m PyInstaller --noconfirm --clean --onefile --windowed --name TrackHunter --icon assets\app_icon.ico --add-data "assets\logo.png;assets" --add-data "assets\app_icon.png;assets" --distpath dist-onefile --workpath build-onefile scripts\trackhunter_gui.py
```

Para gerar o instalador:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_installer.ps1
```

Opcionalmente, voce pode forcar a versao pelo comando:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1 -Version v2.2.0
```
