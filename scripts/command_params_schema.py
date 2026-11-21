"""Esquema fechado de `params` por operação (GAP-A, GA-1) e bloqueio de registro pessoal enquanto a flag estiver falsa.

Achado de 21/11/2026 (Tutor e Coach, sintético): `config/agent_command_schema.json` não fechava os campos de `params` por operação; o
validador aceitava `registrar_resultado` com parâmetros arbitrários e só barrava chaves proibidas. Aqui:
  - `enviar_mensagem`: só `texto` (string);  `enviar_prompt_notebook`: só `prompt` e `prompt_sha256` (conferidos pelo `notebook_prompt_validator`).
  - `registrar_resultado`, `registrar_exportacao_desempenho` e `registrar_acompanhamento` são RECUSADOS enquanto `personal_results_writes_enabled`
    for falso; sem a flag legível, também (fail-closed).
  - `ler_arquivo_repositorio`, `criar_lembrete`, `consultar_agenda_minima` e `registrar_plano` AINDA NÃO têm esquema fechado: pendência declarada
    em `SEM_ESQUEMA_FECHADO` (a forma deles não está especificada com campos); fecham no lote seguinte.
Sem efeito externo: só lê `settings.json`. Não prova que a Zapia use o validador.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG = "personal_results_writes_enabled"
REGISTRO_PESSOAL = ("registrar_resultado", "registrar_exportacao_desempenho", "registrar_acompanhamento")
ESQUEMAS = {
    "enviar_mensagem": {"texto": str},
    "enviar_prompt_notebook": {"prompt": str, "prompt_sha256": str},
}
SEM_ESQUEMA_FECHADO = ("ler_arquivo_repositorio", "criar_lembrete", "consultar_agenda_minima", "registrar_plano")


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
    return None
