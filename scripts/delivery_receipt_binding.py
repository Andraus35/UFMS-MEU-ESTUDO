"""RG: liga o recibo de START (RS) ao verificador de entrega (GE) — S14-R3.

Calcula, a partir do repositório no SHA do contrato fixado, o recibo que a entrega de um papel DEVERIA trazer (`recibo_esperado` do
contexto do verificador). Sem rede, sem credencial, sem modelo, sem escrita. Fail-closed: qualquer dúvida devolve None, e o verificador de
entrega trata `None` como recibo não conferido (recusa tipo com efeito externo e avisa os demais).

Papéis do envelope com START definido: `tutor` e `coach` (quatro arquivos de estudo). A `zapia` não tem START de arquivos definido neste
contrato: devolve None (não conferido). O que isto prova e o que não prova é o limite de `start_receipt.py`: bytes na revisão fixada; não
prova compreensão nem quem emitiu o recibo.
"""
import start_receipt

PAPEIS_COM_START = ("tutor", "coach")


def recibo_esperado(root, sha_contrato, papel):
    """Recibo {sha, hashes} esperado para o papel no SHA do contrato, ou None se não puder ser calculado."""
    if papel not in PAPEIS_COM_START:
        return None
    try:
        return start_receipt.emitir(root, sha_contrato, papel)
    except start_receipt.ReciboInvalido:
        return None
