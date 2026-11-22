"""Esquema fechado de `params` por operação (GAP-A, GA-1) e bloqueio de registro pessoal enquanto a flag estiver falsa.

Achado de 21/11/2026 (Tutor e Coach, sintético): `config/agent_command_schema.json` não fechava os campos de `params` por operação; o
validador aceitava `registrar_resultado` com parâmetros arbitrários e só barrava chaves proibidas. Aqui:
  - `enviar_mensagem`: só `texto` (string);  `enviar_prompt_notebook`: só `prompt` e `prompt_sha256` (conferidos pelo `notebook_prompt_validator`).
  - `registrar_resultado`, `registrar_exportacao_desempenho` e `registrar_acompanhamento` são RECUSADOS enquanto `personal_results_writes_enabled`
    for falso; sem a flag legível, também (fail-closed).
  - GAP-A2: `ler_arquivo_repositorio` (`caminho` relativo seguro), `consultar_agenda_minima` (`data`), `criar_lembrete` (`atividade_ids` e
    `lembrete_sha256`, vínculo com o LEMBRETE, GA-4) e `registrar_plano` (`plano` só com as chaves do plano) fecharam: PROPOSTA de forma, a
    confirmar pelo proprietário (as especificações não fixavam os campos). `registrar_plano` é registro pessoal: recusado com a flag falsa.
Sem efeito externo: só lê `settings.json`. Não prova que a Zapia use o validador.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

try:
    import command_idempotency
    import content_filters
except ImportError:  # pragma: no cover - importação por pacote
    from scripts import command_idempotency, content_filters

ROOT = Path(__file__).resolve().parents[1]
FLAG = "personal_results_writes_enabled"
REGISTRO_PESSOAL = ("registrar_resultado", "registrar_exportacao_desempenho", "registrar_acompanhamento", "registrar_plano")
ESQUEMAS = {
    "enviar_mensagem": {"texto": str},
    "enviar_prompt_notebook": {"prompt": str, "prompt_sha256": str},
    "ler_arquivo_repositorio": {"caminho": str},
    "consultar_agenda_minima": {"data": str},
    "criar_lembrete": {"atividade_ids": list, "lembrete_sha256": str},
    "registrar_plano": {"plano": dict},
}
SEM_ESQUEMA_FECHADO: tuple = ()  # GAP-A2: nenhuma operação fica sem esquema
CHAVES_DO_PLANO = frozenset({"parameters", "days", "unscheduled_reviews", "topics_not_reached", "note"})
OBRIGATORIAS_DO_PLANO = frozenset({"parameters", "days"})
MAX_CAMINHO = 200


def _caminho_invalido(caminho: str) -> bool:
    if not caminho or len(caminho) > MAX_CAMINHO or "\\" in caminho or "\x00" in caminho or caminho.startswith(("/", "~")):
        return True
    return any(parte in ("", "..") or parte.startswith(".") for parte in caminho.split("/"))  # sem "..", oculto (.git, .env) nem segmento vazio


def _validar_conteudo(operation: str, params: dict) -> str | None:
    if operation == "enviar_mensagem":  # COR-C, AT-5: o validador e a caixa não podem ser mais permissivos que o verificador de entrega
        if content_filters.tem_url(params["texto"]):
            return "PARAMS_URL"
        if content_filters.instrucao_embutida(params["texto"]) or content_filters.mistura_de_scripts(params["texto"]):
            return "PARAMS_INSTRUCAO_EMBUTIDA"
    if operation == "ler_arquivo_repositorio" and _caminho_invalido(params["caminho"]):
        return "PARAMS_CAMINHO_INVALIDO"
    if operation == "consultar_agenda_minima":
        dia = params["data"]
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dia):
                raise ValueError
            date.fromisoformat(dia)
        except ValueError:
            return "PARAMS_DATA_INVALIDA"
    if operation == "criar_lembrete":
        if not command_idempotency.lista_de_atividades_valida(params["atividade_ids"]):
            return "PARAMS_LISTA_INVALIDA"
        if not command_idempotency.HEX64.fullmatch(params["lembrete_sha256"]):
            return "PARAMS_HASH_INVALIDO"
    if operation == "registrar_plano":
        chaves = set(params["plano"])
        if not OBRIGATORIAS_DO_PLANO <= chaves <= CHAVES_DO_PLANO:
            return "PARAMS_PLANO_INVALIDO"
    return None


def flag_resultados_pessoais(root: Path = ROOT):
    """Valor da flag em `settings.json`; None se ilegível ou ausente (fail-closed: tratado como falso na recusa)."""
    try:
        dados = json.loads((root / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    achados = []

    def procurar(no):  # a flag fica aninhada em `settings.json`; qualquer ocorrência não booleana ou divergente vira "indeterminado"
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
    if len(achados) != 1 or not isinstance(achados[0], bool):
        return None
    return achados[0]


def registro_pessoal_bloqueado(operation: str, flags: dict | None = None) -> bool:
    """True se a operação grava resultado pessoal e a flag não está explicitamente verdadeira."""
    if operation not in REGISTRO_PESSOAL:
        return False
    valor = flag_resultados_pessoais() if flags is None else flags.get(FLAG)
    return valor is not True


def validar_params(operation: str, params) -> str | None:
    """None se os params cabem no esquema fechado da operação (ou se ela ainda não tem esquema); senão o código da recusa."""
    esquema = ESQUEMAS.get(operation)
    if esquema is None:
        return None
    if not isinstance(params, dict):
        return "PARAMS_NAO_OBJETO"
    if set(params) - set(esquema):
        return "PARAMS_CAMPO_DESCONHECIDO"
    for campo, tipo in esquema.items():
        if campo not in params:
            return "PARAMS_CAMPO_OBRIGATORIO_AUSENTE"
        if not isinstance(params[campo], tipo):
            return "PARAMS_TIPO_INVALIDO"
    return _validar_conteudo(operation, params)
