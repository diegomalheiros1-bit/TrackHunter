# Changelog

## Unreleased

### Added
- Historico local em `state/track_history.json`.
- Bloqueio automatico para evitar download duplicado de faixas ja baixadas.
- Registro persistente de musicas nao encontradas, mantendo elas elegiveis para novas buscas.
- Opcao `--force-download` para ignorar o historico quando necessario.
- Opcao `--retry-missing-only` para buscar somente faixas nao encontradas anteriormente.

## v1.0.0 - 2026-04-28

### Added
- Automacao de login no Muzpa (modo automatico e manual).
- Busca por faixa via tracklist (`tracklist.txt`), processando uma musica por vez.
- Download priorizando botao `MP3`, com fallback para `ZIP/Download`.
- Segunda tentativa automatica de busca: `titulo + versao/remix` sem artista.
- Salvamento dos arquivos baixados em `downloads/`.
- Log textual consolidado por execucao em `logs/log_execucao_YYYYMMDD_HHMMSS.txt`.

### Changed
- Refatoracao para arquitetura modular:
  - `muzpa_bot.py` (orquestrador)
  - `auth.py` (autenticacao)
  - `search.py` (busca/matching)
  - `download.py` (fluxo de download)
  - `report.py` (saida de log)
  - `utils.py` e `models.py` (suporte)
- Melhorias de desempenho no matching (limite de candidatos analisados).

### Removed
- Geracao de relatorios CSV/Excel (mantido somente log `.txt`).
