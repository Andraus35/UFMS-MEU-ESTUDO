"""Runner da caixa de comandos (S6-R8, R12; tarefa COMANDOS): liga `command_box` ao repositório `entrada` pelo mesmo desenho do
runner de promoção (`promotion_runner`): transporte injetado, flag falsa ⇒ nenhuma chamada, SHA do validador conferido.

Fluxo por comando (arquivo `comandos/<nome>.json` no checkout do evento), em série e em ordem de nome:
  validar (`command_box.validar`) → copiar os MESMOS bytes para `comandos/validados/<nome>` → confirmar nonce e chave no
  ledger durável → gravar `comandos/recibos/<nome>` (só hash e código) → remover a entrada.
Rejeitado: `comandos/rejeitadas/<nome>` só com código e id, e a entrada sai. Erro de API (leitura do ledger, escrita) NÃO rejeita:
a entrada fica na caixa e a próxima execução repete, de forma idempotente (nada de comando válido perdido por falha transitória).

Decisões e limites:
- O canal segue a MESMA flag do fluxo, `private_flow_promotion_enabled` (a `personal_results_writes_enabled` do público segue falsa), do `settings.json` do SHA fixado (fail-closed): com ela falsa
  (hoje) não há rede, nem token lido, nem escrita. Não há flag própria dos comandos (criar uma exige PR de configuração).
- Só o token da fila (`GH_TOKEN`, escopo de `entrada`) é usado: este passo NÃO recebe o segredo do histórico `dados`.
- O ledger (`comandos/ledger/`) só é gravado DEPOIS da promoção; assim uma queda no meio não consome o nonce de um comando que
  ficou sem cópia em `validados/`. Uma entrada cujo `validados/<nome>` idêntico já existe é apenas finalizada (retomada).
- Janela de tempo do comando: 300 s injetada aqui (o esquema, 120 s, fica intacto); nonce e idempotência seguem valendo.
- Dia de descanso: sem leitor do plano, `dia_de_descanso` é desconhecido, então `criar_lembrete` é recusado
  (DESCANSO_DESCONHECIDO); mensagens e prompts passam. Um leitor do plano é outra tarefa.
- Não prova que a Zapia leia só de `validados/` (autorrelato), nem a origem do comando (S6-R7); só o fake provou o contrato do
  GitHub (a prova real é a C5); a regra de duas mensagens por dia e os limites de job (S8) são do decisor da rotina.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import agent_commands
    import command_box
    import promotion_runner as pr
    from core import ROOT
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, command_box
    from scripts import promotion_runner as pr
    from scripts.core import ROOT

BOX = "comandos"
VALIDATED = BOX + "/validados/"
RECEIPTS = BOX + "/recibos/"
REJECTED = BOX + "/rejeitadas/"
LEDGER = BOX + "/ledger/"
WINDOW_SECONDS = 300
RESUME_WINDOW_SECONDS = 86400  # só na retomada de uma execução interrompida
FILA_MAX = 500


class Caixa(pr.FilaEntrada):
    """`FilaEntrada` (escrever arquivo novo e idempotente, remover) mais a leitura de um arquivo."""

    def ler(self, caminho):
        try:
            _, obj = self.api.chamar("GET", self._base + caminho)
        except pr.ApiError as erro:
            if erro.status == 404:
                return None
            raise
        if not (isinstance(obj, dict) and obj.get("type") == "file" and isinstance(obj.get("content"), str)):
            raise pr.ApiError(0)
        return pr._decodifica(obj["content"])


class _SemEstado:
    """Ledger sem memória, só para a revalidação estática da retomada."""

    def admit(self, nonce, chave, corpo):
        return "ok"


def _nome_ledger(prefixo, valor):
    return f"{LEDGER}{prefixo}-{hashlib.sha256(valor.encode('utf-8')).hexdigest()[:40]}.json"


def _canonico(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class LedgerDuravel:
    """Contrato `admit` do `command_box`, apoiado em arquivos de `comandos/ledger/` (o Actions não guarda estado).

    `admit` só LÊ (e guarda a intenção em memória, para duas entradas da mesma execução); a gravação é de `confirmar`, depois
    da promoção. Falha de leitura propaga: o runner a trata como transitória e mantém a entrada."""

    def __init__(self, caixa):
        self.caixa = caixa
        self.nonces, self.chaves = set(), {}

    def admit(self, nonce, chave, corpo):
        if nonce in self.nonces or self.caixa.ler(_nome_ledger("n", nonce)) is not None:
            return "nonce_repeated"
        anterior = self.chaves.get(chave)
        if anterior is None:
            gravado = self.caixa.ler(_nome_ledger("k", chave))
            anterior = None if gravado is None else json.loads(gravado.decode("utf-8")).get("corpo")
        if anterior is not None:
            if anterior != corpo:
                return "conflict"
            self.nonces.add(nonce)
            return "duplicate"
        self.nonces.add(nonce)
        self.chaves[chave] = corpo
        return "ok"

    def confirmar(self, nonce, chave, corpo):
        """Grava chave e nonce (arquivo novo, idempotente). Repetir com o mesmo conteúdo é seguro."""
        self.caixa.escrever(_nome_ledger("k", chave), _canonico({"corpo": corpo}))
        self.caixa.escrever(_nome_ledger("n", nonce), _canonico({"corpo": corpo}))


def _campos(bruto):
    """(nonce, chave, hash do corpo) de um comando JÁ validado, no mesmo cálculo do `command_box`."""
    c = json.loads(bytes(bruto).decode("utf-8"))
    corpo = agent_commands.params_hash({"operation": c["operation"], "destination": c["destination"], "params": c["params"]})
    return c["nonce"], c["idempotency_key"], corpo


def _recibo(nome, status, codigo, hash_corpo, execucao, validador_sha):
    return _canonico({"entrada_id": nome, "status": status, "codigo": codigo, "hash_corpo": hash_corpo,
                      "execucao": execucao, "validador_sha": validador_sha})


def executar(entradas, contexto, caixa):
    """Processa a caixa EM SÉRIE e em ordem de nome. `contexto`: `escritas_habilitadas`, `agora`, `execucao`, `validador_sha`,
    `validador_sha_fixado`, opcionais `dia_de_descanso`, `atividades_pendentes` e `chaves_do_dia` (COR-B; ausentes recusam lembrete2/criar_lembrete e a chave de rotina). Resumo só com contagens, códigos e ids."""
    resumo = {"flag": contexto.get("escritas_habilitadas") is True, "itens": [], "falhas_de_registro": 0}
    if not resumo["flag"]:
        resumo["estado"] = "FLAG_DESLIGADA"
        resumo["mantidas"] = len(list(entradas))
        return resumo
    sha, fixado = contexto.get("validador_sha"), contexto.get("validador_sha_fixado")
    if not (isinstance(sha, str) and sha == fixado and pr._SHA40.fullmatch(sha)):
        resumo.update(estado="VALIDADOR_DIVERGENTE", mantidas=len(list(entradas)))
        return resumo
    ledger = LedgerDuravel(caixa)
    ctx = {"agora": contexto["agora"], "ledger": ledger, "dia_de_descanso": contexto.get("dia_de_descanso"),
           "atividades_pendentes": contexto.get("atividades_pendentes"), "chaves_do_dia": list(contexto["chaves_do_dia"]) if isinstance(contexto.get("chaves_do_dia"), (list, tuple, set, frozenset)) else None,
           "janela_segundos": contexto.get("janela_segundos", WINDOW_SECONDS)}
    execucao = contexto.get("execucao")
    for nome, bruto in sorted(entradas, key=lambda par: str(par[0])):
        item = {"entrada_id": nome if isinstance(nome, str) and command_box._NAME.fullmatch(nome) and ".." not in nome else "invalido"}
        resumo["itens"].append(item)
        if item["entrada_id"] == "invalido":
            item.update(status="IGNORADA", codigo="NOME_INVALIDO")
            continue
        try:
            _processar(nome, bruto, ctx, caixa, ledger, execucao, sha, item)
        except Exception:  # erro de API: a entrada fica e a próxima execução repete
            resumo["falhas_de_registro"] += 1
            item.setdefault("status", "MANTIDA")
            item["registro"] = "FALHOU"
    resumo["estado"] = "PROCESSADO"
    return resumo


def _processar(nome, bruto, ctx, caixa, ledger, execucao, sha, item):
    existente = caixa.ler(VALIDATED + nome)
    if existente is not None:
        if existente != bytes(bruto):  # mesmo nome, outro conteúdo: nunca sobrescreve nem aceita
            return _rejeitar(nome, "NOME_JA_VALIDADO", ctx, caixa, item)
        # Retomada: já promovido, só finaliza (ledger, recibo, saída da fila). NUNCA confia na existência do arquivo: revalida a
        # parte estática (forma, tabela por origem, destino, filtro, descanso); só dispensa a janela (o comando é antigo de
        # propósito) e a novidade do nonce (já foi consumido pela execução interrompida).
        chaves = ctx["chaves_do_dia"] + [_campos(bruto)[1]] if ctx["chaves_do_dia"] is not None else None  # a própria chave já ocupava o teto
        rev = command_box.validar(nome, bruto, dict(ctx, ledger=_SemEstado(), janela_segundos=RESUME_WINDOW_SECONDS, chaves_do_dia=chaves))
        if rev["status"] != command_box.PROMOVER:
            if rev["codigo"] == "ERRO_INTERNO":
                raise RuntimeError("erro interno transitório")
            return _rejeitar(nome, rev["codigo"], ctx, caixa, item, rev["rejeicao"])
        nonce, chave, corpo = _campos(bruto)
        ledger.confirmar(nonce, chave, corpo)
        _ocupar_teto(ctx, chave)
        caixa.escrever(RECEIPTS + nome, _recibo(nome, "PROMOVER", "RETOMADA", rev["hash_corpo"], execucao, sha))
        caixa.remover(f"{BOX}/{nome}")
        item.update(status="PROMOVER", codigo="RETOMADA")
        return
    res = command_box.validar(nome, bruto, ctx)
    item.update(status=res["status"], codigo=res["codigo"])
    if res["status"] == command_box.DENIED:
        if res["codigo"] == "ERRO_INTERNO":  # falha transitória (ex.: leitura do ledger): não rejeita, mantém
            item["status"] = "MANTIDA"
            raise RuntimeError("erro interno transitório")
        return _rejeitar(nome, res["codigo"], ctx, caixa, item, res["rejeicao"])
    nonce, chave, corpo = _campos(bruto)
    if res["status"] == command_box.PROMOVER:
        caixa.escrever(VALIDATED + nome, bytes(bruto))  # os MESMOS bytes que foram validados
    ledger.confirmar(nonce, chave, corpo)
    _ocupar_teto(ctx, chave)
    caixa.escrever(RECEIPTS + nome, _recibo(nome, res["status"], res["codigo"], res["hash_corpo"], execucao, sha))
    caixa.remover(f"{BOX}/{nome}")


def _ocupar_teto(ctx, chave):
    """A execução é em série: a chave promovida passa a contar no teto diário das entradas seguintes (COR-B, AC-3)."""
    if ctx.get("chaves_do_dia") is not None and chave not in ctx["chaves_do_dia"]:
        ctx["chaves_do_dia"].append(chave)


def _rejeitar(nome, codigo, ctx, caixa, item, registro=None):
    item.update(status=command_box.DENIED, codigo=codigo)
    registro = registro or command_box.rejection_record(nome, codigo, ctx["agora"])
    caixa.escrever(REJECTED + nome, _canonico(registro))
    caixa.remover(f"{BOX}/{nome}")


def ler_caixa(diretorio):
    """Só arquivos `.json` comuns diretamente em `comandos/` (sem link, sem subpasta), com teto de quantidade."""
    saida = []
    if not Path(diretorio).is_dir():  # um push que só tocou a outra fila: pasta ausente é caixa vazia
        return saida
    for caminho in sorted(Path(diretorio).iterdir()):
        if caminho.is_symlink() or not caminho.is_file() or caminho.suffix != ".json":
            continue
        saida.append((caminho.name, caminho.read_bytes()))
        if len(saida) > FILA_MAX:
            raise ValueError("caixa grande demais")
    return saida


def main(argv=None, transporte=None, ambiente=None, agora=None):
    p = argparse.ArgumentParser(description="Valida e promove comandos da caixa de `entrada` (COMANDOS).")
    p.add_argument("--comandos", required=True)
    p.add_argument("--execucao", required=True)
    p.add_argument("--validador-sha", required=True)
    p.add_argument("--entrada-repo", required=True)
    p.add_argument("--validador-dir", default=str(ROOT))
    a = p.parse_args(argv)
    ambiente = os.environ if ambiente is None else ambiente
    validador = Path(a.validador_dir)
    if not pr.ler_flag((validador / "settings.json").read_text(encoding="utf-8")):  # sem rede, sem token, sem escrita
        n = len(ler_caixa(a.comandos)) if Path(a.comandos).is_dir() else 0
        print(json.dumps({"estado": "FLAG_DESLIGADA", "mantidas": n, "flag": False}))
        return 0
    if not pr._REPO.fullmatch(a.entrada_repo or ""):
        print(json.dumps({"estado": "ERRO", "codigo": "ENTRADA_REPO_INVALIDO"}))
        return 1
    try:
        t = transporte or pr.transporte_urllib
        caixa = Caixa(pr.GitHubApi(ambiente.get("GH_TOKEN", ""), t), a.entrada_repo)
        contexto = {"escritas_habilitadas": True, "agora": agora or datetime.now(timezone.utc), "execucao": a.execucao,
                    "validador_sha": pr.ler_head_sha(validador), "validador_sha_fixado": a.validador_sha}
        resumo = executar(ler_caixa(a.comandos), contexto, caixa)
    except Exception as erro:  # nunca imprime a exceção: só a classe
        print(json.dumps({"estado": "ERRO", "codigo": type(erro).__name__}))
        return 1
    print(json.dumps(resumo, ensure_ascii=False))
    return 1 if resumo["falhas_de_registro"] or resumo["estado"] == "VALIDADOR_DIVERGENTE" else 0


if __name__ == "__main__":
    sys.exit(main())
