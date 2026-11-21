# E12 — Hook geral de passagem entre sessões (`claude_context_guard`)

**Natureza:** registro do item `HOOKG` (pedido do proprietário de 21/11/2026). **E12-A (PR #157, mesclado):** o código é **ferramenta de usuário**, vale para **todos os projetos** e é instalado por **ele** em `~/.claude`. **E12-B (este lote, PR #158):** **ativação no projeto**, para valer também nas sessões na nuvem (que não leem o `~/.claude` dele): alteração de `.claude/settings.json` e criação de `.claude/context-guard.json`, **arquivos de contrato** (`CODEOWNERS`). **Situação de E12-B: proposta aguardando a aprovação expressa do texto e do merge, citando PR e head;** até lá, nada vale na `main`.

## O que faz (em código, não por pedido ao modelo)

Mede a janela de contexto da sessão e, ao atingir **50%**, faz a sessão preparar memória, estado do repositório e um **prompt de start** para a próxima sessão, que a sessão nova recebe sozinha.

| Evento | Ação do script |
|---|---|
| `UserPromptSubmit`, `PostToolUse` | mede o contexto pelo `usage` da última chamada à API; a partir do limite injeta a ordem de preparar a passagem, **repetida até o prompt estar selado** |
| `Stop` | **bloqueia o fim do turno** enquanto o prompt não estiver selado, no máximo 3 vezes (nunca prende a sessão) |
| `PreCompact`, `SessionEnd` | sem prompt selado e com trabalho feito, **o próprio script gera** um prompt de fallback (git e últimos pedidos do usuário) |
| `SessionStart` (`startup`, `clear`, `compact`) | entrega à sessão nova o prompt **do mesmo projeto** (raiz do git; pastas com o mesmo nome em caminhos diferentes não se misturam); marca o fallback como "pista, não fato" |
| (aos 50%, **ordem imposta**) | 1) **verificar o fim do lote** (git medido) e concluir só o ponto de corte, 2) **persistir sem pedir permissão** (commit e push na branch de trabalho, nunca force push, merge nem branch principal), 3) selar; `Stop` bloqueia até selar **e** persistir (ver E13) |
| (acima do limite, **já selado**) | a cada prompt e ferramenta avisa para **não propor novo lote** e encerrar se o lote está finalizado, ou finalizar o lote pendente antes (correção de 21/11/2026; ver E13); e **faz as perguntas de continuidade do projeto cederem** |
| `seal` (comando) | aceita o prompt só com `## Primeiro passo`, `## Estado` e `## Pendências` e ao menos 400 caracteres; anexa fatos do git e do contexto; arquiva o prompt anterior |

Prompts ficam em `~/.claude/handoffs/<projeto>-<hash>/NEXT_SESSION_PROMPT.md` (histórico em `history/`). Falha do script é **aberta** (nunca derruba a sessão) e vai para `~/.claude/context-guard/errors.log`. Configuração opcional em `~/.claude/context-guard.json`: `threshold` (0,5), `window_tokens` (1000000), `max_stop_blocks` (3), `repo_copy` (cópia do prompt dentro do repositório; nulo por padrão).

## Onde está e como instalar

- `scripts/claude_context_guard.py` (o hook) e `scripts/claude_context_guard_install.py` (instalador); testes em `tests/test_claude_context_guard.py` (26) e `tests/test_e12_hook_geral.py`.
- No computador do proprietário: `python3 scripts/claude_context_guard_install.py` (copia o script para `~/.claude/hooks/` e **mescla** os hooks em `~/.claude/settings.json`, com cópia `settings.json.bak-<data>`, sem apagar hooks existentes e de forma idempotente); `--check` confere; `--uninstall` remove só o que instalou. Depois, `/hooks` ou reiniciar.
- **Conferir na prática antes de confiar:** `CONTEXT_GUARD_THRESHOLD=0.01 claude`, mandar uma mensagem e ver a sessão preparar o prompt e rodar o `seal`; abrir uma sessão nova no mesmo projeto e ver o prompt anterior citado.

## O que está provado e o que não está

- **Provado (testes sintéticos em HOME temporário):** limite exato de 50%, não contar subagente nem `isSidechain`, janela 200k ou 1M, limite configurável, transcript ausente ou corrompido sem quebrar, recusa de prompt sem seção ou curto, bloqueio do `Stop` com teto de 3, fallback só quando houve trabalho, não sobrescrever prompt selado da mesma sessão, isolamento entre projetos, falha aberta, instalador que preserva e remove só o seu. **18 de 18 mutações do código mortas** (as duas que sobreviveram na primeira rodada ganharam teste).
- **Não provado:** **nenhum teste em Claude Code real**: os testes simulam a entrada dos hooks; o formato exato da entrada de cada evento (por exemplo `source` do `SessionStart` e a injeção de contexto no `PostToolUse`) é o documentado, não observado. O **percentual é estimativa** do `usage` da última chamada (entrada mais cache) com janela de **1M** por padrão (corrigido no lote HOOKW de 21/11/2026: o padrão de 200k dava falso alarme, 97% quando a interface mostrava 19%); configurável; não é o número da interface. O **conteúdo** do prompt é redigido pelo modelo: o script exige a forma e confere fatos do git, não a verdade do texto (por isso a sessão nova o lê como "confira o estado real"). **Commit e push não são feitos pelo hook**: a ordem manda fazê-los só se as regras do projeto e do usuário permitirem. **Hooks de usuário não existem em sessões na nuvem.**

## E12-B — ativação no projeto (este PR; aguarda a aprovação dele)

**O que muda (somente `.claude/`):**

| Arquivo | Antes | Depois |
|---|---|---|
| `.claude/settings.json` | só dois hooks `Stop` (`perguntas_boas_praticas.py`, `entrega_final.py`) | **preserva os dois** e acrescenta `SessionStart` (`startup\|resume\|clear\|compact`), `UserPromptSubmit`, `PostToolUse`, `Stop`, `PreCompact` e `SessionEnd`, todos com `python3 "$CLAUDE_PROJECT_DIR/scripts/claude_context_guard.py" <Evento>` e `timeout` 30 |
| `.claude/context-guard.json` (novo) | não existia | `extra_instruction` do projeto: onde registrar o ponto de retomada (`memory/HANDOFF.md`), quais gates rodar, **commit e push só na branch de trabalho e só se o lote foi autorizado; nunca merge, push forçado nem arquivo de contrato sem aprovação expressa**, e o prompt de start abre com `bootstrap.py --mode engineering` e `next_task.py` |

**Ajustes no script (mesmo PR, sem mudar o comportamento já testado):** o comando de `seal` aponta para o **próprio caminho do script** (`$HOME/...` se estiver sob o HOME, senão o absoluto), e o script lê `.claude/context-guard.json` do projeto (apenas `threshold`, `window_tokens`, `max_stop_blocks`, `min_prompt_chars` e `extra_instruction`; **`repo_copy` do projeto é ignorado**).

**O que NÃO muda:** nenhuma regra do `AGENTS.md`, `PRODUCT.md`, `agents/`, esquema de comandos, flags de escrita nem os dois hooks `Stop` existentes. Não há regra de permissão nova: o `seal` pode pedir confirmação de execução, a menos que o instalador de usuário (que acrescenta a regra no `~/.claude`) esteja instalado.

**Riscos e limites declarados:**
- **Três hooks `Stop` no mesmo evento** (perguntas, entrega final e este). Todos podem bloquear o fim do turno; o deste é limitado a 3 bloqueios, o de entrega final tem trava própria. **A combinação não foi testada em Claude Code real.**
- **Persistência na nuvem:** o prompt selado fica em `~/.claude/handoffs/` **da máquina da sessão**, que na nuvem é efêmera. O que sobrevive é o que for **commitado**: por isso a instrução do projeto manda registrar o essencial no `memory/HANDOFF.md`. **Não há `repo_copy` no projeto** (um arquivo não rastreado sujaria a árvore e faria o hook de entrega final bloquear). Corrige o que o registro E12-A dizia sobre `repo_copy` resolver a máquina efêmera.
- O hook **mede com atraso de um turno** e o percentual é estimativa; o conteúdo do prompt é do modelo; commit e push não são feitos pelo hook.
- Se o script faltar ou falhar, o hook falha **aberto** (a sessão segue) e registra em `~/.claude/context-guard/errors.log`.

**Como desfazer:** reverter este PR, ou remover as seis entradas `claude_context_guard` de `.claude/settings.json`.

## Frases literais do proprietário

- Conferência feita: `Hook conferido: a ordem apareceu aos <limite> e o seal rodou; a sessão nova citou o prompt anterior.` (ou o que **não** funcionou, com o erro de `~/.claude/context-guard/errors.log`, sem dado pessoal).
- Aprovação da E12-B (altera `.claude/`): `Aprovo o texto e o merge do PR #158, head <sha completo>.`


**Lote HOOKW (21/11/2026):** o padrão da janela passou de 200k para 1M (script e `.claude/context-guard.json`), e depois do selo o aviso sai **uma vez por estado do lote**, não a cada ferramenta (antes repetia cerca de 600 tokens por chamada). Testes: `JanelaPadraoTests` (187k não dispara, 500k dispara, config versionada, silêncio após o aviso). **Não provado:** o percentual continua a estimativa da última chamada, 2 a 3 pontos acima da interface.
