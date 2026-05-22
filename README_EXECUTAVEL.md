# TrackHunter Executavel

Use o ZIP em `release/TrackHunter-v2.0-ui-polish.zip` para distribuir o programa para usuarios finais.

## Opcoes

- `release/TrackHunter-v2.0-ui-polish.zip`
  - Pacote pronto para enviar ao usuario.

- `release/TrackHunter-v2.0-ui-polish/TrackHunter.exe`
  - Executavel principal. O usuario deve clicar duas vezes nele para abrir o programa.

- `scripts/`
  - Contem scripts auxiliares para desenvolvimento, build e execucao via Python.

## Importante

- Na interface, use o botao `Tracklist` para adicionar, editar e salvar as musicas.
- Downloads vao para `downloads/`.
- Logs vao para `logs/`.
- Historico fica em `state/track_history.json`.
- A lista salva fica em `state/tracklist.txt`.

## Estrutura esperada

Nao mova o executavel sozinho. Para distribuir, envie o arquivo `release/TrackHunter-v2.0-ui-polish.zip`.
Depois de extrair o ZIP, o usuario deve abrir `TrackHunter.exe`.

## Gerar um novo pacote

Depois de recompilar o executavel, rode:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```
