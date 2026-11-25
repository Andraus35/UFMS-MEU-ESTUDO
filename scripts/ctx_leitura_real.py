"""ZAPIA-CTX, prova real SOMENTE LEITURA (E29): roda `ler_contexto_agendar` contra o `entrada` REAL e imprime só contagens e prefixos de hash.

Ato do proprietário (Termux, sessão dele do `gh`; nenhum token passa pelo modelo): `GH_TOKEN="$(gh auth token)" python scripts/ctx_leitura_real.py`.
Só GET: o cliente embrulhado recusa qualquer outro método antes de tocar a rede. NÃO liga flag, NÃO promove, NÃO grava, NÃO apaga. O que prova:
a listagem de diretório e a leitura de arquivo do GitHub REAL têm o formato que o runner espera (o que o GitHub falso dos testes só supõe).
Saída sem texto de comando, sem nonce e sem token.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

try:
    import command_box_runner as cbr
    import promotion_runner as pr
except ModuleNotFoundError:  # uso como pacote
    from scripts import command_box_runner as cbr
    from scripts import promotion_runner as pr

REPO_PADRAO = "Andraus35/ufms-meu-estudo-entrada"


class ApiSoLeitura:
    """Embrulha um cliente: só deixa passar GET."""

    def __init__(self, api):
        self._api = api

    def chamar(self, metodo, caminho, corpo=None):
        if metodo != "GET" or corpo is not None:
            raise pr.ApiError(0)
        return self._api.chamar("GET", caminho)


def sondar(caixa, agora):
    ctx = cbr.ler_contexto_agendar(caixa, agora)
    if not ctx:
        return {"ok": False, "codigo": "RELOGIO_SEM_FUSO"}
    return {"ok": True, "validados": len(caixa.listar(cbr.VALIDATED)), "recibos": len(caixa.listar(cbr.RECEIPTS)),
            "hashes_promovidos": len(ctx["hashes_promovidos"]), "prefixos": [h[:12] for h in ctx["hashes_promovidos"]],
            "agendamentos_do_dia": sorted(o for o in ctx["agendamentos_do_dia"] if isinstance(o, str))}


def main(argv=None, transporte=None, ambiente=None, agora=None) -> int:
    ambiente = os.environ if ambiente is None else ambiente
    repo = (argv or [REPO_PADRAO])[0] if argv else REPO_PADRAO
    if not pr._REPO.fullmatch(repo):
        print(json.dumps({"ok": False, "codigo": "REPO_INVALIDO"}))
        return 2
    try:
        api = ApiSoLeitura(pr.GitHubApi(ambiente.get("GH_TOKEN", ""), transporte or pr.transporte_urllib, rotulo="entrada"))
        caixa = cbr.Caixa(api, repo)
        resumo = sondar(caixa, agora or datetime.now(timezone.utc))
    except Exception as erro:  # nunca imprime a mensagem (pode ter metadado do token): só a classe e, se houver, o status
        print(json.dumps({"ok": False, "codigo": type(erro).__name__, "status": getattr(erro, "status", None)}))
        return 1
    print(json.dumps(resumo, ensure_ascii=False))
    return 0 if resumo["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
