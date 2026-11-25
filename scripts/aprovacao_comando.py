"""Aprovação destacada do proprietário sobre o `hash_corpo` de um comando (E41, lote VOLTA-N1; limite 3, "origem declarada").

Por que destacada: a caixa de comandos RECUSA o campo `signature` no comando (S6-R7: na nuvem não há assinatura que o modelo não possa forjar).
Aqui a chave privada fica FORA do modelo e FORA do repositório (Termux do proprietário, modo 0600, guarda de `agent_keys`); ele assina só o
`hash_corpo` do comando que o subagent Tutor propôs e ele leu. A verificação é OFFLINE, com a chave pública (hexadecimal) que ele registra.

O que prova: que quem tem a chave privada aprovou ESTE hash (portanto este texto de comando). O que NÃO prova: que o Tutor escreveu o prompt, nem que a Zapia
executou, nem a qualidade pedagógica; e a verificação é feita depois (auditoria), porque o hook da Zapia não executa Ed25519.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import agent_keys
    import ed25519_pure
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_keys, ed25519_pure

DOMINIO = b"UFMS-APROVACAO-COMANDO-V1\n"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX128 = re.compile(r"^[0-9a-f]{128}$")
CAMPOS = {"hash_corpo", "aprovado_por", "assinatura"}


def _mensagem(hash_corpo: str) -> bytes:
    return DOMINIO + hash_corpo.encode("ascii")


def aprovar(hash_corpo: str, chave_privada, *, repo_root: Path = agent_keys.ROOT) -> dict:
    """Assina o hash do comando. Levanta ValueError se o hash for malformado ou a chave não passar na guarda (fora do repositório, modo 0600...)."""
    if not isinstance(hash_corpo, str) or not _HEX64.fullmatch(hash_corpo):
        raise ValueError("hash_corpo inválido")
    secret = agent_keys._read_secret(chave_privada, repo_root=repo_root)
    return {"hash_corpo": hash_corpo, "aprovado_por": "proprietario", "assinatura": ed25519_pure.sign(secret, _mensagem(hash_corpo)).hex()}


def verificar(aprovacao, hash_corpo: str, chave_publica_hex: str) -> str | None:
    """None se a aprovação é válida para ESTE hash e esta chave pública; senão o código. Nunca levanta."""
    try:
        if not isinstance(aprovacao, dict) or set(aprovacao) != CAMPOS:
            return "APROVACAO_FORA_DO_FORMATO"
        if aprovacao["aprovado_por"] != "proprietario" or aprovacao["hash_corpo"] != hash_corpo or not _HEX64.fullmatch(str(hash_corpo)):
            return "APROVACAO_DE_OUTRO_COMANDO"
        if not isinstance(chave_publica_hex, str) or not re.fullmatch(r"[0-9a-f]{64}", chave_publica_hex):
            return "CHAVE_PUBLICA_INVALIDA"
        if not isinstance(aprovacao["assinatura"], str) or not _HEX128.fullmatch(aprovacao["assinatura"]):
            return "ASSINATURA_MALFORMADA"
        ok = ed25519_pure.verify(bytes.fromhex(chave_publica_hex), _mensagem(hash_corpo), bytes.fromhex(aprovacao["assinatura"]))
        return None if ok else "ASSINATURA_NAO_CONFERE"
    except Exception:
        return "APROVACAO_ILEGIVEL"


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar-chave", help="gera a chave privada FORA do repositório e imprime a pública")
    g.add_argument("--privada", required=True)
    s = sub.add_parser("aprovar", help="assina o hash_corpo de cada comando do meta.json")
    s.add_argument("--privada", required=True)
    s.add_argument("--meta", required=True)
    s.add_argument("--saida", required=True, help="pasta onde gravar <nome>.aprovacao.json")
    v = sub.add_parser("verificar")
    v.add_argument("--publica", required=True)
    v.add_argument("--meta", required=True)
    v.add_argument("--aprovacoes", required=True)
    a = p.parse_args(argv)
    if a.cmd == "gerar-chave":
        print(json.dumps({"publica": agent_keys.generate(a.privada)}))
        return 0
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    if a.cmd == "aprovar":
        out = Path(a.saida)
        out.mkdir(parents=True, exist_ok=True)
        for nome, info in sorted(meta["itens"].items()):
            (out / (nome.replace(".json", "") + ".aprovacao.json")).write_text(json.dumps(aprovar(info["hash_corpo"], a.privada), indent=2), encoding="utf-8")
        print(json.dumps({"aprovados": sorted(meta["itens"])}))
        return 0
    falhas = {}
    for nome, info in sorted(meta["itens"].items()):
        arq = Path(a.aprovacoes) / (nome.replace(".json", "") + ".aprovacao.json")
        try:
            falhas[nome] = verificar(json.loads(arq.read_text(encoding="utf-8")), info["hash_corpo"], a.publica)
        except (OSError, ValueError):
            falhas[nome] = "APROVACAO_AUSENTE"
    print(json.dumps({"resultado": falhas}, ensure_ascii=False))
    return 0 if not any(falhas.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
