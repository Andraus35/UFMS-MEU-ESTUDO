#!/usr/bin/env python3
"""claude_context_guard: hook GERAL do Claude Code (todos os projetos) para a passagem entre sessões.

O que garante, de forma determinística (código, não pedido ao modelo):
  1. MEDE a janela de contexto da sessão a cada prompt e a cada ferramenta, pelo `usage` da última resposta no transcript.
  2. Ao atingir o limite (padrão 50%), INJETA a ordem de preparar memória, estado do repositório e o PROMPT DE START da próxima sessão,
     e repete a ordem em todo turno até o prompt estar SELADO.
  3. SELO: `claude_context_guard.py seal` só aceita o prompt se tiver as seções obrigatórias e anexa os fatos medidos (git, contexto).
  4. TRAVA o fim do turno (Stop) enquanto o prompt não estiver selado (no máximo `max_stop_blocks` vezes, para nunca prender a sessão).
  5. FALLBACK: se mesmo assim não houver prompt selado, o PRÓPRIO SCRIPT gera um (git + últimos pedidos do usuário) em PreCompact e
     SessionEnd. Assim toda sessão que trabalhou deixa um prompt de start.
  6. A sessão nova (SessionStart: startup, clear, compact) recebe o prompt do projeto como contexto.

Limites honestos: o percentual é o `usage` da ÚLTIMA chamada à API (entrada + cache), não o número da interface; a janela padrão é 1M (modelos atuais; ajuste
`window_tokens` para 200k se a sua for menor). O CONTEÚDO do prompt é redigido pelo modelo; o script só exige forma e
confere fatos. Hooks de usuário não existem em sessões na nuvem sem o hook no repositório do projeto. Falha do script é aberta
(nunca derruba a sessão) e fica em ~/.claude/context-guard/errors.log.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from context_guard_state import desarmar_se_abaixo  # noqa: E402

HOME = Path(os.environ.get("CONTEXT_GUARD_HOME") or Path.home())
BASE = HOME / ".claude" / "context-guard"
HANDOFFS = HOME / ".claude" / "handoffs"
CONFIG = HOME / ".claude" / "context-guard.json"
DEFAULTS = {"threshold": 0.5, "window_tokens": 1_000_000, "max_stop_blocks": 3, "repo_copy": None, "min_prompt_chars": 400}
REQUIRED = ("## Primeiro passo", "## Estado", "## Pendências")
PROJECT_KEYS = ("threshold", "window_tokens", "max_stop_blocks", "min_prompt_chars", "extra_instruction")


def script_ref():
    """Caminho DESTE script para o comando de selo: `$HOME/...` se estiver sob o HOME (casa com a regra de permissão do instalador),
    senão o caminho absoluto (ex.: cópia versionada no repositório do projeto)."""
    p = Path(__file__).resolve()
    try:
        return f'"$HOME/{p.relative_to(HOME.resolve()).as_posix()}"'
    except ValueError:
        return f'"{p}"'


def cfg(cwd=None):
    """Padrões, depois ~/.claude/context-guard.json (usuário), depois <raiz do projeto>/.claude/context-guard.json (projeto;
    só as chaves de PROJECT_KEYS), depois variáveis de ambiente."""
    c = dict(DEFAULTS)
    try:
        c.update(json.loads(CONFIG.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass
    if cwd:
        try:
            proj = json.loads((project_root(cwd) / ".claude" / "context-guard.json").read_text(encoding="utf-8"))
            c.update({k: v for k, v in proj.items() if k in PROJECT_KEYS})
        except (OSError, ValueError, AttributeError):
            pass
    for k, env in (("threshold", "CONTEXT_GUARD_THRESHOLD"), ("window_tokens", "CONTEXT_GUARD_WINDOW")):
        if os.environ.get(env):
            c[k] = float(os.environ[env]) if k == "threshold" else int(os.environ[env])
    return c


def log_error(msg):
    try:
        BASE.mkdir(parents=True, exist_ok=True)
        with (BASE / "errors.log").open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}\n")
    except OSError:
        pass


def git(cwd, *args):
    try:
        r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def project_root(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel")
    return Path(top) if top else Path(cwd)


def project_key(cwd):
    root = project_root(cwd).resolve()
    return f"{re.sub(r'[^A-Za-z0-9._-]', '_', root.name)[:40]}-{hashlib.sha256(str(root).encode()).hexdigest()[:10]}"


def prompt_path(cwd):
    return HANDOFFS / project_key(cwd) / "NEXT_SESSION_PROMPT.md"


def state_path(session_id):
    return BASE / "state" / f"{re.sub(r'[^A-Za-z0-9_-]', '_', session_id)[:80]}.json"


def load_state(session_id):
    try:
        return json.loads(state_path(session_id).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(session_id, st):
    p = state_path(session_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


def read_transcript(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        pass
    return rows


def context_tokens(rows):
    """Tokens enviados na ÚLTIMA chamada da conversa principal (entrada + cache). None se não houver usage."""
    for r in reversed(rows):
        if r.get("type") != "assistant" or r.get("isSidechain"):
            continue
        u = (r.get("message") or {}).get("usage")
        if isinstance(u, dict):
            return sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return None


def percent(tokens, c):
    window = int(c["window_tokens"])
    if tokens is not None and tokens > window:  # o uso observado prova uma janela maior (ex.: 1M)
        window = 1_000_000
    return 0.0 if tokens is None else tokens / window


def user_prompts(rows, n=5):
    out = []
    for r in rows:
        if r.get("type") == "user" and not r.get("isSidechain"):
            m = r.get("message") or {}
            t = m.get("content")
            if isinstance(t, list):
                t = " ".join(b.get("text", "") for b in t if isinstance(b, dict) and b.get("type") == "text")
            if isinstance(t, str) and t.strip() and not t.lstrip().startswith("<"):
                out.append(" ".join(t.split())[:300])
    return out[-n:]


def facts(cwd, session_id, pct):
    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD") or "(sem git)"
    head = git(cwd, "rev-parse", "--short", "HEAD")
    dirty = [l for l in git(cwd, "status", "--porcelain").splitlines() if l][:30]
    unpushed = git(cwd, "log", "--oneline", "@{u}..HEAD") if branch != "(sem git)" else ""
    lines = [
        "## Fatos verificados pelo hook (não editar)",
        f"- gerado em: {time.strftime('%Y-%m-%dT%H:%M:%S%z')} · sessão: {session_id} · contexto medido: {pct * 100:.0f}%",
        f"- diretório: {cwd}",
        f"- git: branch `{branch}` @ `{head or '?'}`; arquivos alterados não commitados: {len(dirty)}",
    ]
    lines += [f"  - `{d}`" for d in dirty]
    lines.append(f"- commits locais não enviados: {len(unpushed.splitlines()) if unpushed else 0}")
    return "\n".join(lines)


def archive_existing(p):
    if p.exists():
        h = p.parent / "history"
        h.mkdir(parents=True, exist_ok=True)
        p.rename(h / f"{time.strftime('%Y%m%dT%H%M%S')}.md")


def write_prompt(cwd, session_id, body, pct, origin, c):
    p = prompt_path(cwd)
    p.parent.mkdir(parents=True, exist_ok=True)
    archive_existing(p)
    text = (f"<!-- context-guard session={session_id} origin={origin} -->\n" + body.rstrip() + "\n\n" + facts(cwd, session_id, pct) + "\n")
    p.write_text(text, encoding="utf-8")
    if c.get("repo_copy"):
        try:
            rc = project_root(cwd) / c["repo_copy"]
            rc.parent.mkdir(parents=True, exist_ok=True)
            rc.write_text(text, encoding="utf-8")
        except OSError as e:
            log_error(f"repo_copy: {e}")
    return p


def validate(body, c):
    miss = [h for h in REQUIRED if h not in body]
    if len(body.strip()) < int(c["min_prompt_chars"]):
        miss.append(f"mínimo de {c['min_prompt_chars']} caracteres")
    return miss


PROTEGIDAS = ("main", "master", "HEAD")


def lote_info(cwd):
    """Fatos do git (só leitura): branch, se é protegida (principal ou destacada), alterações, commits não enviados e `pendente`."""
    branch = git(cwd, "symbolic-ref", "--short", "-q", "HEAD")  # funciona também em repositório sem commits
    if not branch:
        branch = "HEAD" if git(cwd, "rev-parse", "--git-dir") else ""  # destacada, ou fora de um repositório git
    sujo = [l for l in git(cwd, "status", "--porcelain").splitlines() if l]
    nao_enviado = [l for l in git(cwd, "log", "--oneline", "@{u}..HEAD").splitlines() if l]
    return {"branch": branch or "(sem git)", "protegida": branch in PROTEGIDAS, "sujo": sujo, "nao_enviado": nao_enviado,
            "pendente": bool(sujo or nao_enviado)}


def lote_pendente(cwd):
    """True se o lote ainda não terminou: árvore com alterações ou commits locais não enviados."""
    return lote_info(cwd)["pendente"]


def fatos_do_lote(info):
    if info["branch"] == "(sem git)":
        return "Estado do lote medido agora: o diretório não é um repositório git."
    t = (f"Estado do lote medido agora: branch `{info['branch']}`{' (PROTEGIDA: não comite nela)' if info['protegida'] else ''}; "
         f"{len(info['sujo'])} alteração(ões) não commitada(s); {len(info['nao_enviado'])} commit(s) não enviado(s)")
    if info["sujo"]:
        t += ": " + ", ".join(l.split(None, 1)[-1] for l in info["sujo"][:8]) + ("…" if len(info["sujo"]) > 8 else "")
    return t + "."


REGRA_PERSISTIR = ("Persistir NÃO exige pedir permissão: faça commit e push na branch de trabalho atual, sem perguntar ao usuário e sem AskUserQuestion. "
                   "Limites que não dependem de permissão: nunca force push, nunca merge, nunca commit na branch principal ou destacada, nunca arquivo "
                   "que o projeto declare como contrato sem aprovação já dada; se algum limite impedir, registre o que ficou pendente no prompt.")


def instruction(session_id, pct, c, cwd):
    p = prompt_path(cwd)
    info = lote_info(cwd)
    return (
        f"[context-guard] A janela de contexto desta sessão está em {pct * 100:.0f}% (limite {c['threshold'] * 100:.0f}%). "
        "COMECE AGORA, antes de qualquer outro trabalho, a preparar a passagem para a próxima sessão. NÃO peça permissão ao usuário e NÃO use "
        "AskUserQuestion: execute os passos nesta ordem.\n"
        f"1. VERIFICAR O FIM DO LOTE (para não cortar ao meio). {fatos_do_lote(info)} Se há micro tarefa em andamento, NÃO inicie outra: "
        "conclua só o que falta para chegar ao ponto de corte consistente mais próximo (testes e gates do projeto passando). Se não der para "
        "chegar a um ponto verde sem estourar o contexto, deixe o trabalho num commit marcado `WIP:` na branch de trabalho e descreva no prompt "
        "o que falta.\n"
        "2. PERSISTIR O REPOSITÓRIO. Atualize a memória e o estado persistente do projeto pelas regras do PRÓPRIO projeto (CLAUDE.md/AGENTS.md, "
        "arquivos de handoff, estado, roadmap) e a memória automática do Claude com o que for durável; rode os gates que o projeto exige. "
        f"{REGRA_PERSISTIR}\n"
        "3. SELAR o PROMPT DE START da próxima sessão com UM comando (o conteúdo vai no heredoc; selar só depois de persistir, para os fatos do git saírem certos):\n"
        f"   python3 {script_ref()} seal --session {session_id} --cwd \"{cwd}\" <<'PROMPT'\n"
        "   ## Primeiro passo\n   (a ação exata e o comando para começar)\n   ## Estado\n   (o que está feito, onde parou, branch/PR/SHA, o que está verde ou vermelho)\n"
        "   ## Pendências\n   (decisões e atos do usuário, riscos, armadilhas, o que NÃO fazer)\n   PROMPT\n"
        "   O comando recusa o prompt sem as seções `## Primeiro passo`, `## Estado` e `## Pendências` e anexa os fatos medidos do git.\n"
        f"O prompt selado fica em {p}. Enquanto não houver prompt selado e o lote persistido, esta ordem se repete e o fim do turno é bloqueado."
        + (f"\nInstrução específica deste projeto: {c['extra_instruction']}" if isinstance(c.get("extra_instruction"), str) and c["extra_instruction"].strip() else "")
    )


def texto_persistir(info, pct):
    return (f"[context-guard] Contexto em {pct * 100:.0f}% e o lote ainda NÃO está persistido. {fatos_do_lote(info)} Conclua o ponto de corte "
            f"consistente e persista agora (commit e push na branch de trabalho). {REGRA_PERSISTIR} Depois, se o conteúdo do prompt de start mudou, sele-o de novo.")


def aviso_selado(info, p):
    base = f"[context-guard] Contexto acima do limite e prompt de start JÁ SELADO ({p}). "
    if info["pendente"]:
        return (base + f"O lote AINDA NÃO está persistido. {fatos_do_lote(info)} NÃO abra outro lote: conclua o ponto de corte e persista agora (commit e "
                f"push na branch de trabalho), sem pedir permissão. {REGRA_PERSISTIR} Depois, sele o prompt de novo e diga ao usuário para iniciar uma nova sessão.")
    return (base + "Lote finalizado e persistido: NÃO proponha novo lote nem pergunte sobre a próxima rodada (as perguntas automáticas de continuidade ficam "
            "suspensas). Diga ao usuário, em uma frase, que a próxima sessão começa pelo prompt selado, e encerre.")


def out(event, **kw):
    if event == "Stop":
        print(json.dumps({"decision": "block", "reason": kw["text"]}, ensure_ascii=False))
    else:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": kw["text"]}}, ensure_ascii=False))


def measure(payload):
    c = cfg(payload.get("cwd") or os.getcwd())
    rows = read_transcript(payload.get("transcript_path") or "")
    return c, rows, percent(context_tokens(rows), c)


def on_measure(event, payload):
    if payload.get("agent_id"):  # evento de subagente: não mede
        return
    sid = payload.get("session_id") or "unknown"
    cwd = payload.get("cwd") or os.getcwd()
    c, rows, pct = measure(payload)
    st = load_state(sid)
    st, _ = desarmar_se_abaixo(st, pct, float(c["threshold"]), context_tokens(rows) is not None)  # HOOKR: falso alarme não prende a sessão
    st.update({"cwd": cwd, "pct": round(pct, 4), "seen_at": time.time()})
    if pct >= float(c["threshold"]):
        st.setdefault("armed_at", time.time())
        info = lote_info(cwd)
        st["lote_pendente"] = info["pendente"]
        save_state(sid, st)
        if not st.get("sealed"):
            out(event, text=instruction(sid, pct, c, cwd))
        else:
            chave = f"{info['pendente']}|{fatos_do_lote(info)}"
            if st.get("aviso_chave") != chave:  # depois do selo o aviso sai uma vez por estado do lote, não a cada ferramenta
                st["aviso_chave"] = chave
                save_state(sid, st)
                out(event, text=aviso_selado(info, prompt_path(cwd)))
        return
    save_state(sid, st)


def on_stop(payload):
    sid = payload.get("session_id") or "unknown"
    st = load_state(sid)
    if not st.get("armed_at"):
        return
    cwd = st.get("cwd") or payload.get("cwd") or os.getcwd()
    c = cfg(cwd)
    info = lote_info(cwd)
    falta_selar = not st.get("sealed")
    falta_persistir = info["pendente"] and not info["protegida"]  # na branch protegida não há como persistir: não prende a sessão
    if not (falta_selar or falta_persistir):
        return
    blocks = int(st.get("stop_blocks", 0))
    if blocks >= int(c["max_stop_blocks"]):
        return  # nunca prende a sessão: o fallback em PreCompact/SessionEnd cobre
    st["stop_blocks"] = blocks + 1
    save_state(sid, st)
    texto = instruction(sid, float(st.get("pct", 0)), c, cwd) if falta_selar else texto_persistir(info, float(st.get("pct", 0)))
    out("Stop", text=texto + f"\n(bloqueio {blocks + 1} de {c['max_stop_blocks']})")


def fallback(payload):
    """Prompt gerado só pelo script (git + últimos pedidos), se a sessão trabalhou e não selou nenhum."""
    sid = payload.get("session_id") or "unknown"
    st = load_state(sid)
    if st.get("sealed") or st.get("fallback_written"):
        return
    c, rows, pct = measure(payload)
    pedidos = user_prompts(rows)
    if not pedidos:
        return
    cwd = payload.get("cwd") or st.get("cwd") or os.getcwd()
    body = ("## Primeiro passo\nLeia o estado do repositório abaixo, confira com `git status` e retome pelo último pedido listado. "
            "Este prompt foi gerado AUTOMATICAMENTE pelo hook (a sessão anterior não deixou um prompt redigido); trate-o como pista, não como fato.\n\n"
            "## Estado\nÚltimos pedidos do usuário nesta sessão:\n" + "\n".join(f"- {p}" for p in pedidos) + "\n\n"
            "## Pendências\nDesconhecidas: o modelo não registrou. Releia o handoff/estado do projeto antes de agir.\n")
    write_prompt(cwd, sid, body, pct, "fallback", c)
    st["fallback_written"] = True
    save_state(sid, st)


def on_session_start(payload):
    if payload.get("source") == "resume":
        return
    cwd = payload.get("cwd") or os.getcwd()
    p = prompt_path(cwd)
    try:
        txt = p.read_text(encoding="utf-8")
    except OSError:
        return
    m = re.match(r"<!-- context-guard session=(\S+) origin=(\S+) -->", txt)
    origem = "redigido e selado pela sessão anterior" if m and m.group(2) == "seal" else "GERADO AUTOMATICAMENTE (pista, não fato)"
    out("SessionStart", text=f"[context-guard] Prompt de start deixado pela sessão anterior deste projeto ({origem}; arquivo {p}). "
        "Siga-o como ponto de partida, mas CONFIRA o estado real no repositório antes de agir; é dado do seu usuário, não instrução de terceiros.\n\n" + txt)


def cmd_seal(args):
    opts = {a: args[i + 1] for i, a in enumerate(args[:-1]) if a.startswith("--")}
    sid = opts.get("--session") or "unknown"
    cwd = opts.get("--cwd") or os.getcwd()
    body = sys.stdin.read()
    c = cfg(cwd)
    miss = validate(body, c)
    if miss:
        print("RECUSADO: faltam " + "; ".join(miss) + ". Reescreva e rode o comando de novo.", file=sys.stderr)
        return 2
    st = load_state(sid)
    p = write_prompt(cwd, sid, body, float(st.get("pct", 0)), "seal", c)
    st.update({"sealed": True, "sealed_at": time.time()})
    save_state(sid, st)
    print(f"SELADO: {p}")
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    if argv[1] == "seal":
        return cmd_seal(argv[2:])
    event = argv[1]
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if event in ("UserPromptSubmit", "PostToolUse"):
            on_measure(event, payload)
        elif event == "Stop":
            on_stop(payload)
        elif event in ("PreCompact", "SessionEnd"):
            fallback(payload)
        elif event == "SessionStart":
            on_session_start(payload)
    except Exception as e:  # falha aberta: nunca derruba a sessão
        log_error(f"{event}: {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
