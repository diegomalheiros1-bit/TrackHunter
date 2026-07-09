# TrackHunter Executavel

Use o ZIP da ultima release final para distribuir o programa para usuarios finais.

Versao em desenvolvimento definida: `v2.0.5`.

Ultima release final gerada: `v2.0.3`.

A versao `v2.0.5` esta salva localmente e compilada em `dist/TrackHunter`, mas ainda nao foi empacotada como release final em ZIP.

## Opcoes

- `release/TrackHunter-<versao>.zip`
  - Pacote pronto para enviar ao usuario.

- `release/TrackHunter-<versao>/TrackHunter.exe`
  - Executavel principal. O usuario deve clicar duas vezes nele para abrir o programa.

- `release/TrackHunter-v2.0.3.zip`
  - ZIP atual gerado para distribuicao.

- `dist/TrackHunter/TrackHunter.exe`
  - Executavel local de desenvolvimento da versao `v2.0.5`.

- `scripts/`
  - Contem scripts auxiliares para desenvolvimento, build e execucao via Python.

## Importante

- Na interface, use o botao `Tracklist` para adicionar, editar e salvar as musicas.
- Use os toggles `Download MP3` e `Download AIFF` em `Opcoes` para escolher o formato antes de iniciar.
- O historico respeita o formato escolhido, entao uma faixa ja baixada em `MP3` ainda pode ser baixada em `AIFF`.
- O modo `Somente nao encontradas` tambem respeita o formato escolhido.
- O download automatico nao usa `ZIP`/`Download` como fallback.
- A tela principal usa layout responsivo com quatro quadros alinhados para diferentes resolucoes.
- Downloads vao para `downloads/`.
- Logs vao para `logs/`.
- Historico fica em `state/track_history.json`.
- A lista salva fica em `state/tracklist.txt`.

## Estrutura esperada

Nao mova o executavel sozinho. Para distribuir, envie o arquivo `release/TrackHunter-<versao>.zip`.
Depois de extrair o ZIP, o usuario deve abrir `TrackHunter.exe`.

## Gerar um novo pacote

1. Atualize `RELEASE_VERSION.txt` para uma nova versao (exemplo: `v2.1.0`, `v2.1.1-hotfix`).
2. Recompile o executavel.
3. Rode o script de release.

Antes de recriar uma release ja existente, feche qualquer `TrackHunter.exe` aberto dentro da pasta `release/`, pois o Windows pode bloquear arquivos internos do pacote.

Depois de recompilar o executavel, rode:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

Opcionalmente, voce pode forcar a versao pelo comando:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1 -Version v2.1.0
```
