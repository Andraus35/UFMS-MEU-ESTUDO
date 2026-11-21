#!/usr/bin/env python3
"""Instala (ou remove) o context-guard no usuário: copia o script e MESCLA os hooks em ~/.claude/settings.json, sem apagar nada.

Uso:  python3 install.py            instala/atualiza (idempotente; guarda cópia em settings.json.bak-AAAAMMDDHHMMSS)
      python3 install.py --uninstall  remove só o que este instalador criou
      python3 install.py --check      confere se está instalado, sem escrever
"""
import json
import shutil
import sys
import time
from pathlib import Path

def _home():
    if "--home" in sys.argv:  # só para teste: instala num HOME alternativo
        i = sys.argv.index("--home")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return Path.home()


HOME = _home()
SETTINGS = HOME / ".claude" / "settings.json"
DEST = HOME / ".claude" / "hooks" / "claude_context_guard.py"
SRC = Path(__file__).resolve().parent / "claude_context_guard.py"
MARK = "claude_context_guard.py"
CMD = 'python3 "$HOME/.claude/hooks/claude_context_guard.py" {}'
EVENTS = {"SessionStart": "startup|resume|clear|compact", "UserPromptSubmit": None, "PostToolUse": None, "Stop": None,
          "PreCompact": None, "SessionEnd": None}
ALLOW = ['Bash(python3 "$HOME/.claude/hooks/claude_context_guard.py" seal*)']


def load():
    if not SETTINGS.exists():
        return {}
    return json.loads(SETTINGS.read_text(encoding="utf-8"))  # JSON inválido: levanta, nada é escrito


def ours(group):
    return any(MARK in (h.get("command") or "") for h in group.get("hooks", []))


def merge(s):
    hooks = s.setdefault("hooks", {})
    for ev, matcher in EVENTS.items():
        groups = [g for g in hooks.get(ev, []) if not ours(g)]  # troca só o nosso, preserva os outros
        g = {"hooks": [{"type": "command", "command": CMD.format(ev), "timeout": 30}]}
        if matcher:
            g["matcher"] = matcher
        hooks[ev] = groups + [g]
    allow = s.setdefault("permissions", {}).setdefault("allow", [])
    for a in ALLOW:
        if a not in allow:
            allow.append(a)
    return s


def strip(s):
    hooks = s.get("hooks", {})
    for ev in list(hooks):
        hooks[ev] = [g for g in hooks[ev] if not ours(g)]
        if not hooks[ev]:
            del hooks[ev]
    if not hooks:
        s.pop("hooks", None)
    allow = s.get("permissions", {}).get("allow", [])
    s.get("permissions", {})["allow"] = [a for a in allow if a not in ALLOW]
    return s


def installed(s):
    hooks = s.get("hooks", {})
    return all(any(ours(g) for g in hooks.get(ev, [])) for ev in EVENTS) and DEST.exists()


def main():
    mode = next((a for a in sys.argv[1:] if a in ("--uninstall", "--check")), "install")
    s = load()
    if mode == "--check":
        print("INSTALADO" if installed(s) else "NÃO INSTALADO")
        return 0 if installed(s) else 1
    if SETTINGS.exists():
        shutil.copy2(SETTINGS, SETTINGS.with_name(f"settings.json.bak-{time.strftime('%Y%m%d%H%M%S')}"))
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    if mode == "--uninstall":
        s = strip(s)
    else:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC, DEST)
        s = merge(s)
    SETTINGS.write_text(json.dumps(s, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(("REMOVIDO" if mode == "--uninstall" else "INSTALADO") + f": {SETTINGS}")
    print("Abra /hooks no Claude Code (ou reinicie) para recarregar a configuração.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
