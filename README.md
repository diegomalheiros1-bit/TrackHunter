# TrackHunter

TrackHunter e uma automacao em Python + Playwright para buscar faixas no Muzpa, baixar arquivos MP3 ou AIFF e manter um historico local para evitar downloads duplicados.

> Estado tecnico atual: a `main` contem a versao definitiva mais recente, com baseline tecnico, testes automatizados, configuracao tipada, logging tecnico e persistencia de historico mais segura sem mudar o fluxo principal da interface ou da CLI.

## O Que Ele Faz

O TrackHunter automatiza este fluxo:

1. Acessa o Muzpa.
2. Faz login automatico ou manual.
3. Usa uma tracklist flexivel, editavel pela interface ou por arquivo no modo CLI.
4. Busca uma musica por vez.
5. Clica no melhor candidato do formato escolhido, `MP3` ou `AIFF`, encontrado nos resultados.
6. Salva os arquivos baixados em `downloads/`.
7. Gera um log legivel em `logs/`.
8. Mantem historico local em `state/track_history.json`.

## Stack

- Python 3.10+
- Playwright para Python
- Automacao com navegador Chromium

## Estrutura do Projeto

```text
TrackHunter/
|- trackhunter/      # pacote principal da aplicacao
|  |- app.py         # interface desktop PySide6
|  |- cli.py         # entrada CLI e orquestracao principal
|  |- auth.py        # fluxo de login e autenticacao
|  |- search.py      # deteccao do campo de busca e matching dos resultados
|  |- download.py    # fluxo de download por faixa
|  |- report.py      # geracao do log final em TXT
|  |- history.py     # historico local de baixadas e nao encontradas
|  |- utils.py       # normalizacao de texto, parsing da tracklist e helpers
|  `- models.py      # dataclasses usadas entre os modulos
|- scripts/          # scripts auxiliares de build/execucao
|- tests/            # testes unitarios sem acesso ao Muzpa
|- docs/             # baseline, arquitetura, instalador e processo de release
|- dist/             # executavel gerado pelo PyInstaller
|- assets/           # logo e icone do aplicativo
|- requirements.txt
|- tracklist.txt     # lista exemplo usada para popular o pacote inicial
|- downloads/        # arquivos baixados
|- logs/             # logs de execucao (.txt)
`- state/            # historico local e tracklist salva
```

## Instalacao

```bash
pip install -r requirements.txt
playwright install chromium
```

Para desenvolvimento e testes:

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

## Tracklist

Na interface desktop, clique em `Tracklist` para adicionar, editar, colar e salvar as musicas diretamente no software.

O usuario pode informar apenas o nome da musica ou usar o formato `Artista - Titulo` para melhorar a precisao da busca:

```text
Kill Me Slow (Agents Of Time Remix)
Kaskade & CID ft. Anabel Englund - Vision Blurred (Agents Of Time Remix)
Agents Of Time & Miss Monique - Rajada
Supermode - Tell Me Why
```

A lista salva pela interface fica em:

```text
state/tracklist.txt
```

No modo CLI, tambem e possivel informar um arquivo `.txt` com `--tracklist`.

## Login Automatico

Configure as credenciais por variaveis de ambiente:

```powershell
$env:MUZPA_EMAIL="seu_email"
$env:MUZPA_PASSWORD="sua_senha"
python -m trackhunter.cli --tracklist .\tracklist.txt --headless
```

## Login Manual

Use este modo quando quiser fazer login pela janela do navegador:

```powershell
python -m trackhunter.cli --tracklist .\tracklist.txt --manual-login
```

## Comandos Uteis

Executar com navegador visivel:

```powershell
python -m trackhunter.cli --tracklist .\tracklist.txt
```

Executar sem interface grafica:

```powershell
python -m trackhunter.cli --tracklist .\tracklist.txt --headless
```

Forcar download mesmo quando a faixa ja estiver no historico:

```powershell
python -m trackhunter.cli --tracklist .\tracklist.txt --force-download
```

Tentar novamente somente faixas marcadas como nao encontradas:

```powershell
python -m trackhunter.cli --retry-missing-only --headless
```

Usar pastas customizadas:

```powershell
python -m trackhunter.cli --tracklist .\tracklist.txt --downloads .\downloads --logs .\logs --history .\state\track_history.json
```

## Interface Grafica

Agora o projeto inclui uma interface desktop em `trackhunter/app.py`, para executar sem usar terminal.
A janela principal se adapta a diferentes resolucoes, incluindo notebooks, compactando logo, margens, espacamentos e area de log sem usar rolagem na tela inicial.

Instale as dependencias:

```bash
pip install -r requirements.txt
playwright install chromium
```

Abra a interface:

```bash
python -m trackhunter.app
```

Pela tela voce pode:

- informar usuario e senha do MUZPA
- escolher o formato de download em `Opcoes`: `Download MP3` ou `Download AIFF`
- ajustar `Timeout Busca` para aguardar mais em conexoes lentas antes de marcar uma musica como nao encontrada
- acompanhar o indicador de conexao com o Muzpa na tela principal
- abrir o editor Tracklist para adicionar, editar e salvar musicas sem mexer em arquivo manualmente
- escolher a pasta de downloads e abrir arquivos gerados
- ligar/desligar login manual, busca assistida, baixar novamente e somente nao encontradas
- acompanhar o log em tempo real
- conferir resumo de baixadas, ignoradas, nao encontradas e erros
- interromper uma execucao em andamento com o botao `Parar`
- usar a interface em diferentes resolucoes com layout responsivo, mantendo os quatro quadros principais alinhados

## Versao e Release

A versao oficial de distribuicao e controlada por:

- `RELEASE_VERSION.txt`
- Versao em desenvolvimento: `v2.1`
- Ultima release gerada: `v2.1`

Com isso, os artefatos finais sempre seguem o padrao:

- `release/TrackHunter-<versao>/TrackHunter.exe`
- `release/TrackHunter-<versao>.zip`
- `release/TrackHunter-<versao>-Setup.exe`

Release atual gerada:

- `release/TrackHunter-v2.1/TrackHunter.exe`
- `release/TrackHunter-v2.1.zip`

Executavel local de desenvolvimento:

- `dist/TrackHunter/TrackHunter.exe`
- `dist-onefile/TrackHunter.exe`

Regra de trabalho: sempre que houver alteracao relevante de interface, fluxo ou empacotamento, atualize a versao antes de gerar nova release.

Documentacao detalhada:

- `docs/TECHNICAL_BASELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/RELEASE_PROCESS.md`
- `docs/INSTALLER.md`

## Argumentos CLI

- `--tracklist`: caminho do arquivo `.txt` com as musicas.
- `--downloads`: pasta onde os arquivos baixados serao salvos.
- `--logs`: pasta onde os logs de execucao serao salvos.
- `--history`: arquivo JSON usado como historico local.
- `--output`: alias legado para a pasta de downloads.
- `--download-format`: formato desejado para download (`mp3` ou `aiff`).
- `--headless`: executa sem interface grafica.
- `--wait-login`: timeout do login em milissegundos.
- `--search-timeout`: timeout da pesquisa de cada musica em milissegundos.
- `--manual-login`: desativa preenchimento automatico de credenciais.
- `--force-download`: ignora o historico e baixa novamente.
- `--retry-missing-only`: executa somente faixas registradas como nao encontradas.

## Historico Inteligente

O TrackHunter guarda estado local em:

```text
state/track_history.json
```

Esse historico serve para:

- evitar baixar a mesma musica repetidas vezes
- lembrar musicas que nao foram encontradas
- tentar musicas nao encontradas em execucoes futuras
- remover uma musica das pendencias quando ela for baixada
- separar downloads por formato, permitindo baixar a mesma faixa em `MP3` e depois em `AIFF`
- preservar progresso durante a execucao, salvando o historico apos cada faixa resolvida ou marcada como nao encontrada

Comportamentos importantes:

- Uma faixa so e ignorada quando esta no historico para o formato selecionado e o arquivo ainda existe em `downloads/`.
- Se o arquivo foi apagado de `downloads/`, o TrackHunter baixa novamente.
- Musicas nao encontradas continuam elegiveis para buscas futuras.
- O modo `Somente nao encontradas` respeita o formato selecionado: pendencias de `MP3` nao sao misturadas com pendencias de `AIFF`.
- `--force-download` ignora o historico.
- A escrita do historico e atomica: primeiro grava um arquivo temporario, depois substitui o JSON final.
- Se `state/track_history.json` estiver corrompido, o TrackHunter cria um backup `track_history.corrupted_YYYYMMDD_HHMMSS.json` e inicia com historico vazio.

## Testes

A suite de testes usa `pytest` e nao abre Chromium, nao acessa o Muzpa e nao realiza downloads reais.

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Cobertura atual:

- `tests/test_utils.py`: normalizacao, parsing e tracklist.
- `tests/test_search.py`: scoring de candidatos e falsos positivos conhecidos.
- `tests/test_history.py`: persistencia, formatos, JSON corrompido e escrita atomica.
- `tests/test_report.py`: formatacao de duracao e geracao de logs finais.
- `tests/test_config.py`: configuracao tipada, validacao de paths, formatos e credenciais.
- `tests/test_logging_config.py`: log tecnico em arquivo e handler para interface grafica.

Resultado validado nesta branch:

```text
49 passed
```

## Instalador Windows

O instalador atual e gerado por:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_installer.ps1
```

Ele usa `dist-onefile/TrackHunter.exe` e gera:

```text
release/TrackHunter-v2.1-Setup.exe
```

Fluxo atual:

- mostra Termo de Uso antes da instalacao;
- bloqueia `Continuar` ate o usuario aceitar o termo;
- permite escolher a pasta de instalacao;
- cria atalhos;
- registra o app em Aplicativos instalados do Windows;
- inclui desinstalador.

O setup gerado tem cerca de 381 MB e nao deve ser commitado no GitHub.

## Estrategia de Busca

Para cada faixa, o TrackHunter tenta:

1. Busca completa usando o texto salvo na tracklist.
2. Busca alternativa usando `titulo + versao/remix`, sem artista.

Ele prioriza somente botoes do formato escolhido. Para `MP3`, procura botoes `MP3`; para `AIFF`, alterna o Muzpa para `LOSSLESS` e procura botoes `AIFF`. O download automatico nao usa `ZIP/Download` como fallback.

Em conexoes lentas, use `Timeout Busca` na interface ou `--search-timeout` no CLI para aumentar o tempo maximo de espera pelos resultados antes de considerar uma musica como nao encontrada.

Antes de clicar, o resultado precisa bater o titulo em ordem, considerando tambem palavras curtas como `me`, `you`, `it`, `on` e `up`. Quando a tracklist informa artista e versao/remix, esses dados tambem entram na validacao para reduzir falso positivo.

## Formato do Log

Cada execucao gera um unico log TXT:

```text
logs/log_execucao_YYYYMMDD_HHMMSS.txt
```

O log e organizado em:

- `Resumo da execucao`
- `Tempo de execucao`
- `Concluidas com sucesso`
- `Ja baixadas / ignoradas`
- `Nao encontradas`
- `Erros`

Na interface, o `Log de execucao` lista as etapas conforme o processo avanca, incluindo buscas, avisos, erros e status final de cada faixa.

## Arquivos Locais

Estes arquivos/pastas sao artefatos locais de execucao e ficam fora do Git:

- `downloads/*`
- `logs/*.txt`
- `logs/*.csv`
- `state/*.json`
- `state/*.txt`
- `.env`

## Observacoes

- Nao deixe credenciais fixas no codigo.
- Use variaveis de ambiente para `MUZPA_EMAIL` e `MUZPA_PASSWORD` no CLI, ou informe pela tela do app.
- Consulte `logs/trackhunter-runtime.log` para diagnostico tecnico da execucao.
- Revise o log TXT depois de cada execucao para validar o que foi baixado.
- O matching flexivel ajuda com remixes e versoes alternativas, mas o log deve sempre ser conferido.

## Autor

Projeto desenvolvido e evoluido por Diego Stanisci Malheiros como automacao real e projeto de portfolio.
