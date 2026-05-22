# TrackHunter Executavel

Use o ZIP da versao definida em `RELEASE_VERSION.txt` para distribuir o programa para usuarios finais.

Versao atual definida: `v2.0.2`.

## Opcoes

- `release/TrackHunter-<versao>.zip`
  - Pacote pronto para enviar ao usuario.

- `release/TrackHunter-<versao>/TrackHunter.exe`
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

Nao mova o executavel sozinho. Para distribuir, envie o arquivo `release/TrackHunter-<versao>.zip`.
Depois de extrair o ZIP, o usuario deve abrir `TrackHunter.exe`.

## Gerar um novo pacote

1. Atualize `RELEASE_VERSION.txt` para uma nova versao (exemplo: `v2.1.0`, `v2.1.1-hotfix`).
2. Recompile o executavel.
3. Rode o script de release.

Depois de recompilar o executavel, rode:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

Opcionalmente, voce pode forcar a versao pelo comando:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1 -Version v2.1.0
```
