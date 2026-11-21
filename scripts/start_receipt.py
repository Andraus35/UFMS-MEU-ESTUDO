"""RS: recibo de START verificável (S14-R2 e S14-R3).

O recibo é o par {"sha", "hashes"}: o SHA Git da revisão e o SHA-256 dos arquivos do START do papel (quatro de estudo, seis de
engenharia, a mesma lista do broker `ReadOnlyAgentBroker`). É o formato que o verificador de entrega (`delivery_gate.py`) já aceita.
O papel NÃO vai no recibo (o formato do GE é fechado): ele é declarado por quem verifica ou deduzido do conjunto de arquivos.

O verificador RECALCULA os hashes a partir dos objetos Git da revisão fixada (`git cat-file`), não da árvore de trabalho: sem rede,
sem credencial, sem modelo; o mesmo código roda local (Termux) e no CI. Função pura e fail-closed: qualquer dúvida recusa.

O QUE PROVA: que os bytes de cada arquivo do START, naquela revisão fixada, têm aqueles hashes.
O QUE NÃO PROVA (limite declarado, S14-R3 e R19): que o modelo leu ou compreendeu os arquivos; quem emitiu o recibo (sem orquestrador
externo que o emita por sessão, qualquer um que conheça o repositório calcula um recibo válido); que a sessão obedeceu ao contrato.
Classe de garantia: ENFORÇADA onde o portão exige o recibo para efeito externo; VERIFICÁVEL no chat direto; NÃO GATEÁVEL: compreensão.

Códigos de saída: 0 recibo válido (ou emitido), 1 recusado, 2 uso incorreto (argparse).
"""
import argparse
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"^[0-9a-f]{40}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")

# Mesma lista e mesma ordem do START (AGENTS.md; settings.json "arquivos obrigatórios"): estudo = 4, engenharia = 6.
ARQUIVOS = {
    "study": ("AGENTS.md", "ROADMAP.md", "memory/HANDOFF.md", "state/CURRENT.json"),
    "engineering": ("AGENTS.md", "ROADMAP.md", "PRODUCT.md", "memory/HANDOFF.md", "state/CURRENT.json", "state/WORKFLOW.json"),
}
PAPEL_MODO = {"tutor": "study", "coach": "study", "engineer": "engineering", "auditor": "engineering"}
MAX_BYTES = 4 * 1024 * 1024

LIMITE = ("O recibo prova que os bytes dos arquivos do START, na revisão fixada, têm estes hashes. NÃO prova que o modelo leu ou "
          "compreendeu os arquivos, nem quem emitiu o recibo, nem que a sessão cumpriu o contrato (S14-R3).")


class ReciboInvalido(ValueError):
    """Recibo ou revisão não verificável; carrega o código do motivo."""

    def __init__(self, motivo):
        super().__init__(motivo)
        self.motivo = motivo


def _modo(papel):
    if papel not in PAPEL_MODO:
        raise ReciboInvalido("papel_invalido")
    return PAPEL_MODO[papel]


def _sha_valido(sha):
    return isinstance(sha, str) and SHA40.fullmatch(sha) is not None


def _blob(root, sha, caminho):
    """Bytes do arquivo no objeto Git da revisão; falha fechada se a revisão ou o arquivo não existirem."""
    try:
        proc = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"{sha}:{caminho}"],
                              capture_output=True, check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReciboInvalido("git_indisponivel") from exc
    if proc.returncode != 0:
        raise ReciboInvalido("revisao_ou_arquivo_inexistente")
    if len(proc.stdout) > MAX_BYTES:
        raise ReciboInvalido("arquivo_extenso_demais")
    return proc.stdout


def calcular(root, sha, modo):
    """Hashes SHA-256 dos arquivos do START do modo, lidos da revisão `sha`."""
    if not _sha_valido(sha):
        raise ReciboInvalido("sha_invalido")
    if modo not in ARQUIVOS:
        raise ReciboInvalido("modo_invalido")
    return {nome: hashlib.sha256(_blob(root, sha, nome)).hexdigest() for nome in ARQUIVOS[modo]}


def emitir(root, sha, papel):
    """Recibo do START do papel na revisão `sha`. Em sessão controlada, `sha` é o SHA externo de confiança."""
    return {"sha": sha, "hashes": calcular(root, sha, _modo(papel))}


def recibo_do_broker(resposta):
    """Recibo a partir da resposta de `ReadOnlyAgentBroker.request`: o broker já validou HEAD, árvore limpa e bootstrap."""
    if not (isinstance(resposta, dict) and resposta.get("status") == "start_verified"):
        raise ReciboInvalido("resposta_do_broker_invalida")
    return {"sha": resposta.get("head"), "hashes": dict(resposta.get("sha256") or {})}


def _forma(recibo):
    ok = (isinstance(recibo, dict) and set(recibo) == {"sha", "hashes"} and _sha_valido(recibo["sha"])
          and isinstance(recibo["hashes"], dict) and recibo["hashes"]
          and all(isinstance(k, str) and isinstance(v, str) and HASH64.fullmatch(v) for k, v in recibo["hashes"].items()))
    if not ok:
        raise ReciboInvalido("recibo_ausente_ou_malformado")


def verificar(recibo, root, sha_fixado, papel=None):
    """Recalcula e confere. Devolve {"valido", "motivos", "modo", ...}; nunca levanta por recibo ruim (fail-closed)."""
    motivos = []
    modo = None
    try:
        _forma(recibo)
        if not _sha_valido(sha_fixado):
            raise ReciboInvalido("sha_fixado_ausente_ou_invalido")
        if recibo["sha"] != sha_fixado:
            raise ReciboInvalido("sha_diferente_do_fixado")
        conjunto = set(recibo["hashes"])
        if papel is not None:
            modo = _modo(papel)
            if conjunto != set(ARQUIVOS[modo]):
                raise ReciboInvalido("arquivos_diferentes_dos_do_papel")
        else:
            achados = [m for m, nomes in ARQUIVOS.items() if conjunto == set(nomes)]
            if not achados:
                raise ReciboInvalido("arquivos_diferentes_dos_do_start")
            modo = achados[0]
        esperado = calcular(root, sha_fixado, modo)
        for nome in ARQUIVOS[modo]:
            if not hmac.compare_digest(esperado[nome], recibo["hashes"][nome]):
                motivos.append("hash_divergente:" + nome)
    except ReciboInvalido as exc:
        motivos.append(exc.motivo)
    return {"valido": not motivos, "motivos": motivos, "modo": modo if not motivos else None,
            "sha": sha_fixado if _sha_valido(sha_fixado) else None, "compreensao_comprovada": False, "limite": LIMITE}


def _ler_recibo(caminho):
    texto = sys.stdin.read() if caminho == "-" else Path(caminho).read_text(encoding="utf-8")
    return json.loads(texto)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("acao", choices=("emitir", "verificar"))
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--sha", default=os.environ.get("UFMS_TRUSTED_HEAD_SHA", ""), help="SHA fixado (padrão: UFMS_TRUSTED_HEAD_SHA)")
    p.add_argument("--role", choices=sorted(PAPEL_MODO), help="obrigatório em emitir; opcional em verificar")
    p.add_argument("--recibo", default="-", help="arquivo JSON do recibo ou - para a entrada padrão (verificar)")
    a = p.parse_args(argv)
    try:
        if a.acao == "emitir":
            if not a.role:
                p.error("emitir exige --role")
            saida = emitir(a.root, a.sha, a.role)
            print(json.dumps(saida, ensure_ascii=False, sort_keys=True))
            return 0
        try:
            recibo = _ler_recibo(a.recibo)
        except (OSError, UnicodeError, json.JSONDecodeError):
            recibo = None
        res = verificar(recibo, a.root, a.sha, a.role)
        print(json.dumps(res, ensure_ascii=False, sort_keys=True))
        return 0 if res["valido"] else 1
    except ReciboInvalido as exc:
        print("BLOQUEADO: " + exc.motivo, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
