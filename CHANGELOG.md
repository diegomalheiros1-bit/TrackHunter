# Changelog

## Unreleased

### Added
- Interface desktop moderna com tema escuro, logo e icone do aplicativo.
- Editor de Tracklist dentro do software, com suporte a colar, editar e salvar musicas.
- Suporte visual para buscar por nome da musica ou pelo formato `Artista - Titulo`.
- Pacote Windows com `TrackHunter.exe` direto para o usuario abrir com dois cliques.
- Botao `Parar` funcional para interromper uma execucao em andamento com seguranca.
- Log de execucao mais compacto, listando as etapas conforme o processo roda.
- Barra de progresso reposicionada ao lado dos botoes de acao para ampliar o log visual.
- Historico local em `state/track_history.json`.
- Bloqueio automatico para evitar download duplicado de faixas ja baixadas.
- Registro persistente de musicas nao encontradas, mantendo elas elegiveis para novas buscas.
- Opcao `--force-download` para ignorar o historico quando necessario.
- Opcao `--retry-missing-only` para buscar somente faixas nao encontradas anteriormente.
- Timeout padrao de login ajustado para `30000 ms` na interface.

### Changed
- A tracklist da interface agora e gerenciada em `state/tracklist.txt`, sem exigir importacao manual de arquivo.

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
