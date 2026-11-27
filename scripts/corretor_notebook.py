"""E45: corretor SIMULADO do Notebook (fora do modelo). Sem rede, sem credencial real, sem tocar o `entrada`.

O corretor é o único componente que, num desenho futuro, guardaria a credencial do Google (D-26 proíbe esse segredo no modelo). Ele recebe só o
comando JÁ validado e o recibo, revalida tudo em código (caixa de comandos, hash, idade, operação), executa num backend e devolve uma resposta de
campos fixos, marcada como dado NÃO confiável. O backend oficial (`BackendOficialV1Alpha`) só MONTA requisições (não as envia) e recusa o que a
documentação oficial não descreve (perguntar ao caderno). Não prova nada sobre o Notebook real; prova o contrato e as recusas do corretor.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

try:
    import agent_commands
    import command_box
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, command_box

OPERACAO = "enviar_prompt_notebook"
LIMITE_FONTE_BYTES = 200_000  # teto do corretor, NÃO é limite da API (a documentação não informa)
LIMITE_RESPOSTA = 8000
SEGREDO = re.compile(r"(ya29\.[\w-]{10,}|AIza[\w-]{20,}|Bearer\s+[\w.~+/-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY|\"refresh_token\"|\"client_secret\")")
CODIGOS = ("COMANDO_RECUSADO", "HASH_NAO_CONFERE", "RECIBO_INVALIDO", "OPERACAO_NAO_PERMITIDA", "FONTE_AUSENTE", "FONTE_NAO_ADICIONADA",
           "PERGUNTA_NAO_SUPORTADA", "BACKEND_FALHOU", "SEGREDO_NA_SAIDA", "RESPOSTA_INVALIDA")


class CapacidadeNaoDocumentada(Exception):
    """A documentação oficial lida em 27/11/2026 não descreve este método."""


class SemCredencial(Exception):
    """Este repositório nunca guarda credencial: o backend oficial real só existiria fora dele."""


class BackendSimulado:
    """Caderno em memória. `falhar` escolhe a etapa que falha: criar, fonte ou perguntar."""

    def __init__(self, resposta="O trecho cita a União, os Estados, o Distrito Federal e os Municípios.", falhar=None):
        self.resposta, self.falhar, self.chamadas, self.cadernos = resposta, falhar, [], {}

    def _ponto(self, etapa):
        self.chamadas.append(etapa)
        if self.falhar == etapa:
            raise RuntimeError("falha simulada em " + etapa)

    def criar_caderno(self, titulo):
        self._ponto("criar")
        cid = "caderno-" + str(len(self.cadernos) + 1)
        self.cadernos[cid] = {"titulo": titulo, "fontes": []}
        return cid

    def adicionar_fonte_texto(self, caderno, nome, texto):
        self._ponto("fonte")
        self.cadernos[caderno]["fontes"].append({"nome": nome, "texto": texto})
        return len(self.cadernos[caderno]["fontes"])

    def perguntar(self, caderno, prompt):
        self._ponto("perguntar")
        return self.resposta


class BackendOficialV1Alpha:
    """Monta as requisições da API oficial (Preview, v1alpha) sem enviá-las e sem token. Só `textContent`: URL, vídeo e Drive ficam de fora."""

    BASE = "https://{loc}-discoveryengine.googleapis.com/v1alpha/projects/{proj}/locations/{loc}/notebooks"

    def __init__(self, projeto="PROJECT_NUMBER", local="global"):
        self.projeto, self.local = projeto, local

    def _base(self):
        return self.BASE.format(loc=self.local, proj=self.projeto)

    def requisicao_criar(self, titulo):
        return {"metodo": "POST", "url": self._base(), "corpo": {"title": titulo}}

    def requisicao_fonte(self, caderno_id, nome, texto):
        corpo = {"userContents": [{"textContent": {"sourceName": nome, "content": texto}}]}
        return {"metodo": "POST", "url": f"{self._base()}/{caderno_id}/sources:batchCreate", "corpo": corpo}

    def criar_caderno(self, titulo):
        raise SemCredencial("sem credencial neste repositório")

    def adicionar_fonte_texto(self, caderno, nome, texto):
        raise SemCredencial("sem credencial neste repositório")

    def perguntar(self, caderno, prompt):
        raise CapacidadeNaoDocumentada("a documentação lida não descreve método de pergunta ou chat")


def _parar(entrada_id, hash_corpo, codigo, etapa, detalhe=""):
    return {"entrada_id": entrada_id, "hash_corpo": hash_corpo, "estado": "PARADO", "codigo_parada": codigo, "etapa": etapa, "detalhe": detalhe[:120],
            "nao_confiavel": True}


class Corretor:
    """Executa UM comando validado por vez. `token` é o segredo SIMULADO que o corretor guarda; nunca sai nos resultados."""

    def __init__(self, backend, token="ya29.TOKEN-SIMULADO-APENAS-PARA-TESTE", ja_respondidos=None):
        self._backend, self._token = backend, token
        self.ja_respondidos = set(ja_respondidos or ())  # idempotência por hash do comando

    def _vaza(self, texto):
        return bool(SEGREDO.search(texto)) or (bool(self._token) and self._token in texto)

    def executar(self, nome, comando_bytes, recibo, fonte_nome, fonte_bytes, agora):
        if not isinstance(recibo, dict) or recibo.get("status") != "PROMOVER" or not isinstance(recibo.get("hash_corpo"), str):
            return _parar(nome, None, "RECIBO_INVALIDO", "recibo")
        esperado = recibo["hash_corpo"]
        r = command_box.validar(nome, comando_bytes, {"agora": agora, "ledger": agent_commands.CommandLedger(), "dia_de_descanso": False,
                                                       "atividades_pendentes": [], "chaves_do_dia": []})
        if r["status"] != command_box.PROMOVER:
            return _parar(nome, esperado, "COMANDO_RECUSADO", "caixa", str(r.get("codigo")))
        comando = json.loads(comando_bytes.decode("utf-8"))
        if command_box.command_hash(comando) != esperado:
            return _parar(nome, esperado, "HASH_NAO_CONFERE", "hash")
        if comando.get("operation") != OPERACAO or comando.get("origin") != "tutor":
            return _parar(nome, esperado, "OPERACAO_NAO_PERMITIDA", "operacao")
        if esperado in self.ja_respondidos:
            return {"entrada_id": nome, "hash_corpo": esperado, "estado": "JA_RESPONDIDO", "nao_confiavel": True}
        if not isinstance(fonte_bytes, (bytes, bytearray)) or not fonte_bytes or len(fonte_bytes) > LIMITE_FONTE_BYTES or not isinstance(fonte_nome, str) or not fonte_nome:
            return _parar(nome, esperado, "FONTE_AUSENTE", "fonte")
        try:
            texto = bytes(fonte_bytes).decode("utf-8")
        except UnicodeDecodeError:
            return _parar(nome, esperado, "FONTE_AUSENTE", "fonte", "utf-8")
        if self._vaza(texto) or self._vaza(comando["params"].get("prompt", "")):
            return _parar(nome, esperado, "SEGREDO_NA_SAIDA", "entrada")
        try:
            caderno = self._backend.criar_caderno("descartavel-" + esperado[:12])
            self._backend.adicionar_fonte_texto(caderno, fonte_nome, texto)
        except SemCredencial:
            return _parar(nome, esperado, "BACKEND_FALHOU", "caderno", "sem credencial")
        except Exception as e:
            return _parar(nome, esperado, "FONTE_NAO_ADICIONADA", "fonte", type(e).__name__)
        try:
            resposta = self._backend.perguntar(caderno, comando["params"]["prompt"])
        except CapacidadeNaoDocumentada:
            return _parar(nome, esperado, "PERGUNTA_NAO_SUPORTADA", "perguntar")
        except Exception as e:
            return _parar(nome, esperado, "BACKEND_FALHOU", "perguntar", type(e).__name__)
        if not isinstance(resposta, str) or not resposta.strip() or len(resposta) > LIMITE_RESPOSTA:
            return _parar(nome, esperado, "RESPOSTA_INVALIDA", "resposta")
        if self._vaza(resposta):
            return _parar(nome, esperado, "SEGREDO_NA_SAIDA", "resposta")  # a resposta é descartada, não repassada
        self.ja_respondidos.add(esperado)
        return {"entrada_id": nome, "hash_corpo": esperado, "estado": "RESPONDIDO", "resposta": resposta, "fonte_sha256": hashlib.sha256(bytes(fonte_bytes)).hexdigest(),
                "respondido_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "nao_confiavel": True}
