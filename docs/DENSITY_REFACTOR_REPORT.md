# TrackHunter density refactor report

Relatorio local da refatoracao de densidade visual executada em 2026-07-14.

## Objetivo

Reduzir espacos desperdicados sem alterar identidade visual, tema, cores, fontes, estilo dos paineis, botoes ou organizacao geral.

## Contagem estrutural

As chamadas continuam existindo porque a alteracao foi conservadora: reduzi valores e padronizei escala, sem trocar a arquitetura visual.

| Metodo | Antes | Depois | Observacao |
| --- | ---: | ---: | --- |
| `setFixedHeight` | 13 | 13 | Valores reduzidos em header, logo, titulo, cards e labels. |
| `setMinimumHeight` | 14 | 14 | Valores reduzidos em paineis, log, timeouts e cards. |
| `setContentsMargins` | 34 | 34 | Valores reduzidos e parte deles passou a usar constantes. |
| `setSpacing` | 27 | 27 | Valores reduzidos e parte deles passou a usar constantes. |
| `resize` | 5 | 5 | Sem alteracao nesta etapa. |
| `setFixedSize` | 5 | 5 | Mantidos para preservar botoes principais e dialogos. |

## Proxy quantitativo de densidade

Proxy calculado somando alturas fixas, alturas minimas numericas, alturas de `setFixedSize`, spacings e margens verticais.

| Grupo | Antes | Depois | Reducao |
| --- | ---: | ---: | ---: |
| `setFixedHeight` | 450 | 422 | 6,22% |
| `setMinimumHeight` | 656 | 572 | 12,80% |
| `setFixedSize` | 192 | 192 | 0,00% |
| `setSpacing` | 214 | 103 | 51,87% |
| `setContentsMargins` | 297 | 172 | 42,09% |
| Total | 1809 | 1461 | 19,24% |

## Componentes ajustados

- `Panel`: margem e spacing padrao reduzidos.
- `SummaryCard`: altura minima, padding interno e distancia entre valor/titulo reduzidos.
- `TrackHunterWindow._layout_profile`: alturas de linhas, gaps, margens da janela e altura de log reduzidas.
- `Autenticacao`: espaco vertical desperdicado reduzido removendo stretch superior.
- `Opcoes`: spacing do grid, altura das linhas e blocos de timeout reduzidos.
- `Arquivos`: margens internas, spacing e altura minima das linhas reduzidos.
- `Resumo`: spacing entre cards, margem do painel e bloco de historico reduzidos.
- `Acoes`: spacing entre barra, percentual e botoes reduzido.
- `Log`: altura minima do painel e da lista reduzida.
- `Header`: altura do logo/header reduzida de forma conservadora.

## Constantes criadas

- `PANEL_MARGIN = 12`
- `PANEL_SPACING = 8`
- `SECTION_SPACING = 8`
- `FIELD_SPACING = 6`
- `CARD_MARGIN = 10`
- `CARD_SPACING = 8`
- `GROUPBOX_PADDING = 12`
- `LOG_PADDING = 8`

## Margens e paddings alterados

- Painel padrao: `16,14,16,14` para `12,12,12,12`.
- Arquivos: `16,14,16,12` para `12,12,12,10`.
- Opcoes: `16,14,16,18` para `12,12,12,12`.
- Resumo: `16,14,16,14` para `12,12,12,12`.
- Cards: `14,9,14,8` para `10,6,10,6`.
- Janela principal: `22,16,22,10` para `18,12,18,8`.

## Alturas reduzidas

- Linha superior ampla: `310` para `286`.
- Linha superior notebook: `310` para `276`.
- Linha superior compacta: `306` para `266`.
- Linha inferior ampla: `210` para `184`.
- Linha inferior notebook: `210` para `176`.
- Linha inferior compacta: `182` para `160`.
- Log amplo: `210/176` para `180/150`.
- Log notebook: `112` para `96`.
- `SummaryCard`: `66` para `58`.
- `Log panel`: `212` para `180`.
- `Output log`: `124` para `104`.
- Header/logo inicial: `76/70` para `68/62`.

## Tamanhos minimos removidos

Nenhum tamanho minimo foi removido nesta etapa. A estrategia foi reduzir valores e manter restricoes existentes para evitar regressao visual.

## Validacao de resolucoes

Smoke test em Qt offscreen:

| Resolucao alvo | Janela testada | Resultado |
| --- | --- | --- |
| 1920x1080 | 1480x996 | OK |
| 1600x900 | 1472x846 | OK |
| 1366x768 | 1256x722 | OK |
| 1280x720 | 1180x680 | OK |

## Screenshots

- Antes: `docs/screenshots/density_refactor/before/`
- Depois: `docs/screenshots/density_refactor/after/`

Observacao: as screenshots sao geradas via Qt offscreen para evidencia tecnica; em algumas maquinas esse modo pode renderizar glifos de texto de forma simplificada, mas preserva layout, espacamento e proporcoes.

## Arquivos modificados

- `trackhunter/app.py`
- `docs/DENSITY_REFACTOR_REPORT.md`
