"""Contrato determinístico local de bootstrap e interfaces de hooks.

Verifica bytes e interfaces, nao comprova que agente externo leu arquivos,
nem registra hooks nativos no GitHub ou na ferramenta de IA.
"""
import ast
import hashlib
import re
from pathlib import Path

try:
    from core import ROOT, load_json
except ModuleNotFoundError:
    from scripts.core import ROOT, load_json

BOOTSTRAP_FILES = (
    "AGENTS.md", "ROADMAP.md", "memory/HANDOFF.md", "state/CURRENT.json",
)
ROADMAP_SECTIONS = (
    "# ROADMAP — UFMS MEU ESTUDO",
    "## Governança e leitura obrigatória",
    "## Estado observado",
    "## Fila de execução",
    "## Critérios de promoção",
)
ROADMAP_ITEMS = tuple(f"RM-{n:02d}" for n in range(11))
ROADMAP_STATES = frozenset({
    "planejado", "em_andamento", "implementado_nao_homologado",
    "bloqueado", "homologado",
})


ROADMAP_APPROVED_BASELINE = {
    "RM-00": ("P0", "implementado_nao_homologado", "gates automáticos de entrega: proteção main confirmada; gate serial vincula PR à base main e ao SHA exato; CI verde no HEAD e pós-merge; hooks locais não foram executados via API"),
    "RM-01": ("P0", "implementado_nao_homologado", "Fonte/versionamento verificados, alerta conhecido preservado, monitoramento efetivo"),
    "RM-02": ("P0", "implementado_nao_homologado", "IGP-12/13/14 integrados em schema aditivo; zero eventos pessoais a migrar; regressões legadas e testes negativos CI verdes; plataforma real não homologada"),
    "RM-03": ("P1", "implementado_nao_homologado", "E0-E4 integrados ao rebuild; desconhecidos explícitos; CI verde; sem evidência real para homologação pedagógica"),
    "RM-04": ("P1", "implementado_nao_homologado", "Ranking por snapshot/política; desconhecidos explícitos; CI e contraprovas verdes; pesos provisórios sem calibração em dados reais"),
    "RM-05": ("P1", "implementado_nao_homologado", "Filtros em camadas e fallback; disponibilidade/IDs desconhecidos preservados; CI e contraprovas verdes; plataforma real não homologada"),
    "RM-06": ("P1", "planejado", "Rastrear/implementar/registrar execução dos 102 cenários e mutantes aplicáveis"),
    "RM-07": ("P1", "bloqueado", "Reauditar 9 NCs do PR #5, executar 27 checks funcionais; sem confundir validação documental com operacional"),
    "RM-08": ("P2", "bloqueado", "Recomendação → execução humana → resultado → reavaliação, persistência/replay consentidos"),
    "RM-09": ("P2", "planejado", "Provas de autorização e fluxo com Gemini Notebook, Zapia e GitHub Projects; sem reabrir PR #3"),
    "RM-10": ("P2", "bloqueado", "Privacidade, autorização, observações reais e avaliação prudente de utilidade"),
}

def validate_roadmap_text(contents):
    """Rejeita cabeçalhos-placeholder e fila incompleta ou contraditória."""
    if not isinstance(contents, str):
        raise ValueError("Roadmap não é texto")
    if len(contents.encode("utf-8")) < 3000:
        raise ValueError("Roadmap truncado/placeholder")
    for heading in ROADMAP_SECTIONS:
        if contents.count(heading) != 1:
            raise ValueError("Seção obrigatória do roadmap ausente/duplicada: " + heading)
    seen = {}
    for line in contents.splitlines():
        if not re.match(r"^\|\s*RM-\d+", line):
            continue
        columns = [item.strip() for item in line.strip().split("|")[1:-1]]
        if len(columns) != 5:
            raise ValueError("Linha de roadmap inválida: " + line[:60])
        code, priority, _, status, done = columns
        if code in seen:
            raise ValueError("ID de roadmap duplicado: " + code)
        if priority not in ("P0", "P1", "P2"):
            raise ValueError("Prioridade inválida: " + code)
        if status not in ROADMAP_STATES:
            raise ValueError("Status de roadmap inválido: " + code)
        if len(done) < 25:
            raise ValueError("Critério de aceite vazio ou superficial: " + code)
        if ROADMAP_APPROVED_BASELINE.get(code) != (priority, status, done):
            raise ValueError("Mudança estratégica exige baseline auditada: " + code)
        seen[code] = True
    if tuple(seen) != ROADMAP_ITEMS:
        raise ValueError("Fila de roadmap incompleta, reordenada ou adulterada")
    return True


SIMPLIFICATION_BASELINE = {
    "SIM-01": "ALTA", "SIM-02": "ALTA", "SIM-03": "ALTA",
    "SIM-04": "MEDIA", "SIM-05": "MEDIA", "SIM-06": "MEDIA",
    "SIM-07": "MEDIA", "SIM-08": "MEDIA",
    "SIM-09": "BAIXA", "SIM-10": "BAIXA", "SIM-11": "MEDIA", "SIM-12": "MEDIA",
}
SIMPLIFICATION_STATES = {"pendente", "em_andamento", "concluido", "documentado"}


def validate_simplification_queue(contents):
    """Impede perda da fila e de testes/registro de criticidade, não homologa operação."""
    heading = "## Fila de simplificação pessoal — 05/11/2026"
    if not isinstance(contents, str) or contents.count(heading) != 1:
        raise ValueError("Fila de simplificação ausente/duplicada")
    section = contents.split(heading, 1)[1].split("\n## ", 1)[0]
    marker = re.search(r"\*\*(?:Próxima tarefa: (SIM-\d{2})|Fila de simplificação concluída)\*\*", section)
    if marker is None or (marker.group(1) is not None and marker.group(1) not in SIMPLIFICATION_BASELINE):
        raise ValueError("Retomada sem próxima tarefa SIM válida ou marcador terminal")
    next_task = marker.group(1)
    observed = []
    observed_states = {}
    for line in section.splitlines():
        if not line.startswith("| SIM-"):
            continue
        columns = [p.strip() for p in line.split("|")[1:-1]]
        if len(columns) != 6:
            raise ValueError("Linha SIM inválida")
        code, severity, problem, how, tests, state = columns
        if code not in SIMPLIFICATION_BASELINE or severity != SIMPLIFICATION_BASELINE[code]:
            raise ValueError("Criticidade SIM indevidamente alterada: " + code)
        if code in observed or state not in SIMPLIFICATION_STATES:
            raise ValueError("ID/estado SIM inválido: " + code)
        if len(problem) < 25 or len(how) < 55:
            raise ValueError("Ação ou aceite SIM superficial: " + code)
        if severity in ("ALTA", "MEDIA"):
            files = re.findall(r"`(tests/[A-Za-z0-9_./-]+\.py)`", tests)
            if not files or "teste:" not in tests and "negativo:" not in tests and "mutantes:" not in tests and "exigir" not in tests and "ampliar" not in tests:
                raise ValueError("Item ALTA/MEDIA sem plano explícito de contraprova: " + code)
            if not all((ROOT / f).is_file() for f in files):
                raise ValueError("Teste referenciado não existe: " + code)
        elif not tests.startswith("registro:"):
            raise ValueError("Item BAIXA sem registro e risco aceito: " + code)
        observed.append(code)
        observed_states[code] = state
    if observed != list(SIMPLIFICATION_BASELINE):
        raise ValueError("Fila SIM omitida, duplicada ou reordenada")
    if next_task is None and not all(state in ("concluido", "documentado") for state in observed_states.values()):
        raise ValueError("Fila marcada concluída com itens pendentes")
    return True


HOOK_FILES = {
    "before_write": "hooks/before_write.py",
    "after_write": "hooks/after_write.py",
    "checkpoint": "hooks/checkpoint.py",
}


def _contained_file(root, relative):
    if not isinstance(relative, str) or relative.startswith("/") or "\\" in relative:
        raise ValueError("Caminho de gate inválido")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Caminho de gate inseguro")
    resolved_root = Path(root).resolve()
    path = resolved_root / candidate
    if path.is_symlink() or not path.resolve().is_relative_to(resolved_root):
        raise ValueError("Gate fora do repositório ou symlink")
    if not path.is_file():
        raise ValueError("Arquivo de gate ausente: " + relative)
    return path


def check_bootstrap(root=ROOT):
    settings = load_json(Path(root) / "settings.json")
    mandatory = settings.get("bootstrap", {}).get("mandatory")
    if mandatory != list(BOOTSTRAP_FILES):
        raise ValueError("Conjunto e ordem do bootstrap divergentes do contrato")
    hashes = {}
    for name in BOOTSTRAP_FILES:
        raw = _contained_file(root, name).read_bytes()
        if not raw.strip():
            raise ValueError("Arquivo obrigatório vazio: " + name)
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Bootstrap não UTF-8: " + name) from exc
        if name == "ROADMAP.md":
            validate_roadmap_text(raw.decode("utf-8"))
            validate_simplification_queue(raw.decode("utf-8"))
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return hashes


def check_hook_contract(root=ROOT):
    settings = load_json(Path(root) / "settings.json")
    cfg = settings.get("hooks")
    if not isinstance(cfg, dict) or cfg.get("native_registration_required") is not True:
        raise ValueError("Registro nativo de hooks deve permanecer explicitamente requerido")
    for name, path in HOOK_FILES.items():
        if cfg.get(name) != path:
            raise ValueError("Hook obrigatório divergente: " + name)
        source = _contained_file(root, path).read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            raise ValueError("Sintaxe de hook inválida: " + name) from exc
        if not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "run"
                   for n in tree.body):
            raise ValueError("Hook sem interface run: " + name)
    return tuple(HOOK_FILES)
