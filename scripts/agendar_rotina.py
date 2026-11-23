"""Operação `agendar_rotina` (E24, E26; ZAPIA-APL): o Tutor e o Coach pedem à Zapia uma rotina agendada; a Zapia a cria no app dela.

Função pura, sem rede, arquivo próprio (só lê `settings.json` e `config/rotina_instrucoes.json` quando chamada) nem modelo.

- **Params fechados, sem texto livre:** `modelo` (lista fechada), `agendado_utc` (primeiro disparo, UTC) e `comandos_sha256` (hashes de comandos JÁ
  promovidos; 1 para `F1_ENTREGA_UNICA`, 0 para os modelos de escuta diária).
- **Cada modelo pertence a uma origem** (`MODELOS`): a caixa recusa o cruzado (`ORIGEM_FORA_DO_MODELO`).
- **Limites determinísticos** (a autorização é permanente, E26, não há frase por mensagem): primeiro disparo entre 90 min e 24 h depois do `issued_at`;
  no máximo 1 pedido por dia por origem; cada hash tem de ser de comando já promovido; **chave de parada** versionada
  (`automation.agendar_rotina_enabled` em `settings.json`): falsa, ausente ou ilegível recusa (`ROTINA_PARADA`).
- **A instrução que a Zapia segue NÃO vem do comando:** vem dos modelos versionados de `config/rotina_instrucoes.json`, com hash conferido por `check`,
  com URLs completos e literais (lição do E23: a rotina traduziu `comandos` para `commands`).

Limites: não prova que a Zapia crie a rotina nem a obedeça (autorrelato até o recibo e o verificador `zapia_disparo.py`); a origem do comando não é
provada na nuvem (S4-R2).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPERACAO = "agendar_rotina"
DESTINO = "zapia_rotina"
FLAG = "agendar_rotina_enabled"
ANTECEDENCIA_MINIMA = timedelta(minutes=90)  # decisão do proprietário de 23/11/2026 (E25, seção F; antes 15 min)
ANTECEDENCIA_MAXIMA = timedelta(hours=24)
MAX_POR_DIA_POR_ORIGEM = 1
INSTRUCOES = "config/rotina_instrucoes.json"
POLLER = "POLLER"  # instrução do poller de teste (ZAPIA-F3): lê um pedido promovido e cria a rotina filha; não é um modelo de pedido
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
CAMPOS = ("modelo", "agendado_utc", "comandos_sha256")

# modelo -> origens que podem pedir, dias de execução, hashes exigidos e modelo de instrução (config/rotina_instrucoes.json)
MODELOS = {
    "F1_ENTREGA_UNICA": {"origens": frozenset({"tutor", "coach"}), "dias": 1, "hashes": 1, "instrucao": "UNICA"},
    "ROTINA_ESTUDO_DIARIA": {"origens": frozenset({"tutor"}), "dias": 2, "hashes": 0, "instrucao": "ESCUTA"},
    "ROTINA_ESTUDO_SEMANAL": {"origens": frozenset({"tutor"}), "dias": 7, "hashes": 0, "instrucao": "ESCUTA"},
    "BRIEFING_DIARIO": {"origens": frozenset({"coach"}), "dias": 7, "hashes": 0, "instrucao": "ESCUTA"},
}


def parse_utc(texto):
    if not isinstance(texto, str) or not _UTC.match(texto):
        return None
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def validar_forma(params) -> str | None:
    """Forma do pedido, sem contexto: modelo da lista, `agendado_utc` bem formado e hashes no número do modelo, sem repetição."""
    if not isinstance(params, dict) or set(params) != set(CAMPOS):
        return "PARAMS_CAMPO_DESCONHECIDO"
    modelo = params["modelo"]
    if not isinstance(modelo, str) or modelo not in MODELOS:
        return "PARAMS_MODELO_DESCONHECIDO"
    if parse_utc(params["agendado_utc"]) is None:
        return "PARAMS_AGENDAMENTO_INVALIDO"
    hashes = params["comandos_sha256"]
    if not isinstance(hashes, list) or len(hashes) != MODELOS[modelo]["hashes"] or len(set(map(str, hashes))) != len(hashes):
        return "PARAMS_LISTA_INVALIDA"
    if not all(isinstance(h, str) and _HEX64.fullmatch(h) for h in hashes):
        return "PARAMS_HASH_INVALIDO"
    return None


def flag_habilitada(root: Path = ROOT):
    """Valor da chave de parada em `settings.json`; None se ilegível, ausente, repetida ou não booleana (fail-closed: tratado como parada)."""
    try:
        dados = json.loads((Path(root) / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    achados = []

    def procurar(no):
        if isinstance(no, dict):
            for k, v in no.items():
                if k == FLAG:
                    achados.append(v)
                else:
                    procurar(v)
        elif isinstance(no, list):
            for v in no:
                procurar(v)

    procurar(dados)
    return achados[0] if len(achados) == 1 and isinstance(achados[0], bool) else None


def decidir(origem, params, emitido, ctx) -> str | None:
    """Regras com contexto injetado (a caixa as chama depois da forma): None se pode, senão o código. Tudo que o contexto não informa recusa.

    `ctx`: `agendar_rotina_habilitada` (bool, a chave de parada), `hashes_promovidos` (hashes de comandos já promovidos) e
    `agendamentos_do_dia` (origens que já pediram hoje)."""
    if ctx.get("agendar_rotina_habilitada") is not True:
        return "ROTINA_PARADA"
    motivo = validar_forma(params)
    if motivo:
        return motivo
    modelo = MODELOS[params["modelo"]]
    if origem not in modelo["origens"]:
        return "ORIGEM_FORA_DO_MODELO"
    agendado = parse_utc(params["agendado_utc"])
    if not isinstance(emitido, datetime) or emitido.tzinfo is None:
        return "RELOGIO_AUSENTE"
    antecedencia = agendado - emitido.astimezone(timezone.utc)
    if not (ANTECEDENCIA_MINIMA <= antecedencia <= ANTECEDENCIA_MAXIMA):
        return "AGENDAMENTO_FORA_DA_JANELA"
    promovidos = ctx.get("hashes_promovidos")
    if params["comandos_sha256"]:
        if not isinstance(promovidos, (set, frozenset, list, tuple)):
            return "ALVOS_DESCONHECIDOS"
        if not set(params["comandos_sha256"]) <= set(promovidos):
            return "ALVO_NAO_PROMOVIDO"
    do_dia = ctx.get("agendamentos_do_dia")
    if not isinstance(do_dia, (set, frozenset, list, tuple)):
        return "TETO_DESCONHECIDO"
    if sum(1 for o in do_dia if o == origem) >= MAX_POR_DIA_POR_ORIGEM:
        return "TETO_DIARIO_AGENDAMENTO"
    return None


def carregar_instrucoes(root: Path = ROOT) -> dict:
    return json.loads((Path(root) / INSTRUCOES).read_text(encoding="utf-8"))


def hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def check(root: Path = ROOT) -> list:
    """Consistência dos modelos de instrução: hash conferido, URLs completos e literais, sem `commands`, sem credencial nem token."""
    erros = []
    try:
        dados = carregar_instrucoes(root)
    except (OSError, ValueError):
        return ["config/rotina_instrucoes.json ausente ou ilegível"]
    for chave in {m["instrucao"] for m in MODELOS.values()} | {POLLER}:
        item = dados.get(chave)
        if not isinstance(item, dict) or not isinstance(item.get("template"), str):
            erros.append(f"modelo de instrução ausente: {chave}")
            continue
        t = item["template"]
        if item.get("sha256") != hash_texto(t):
            erros.append(f"{chave}: hash não confere com o texto")
        finais = "criadas" if chave == POLLER else "entregas"
        for url in ("https://api.github.com/repos/{REPO}/contents/comandos/recibos", "https://api.github.com/repos/{REPO}/contents/comandos/validados",
                    "https://api.github.com/repos/{REPO}/contents/comandos/" + finais):
            if url not in t:
                erros.append(f"{chave}: URL literal ausente: {url}")
        if "commands/" in t:
            erros.append(f"{chave}: caminho traduzido (commands)")
        if re.search(r"ghp_|github_pat_|Bearer\s+[A-Za-z0-9]", t):
            erros.append(f"{chave}: segredo no texto")
        if "never reveal" not in t or "Do not translate" not in t:
            erros.append(f"{chave}: faltam as ordens de sigilo e de não traduzir")
    return erros


def renderizar(modelo, *, repo, credencial, agendado_utc, hashes=(), origem=None, root: Path = ROOT) -> str:
    """Texto da instrução da rotina, do modelo versionado, com URLs completos. Levanta ValueError se algo não couber."""
    if modelo not in MODELOS:
        raise ValueError("modelo desconhecido")
    if parse_utc(agendado_utc) is None or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", repo) or not re.fullmatch(r"[A-Za-z0-9_]{1,64}", credencial):
        raise ValueError("parâmetro inválido")
    erros = check(root)
    if erros:
        raise ValueError("modelos de instrução inconsistentes: " + "; ".join(erros))
    info = MODELOS[modelo]
    if len(hashes) != info["hashes"] or not all(_HEX64.fullmatch(h) for h in hashes):
        raise ValueError("hashes fora do modelo")
    if origem is not None and origem not in info["origens"]:
        raise ValueError("origem fora do modelo")
    t = carregar_instrucoes(root)[info["instrucao"]]["template"]
    valores = {"REPO": repo, "CREDENCIAL": credencial, "AGENDADO_UTC": agendado_utc, "DIAS": str(info["dias"]),
               "HASH": hashes[0] if hashes else "", "ORIGEM": origem or "tutor or coach"}
    return re.sub(r"\{([A-Z_]+)\}", lambda m: valores.get(m.group(1), m.group(0)), t)


def renderizar_poller(*, repo, credencial, agendado_utc, ref, publico="Andraus35/UFMS-MEU-ESTUDO", root: Path = ROOT) -> str:
    """Instrução do poller de teste (ZAPIA-F3), do modelo versionado `POLLER`, com o commit do repositório público e o hash do modelo filho FIXADOS (pin).
    A rotina filha usa o modelo `UNICA`; o poller só a cria se o modelo lido no commit `ref` tiver exatamente o hash fixado aqui."""
    if parse_utc(agendado_utc) is None or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", repo) or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", publico) \
            or not re.fullmatch(r"[A-Za-z0-9_]{1,64}", credencial) or not re.fullmatch(r"[0-9a-f]{40}", ref or ""):
        raise ValueError("parâmetro inválido")
    erros = check(root)
    if erros:
        raise ValueError("modelos de instrução inconsistentes: " + "; ".join(erros))
    dados = carregar_instrucoes(root)
    valores = {"REPO": repo, "CREDENCIAL": credencial, "AGENDADO_UTC": agendado_utc, "REF": ref, "PUBLICO": publico, "UNICA_SHA256": dados["UNICA"]["sha256"]}
    return re.sub(r"\{([A-Z_0-9]+)\}", lambda m: valores.get(m.group(1), m.group(0)), dados[POLLER]["template"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Operação agendar_rotina: confere os modelos de instrução ou renderiza a instrução de uma rotina.")
    p.add_argument("--check", action="store_true")
    p.add_argument("--instrucao", choices=sorted(MODELOS))
    p.add_argument("--repo", default="Andraus35/ufms-meu-estudo-entrada")
    p.add_argument("--credencial", default="github_ufms_repo_token")
    p.add_argument("--agendado", help="primeiro disparo em UTC, AAAA-MM-DDTHH:MM:SSZ")
    p.add_argument("--hash", action="append", default=[], help="hash_corpo do comando já promovido (F1_ENTREGA_UNICA)")
    p.add_argument("--origem", choices=("tutor", "coach"))
    p.add_argument("--poller", action="store_true", help="imprime a instrução do poller de teste (ZAPIA-F3); exige --agendado e --ref")
    p.add_argument("--ref", help="commit (40 hex) do repositório público onde o poller lê o modelo filho")
    a = p.parse_args(argv)
    if a.check:
        erros = check()
        print("FALHA: " + "; ".join(erros) if erros else "OK: modelos de instrução de rotina conferidos (hash, URLs literais, sem segredo)")
        return 1 if erros else 0
    if a.poller:
        try:
            print(renderizar_poller(repo=a.repo, credencial=a.credencial, agendado_utc=a.agendado or "", ref=a.ref or ""))
        except ValueError as erro:
            print("FALHA: " + str(erro))
            return 2
        return 0
    if a.instrucao:
        try:
            print(renderizar(a.instrucao, repo=a.repo, credencial=a.credencial, agendado_utc=a.agendado or "", hashes=a.hash, origem=a.origem))
        except ValueError as erro:
            print("FALHA: " + str(erro))
            return 2
        return 0
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
