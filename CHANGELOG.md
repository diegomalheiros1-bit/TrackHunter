# Changelog

## v2.2 - 2026-07-14

### Added
- `docs/TECHNICAL_BASELINE.md` com estado inicial, comandos executados, artefatos gerados, riscos e limitacoes.
- Suite inicial de testes automatizados com `pytest`, cobrindo utilitarios, matching, historico, relatorios, configuracao e logging.
- `requirements-dev.txt` para dependencias de teste.
- `pyproject.toml` com configuracao inicial de `pytest`.
- Documentacao tecnica em `docs/ARCHITECTURE.md`, `docs/RELEASE_PROCESS.md` e `docs/INSTALLER.md`.
- Configuracao tipada em `trackhunter/config.py` para paths, formato, timeouts e credenciais.
- Logging tecnico em `trackhunter/logging_config.py`, com arquivo `logs/trackhunter-runtime.log`.
- Versao de distribuicao atualizada para `v2.2`.

### Changed
- Historico agora e salvo com escrita atomica por arquivo temporario e substituicao do JSON final.
- CLI passa callback para persistir o historico apos cada faixa resolvida ou marcada como nao encontrada.
- GUI passa credenciais diretamente para o worker, sem alterar variaveis de ambiente globais.
- Documentacao principal atualizada com testes, instalador, artefatos e fluxo de distribuicao.
- Titulo da janela atualizado para `TrackHunter v2.2`.

### Fixed
- JSON de historico corrompido agora gera backup `track_history.corrupted_YYYYMMDD_HHMMSS.json` e nao impede a abertura do historico.

### Tested
- `python -m pytest -v`: 49 testes passando.
- `python -m trackhunter.cli --help`: validado.
- Artefatos finais devem ser regerados apos a validacao visual da interface `v2.2`.

## v2.1 - 2026-07-09

### Added
- Controle `Timeout Busca` para aguardar mais tempo pelos resultados de cada musica em conexoes lentas.
- Argumento CLI `--search-timeout` para configurar o timeout da pesquisa por musica.
- Indicador visual de conexao com medicao periodica de resposta do Muzpa.

### Changed
- Fluxo de busca agora aguarda candidato valido ate o `Timeout Busca` antes de marcar a musica como nao encontrada.
- Indicador de conexao refinado com icone de Wi-Fi, campo compacto e cores por latencia: otima abaixo de `2500 ms`, boa ate `4499 ms` e ruim acima disso.
- Quadro `Autenticacao` ajustado para centralizar verticalmente campos e controles.
- Campos de timeout compactados para reduzir sobra visual nos seletores de milissegundos.
- Botao `Arquivos` reposicionado a direita da linha de opcoes, mantendo bordas e espacamentos do layout.
- Versao local marcada como `v2.1`.

### Tested
- Validado argumento CLI `--search-timeout`.
- Validado layout principal em `1916x1028`, `1366x768` e `1180x690`.
- Recompilado executavel local em `dist/TrackHunter`.

## v2.0.5 - 2026-07-09

### Changed
- Interface principal refinada para manter os quatro quadros (`Autenticacao`, `Opcoes`, `Arquivos` e `Resumo`) alinhados em diferentes resolucoes.
- Titulos dos quadros padronizados com o mesmo recuo interno para melhorar a consistencia visual.
- Painel `Opcoes` reorganizado com dois toggles por linha e linha final dedicada a `Timeout Login` e `Arquivos`.
- Linha de progresso compactada, mantendo barra, percentual e botoes de acao alinhados.
- Botoes `Iniciar` e `Parar` reduzidos proporcionalmente para melhorar o equilibrio visual.
- Quadros `Arquivos` e `Resumo` ajustados para ganhar altura sem deslocar os campos internos.
- Resumo de historico alinhado a esquerda com borda visual, mantendo o botao `Ver historico` a direita.
- Regras responsivas revisadas para evitar cortes, sobreposicoes e excesso de espacos vazios em telas de notebook e monitores maiores.
- Versao local em desenvolvimento marcada como `v2.0.5`.

### Tested
- Validado layout principal em `1916x1028`, `1452x993`, `1366x768`, `1280x720` e `1180x690`.
- Validado alinhamento dos titulos dos quadros com offset interno padronizado.

## v2.0.4 - Em desenvolvimento

### Added
- Seletor de formato na tela principal para escolher downloads em `MP3` ou `AIFF`.
- Argumento CLI `--download-format` com opcoes `mp3` e `aiff`.
- Alternancia automatica para modo `LOSSLESS` no Muzpa quando o formato escolhido for `AIFF`.

### Changed
- Download automatico agora aceita somente o botao do formato escolhido, removendo fallback para `ZIP`/`Download`.
- Versao local em desenvolvimento marcada como `v2.0.4`.
- Matching de resultados reforcado para considerar a frase completa do titulo, incluindo palavras curtas, e respeitar versao/remix quando informado.
- Historico e modo `Somente nao encontradas` separados por formato de download.
- Executavel local atualizado em `dist/TrackHunter`, sem gerar release final em ZIP.
- Controles de formato movidos para `Opcoes` como toggles `Download MP3` e `Download AIFF`, com selecao exclusiva.
- Linha de `Timeout Login` e `Arquivos` ajustada para evitar sobreposicao no painel `Opcoes`.

### Tested
- Teste real com `state/tracklist.txt` em modo `AIFF`: 9 baixadas, 11 nao encontradas, 0 ZIP e 0 erros.
- Validado que falso positivo conhecido passou a ser marcado como `nao encontrada` em vez de baixar arquivo incorreto.

## v2.0.3 - 2026-07-02

### Added
- Interface desktop moderna com tema escuro, logo e icone do aplicativo.
- Editor de Tracklist dentro do software, com suporte a colar, editar e salvar musicas.
- Suporte visual para buscar por nome da musica ou pelo formato `Artista - Titulo`.
- Pacote Windows com `TrackHunter.exe` direto para o usuario abrir com dois cliques.
- Botao `Parar` funcional para interromper uma execucao em andamento com seguranca.
- Log de execucao mais compacto, listando as etapas conforme o processo roda.
- Barra de progresso reposicionada ao lado dos botoes de acao para ampliar o log visual.
- Barra de progresso expandida para preencher melhor o espaco antes do texto de percentual.
- Cards do resumo padronizados com largura e espacamento uniformes.
- Historico local em `state/track_history.json`.
- Bloqueio automatico para evitar download duplicado de faixas ja baixadas.
- Registro persistente de musicas nao encontradas, mantendo elas elegiveis para novas buscas.
- Opcao `--force-download` para ignorar o historico quando necessario.
- Opcao `--retry-missing-only` para buscar somente faixas nao encontradas anteriormente.
- Timeout padrao de login ajustado para `30000 ms` na interface.
- Versionamento de release centralizado em `RELEASE_VERSION.txt`.
- Feedback visual de hover/pressed nos botoes `Tracklist` e `Selecionar` (`BrowseButton`), alinhando com os demais botoes da interface.

### Changed
- Interface principal ajustada para se adaptar melhor a telas de notebook sem depender de rolagem na tela inicial.
- Tamanho inicial da janela agora considera a area disponivel do monitor.
- Layout reduz logo, margens, espacamentos e area de log automaticamente em telas mais baixas.
- Tema escuro original preservado nos ajustes de responsividade.
- A tracklist da interface agora e gerenciada em `state/tracklist.txt`, sem exigir importacao manual de arquivo.
- Script `scripts/create_release.ps1` atualizado para gerar pasta e ZIP com base na versao atual.
- Versao atual de release definida para `v2.0.3` em `RELEASE_VERSION.txt`.

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
