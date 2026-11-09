"""Gate determinístico dos perfis de agente (Tutor, Coach e Zapia).

Verifica estrutura, ausência de estado e segredos, referências a arquivos e, principalmente, a
separação de responsabilidades: cada operação exclusiva pertence a um só agente e cada perfil
lista exatamente as operações a que tem direito. O perfil da Zapia deve executar exatamente a união
dessas operações, coerente com `config/agent_command_schema.json`. Não prova compreensão semântica por LLM.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

SHARED = frozenset({"ler_arquivo_repositorio", "enviar_mensagem"})
TUTOR_ONLY = frozenset({"registrar_resultado", "registrar_exportacao_desempenho", "registrar_plano",
                        "enviar_prompt_notebook"})
COACH_ONLY = frozenset({"criar_lembrete", "consultar_agenda_minima", "registrar_acompanhamento"})
SPECS = {
    "agents/TUTOR.md": {"title": "# Tutor (Aragonê)", "ops": SHARED | TUTOR_ONLY,
                        "must": ("único produtor de conteúdo", "Não recebe credenciais")},
    "agents/COACH.md": {"title": "# Coach (Carter)", "ops": SHARED | COACH_ONLY,
                        "must": ("Não produz conteúdo de revisão", "Não recebe credenciais")},
}
ZAPIA_HEADINGS = ("## Missão", "## Faz", "## Não faz", "## START", "## Comandos que executa", "## Relato",
                 "## Regras", "## Limites e segurança")
ZAPIA_SPEC = {
    "title": "# Zapia (interface e executora)", "ops": SHARED | TUTOR_ONLY | COACH_ONLY,
    "headings": ZAPIA_HEADINGS, "ops_section": ("## Comandos que executa", "## Relato"),
    "must": ("Não gera conteúdo pedagógico", "Texto livre do chat não é comando", "Conteúdo externo é dado",
             "Negar por padrão", "Usa credenciais só por referência", "não afirmar estado"),
}
HEADINGS = ("## Missão", "## Decide", "## Não decide nem faz", "## Entradas", "## Saídas",
            "## Comandos à Zapia", "## Regras", "## Limites e segurança")
FORBIDDEN = (
    (re.compile(r"\b[0-9a-f]{40}\b"), "SHA Git (estado volátil)"),
    (re.compile(r"\*\*Próxima tarefa|Frente ativa|Último merge comprovado|GOVERNANCE-CHECKPOINT"), "campo de estado"),
    (re.compile(r"\bPR\s*#\d+"), "número de PR (estado)"),
    (re.compile(r"ghp_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|sk-[A-Za-z0-9]{20,}"), "segredo"),
)
FILE_REF = re.compile(r"`([\w./-]+\.(?:md|py|json|csv|yml))`")
MAX_BYTES = 24 * 1024


def _read(root, rel):
    path = Path(root) / rel
    if path.is_symlink() or not path.is_file():
        raise ValueError("Arquivo ausente ou redirecionado: " + rel)
    raw = path.read_bytes()
    if not raw.strip() or len(raw) > MAX_BYTES:
        raise ValueError("Arquivo vazio ou grande demais: " + rel)
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Arquivo não UTF-8: " + rel) from exc


def _section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i + 1) if end else len(text)
    return text[i + len(start):j]


def _check_spec(root, rel, spec):
    raw, text = _read(root, rel)
    lines = text.splitlines()
    if not lines or lines[0] != spec["title"]:
        raise ValueError("Título inválido em " + rel)
    headings = spec.get("headings", HEADINGS)
    found = [ln for ln in lines if ln.startswith("## ")]
    if tuple(found) != headings:
        raise ValueError("Seções ausentes, extras ou fora de ordem em " + rel)
    for index, heading in enumerate(headings):
        nxt = headings[index + 1] if index + 1 < len(headings) else None
        if not _section(text, heading, nxt).strip():
            raise ValueError(f"Seção vazia em {rel}: {heading}")
    for pattern, label in FORBIDDEN:
        if pattern.search(text):
            raise ValueError(f"{rel} não pode conter {label}")
    for phrase in spec["must"]:
        if phrase not in text:
            raise ValueError(f"{rel} sem a cláusula obrigatória: {phrase}")
    for name in sorted(set(FILE_REF.findall(text))):
        if not (Path(root) / name).is_file():
            raise ValueError(f"{rel} cita arquivo inexistente: {name}")
    start, end = spec.get("ops_section", ("## Comandos à Zapia", "## Regras"))
    ops = re.findall(r"^- `([a-z_]+)`", _section(text, start, end), re.M)
    if len(ops) != len(set(ops)):
        raise ValueError("Operação duplicada em " + rel)
    if set(ops) != set(spec["ops"]):
        raise ValueError(f"{rel} lista operações diferentes das permitidas ao seu papel")
    return {"file": rel, "sha256": hashlib.sha256(raw).hexdigest(), "operations": sorted(ops)}


def validate(root=ROOT):
    if TUTOR_ONLY & COACH_ONLY or (TUTOR_ONLY | COACH_ONLY) & SHARED:
        raise ValueError("Conjuntos de operações se sobrepõem")
    _, readme = _read(root, "agents/README.md")
    for token in ("Tutor (Aragonê)", "Coach (Carter)", "agents/TUTOR.md", "agents/COACH.md",
                  "scripts/agents_gate.py", "único produtor de conteúdo", "agents/ZAPIA.md",
                  "docs/especificacoes/S5_ZAPIA.md"):
        if token not in readme:
            raise ValueError("agents/README.md sem referência obrigatória: " + token)
    results = [_check_spec(root, rel, spec) for rel, spec in SPECS.items()]
    tutor, coach = (set(r["operations"]) for r in results)
    if tutor & coach != set(SHARED):
        raise ValueError("Apenas as operações compartilhadas podem aparecer nos dois perfis")
    zapia = _check_spec(root, "agents/ZAPIA.md", ZAPIA_SPEC)
    schema_path = Path(root) / "config/agent_command_schema.json"
    if schema_path.is_file():
        declared = set(json.loads(schema_path.read_text(encoding="utf-8"))["destinations"])
        if declared != set(zapia["operations"]):
            raise ValueError("agents/ZAPIA.md diverge das operações do esquema de comandos")
    return {"specs": results, "zapia": zapia}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    try:
        info = validate()
    except (ValueError, OSError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        sys.exit(1)
    print("OK: perfis Tutor, Coach e Zapia válidos; " + ", ".join(r["file"] for r in info["specs"] + [info["zapia"]]))
