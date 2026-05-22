# TrackHunter

TrackHunter e uma automacao em Python + Playwright para buscar faixas no Muzpa, baixar arquivos MP3 e manter um historico local para evitar downloads duplicados.

## O Que Ele Faz

O TrackHunter automatiza este fluxo:

1. Acessa o Muzpa.
2. Faz login automatico ou manual.
3. Usa uma tracklist flexivel, editavel pela interface ou por arquivo no modo CLI.
4. Busca uma musica por vez.
5. Clica no melhor candidato de MP3 encontrado nos resultados.
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
|- dist/             # executavel gerado pelo PyInstaller
|- assets/           # logo e icone do aplicativo
|- requirements.txt
|- tracklist.txt     # lista exemplo usada para popular o pacote inicial
|- downloads/        # arquivos MP3 baixados
|- logs/             # logs de execucao (.txt)
`- state/            # historico local e tracklist salva
```

## Instalacao

```bash
pip install -r requirements.txt
playwright install chromium
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
- abrir o editor Tracklist para adicionar, editar e salvar musicas sem mexer em arquivo manualmente
- escolher a pasta de downloads e abrir arquivos gerados
- ligar/desligar login manual, busca assistida, baixar novamente e somente nao encontradas
- acompanhar o log em tempo real
- conferir resumo de baixadas, ignoradas, nao encontradas e erros
- interromper uma execucao em andamento com o botao `Parar`

## Versao Definitiva (Release)

A versao final aprovada desta interface e:

- `release/TrackHunter-v2.0-ui-polish/TrackHunter.exe`
- `release/TrackHunter-v2.0-ui-polish.zip`

Essa e a build oficial para distribuicao nesta fase do projeto.

## Argumentos CLI

- `--tracklist`: caminho do arquivo `.txt` com as musicas.
- `--downloads`: pasta onde os MP3 serao salvos.
- `--logs`: pasta onde os logs de execucao serao salvos.
- `--history`: arquivo JSON usado como historico local.
- `--output`: alias legado para a pasta de downloads.
- `--headless`: executa sem interface grafica.
- `--wait-login`: timeout do login em milissegundos.
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

Comportamentos importantes:

- Uma faixa so e ignorada quando esta no historico e o MP3 ainda existe em `downloads/`.
- Se o MP3 foi apagado de `downloads/`, o TrackHunter baixa novamente.
- Musicas nao encontradas continuam elegiveis para buscas futuras.
- `--force-download` ignora o historico.

## Estrategia de Busca

Para cada faixa, o TrackHunter tenta:

1. Busca completa usando o texto salvo na tracklist.
2. Busca alternativa usando `titulo + versao/remix`, sem artista.

Ele prioriza botoes MP3, usando ZIP/Download como fallback quando necessario.

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
- Use variaveis de ambiente para `MUZPA_EMAIL` e `MUZPA_PASSWORD`.
- Revise o log TXT depois de cada execucao para validar o que foi baixado.
- O matching flexivel ajuda com remixes e versoes alternativas, mas o log deve sempre ser conferido.

## Autor

Projeto desenvolvido e evoluido por Diego Stanisci Malheiros como automacao real e projeto de portfolio.
