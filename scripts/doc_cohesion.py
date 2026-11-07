#!/usr/bin/env python3
"""Coesão documental: os documentos normativos não podem se contradizer nem apontar para o que não existe.

Verificações determinísticas (sem LLM, sem rede):
  C1 caminhos citados entre crases existem no repositório;
  C2 links Markdown relativos resolvem;
  C3 IDs D-xx, PR-xxx, OPEN-xx, E-xx e RM-xx citados estão definidos (PRODUCT.md / ROADMAP.md);
  C4 IDs definidos em PRODUCT.md não se repetem;
  C5 `settings.json` e documentos concordam (intervalos de revisão, flags de agenda fixa, START de engenharia);
  C6 frases superadas (decisões revogadas) não reaparecem nos normativos;
  C7 toda especificação em docs/especificacoes/S*.md tem a seção "## Pesquisa" com link e linha de lacunas (D-16);
  C8 a fila work_queue de state/WORKFLOW.json é válida (campos, ids únicos, dependências, tarefa no ROADMAP, entrega em docs/especificacoes);
  C9 as rotas de sessão (config/session_routes.json) existem, apontam para arquivos e scripts reais e concordam com settings.json e com as regras de escrita do AGENTS.md.

Uso: python scripts/doc_cohesion.py --check [--root DIR]
Não prova compreensão semântica: pega divergência mecânica. Estado do ciclo é coberto por governance_sync_gate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Documentos normativos: o que os agentes construtores leem para decidir.
NORMATIVE = (
    "AGENTS.md", "ROADMAP.md", "PRODUCT.md", "memory/HANDOFF.md",
    "docs/OPERACAO.md", "docs/PLATFORMS.md", "docs/METHOD.md",
    "docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md",
    "docs/pedagogia/README.md", "docs/especificacoes/README.md",
)
NORMATIVE_GLOBS = ("agents/*.md", "rules/*.md", "docs/especificacoes/S*.md")
# IDs do PRODUCT.md só são citados com esse significado nestes documentos.
PRODUCT_ID_DOCS = (
    "PRODUCT.md", "AGENTS.md", "docs/PLATFORMS.md",
    "docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md",
)
PRODUCT_ID_GLOBS = ("agents/*.md",)

PATH_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
ID_RE = re.compile(r"\b(D-\d{2}|PR-\d{3}|OPEN-\d{2}|E-\d{2})\b")
RM_RE = re.compile(r"\bRM-\d{2}(?:-[A-Z]+)?\b")
DEF_RE = {
    "D": re.compile(r"^- \*\*(D-\d{2})\b", re.M),
    "PR": re.compile(r"^- \*\*(PR-\d{3})\b", re.M),
    "OPEN": re.compile(r"^- \*\*(OPEN-\d{2})\b", re.M),
    "E": re.compile(r"^- \*\*(E-\d{2})\b", re.M),
}
TOP_DIRS = ("agents", "config", "docs", "edital", "guardrails", "hooks", "memory", "poc",
            "rules", "scripts", "state", "tests", ".github", ".specs")
TOP_FILES = ("AGENTS.md", "ROADMAP.md", "PRODUCT.md", "settings.json", "README.md", "STATUS.md")

# Frases de decisões revogadas: (regex, motivo, trecho que isenta a linha, p.ex. a versão já emendada).
# Ao revogar algo, acrescente aqui.
STALE = (
    (re.compile(r"não acessar conta privada por bots", re.I), "contradiz D-14/D-15 (acesso direto autorizado pelo proprietário)", None),
    (re.compile(r"Zapia (?:atua|age|funciona) como (?:Tutor|Coach)", re.I), "contradiz D-10 (Zapia é só interface e executora)", None),
    (re.compile(r"nenhum intervalo (?:fixo|universal)", re.I), "contradiz D-11 (padrão do proprietário 7/15/30)", "padrão"),
)


def _files(root: Path, names, globs):
    out = []
    for n in names:
        p = root / n
        if p.is_file():
            out.append(p)
    for g in globs:
        out.extend(sorted(root.glob(g)))
    return out


def _rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def _looks_like_repo_path(token: str) -> bool:
    if any(c in token for c in "*<>{}$~|") or token.startswith(("http", "git ", "python ", "-", "/", "#")):
        return False
    first = token.split()[0] if token.split() else ""
    if first != token and not token.startswith(("python ", "git ")):
        token = first
    if "/" in token:
        return token.split("/", 1)[0] in TOP_DIRS
    return token in TOP_FILES


def _path_token(token: str) -> str:
    return token.split()[0] if " " in token else token


def check_paths(root: Path, files) -> list[str]:
    errs = []
    for f in files:
        in_fence = False
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in PATH_RE.finditer(line):
                tok = m.group(1).strip()
                if not _looks_like_repo_path(tok):
                    continue
                path = _path_token(tok).rstrip(".,;:)")
                if "#" in path:
                    path = path.split("#", 1)[0]
                if path and not (root / path).exists():
                    errs.append(f"C1 {_rel(root, f)}:{n}: caminho inexistente `{path}`")
    return errs


def check_links(root: Path, files) -> list[str]:
    errs = []
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                if target and not (f.parent / target).exists():
                    errs.append(f"C2 {_rel(root, f)}:{n}: link relativo quebrado ({target})")
    return errs


def product_ids(root: Path):
    text = (root / "PRODUCT.md").read_text(encoding="utf-8")
    defined, dups = set(), []
    for rx in DEF_RE.values():
        seen = set()
        for i in rx.findall(text):
            if i in seen:
                dups.append(i)
            seen.add(i)
        defined |= seen
    return defined, dups


def roadmap_ids(root: Path) -> set[str]:
    text = (root / "ROADMAP.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| (RM-\d{2}(?:-[A-Z]+)?) \|", text, re.M))


def check_ids(root: Path) -> list[str]:
    errs = []
    defined, dups = product_ids(root)
    errs += [f"C4 PRODUCT.md: ID definido mais de uma vez ({i})" for i in sorted(set(dups))]
    rm = roadmap_ids(root)
    for f in _files(root, PRODUCT_ID_DOCS, PRODUCT_ID_GLOBS):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for i in ID_RE.findall(line):
                if i not in defined:
                    errs.append(f"C3 {_rel(root, f)}:{n}: ID não definido no PRODUCT.md ({i})")
    for f in _files(root, NORMATIVE, NORMATIVE_GLOBS):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for i in RM_RE.findall(line):
                if i not in rm:
                    errs.append(f"C3 {_rel(root, f)}:{n}: tarefa fora do ROADMAP ({i})")
    wf = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    for label, tid in (("active", wf.get("active", {}).get("task_id")), ("last_merged", wf.get("last_merged", {}).get("task_id")),
                       ("next_task_after_merge", wf.get("next_task_after_merge"))):
        if tid and tid != "DONE" and tid not in rm:
            errs.append(f"C3 state/WORKFLOW.json: {label} aponta tarefa fora do ROADMAP ({tid})")
    return errs


def check_settings_vs_docs(root: Path) -> list[str]:
    errs = []
    settings = json.loads((root / "settings.json").read_text(encoding="utf-8"))
    plan = settings.get("study", {}).get("owner_default_plan", {})
    if plan.get("review_intervals_days") != [7, 15, 30]:
        errs.append("C5 settings.json: study.owner_default_plan.review_intervals_days diverge do padrão D-11 [7, 15, 30]")
    spec = (root / "docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md").read_text(encoding="utf-8")
    if "7, 15 e 30" not in spec:
        errs.append("C5 plano de estudos: intervalos 7, 15 e 30 ausentes")
    for flag in ("fixed_schedule", "fixed_repetition_intervals"):
        for container in settings.values():
            if isinstance(container, dict) and container.get(flag) not in (None, False):
                errs.append(f"C5 settings.json: {flag} deveria permanecer false")
    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    for name in settings.get("bootstrap", {}).get("engineering_mandatory", []):
        if name not in agents_md:
            errs.append(f"C5 AGENTS.md: START de engenharia não cita {name}")
    product = (root / "PRODUCT.md").read_text(encoding="utf-8")
    for tool in re.findall(r"`(scripts/[a-z_]+\.py)`", product):
        if not (root / tool).exists():
            errs.append(f"C5 PRODUCT.md: script citado inexistente ({tool})")
    return errs


def check_stale(root: Path, files) -> list[str]:
    errs = []
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for rx, why, exempt in STALE:
                if rx.search(line) and not (exempt and exempt in line):
                    errs.append(f"C6 {_rel(root, f)}:{n}: frase superada ({why})")
    return errs


def check_specs(root: Path) -> list[str]:
    errs = []
    for f in sorted((root / "docs/especificacoes").glob("S*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.search(r"^## Pesquisa\b.*?(?=^## |\Z)", text, re.M | re.S)
        rel = _rel(root, f)
        if not m:
            errs.append(f"C7 {rel}: falta a seção '## Pesquisa' (D-16)")
            continue
        if not re.search(r"https?://", m.group(0)):
            errs.append(f"C7 {rel}: a seção Pesquisa não tem nenhum link")
        if not re.search(r"^- \*\*Lacunas:\*\*", m.group(0), re.M):
            errs.append(f"C7 {rel}: a seção Pesquisa não termina com a linha '- **Lacunas:**'")
    return errs


QUEUE_FIELDS = ("id", "title", "roadmap_task", "deliverable", "depends_on", "blocking_inputs", "optional_inputs")


def check_queue(root: Path) -> list[str]:
    errs = []
    wf = json.loads((root / "state/WORKFLOW.json").read_text(encoding="utf-8"))
    queue = wf.get("work_queue", [])
    rm = roadmap_ids(root)
    ids = [i.get("id") for i in queue if isinstance(i, dict)]
    if len(ids) != len(set(ids)):
        errs.append("C8 WORKFLOW.json: work_queue com id repetido")
    for item in queue:
        if not isinstance(item, dict):
            errs.append("C8 WORKFLOW.json: item de work_queue não é objeto")
            continue
        iid = item.get("id", "?")
        for f in QUEUE_FIELDS:
            if f not in item:
                errs.append(f"C8 WORKFLOW.json: item {iid} sem o campo {f}")
        if item.get("roadmap_task") not in rm:
            errs.append(f"C8 WORKFLOW.json: item {iid} aponta tarefa fora do ROADMAP ({item.get('roadmap_task')})")
        if not re.fullmatch(r"docs/especificacoes/S[^/]+\.md", str(item.get("deliverable", ""))):
            errs.append(f"C8 WORKFLOW.json: entrega do item {iid} fora de docs/especificacoes/S*.md")
        for d in item.get("depends_on", []):
            if d not in ids:
                errs.append(f"C8 WORKFLOW.json: item {iid} depende de id inexistente ({d})")
            elif ids.index(d) >= ids.index(iid):
                errs.append(f"C8 WORKFLOW.json: item {iid} depende de item posterior ({d})")
    return errs


WRITE_BEFORE = ("python scripts/bootstrap.py --mode engineering", "python scripts/roadmap_gate.py --check",
                "python hooks/before_write.py", "python scripts/write_policy.py --check")
WRITE_AFTER = ("python hooks/after_write.py", "python hooks/checkpoint.py", "python scripts/governance_sync_gate.py")


def check_routes(root: Path) -> list[str]:
    try:
        from session_route import COMMAND_RE, CONDITIONS, INTENTS, SITUACOES, TYPES
    except ModuleNotFoundError:
        from scripts.session_route import COMMAND_RE, CONDITIONS, INTENTS, SITUACOES, TYPES
    errs = []
    data = json.loads((root / "config/session_routes.json").read_text(encoding="utf-8"))
    routes = data.get("rotas", {})
    for intent in INTENTS:
        if intent not in routes:
            errs.append(f"C9 session_routes.json: rota ausente ({intent})")
    seen = set()
    for intent, route in routes.items():
        for st in route.get("etapas", []):
            sid, kind = st.get("id"), st.get("tipo")
            if sid in seen:
                errs.append(f"C9 session_routes.json: id de etapa repetido ({sid})")
            seen.add(sid)
            if kind not in TYPES:
                errs.append(f"C9 session_routes.json: etapa {sid} com tipo inválido ({kind})")
            if kind in ("ler", "consultar_se") and not (root / st.get("arquivo", "")).is_file():
                errs.append(f"C9 session_routes.json: etapa {sid} aponta arquivo inexistente ({st.get('arquivo')})")
            if kind == "executar":
                cmd = st.get("comando", "")
                if not COMMAND_RE.fullmatch(cmd):
                    errs.append(f"C9 session_routes.json: etapa {sid} com comando fora da lista permitida")
                elif not (root / cmd.split()[1]).is_file():
                    errs.append(f"C9 session_routes.json: etapa {sid} aponta script inexistente ({cmd.split()[1]})")
            if kind in ("parar_se", "aviso_se") and st.get("condicao") not in CONDITIONS:
                errs.append(f"C9 session_routes.json: etapa {sid} com condição desconhecida")
            if kind == "parar_se" and st.get("situacao", "bloqueada") not in SITUACOES:
                errs.append(f"C9 session_routes.json: etapa {sid} com situação inválida")
    if errs:
        return errs
    settings = json.loads((root / "settings.json").read_text(encoding="utf-8"))
    boot = settings.get("bootstrap", {})
    for intent, key in (("study", "mandatory"), ("engineering", "engineering_mandatory")):
        reads = [st["arquivo"] for st in routes[intent]["etapas"] if st["tipo"] == "ler"]
        if reads != boot.get(key):
            errs.append(f"C9 session_routes.json: a rota {intent} diverge de settings.json bootstrap.{key}")
    steps = routes["write"]["etapas"]
    cmds = [st["comando"] for st in steps if st["tipo"] == "executar"]
    manual = [i for i, st in enumerate(steps) if st["tipo"] == "manual"]
    pos = {st["comando"]: i for i, st in enumerate(steps) if st["tipo"] == "executar"}
    for c in WRITE_BEFORE + WRITE_AFTER:
        if c not in cmds:
            errs.append(f"C9 session_routes.json: a rota write não executa `{c}` (AGENTS.md, escrita controlada)")
    if not errs and manual:
        if not all(pos[c] < manual[0] for c in WRITE_BEFORE) or not all(pos[c] > manual[0] for c in WRITE_AFTER):
            errs.append("C9 session_routes.json: a rota write não respeita antes/depois da escrita")
    if not any(st["tipo"] == "parar_se" and st.get("situacao") == "requer_aprovacao_humana" for st in routes["governance"]["etapas"]):
        errs.append("C9 session_routes.json: a rota governance precisa parar por aprovação humana")
    if not any(st["tipo"] == "parar_se" and st.get("condicao") == "gravacao_pessoal_bloqueada" for st in routes["persistence"]["etapas"]):
        errs.append("C9 session_routes.json: a rota persistence precisa parar se a gravação pessoal estiver bloqueada")
    return errs


def validate(root=ROOT) -> dict:
    root = Path(root)
    files = _files(root, NORMATIVE, NORMATIVE_GLOBS)
    missing = [n for n in NORMATIVE if not (root / n).is_file()]
    errs = [f"C0 documento normativo ausente: {n}" for n in missing]
    if not errs:
        errs += check_paths(root, files)
        errs += check_links(root, files)
        errs += check_ids(root)
        errs += check_settings_vs_docs(root)
        errs += check_stale(root, files)
        errs += check_specs(root)
        errs += check_queue(root)
        errs += check_routes(root)
    if errs:
        raise ValueError("coesão documental: " + str(len(errs)) + " divergência(s)\n  " + "\n  ".join(errs))
    return {"documents": len(files), "result": "PASS"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", required=True)
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args(argv)
    try:
        res = validate(Path(args.root))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
