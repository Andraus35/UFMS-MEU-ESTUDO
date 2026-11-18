"""Runner do fluxo de promoção (S6-R4, R5, R6; tarefa RUNNER): liga o portão `promotion_gate.promover` ao GitHub.

É o único código do fluxo que fala com a rede, e o faz por um TRANSPORTE INJETADO (`transporte(metodo, url, cabecalhos, corpo,
tempo) -> (status, bytes)`): nos testes só há transporte falso. O transporte real (`transporte_urllib`) só é criado pelo CLI.

Garantias de projeto:
- A flag `private_flow_promotion_enabled` (própria do fluxo; a `personal_results_writes_enabled` do público segue falsa) vem do `settings.json` do checkout do validador (o SHA fixado, que a Zapia não
  altera). Se não for exatamente `true`, o runner **não faz NENHUMA chamada, não lê token e não grava nada**: as entradas ficam na fila.
- O validador em execução é conferido por `.git/HEAD` do checkout contra o SHA fixado no fluxo (S6-R5).
- Dois tokens, dois clientes: o token da fila (`entrada`) só fala com `entrada`, o do histórico (`dados`) só com `dados`. Token
  nunca é impresso, gravado nem aparece em mensagem de erro; erro de API carrega só o status.
- Serial e idempotente: entradas em ordem de nome; aceita sai da fila depois do recibo; rejeitada vai para `rejeitadas/` só com
  código e id; flag desligada ou readback pendente deixam a entrada na fila (repetir é seguro).

Limites: não prova que o GitHub se comporte como o fake (C5 é a prova real); `existentes()` lê o histórico arquivo a arquivo
(escala pessoal, com teto); não confere se forks estão desabilitados nem os colaboradores (C3); a origem do comando não é provada (S6-R7).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import promotion_gate as pg
    import session_read_guard as srg
    from core import ROOT, topic_rows
    from private_persistence_guard import PersistenceBlocked
except ModuleNotFoundError:  # uso como pacote
    from scripts import promotion_gate as pg
    from scripts import session_read_guard as srg
    from scripts.core import ROOT, topic_rows
    from scripts.private_persistence_guard import PersistenceBlocked

API = "https://api.github.com"
DADOS_REPO = "Andraus35/ufms-meu-estudo-dados"  # P2: destino fixo, no código do SHA fixado (nunca vem da fila)
FILA_DIR = "fila/entradas"
MAX_HISTORICO = 2000
_PATH = re.compile(r"^/repos/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._%=-]+)*$")
# ASCII imprimível sem espaço. O limite de 255 recusava o GITHUB_TOKEN do Actions (prova real de 18/11/2026: `TOKEN_INVALIDO:entrada`):
# os tokens do GitHub podem passar de 255 caracteres. 1024 mantém o teto contra lixo e cabeçalho gigante.
_TOKEN = re.compile(r"^[\x21-\x7e]{8,1024}$")
_REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9._-]{1,100}$")
_NOME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.json$")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class ApiError(Exception):
    """Falha de API: carrega só o status (0 = rede/resposta ilegível); nunca cabeçalho, corpo ou token."""

    def __init__(self, status):
        super().__init__(f"API {status}")
        self.status = status


FLAG_FLUXO = "private_flow_promotion_enabled"


def ler_flag(texto):
    """True só se `storage.private_flow_promotion_enabled` (flag PRÓPRIA do fluxo privado, C6) for exatamente o booleano true.
    A flag `personal_results_writes_enabled` é do repositório PÚBLICO (nunca guarda resultado) e este leitor NÃO a consulta.
    Qualquer dúvida é False."""
    try:
        return json.loads(texto)["storage"][FLAG_FLUXO] is True
    except Exception:
        return False


def ler_head_sha(validador_dir):
    """SHA do commit do checkout do validador, lido de `.git/HEAD` (sem subprocesso); None se não for possível."""
    try:
        git = Path(validador_dir) / ".git"
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref: "):
            ref = head[5:].strip()
            if ".." in ref or not ref.startswith("refs/"):
                return None
            head = (git / ref).read_text(encoding="utf-8").strip()
        return head if _SHA40.fullmatch(head) else None
    except Exception:
        return None


class GitHubApi:
    """Cliente mínimo do GitHub REST com transporte injetado e UM token. Só fala com a API oficial."""

    def __init__(self, token, transporte, base=API, tempo=20, rotulo=""):
        if not (isinstance(token, str) and _TOKEN.fullmatch(token)):
            # nunca ecoa o valor; só o rótulo, o comprimento e se todos os caracteres são ASCII imprimível (metadados sem segredo)
            n = len(token) if isinstance(token, str) else 0
            imprimivel = "sim" if isinstance(token, str) and all(0x21 <= ord(c) <= 0x7E for c in token) else "nao"
            raise ValueError(f"TOKEN_INVALIDO:{rotulo}:len={n}:imprimivel={imprimivel}" if rotulo else "TOKEN_INVALIDO")
        self._token, self._transporte, self._base, self._tempo = token, transporte, base, tempo

    def __repr__(self):
        return "GitHubApi(<token oculto>)"

    def chamar(self, metodo, caminho, corpo=None):
        if not (isinstance(caminho, str) and _PATH.fullmatch(caminho) and ".." not in caminho):
            raise ApiError(0)
        dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
        cabecalhos = {"Authorization": "Bearer " + self._token, "Accept": "application/vnd.github+json",
                      "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "ufms-promocao"}
        try:
            status, bruto = self._transporte(metodo, self._base + caminho, cabecalhos, dados, self._tempo)
            objeto = json.loads(bytes(bruto).decode("utf-8")) if bruto else None
        except Exception:
            raise ApiError(0) from None
        if not isinstance(status, int) or status >= 400:
            raise ApiError(status if isinstance(status, int) else 0)
        return status, objeto


# Mensagens de ValueError que o runner PODE imprimir (formato fechado, escritas por este código; nunca o valor de um token):
# a prova real de 18/11/2026 só mostrou `ValueError`, sem dizer qual dos dois tokens estava malformado.
DETALHE_SEGURO = re.compile(r"^(?:TOKEN_INVALIDO:(?:dados|entrada):len=\d{1,7}:imprimivel=(?:sim|nao)|fila grande demais)$")


def _b64(dados):
    return base64.b64encode(dados).decode("ascii")


def _decodifica(conteudo):
    return base64.b64decode("".join(conteudo.split()), validate=True)


class RepositorioDados:
    """Adaptador do histórico `dados` para o portão: `existentes`, `ler`, `criar`, `ler_de_volta`."""

    def __init__(self, api, repo):
        self.api, self.repo = api, repo
        self._base = f"/repos/{repo}"

    def _contents(self, caminho):
        return f"{self._base}/contents/{caminho}"

    def _arquivo(self, caminho):
        try:
            _, obj = self.api.chamar("GET", self._contents(caminho))
        except ApiError as erro:
            if erro.status == 404:
                return None
            raise
        if not (isinstance(obj, dict) and obj.get("type") == "file" and isinstance(obj.get("content"), str)):
            raise ApiError(0)
        return obj

    def _listar(self, caminho):
        try:
            _, obj = self.api.chamar("GET", self._contents(caminho))
        except ApiError as erro:
            if erro.status == 404:
                return []
            raise
        if not isinstance(obj, list):
            raise ApiError(0)
        return obj

    def existentes(self):
        eventos, total = [], 0
        for mes in self._listar("eventos"):
            if mes.get("type") != "dir":
                continue
            for arq in self._listar("eventos/" + mes["name"]):
                if arq.get("type") != "file":
                    continue
                total += 1
                if total > MAX_HISTORICO:
                    raise ApiError(0)  # histórico grande demais para ler arquivo a arquivo: fecha
                dado = self.ler(f"eventos/{mes['name']}/{arq['name']}")
                try:
                    eventos.append(json.loads(dado.decode("utf-8"))["evento"])
                except (ValueError, KeyError, AttributeError, UnicodeDecodeError):
                    continue  # arquivo estranho: o conflito aparece na idempotência
        return eventos

    def ler(self, caminho):
        obj = self._arquivo(caminho)
        return None if obj is None else _decodifica(obj["content"])

    def criar(self, caminho, dados):
        """Cria um arquivo NOVO (sem `sha`): se já existir, o GitHub devolve 422 e nada é sobrescrito."""
        _, obj = self.api.chamar("PUT", self._contents(caminho), {"message": "promover evento", "content": _b64(dados)})
        return {"commit_sha": obj["commit"]["sha"]}

    def ler_de_volta(self, caminho):
        obj = self._arquivo(caminho)
        _, info = self.api.chamar("GET", self._base)
        _, ref = self.api.chamar("GET", f"{self._base}/git/ref/heads/{info['default_branch']}")
        return {"conteudo": _decodifica(obj["content"]), "blob_sha": obj["sha"], "head_sha": ref["object"]["sha"]}

    def visibilidade(self, alvo):
        """Leitor de P1: só os campos que o guard confere."""
        _, info = self.api.chamar("GET", f"/repos/{alvo}")
        return {"private": info.get("private"), "visibility": info.get("visibility"), "full_name": info.get("full_name")}

    def consentimento(self):
        """Leitor de P3: `consent-v4.json` na raiz do privado (a promoção exige o consentimento v4, que cobre `entrada` e `dados`
        e o app Claude; o v2 e o v3 NÃO bastam). Ausente, ilegível ou inválido vira None (o guard bloqueia)."""
        dado = self.ler("consent-v4.json")
        if dado is None:
            return None
        try:
            consentimento = json.loads(dado.decode("utf-8"))
            srg.check_consent_v4(consentimento)
        except (ValueError, PersistenceBlocked):
            return None
        return consentimento


class FilaEntrada:
    """Adaptador de `entrada`: grava recibo e rejeitada (arquivo novo, idempotente) e remove a entrada aceita ou rejeitada."""

    def __init__(self, api, repo):
        self.api, self.repo = api, repo
        self._base = f"/repos/{repo}/contents/"

    def escrever(self, caminho, dados):
        try:
            self.api.chamar("PUT", self._base + caminho, {"message": "registro do fluxo", "content": _b64(dados)})
        except ApiError as erro:
            if erro.status not in (409, 422):
                raise
            _, obj = self.api.chamar("GET", self._base + caminho)  # já existe: aceito só se for idêntico
            if _decodifica(obj["content"]) != dados:
                raise

    def remover(self, caminho):
        try:
            _, obj = self.api.chamar("GET", self._base + caminho)
        except ApiError as erro:
            if erro.status == 404:
                return
            raise
        self.api.chamar("DELETE", self._base + caminho, {"message": "entrada processada", "sha": obj["sha"]})


def montar_contexto(*, dados, agora, alvo, validador_dir, validador_sha_fixado, execucao):
    """Contexto do portão com o que o runner injeta; `escritas_habilitadas` é lido do settings.json do validador."""
    texto = (Path(validador_dir) / "settings.json").read_text(encoding="utf-8")
    return {"agora": agora, "alvo": alvo, "configurado": DADOS_REPO, "leitor_visibilidade": dados.visibilidade,
            "leitor_consentimento": dados.consentimento, "escritas_habilitadas": ler_flag(texto), "repositorio": dados,
            "topicos": topic_rows(Path(validador_dir)), "validador_sha": ler_head_sha(validador_dir),
            "validador_sha_fixado": validador_sha_fixado, "execucao": execucao}


def executar(entradas, contexto, fila):
    """Processa as entradas EM SÉRIE e em ordem de nome. Devolve um resumo só com contagens, códigos e ids.

    Com a flag desligada não toca em NADA (nenhuma leitura, nenhuma escrita). Falha ao registrar recibo ou rejeição deixa a
    entrada na fila, para a próxima execução repetir de forma idempotente."""
    resumo = {"flag": contexto.get("escritas_habilitadas") is True, "itens": [], "falhas_de_registro": 0}
    if not resumo["flag"]:
        resumo["estado"] = "FLAG_DESLIGADA"
        resumo["mantidas"] = len(list(entradas))
        return resumo
    for nome, bruto in sorted(entradas, key=lambda par: str(par[0])):
        if not (isinstance(nome, str) and _NOME.fullmatch(nome) and ".." not in nome):
            resumo["itens"].append({"entrada_id": "invalido", "status": "IGNORADA", "codigo": "NOME_INVALIDO"})
            continue
        res = pg.promover(bruto, dict(contexto, entrada_id=nome))
        item = {"entrada_id": nome, "status": res["status"], "codigo": res.get("codigo", "OK")}
        try:
            if res["status"] == "COMMITTED":
                fila.escrever("recibos/" + nome, pg.canonical(res["recibo"]))
                fila.remover(f"{FILA_DIR}/{nome}")
            elif res["status"] == "DENIED":
                fila.escrever("rejeitadas/" + nome, pg.canonical(res["rejeicao"]))
                fila.remover(f"{FILA_DIR}/{nome}")
            # NOT_IMPLEMENTED e PENDENTE ficam na fila
        except Exception:
            resumo["falhas_de_registro"] += 1
            item["registro"] = "FALHOU"
        resumo["itens"].append(item)
    resumo["estado"] = "PROCESSADO"
    return resumo


def ler_fila(diretorio):
    """Entradas da fila no checkout: só arquivos comuns (sem link simbólico), nome seguro, com teto de quantidade."""
    saida = []
    if not Path(diretorio).is_dir():  # um push que só tocou a outra fila: pasta ausente é fila vazia
        return saida
    for caminho in sorted(Path(diretorio).iterdir()):
        if caminho.is_symlink() or not caminho.is_file():
            continue
        saida.append((caminho.name, caminho.read_bytes()))
        if len(saida) > 500:
            raise ValueError("fila grande demais")
    return saida


def transporte_urllib(metodo, url, cabecalhos, corpo, tempo):  # pragma: no cover - rede real, só no CLI
    import urllib.error
    import urllib.request

    class SemRedirecionamento(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    if not url.startswith(API + "/"):
        raise ValueError("host fora da API do GitHub")
    pedido = urllib.request.Request(url, data=corpo, method=metodo, headers=cabecalhos)
    abridor = urllib.request.build_opener(SemRedirecionamento)
    try:
        with abridor.open(pedido, timeout=tempo) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read()


def main(argv=None, transporte=None, ambiente=None, agora=None):
    p = argparse.ArgumentParser(description="Promove entradas da fila de `entrada` para o histórico privado (runner).")
    p.add_argument("--fila", required=True)
    p.add_argument("--execucao", required=True)
    p.add_argument("--validador-sha", required=True)
    p.add_argument("--entrada-repo", required=True)
    p.add_argument("--dados-repo", default=DADOS_REPO)
    p.add_argument("--validador-dir", default=str(ROOT))
    a = p.parse_args(argv)
    ambiente = os.environ if ambiente is None else ambiente
    validador = Path(a.validador_dir)
    flag = ler_flag((validador / "settings.json").read_text(encoding="utf-8"))
    if not flag:  # nenhuma rede, nenhum token lido, nada gravado
        n = len(ler_fila(a.fila)) if Path(a.fila).is_dir() else 0
        print(json.dumps({"estado": "FLAG_DESLIGADA", "mantidas": n, "flag": False}))
        return 0
    if not _REPO.fullmatch(a.entrada_repo or ""):
        print(json.dumps({"estado": "ERRO", "codigo": "ENTRADA_REPO_INVALIDO"}))
        return 1
    try:
        t = transporte or transporte_urllib
        dados = RepositorioDados(GitHubApi(ambiente.get("DADOS_TOKEN", ""), t, rotulo="dados"), a.dados_repo)
        fila = FilaEntrada(GitHubApi(ambiente.get("GH_TOKEN", ""), t, rotulo="entrada"), a.entrada_repo)
        contexto = montar_contexto(dados=dados, agora=agora or datetime.now(timezone.utc), alvo=a.dados_repo,
                                   validador_dir=validador, validador_sha_fixado=a.validador_sha, execucao=a.execucao)
        resumo = executar(ler_fila(a.fila), contexto, fila)
    except Exception as erro:  # nunca imprime a exceção (poderia carregar contexto): só a classe e, se for uma das nossas, o detalhe
        saida = {"estado": "ERRO", "codigo": type(erro).__name__}
        if isinstance(erro, ValueError) and DETALHE_SEGURO.fullmatch(str(erro)):
            saida["detalhe"] = str(erro)
        print(json.dumps(saida))
        return 1
    print(json.dumps(resumo, ensure_ascii=False))
    return 1 if resumo["falhas_de_registro"] else 0


if __name__ == "__main__":
    sys.exit(main())
