# E12 — Hook geral de passagem entre sessões (`claude_context_guard`)

**Natureza:** registro do item `HOOKG` (pedido do proprietário de 21/11/2026). O código é **ferramenta de usuário**, vale para **todos os projetos** e é instalado por **ele** em `~/.claude`. **Este PR não ativa nada no projeto**: `.claude/settings.json` e `.claude/` (contrato) **não foram alterados**; a ativação no projeto e na nuvem está no fim, como **proposta para a aprovação dele**.

## O que faz (em código, não por pedido ao modelo)

Mede a janela de contexto da sessão e, ao atingir **50%**, faz a sessão preparar memória, estado do repositório e um **prompt de start** para a próxima sessão, que a sessão nova recebe sozinha.

| Evento | Ação do script |
|---|---|
| `UserPromptSubmit`, `PostToolUse` | mede o contexto pelo `usage` da última chamada à API; a partir do limite injeta a ordem de preparar a passagem, **repetida até o prompt estar selado** |
| `Stop` | **bloqueia o fim do turno** enquanto o prompt não estiver selado, no máximo 3 vezes (nunca prende a sessão) |
| `PreCompact`, `SessionEnd` | sem prompt selado e com trabalho feito, **o próprio script gera** um prompt de fallback (git e últimos pedidos do usuário) |
| `SessionStart` (`startup`, `clear`, `compact`) | entrega à sessão nova o prompt **do mesmo projeto** (raiz do git; pastas com o mesmo nome em caminhos diferentes não se misturam); marca o fallback como "pista, não fato" |
| `seal` (comando) | aceita o prompt só com `## Primeiro passo`, `## Estado` e `## Pendências` e ao menos 400 caracteres; anexa fatos do git e do contexto; arquiva o prompt anterior |

Prompts ficam em `~/.claude/handoffs/<projeto>-<hash>/NEXT_SESSION_PROMPT.md` (histórico em `history/`). Falha do script é **aberta** (nunca derruba a sessão) e vai para `~/.claude/context-guard/errors.log`. Configuração opcional em `~/.claude/context-guard.json`: `threshold` (0,5), `window_tokens` (200000), `max_stop_blocks` (3), `repo_copy` (cópia do prompt dentro do repositório; nulo por padrão).

## Onde está e como instalar

- `scripts/claude_context_guard.py` (o hook) e `scripts/claude_context_guard_install.py` (instalador); testes em `tests/test_claude_context_guard.py` (26) e `tests/test_e12_hook_geral.py`.
- No computador do proprietário: `python3 scripts/claude_context_guard_install.py` (copia o script para `~/.claude/hooks/` e **mescla** os hooks em `~/.claude/settings.json`, com cópia `settings.json.bak-<data>`, sem apagar hooks existentes e de forma idempotente); `--check` confere; `--uninstall` remove só o que instalou. Depois, `/hooks` ou reiniciar.
- **Conferir na prática antes de confiar:** `CONTEXT_GUARD_THRESHOLD=0.01 claude`, mandar uma mensagem e ver a sessão preparar o prompt e rodar o `seal`; abrir uma sessão nova no mesmo projeto e ver o prompt anterior citado.

## O que está provado e o que não está

- **Provado (testes sintéticos em HOME temporário):** limite exato de 50%, não contar subagente nem `isSidechain`, janela 200k ou 1M, limite configurável, transcript ausente ou corrompido sem quebrar, recusa de prompt sem seção ou curto, bloqueio do `Stop` com teto de 3, fallback só quando houve trabalho, não sobrescrever prompt selado da mesma sessão, isolamento entre projetos, falha aberta, instalador que preserva e remove só o seu. **18 de 18 mutações do código mortas** (as duas que sobreviveram na primeira rodada ganharam teste).
- **Não provado:** **nenhum teste em Claude Code real**: os testes simulam a entrada dos hooks; o formato exato da entrada de cada evento (por exemplo `source` do `SessionStart` e a injeção de contexto no `PostToolUse`) é o documentado, não observado. O **percentual é estimativa** do `usage` da última chamada (entrada mais cache) com janela de 200k, ou 1M se configurada ou deduzida; não é o número da interface. O **conteúdo** do prompt é redigido pelo modelo: o script exige a forma e confere fatos do git, não a verdade do texto (por isso a sessão nova o lê como "confira o estado real"). **Commit e push não são feitos pelo hook**: a ordem manda fazê-los só se as regras do projeto e do usuário permitirem. **Hooks de usuário não existem em sessões na nuvem.**

## Proposta para a aprovação dele (NÃO aplicada neste PR)

Ativar o mesmo hook **no projeto** e na **nuvem** exige adicionar ao `.claude/settings.json` (arquivo de contrato, `CODEOWNERS`) os eventos acima apontando para um caminho versionado (por exemplo `python3 scripts/claude_context_guard.py <Evento>`), com `repo_copy` ligado para o prompt sobreviver à máquina efêmera. Isso exige a **aprovação expressa do texto e do merge**, citando PR e head, e é PR **próprio** (outra frente). Texto proposto, para exemplo:

```json
{"hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 scripts/claude_context_guard.py UserPromptSubmit", "timeout": 30}]}]}}
```

(Repetir para `PostToolUse`, `Stop`, `PreCompact`, `SessionEnd` e `SessionStart` com o `matcher` `startup|resume|clear|compact`.) O repositório já tem hooks `Stop` próprios; a mescla precisa preservá-los.

## Frases literais do proprietário

- Conferência feita: `Hook conferido: a ordem apareceu aos <limite> e o seal rodou; a sessão nova citou o prompt anterior.` (ou o que **não** funcionou, com o erro de `~/.claude/context-guard/errors.log`, sem dado pessoal).
- Ativação no projeto: `Aprovo o texto e o merge do PR #<n>, head <sha completo>.`
