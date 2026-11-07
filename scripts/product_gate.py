"""Gate determinístico de estrutura do PRODUCT.md (leitura obrigatória no START de engenharia).

Verifica bytes e estrutura, não compreensão semântica. Garante que o documento não
vire segunda fonte de estado (sem SHAs, marcadores de tarefa ou checkpoint) e que
IDs, requisitos, decisões e referências a arquivos sejam consistentes.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

NAME = "PRODUCT.md"
MAX_BYTES = 40 * 1024
TITLE = "# PRODUCT — UFMS MEU ESTUDO"
HEADINGS = (
    "## 0. Como ler", "## 1. Propósito", "## 2. Atores e responsabilidades",
    "## 3. Fluxo ponta a ponta", "## 4. Fronteiras de dados", "## 5. Decisões do proprietário",
    "## 6. Não objetivos e proibições", "## 7. Requisitos de produto", "## 8. Ordem de construção",
    "## 9. Glossário", "## 10. Mapa de fontes", "## 11. Evidências de referência",
    "## 12. Pontos a confirmar",
)
PRECEDENCE = "`AGENTS.md` (segurança e contrato do agente) > `PRODUCT.md` (o que construir e por quê) > `ROADMAP.md`"
FORBIDDEN = (
    (re.compile(r"\b[0-9a-f]{40}\b"), "SHA Git (estado volátil)"),
    (re.compile(r"\*\*Próxima tarefa"), "marcador de próxima tarefa (estado)"),
    (re.compile(r"GOVERNANCE-CHECKPOINT"), "marcador de checkpoint (estado)"),
    (re.compile(r"Frente ativa|Último merge comprovado"), "campo de estado do ciclo"),
    (re.compile(r"\bPR\s*#\d+"), "referência a número de PR (estado)"),
)
FILE_REF = re.compile(r"`([\w./-]+\.(?:md|py|json|csv|yml))`")


def _section(text, start, end=None):
    i = text.index(start)
    j = text.index(end, i + 1) if end else len(text)
    return text[i:j]


def _ids(section, prefix, width, sep="-"):
    return re.findall(rf"^- \*\*({prefix}{sep}\d{{{width}}})\b", section, re.M)


def validate(root=ROOT):
    root = Path(root)
    path = root / NAME
    if path.is_symlink() or not path.is_file():
        raise ValueError("PRODUCT.md ausente ou redirecionado")
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError("PRODUCT.md vazio")
    if len(raw) > MAX_BYTES:
        raise ValueError("PRODUCT.md acima do limite de tamanho")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("PRODUCT.md não é UTF-8") from exc
    lines = text.splitlines()
    if not lines or lines[0] != TITLE:
        raise ValueError("Título do PRODUCT.md inválido")
    if not re.search(r"^Versão: \d+\.\d+ · Aprovado pelo proprietário em \d{2}/\d{2}/\d{4}", text, re.M):
        raise ValueError("Cabeçalho de versão e aprovação ausente")
    found = [ln for ln in lines if ln.startswith("## ")]
    if tuple(found) != HEADINGS:
        raise ValueError("Seções do PRODUCT.md ausentes, extras ou fora de ordem")
    if PRECEDENCE not in text:
        raise ValueError("Regra de precedência ausente ou alterada")
    for pattern, label in FORBIDDEN:
        if pattern.search(text):
            raise ValueError("PRODUCT.md não pode conter " + label)

    flow = _ids(_section(text, HEADINGS[3], HEADINGS[4]), "F", 1, sep="")
    if flow != [f"F{n}" for n in range(1, 10)]:
        raise ValueError("Fluxo F1 a F9 ausente, duplicado ou fora de ordem")
    decisions = _ids(_section(text, HEADINGS[5], HEADINGS[6]), "D", 2)
    if not decisions or len(set(decisions)) != len(decisions):
        raise ValueError("Decisões D-xx ausentes ou duplicadas")
    reqs_text = _section(text, HEADINGS[7], HEADINGS[8])
    reqs = _ids(reqs_text, "PR", 3)
    if not reqs or len(set(reqs)) != len(reqs):
        raise ValueError("Requisitos PR-xxx ausentes ou duplicados")
    for line in reqs_text.splitlines():
        if re.match(r"^- \*\*PR-\d{3}\b", line) and ("Aceite:" not in line or "Elo: RM-" not in line):
            raise ValueError("Requisito sem Aceite ou sem Elo: " + line[:24])
    opens = _ids(_section(text, HEADINGS[12]), "OPEN", 2)
    if not opens or len(set(opens)) != len(opens):
        raise ValueError("Pontos OPEN-xx ausentes ou duplicados")
    build = _section(text, HEADINGS[8], HEADINGS[9])
    for ref in set(re.findall(r"PR-\d{3}", build)):
        if ref not in reqs:
            raise ValueError("Ordem de construção cita requisito inexistente: " + ref)
    for ref in set(re.findall(r"OPEN-\d{2}", text)):
        if ref not in opens:
            raise ValueError("Referência a ponto OPEN inexistente: " + ref)
    for ref in set(re.findall(r"\bD-\d{2}\b", text)):
        if ref not in decisions:
            raise ValueError("Referência a decisão inexistente: " + ref)
    for name in sorted(set(FILE_REF.findall(text))):
        if not (root / name).is_file():
            raise ValueError("Arquivo citado não existe: " + name)
    return {"file": NAME, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "flow_steps": len(flow), "decisions": len(decisions), "requirements": len(reqs), "open_points": len(opens)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    try:
        info = validate()
    except (ValueError, OSError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        sys.exit(1)
    print("OK: PRODUCT.md válido; SHA-256=" + info["sha256"] + "; requisitos=" + str(info["requirements"]))
