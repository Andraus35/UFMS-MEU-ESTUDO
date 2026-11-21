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

Limites honestos: o percentual é o `usage` da ÚLTIMA chamada à API (entrada + cache), não o número da interface; a janela é 200k, ou
1M se configurada (ou se o uso observado a ultrapassar). O CONTEÚDO do prompt é redigido pelo modelo; o script só exige forma e
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

HOME = Path(os.environ.get("CONTEXT_GUARD_HOME") or Path.home())
BASE = HOME / ".claude" / "context-guard"
HANDOFFS = HOME / ".claude" / "handoffs"
CONFIG = HOME / ".claude" / "context-guard.json"
DEFAULTS = {"threshold": 0.5, "window_tokens": 200000, "max_stop_blocks": 3, "repo_copy": None, "min_prompt_chars": 400}
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


def instruction(session_id, pct, c, cwd):
    p = prompt_path(cwd)
    return (
        f"[context-guard] A janela de contexto desta sessão está em {pct * 100:.0f}% (limite {c['threshold'] * 100:.0f}%). "
        "COMECE AGORA, antes de qualquer outro trabalho, a preparar a passagem para a próxima sessão:\n"
        "1. Atualize a memória e o estado persistente do projeto pelas regras do PRÓPRIO projeto (CLAUDE.md/AGENTS.md, arquivos de handoff, "
        "estado, roadmap) e a memória automática do Claude com o que for durável.\n"
        "2. Deixe o repositório inteiro num estado conhecido: rode os testes/gates que o projeto exige se forem rápidos; faça commit e push "
        "SOMENTE se as regras do projeto e do usuário permitirem; senão liste as alterações pendentes no prompt. Nunca force push nem aja "
        "fora das regras do projeto.\n"
        "3. Redija o PROMPT DE START da próxima sessão e sele-o com UM comando (o conteúdo vai no heredoc):\n"
        f"   python3 {script_ref()} seal --session {session_id} --cwd \"{cwd}\" <<'PROMPT'\n"
        "   ## Primeiro passo\n   (a ação exata e o comando para começar)\n   ## Estado\n   (o que está feito, onde parou, branch/PR/SHA, o que está verde ou vermelho)\n"
        "   ## Pendências\n   (decisões e atos do usuário, riscos, armadilhas, o que NÃO fazer)\n   PROMPT\n"
        "   O comando recusa o prompt sem as seções `## Primeiro passo`, `## Estado` e `## Pendências` e anexa os fatos medidos do git.\n"
        f"O prompt selado fica em {p}. Enquanto não houver prompt selado, esta ordem se repete e o fim do turno é bloqueado."
        + (f"\nInstrução específica deste projeto: {c['extra_instruction']}" if isinstance(c.get("extra_instruction"), str) and c["extra_instruction"].strip() else "")
    )


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
    st.update({"cwd": cwd, "pct": round(pct, 4), "seen_at": time.time()})
    if pct >= float(c["threshold"]):
        st.setdefault("armed_at", time.time())
        save_state(sid, st)
        if not st.get("sealed"):
            out(event, text=instruction(sid, pct, c, cwd))
        return
    save_state(sid, st)


def on_stop(payload):
    sid = payload.get("session_id") or "unknown"
    st = load_state(sid)
    if not st.get("armed_at") or st.get("sealed"):
        return
    c = cfg(st.get("cwd") or payload.get("cwd") or os.getcwd())
    blocks = int(st.get("stop_blocks", 0))
    if blocks >= int(c["max_stop_blocks"]):
        return  # nunca prende a sessão: o fallback em PreCompact/SessionEnd cobre
    st["stop_blocks"] = blocks + 1
    save_state(sid, st)
    out("Stop", text=instruction(sid, float(st.get("pct", 0)), c, st.get("cwd") or payload.get("cwd") or os.getcwd())
        + f"\n(bloqueio {blocks + 1} de {c['max_stop_blocks']})")


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
