"""Validador da caixa de comandos (S6-R7, R8, R12; tarefa C4): decide, em código e sem modelo, se um COMANDO da pasta de
comandos de `entrada` pode ser promovido para `validados`, e quais comandos a Zapia pode executar.

Biblioteca OFFLINE e fail-closed: sem rede, sem arquivo, sem credencial. Relógio, registro de idempotência e a informação de
dia de descanso entram por objetos injetados. Reaproveita o esquema (`config/agent_command_schema.json`), o filtro e o
registro de `scripts/agent_commands.py`; a tabela de operações por origem é DERIVADA de `scripts/agents_gate.py` (via
`agent_commands.OPERATIONS`), sem duplicar nem alterar os perfis de `agents/`.

Diferenças deliberadas em relação a `agent_commands.validate_command` (S6-R7): na nuvem não há assinatura que o modelo não
possa forjar, então o comando da caixa NÃO traz o campo `signature` (aceitá-lo sugeriria uma prova que não existe) e o campo
`origin` é só INFORMATIVO: a operação é conferida contra a tabela da origem declarada e, mesmo assim, quem pode gravar é
definido pelas credenciais, não pela alegação do comando. `registrar_*` não passam por aqui (S6-R3, vão pelo portão de
promoção, C1).

Etapas, em ordem fixa; a primeira que falhar PARA e devolve só um CÓDIGO e o id da entrada (nunca o conteúdo):
  nome · forma e tamanho · campos e versão · origem · operação (lista fechada, fora `registrar_*`, tabela da origem) ·
  destino · chave, nonce e janela · parâmetros (filtro de dado pessoal e segredo; para `enviar_prompt_notebook`, também o
  validador do prompt da N2 e o hash do texto) · dia de descanso · idempotência.

Limites: não prova que a Zapia leia só de `validados` (autorrelato; a defesa é o escopo do token e o recibo, S5-R7); o filtro é
heurístico e não detecta instrução embutida em prosa (o texto de um comando é DADO, S5-R4); a regra de duas mensagens por dia
e os limites de job (S8-R1, R5) são do decisor da rotina, outra tarefa; a origem NÃO é provada (S6-R7).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import agent_commands
    import command_idempotency
    import command_params_schema
    import notebook_prompt_validator
    from core import ROOT
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, command_idempotency, command_params_schema, notebook_prompt_validator
    from scripts.core import ROOT

PROMOVER = "PROMOVER"
DUPLICADO = "DUPLICADO"
DENIED = "DENIED"
BOX_DIR = "comandos/"
VALIDATED_DIR = "comandos/validados/"
LEMBRETE = "criar_lembrete"
PROMPT_NOTEBOOK = "enviar_prompt_notebook"
_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.json$")
_VALIDATED_PATH = re.compile(r"^comandos/validados/([A-Za-z0-9][A-Za-z0-9._-]{0,63}\.json)$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
STEPS = ("nome", "forma", "campos", "origem", "operacao", "destino", "chaves", "parametros", "descanso", "idempotencia")


def box_operations():
    """Tabela de operações por origem DERIVADA dos perfis (agents_gate): tudo o que a origem pode, menos `registrar_*`."""
    return {origem: frozenset(op for op in ops if not op.startswith("registrar_"))
            for origem, ops in agent_commands.OPERATIONS.items()}


def required_fields(schema):
    """Campos do comando da caixa: os do esquema SEM `signature` (a origem não é provada na nuvem)."""
    return set(schema["required_fields"]) - {"signature"}


def _no_duplicate_keys(pairs):
    seen = {}
    for chave, valor in pairs:
        if chave in seen:
            raise ValueError("chave duplicada")
        seen[chave] = valor
    return seen


def parse_command(raw, schema):
    """Etapa de forma: bytes UTF-8, tamanho, JSON sem chave repetida, objeto. Levanta ValueError com o código."""
    if not isinstance(raw, (bytes, bytearray)):
        raise ValueError("COMANDO_TIPO")
    if len(raw) > schema["limits"]["max_command_bytes"]:
        raise ValueError("COMANDO_GRANDE")
    try:
        comando = json.loads(bytes(raw).decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise ValueError("COMANDO_INVALIDO") from None
    if not isinstance(comando, dict):
        raise ValueError("COMANDO_NAO_OBJETO")
    return comando


def command_hash(comando):
    """Hash canônico do comando inteiro (chaves ordenadas, UTF-8); é o que o recibo de promoção guarda."""
    return hashlib.sha256(json.dumps(comando, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def rejection_record(entrada_id, codigo, agora):
    """Registro de rejeição: SÓ o código do motivo e o id da entrada (decisão do proprietário, 17/11/2026)."""
    quando = agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(agora, datetime) else None
    return {"entrada_id": entrada_id, "status": DENIED, "codigo": codigo, "quando": quando}


class _Parar(Exception):
    def __init__(self, codigo, etapa):
        super().__init__(codigo)
        self.codigo, self.etapa = codigo, etapa


def validar(nome, raw, contexto, schema=None):
    """Valida UM arquivo da caixa. Nunca levanta; nada é registrado no ledger se houver recusa antes da etapa final.

    `contexto`: `agora` (datetime UTC com tz), `ledger` (contrato `admit(nonce, chave, hash)`), `dia_de_descanso`
    (True, False ou None=desconhecido), `janela_segundos` (opcional; padrão do esquema). Devolve um dicionário com `status`
    (PROMOVER, DUPLICADO ou DENIED), `codigo`, `etapa`, `entrada_id` e, na aceitação, `hash_corpo` e `destino`."""
    entrada_id = nome if isinstance(nome, str) and _NAME.fullmatch(nome) and ".." not in nome else "invalido"
    agora = (contexto or {}).get("agora")
    try:
        schema = schema or agent_commands.load_schema()
        return _validar(nome, raw, contexto or {}, schema, entrada_id)
    except _Parar as p:
        return {"status": DENIED, "codigo": p.codigo, "etapa": p.etapa, "entrada_id": entrada_id,
                "rejeicao": rejection_record(entrada_id, p.codigo, agora)}
    except Exception:  # defesa final: erro inesperado nunca vira promoção
        return {"status": DENIED, "codigo": "ERRO_INTERNO", "etapa": "interno", "entrada_id": entrada_id,
                "rejeicao": rejection_record(entrada_id, "ERRO_INTERNO", agora)}


def _validar(nome, raw, ctx, schema, entrada_id):
    limites = schema["limits"]
    if entrada_id == "invalido":
        raise _Parar("NOME_INVALIDO", "nome")
    try:
        comando = parse_command(raw, schema)
    except ValueError as erro:
        raise _Parar(str(erro), "forma") from None
    if set(comando) != required_fields(schema):
        raise _Parar("CAMPOS_FORA_DO_ESQUEMA", "campos")  # inclui `signature`: não há assinatura que prove a origem
    if comando["schema_version"] != schema["schema_version"] or isinstance(comando["schema_version"], bool):
        raise _Parar("VERSAO_DESCONHECIDA", "campos")
    origem, operacao = comando["origin"], comando["operation"]
    if origem not in schema["origins"]:  # informativa: só serve para escolher a linha da tabela
        raise _Parar("ORIGEM_DESCONHECIDA", "origem")
    if not isinstance(operacao, str):
        raise _Parar("OPERACAO_INVALIDA", "operacao")
    if operacao.startswith("registrar_"):
        raise _Parar("REGISTRAR_FORA_DA_CAIXA", "operacao")  # S6-R3: só o portão de promoção grava histórico
    if operacao not in set().union(*box_operations().values()):
        raise _Parar("OPERACAO_FORA_DA_LISTA", "operacao")
    if operacao not in box_operations()[origem]:
        raise _Parar("OPERACAO_FORA_DA_TABELA_DA_ORIGEM", "operacao")
    if comando["destination"] != schema["destinations"].get(operacao):
        raise _Parar("DESTINO_NAO_DESIGNADO", "destino")
    chave, nonce = comando["idempotency_key"], comando["nonce"]
    if not isinstance(chave, str) or not re.fullmatch(limites["idempotency_key_pattern"], chave):
        raise _Parar("CHAVE_IDEMPOTENCIA_INVALIDA", "chaves")
    if not isinstance(nonce, str) or not re.fullmatch(limites["nonce_pattern"], nonce):
        raise _Parar("NONCE_INVALIDO", "chaves")
    agora = ctx.get("agora")
    if not (isinstance(agora, datetime) and agora.tzinfo is not None):
        raise _Parar("RELOGIO_AUSENTE", "chaves")
    try:
        emitido = agent_commands._parse_time(comando["issued_at"])
    except (ValueError, TypeError):
        raise _Parar("DATA_INVALIDA", "chaves") from None
    janela = ctx.get("janela_segundos", limites["time_window_seconds"])
    if isinstance(janela, bool) or not isinstance(janela, (int, float)) or janela <= 0:
        raise _Parar("JANELA_INVALIDA", "chaves")
    if abs((agora - emitido).total_seconds()) > janela:
        raise _Parar("FORA_DA_JANELA", "chaves")
    motivo = command_idempotency.conferir_chave_do_comando(operacao, chave, agora)  # GA-5: a mesma regra do validador
    if motivo:
        raise _Parar(motivo, "chaves")
    params = comando["params"]
    if not isinstance(params, dict):
        raise _Parar("PARAMS_NAO_OBJETO", "parametros")
    motivo = agent_commands._scan_params(params, schema)
    if motivo:
        raise _Parar(motivo, "parametros")
    motivo = None if operacao == PROMPT_NOTEBOOK else command_params_schema.validar_params(operacao, params)  # GA-1: o prompt tem validador próprio (N2)
    if motivo:
        raise _Parar(motivo, "parametros")
    if operacao == PROMPT_NOTEBOOK:  # S10-R3 (N2): só prompt que o validador do Tutor aceitou, com o hash do texto validado
        veredito = notebook_prompt_validator.conferir_parametros(params)
        if not veredito.ok:
            raise _Parar("PROMPT_" + veredito.codigo, "parametros")
    if operacao == LEMBRETE:  # S3-R2 e S8-R1: sem lembrete em dia de descanso; desconhecido também recusa (E-07)
        descanso = ctx.get("dia_de_descanso")
        if descanso is True:
            raise _Parar("DIA_DE_DESCANSO", "descanso")
        if descanso is not False:
            raise _Parar("DESCANSO_DESCONHECIDO", "descanso")
    ledger = ctx.get("ledger")
    if ledger is None:
        raise _Parar("REGISTRO_INDISPONIVEL", "idempotencia")
    corpo = agent_commands.params_hash({"operation": operacao, "destination": comando["destination"], "params": params})
    veredito = ledger.admit(nonce, chave, corpo)  # decide e registra de uma vez
    if veredito == "nonce_repeated":
        raise _Parar("NONCE_REPETIDO", "idempotencia")
    if veredito == "conflict":
        raise _Parar("CHAVE_REUTILIZADA_COM_OUTRO_CORPO", "idempotencia")
    if veredito not in ("ok", "duplicate"):
        raise _Parar("REGISTRO_INDISPONIVEL", "idempotencia")
    return {"status": PROMOVER if veredito == "ok" else DUPLICADO, "codigo": "OK" if veredito == "ok" else "IDEMPOTENTE",
            "etapa": "idempotencia", "entrada_id": entrada_id, "hash_corpo": command_hash(comando),
            "destino": VALIDATED_DIR + nome}


def selecionar_executaveis(listagem, recibos):
    """Só o que está em `comandos/validados/` E tem recibo com o MESMO hash canônico é executável (S6-R8, S5-R7).

    `listagem`: {caminho: bytes}; `recibos`: {nome_do_arquivo: hash_corpo}. Comando fora de validados, sem recibo, com
    hash divergente (alterado depois da promoção), ilegível ou com nome suspeito nunca é devolvido. Devolve {caminho: comando}."""
    pronto = {}
    for caminho, raw in (listagem or {}).items():
        achado = _VALIDATED_PATH.fullmatch(caminho) if isinstance(caminho, str) else None
        if not achado or ".." in caminho:
            continue
        esperado = (recibos or {}).get(achado.group(1))
        if not (isinstance(esperado, str) and _HEX64.fullmatch(esperado)):
            continue
        try:
            comando = parse_command(raw, agent_commands.load_schema())
        except ValueError:
            continue
        if command_hash(comando) == esperado:
            pronto[caminho] = comando
    return pronto


def check(root: Path = ROOT):
    """Consistência da tabela da caixa com os perfis e o esquema; sem rede."""
    erros = []
    schema = agent_commands.load_schema(root / "config" / "agent_command_schema.json")
    tabela = box_operations()
    if set(tabela) != set(schema["origins"]):
        erros.append("origens da tabela divergem do esquema")
    for origem, ops in tabela.items():
        if any(op.startswith("registrar_") for op in ops):
            erros.append(f"{origem}: registrar_* na caixa")
        if not ops <= set(schema["destinations"]):
            erros.append(f"{origem}: operação sem destino designado: {sorted(ops - set(schema['destinations']))}")
    if "signature" in required_fields(schema):
        erros.append("campo signature não deveria ser obrigatório na caixa")
    return erros


def main(argv=None):
    p = argparse.ArgumentParser(description="Consistência da tabela de operações por origem da caixa de comandos (C4).")
    p.add_argument("--check", action="store_true")
    p.add_argument("--root", default=str(ROOT))
    a = p.parse_args(argv)
    erros = check(Path(a.root))
    if erros:
        print("FALHA: " + "; ".join(erros))
        return 1
    print("OK: tabela de operações por origem da caixa derivada dos perfis e do esquema (S6-R7, R8)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
