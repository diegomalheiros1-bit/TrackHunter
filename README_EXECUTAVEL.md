# TrackHunter Executavel

Use o ZIP em `release/TrackHunter-v2.0.zip` para distribuir o programa para usuarios finais.

## Opcoes

- `release/TrackHunter-v2.0.zip`
  - Pacote pronto para enviar ao usuario.

- `release/TrackHunter-v2.0/Abrir TrackHunter.bat`
  - Botao de abertura para usuario leigo.

- `release/TrackHunter-v2.0/TrackHunterApp.exe`
  - Executavel principal, que deve permanecer junto da pasta `_internal`.

- `scripts/`
  - Contem scripts auxiliares para desenvolvimento, build e execucao via Python.

## Importante

- Edite `tracklist.txt` antes de rodar.
- Downloads vao para `downloads/`.
- Logs vao para `logs/`.
- Historico fica em `state/track_history.json`.

## Estrutura esperada

Nao mova o executavel sozinho. Para distribuir, envie o arquivo `release/TrackHunter-v2.0.zip`.

## Gerar um novo pacote

Depois de recompilar o executavel, rode:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```
