"""Guarda offline da leitura direta das plataformas (L1; S9-R2 a R5, R8, R9). Somente leitura, sem rede e sem navegador.

Este módulo **decide**; quem navega (a Zapia, fora do modelo) pergunta antes de cada ação e obedece. Ele não abre página,
não guarda cookie nem token e não grava nada. Por decisão do proprietário (21/11/2026), a Zapia está **liberada** a acessar
TEC Concursos e Qconcursos livremente: `PADRAO` habilita as duas plataformas, sem condição de termos, sem decisão
adicional e sem cota de páginas, de intervalo ou de sessões. Permanecem só as travas de segurança: somente leitura,
domínio exato e página tratada como **dado não confiável**.

Limites: heurístico no filtro de instrução e de bloqueio; a trava só vale para quem chamar por aqui (não impede um
navegador que ignore o guarda); páginas e formatos reais das plataformas **não** são supostos (não há parser aqui).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

try:
    import agent_commands
    import gp1_ingestion
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands, gp1_ingestion

# Domínios exatos (S9-R2). Subdomínio ou sufixo parecido NÃO vale.
HOSTS = {
    "tec": frozenset({"tecconcursos.com.br", "www.tecconcursos.com.br"}),
    "qconcursos": frozenset({"qconcursos.com", "www.qconcursos.com"}),
}
FUSO = timezone(timedelta(hours=-4))  # dia da sessão: horário de Mato Grosso do Sul

ACOES_LEITURA = frozenset({"navegar", "ler_texto"})
ACOES_ESCRITA = frozenset({
    "clicar", "digitar", "preencher", "enviar_formulario", "submeter", "resolver_questao", "responder_questao",
    "criar_caderno", "editar_caderno", "mover_caderno", "apagar_caderno", "alterar_configuracao", "alterar_pontuacao",
    "baixar", "download", "exportar", "upload", "executar_codigo", "avaliar_js", "post", "put", "patch", "delete",
})
# Segmentos de caminho ou valores de consulta que indicam efeito (GET com efeito é defesa em profundidade).
SEGMENTOS_COM_EFEITO = frozenset({
    "logout", "sair", "excluir", "apagar", "remover", "deletar", "criar", "novo", "nova", "editar", "salvar",
    "resolver", "responder", "enviar", "configuracoes", "configuracao", "conta", "perfil", "assinatura", "checkout",
    "pagamento", "senha", "exportar", "download", "baixar",
})
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}")
_CONTROLE = re.compile(r"[\x00-\x20\x7f\\]")
_INSTRUCAO = re.compile(
    r"ignor\w* (?:(?:all|todas?|as|os|the|your|suas?|seus?) )*(?:previous|prior|anteriores?|instruc\w*|instructions?|regras|rules)"
    r"|disregard|you are now|voce (?:e|eh) agora|voce agora (?:e|eh)|a partir de agora|system prompt|prompt do sistema"
    r"|(?:execute|run|rode|envie|send|post|grave|write|delete|apague|exclua)\b.{0,40}"
    r"(?:comando|command|token|senha|password|cookie|repositorio|repository|http|curl|rm )"
    r"|nao (?:siga|obede\w+)|do not follow|novas? instruc\w*|new instructions?|override|jailbreak", re.S)
_BLOQUEIO = re.compile(
    r"captcha|nao sou (?:um )?robo|i am not a robot|verifique (?:que )?(?:voce )?(?:e|eh) humano|verify you are human"
    r"|acesso (?:foi )?(?:temporariamente )?bloqueado|bloquead\w+ temporariamente|muitas (?:requisicoes|solicitacoes)"
    r"|too many requests|rate limit|atividade suspeita|suspicious activity|uso anomalo|padr\w+ de uso"
    r"|novo dispositivo|new device|segundo fator|verificacao em duas etapas|two-factor|conta (?:suspensa|bloqueada)"
    r"|account (?:suspended|blocked)|unusual traffic")
LIMITE_NUM = 100_000
CHAVES_RELATORIO = frozenset({
    "event_id", "attempt_id", "recommendation_id", "recorded_at", "attempt_at", "source_ref", "platform_notebook_id",
    "reported_answered", "reported_unanswered", "correct", "incorrect", "topic_results",
})
CHAVES_SAIDA = CHAVES_RELATORIO | {"plataforma", "origem", "lida_em"}
CHAVES_TOPICO = frozenset({"topic_id", "attempted", "correct"})
ORIGENS = frozenset({"leitura_direta", "exportacao"})
_DATA_ISO = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2}))?")


@dataclass(frozen=True)
class Config:
    """Plataformas liberadas por padrão (decisão do proprietário de 21/11/2026); nada suspenso."""

    habilitadas: frozenset = frozenset({"tec", "qconcursos"})
    suspensas: frozenset = frozenset()  # captcha ou bloqueio da própria plataforma suspende a sessão


PADRAO = Config()


@dataclass(frozen=True)
class Decisao:
    ok: bool
    codigo: str  # só código; nunca eco de URL, texto de página ou segredo
    avisar_proprietario: bool = False
    repetir: bool = False  # nunca repetir sozinho


def _sim(codigo="OK"):
    return Decisao(True, codigo)


def _nao(codigo, avisar=False):
    return Decisao(False, codigo, avisar_proprietario=avisar)


def _normaliza(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[_\-.\s]+", " ", base)


def classificar_texto(texto: str):
    """Devolve o código de recusa para texto de página/saída ou None. Heurístico (S9-R5)."""
    if not isinstance(texto, str):
        return "TIPO_INVALIDO"
    motivo = agent_commands.scan_text(texto, html=True)
    if motivo:
        return motivo
    if _INSTRUCAO.search(_normaliza(texto)):
        return "INSTRUCAO_EMBUTIDA"
    return None


def detectar_bloqueio(texto: str) -> bool:
    return isinstance(texto, str) and bool(_BLOQUEIO.search(_normaliza(texto)))


def _plataforma_da_url(url):
    """Devolve (plataforma, codigo_de_recusa). Esquema, host e forma da URL (S9-R2)."""
    if not isinstance(url, str) or not url or len(url) > 2048 or _CONTROLE.search(url):
        return None, "URL_INVALIDA"
    try:
        partes = urlsplit(url)
        porta = partes.port
    except ValueError:
        return None, "URL_INVALIDA"
    if partes.scheme.lower() != "https":
        return None, "ESQUEMA_PROIBIDO"  # inclui file://, http://, data:, javascript:
    if partes.username is not None or partes.password is not None:
        return None, "URL_COM_CREDENCIAL"
    if porta not in (None, 443):
        return None, "PORTA_PROIBIDA"
    host = partes.hostname or ""
    if not host.isascii():
        return None, "DOMINIO_FORA_DA_LISTA"
    for nome, hosts in HOSTS.items():
        if host in hosts:
            return nome, None
    return None, "DOMINIO_FORA_DA_LISTA"


def _tem_efeito(url: str) -> bool:
    partes = urlsplit(url)
    pedacos = [p for p in re.split(r"[/;]", _normaliza(partes.path)) if p]
    for par in re.split(r"[&;]", partes.query):
        pedacos += [p for p in re.split(r"[=\s]", _normaliza(par)) if p]
    return any(token in SEGMENTOS_COM_EFEITO for token in pedacos)


def _dia(agora: datetime) -> str:
    return agora.astimezone(FUSO).date().isoformat()


@dataclass
class Guarda:
    """Uma instância por processo de leitura. `relogio()` devolve datetime com fuso; `sessoes_anteriores` são datas ISO."""

    config: Config = PADRAO
    relogio: object = None
    sessoes_anteriores: tuple = ()
    _plataforma: str | None = field(default=None, init=False)
    _paginas: int = field(default=0, init=False)
    _ultima: datetime | None = field(default=None, init=False)
    _em_voo: bool = field(default=False, init=False)
    _suspensas: set = field(default_factory=set, init=False)
    _dias: list = field(default_factory=list, init=False)

    def __post_init__(self):
        if not callable(self.relogio):
            raise ValueError("relogio deve ser injetado (callable que devolve datetime com fuso)")
        self._dias = list(self.sessoes_anteriores)
        self._suspensas = set(self.config.suspensas)

    # -- consulta -------------------------------------------------------------------------------------------------
    @property
    def sessao_ativa(self) -> bool:
        return self._plataforma is not None

    @property
    def paginas_lidas(self) -> int:
        return self._paginas

    def sessoes_registradas(self) -> tuple:
        """Datas das sessões iniciadas, para o chamador persistir fora daqui (este módulo não grava)."""
        return tuple(self._dias)

    def plataformas_suspensas(self) -> frozenset:
        return frozenset(self._suspensas)

    def _agora(self):
        agora = self.relogio()
        if not isinstance(agora, datetime) or agora.utcoffset() is None:
            return None
        return agora

    # -- habilitação (S9-R8, R9) ------------------------------------------------------------------------------------
    def _habilitada(self, plataforma: str):
        if plataforma in self._suspensas:
            return "PLATAFORMA_SUSPENSA"
        if plataforma not in self.config.habilitadas:
            return "PLATAFORMA_DESABILITADA"
        return None

    # -- sessão ---------------------------------------------------------------------------------------------------
    def iniciar_sessao(self, plataforma) -> Decisao:
        if plataforma not in HOSTS:
            return _nao("PLATAFORMA_DESCONHECIDA")
        if self._plataforma is not None:
            return _nao("SESSAO_EM_ANDAMENTO")  # sem paralelismo
        motivo = self._habilitada(plataforma)
        if motivo:
            return _nao(motivo)
        agora = self._agora()
        if agora is None:
            return _nao("RELOGIO_INVALIDO")
        self._dias.append(_dia(agora))
        self._plataforma, self._paginas, self._ultima, self._em_voo = plataforma, 0, None, False
        return _sim()

    def encerrar_sessao(self) -> Decisao:
        self._plataforma, self._em_voo = None, False
        return _sim()

    # -- ações ----------------------------------------------------------------------------------------------------
    def autorizar(self, acao) -> Decisao:
        """Pergunta ANTES de cada ação. Lista fechada: só `navegar` (GET) e `ler_texto`; o resto é recusado."""
        if not isinstance(acao, dict) or not isinstance(acao.get("tipo"), str):
            return _nao("ACAO_INVALIDA")
        tipo = acao["tipo"].strip().lower()
        if tipo in ACOES_ESCRITA or str(acao.get("metodo", "GET")).upper() != "GET":
            return _nao("OPERACAO_ESCRITA")
        if tipo not in ACOES_LEITURA:
            return _nao("OPERACAO_DESCONHECIDA")
        if self._plataforma is None:
            return _nao("SEM_SESSAO")
        motivo = self._habilitada(self._plataforma)  # a suspensão vale no meio da sessão
        if motivo:
            return _nao(motivo)
        if tipo == "ler_texto":
            return _sim() if not self._em_voo else _nao("PARALELISMO")
        plataforma, recusa = _plataforma_da_url(acao.get("url"))
        if recusa:
            return _nao(recusa)
        if plataforma != self._plataforma:
            return _nao("PLATAFORMA_DIVERGENTE")
        if _tem_efeito(acao["url"]):
            return _nao("URL_COM_EFEITO")
        if self._em_voo:
            return _nao("PARALELISMO")
        agora = self._agora()
        if agora is None:
            return _nao("RELOGIO_INVALIDO")
        if self._ultima is not None and (agora - self._ultima).total_seconds() < 0:
            return _nao("RELOGIO_INVALIDO")
        self._paginas += 1
        self._ultima, self._em_voo = agora, True
        return _sim()

    def concluir_pagina(self, status_http, texto) -> Decisao:
        """Registra o resultado da página. Bloqueio, captcha, limitação ou resposta inesperada ENCERRA a sessão,
        sem repetição, e pede aviso ao proprietário. O texto é só inspecionado; nunca devolvido."""
        self._em_voo = False
        if self._plataforma is None:
            return _nao("SEM_SESSAO")
        if status_http in (403, 429) or detectar_bloqueio(texto):
            self._suspensas.add(self._plataforma)  
            self.encerrar_sessao()
            return _nao("BLOQUEIO_DETECTADO", avisar=True)
        if status_http != 200:
            self.encerrar_sessao()
            return _nao("PAGINA_INESPERADA", avisar=True)
        return _sim()


# -- saída mínima (S9-R5) -----------------------------------------------------------------------------------------------
def _inteiro(valor):
    return type(valor) is int and 0 <= valor <= LIMITE_NUM


def _id_ok(valor):
    return isinstance(valor, str) and _ID.fullmatch(valor) is not None


def saida_minima(leitura, convencao=None):
    """Valida a leitura de uma plataforma contra o contrato mínimo e devolve (decisao, evento_pronto_ou_None).

    Só passa o que o contrato de ingestão (`gp1_ingestion`) conhece, em campos fechados: identificadores curtos
    (sem espaço), contagens inteiras, datas ISO. Qualquer campo a mais (enunciado, comentário, conta, HTML, cookie,
    token) ou valor suspeito recusa a leitura INTEIRA: nada é limpo em silêncio. A convenção de contagem vem do
    chamador confiável, nunca da página. Não gera identidades nem persiste (`canonical_event_created` segue falso)."""
    if not isinstance(leitura, dict):
        return _nao("SAIDA_INVALIDA"), None
    for chave in leitura:
        if not isinstance(chave, str):
            return _nao("SAIDA_INVALIDA"), None
        if chave.strip().lower() in agent_commands.load_schema()["forbidden_param_keys"]:
            return _nao("CAMPO_PROIBIDO"), None
    if set(leitura) - CHAVES_SAIDA:
        return _nao("CAMPO_FORA_DO_CONTRATO"), None
    if leitura.get("plataforma") not in HOSTS or leitura.get("origem") not in ORIGENS:
        return _nao("PLATAFORMA_OU_ORIGEM_INVALIDA"), None
    if not isinstance(leitura.get("lida_em"), str) or not _DATA_ISO.fullmatch(leitura["lida_em"]):
        return _nao("DATA_INVALIDA"), None
    relatorio = {k: v for k, v in leitura.items() if k in CHAVES_RELATORIO}
    for chave in ("event_id", "attempt_id", "recommendation_id", "source_ref"):
        if not _id_ok(relatorio.get(chave)):
            return _nao("CAMPO_INVALIDO"), None
    for chave in ("platform_notebook_id",):
        if relatorio.get(chave) is not None and not _id_ok(relatorio[chave]):
            return _nao("CAMPO_INVALIDO"), None
    for chave in ("recorded_at", "attempt_at"):
        if relatorio.get(chave) is not None and (
                not isinstance(relatorio[chave], str) or not _DATA_ISO.fullmatch(relatorio[chave])):
            return _nao("DATA_INVALIDA"), None
    for chave in ("reported_answered", "reported_unanswered", "correct", "incorrect"):
        if not _inteiro(relatorio.get(chave)):
            return _nao("CONTAGEM_INVALIDA"), None
    topicos = relatorio.get("topic_results", [])
    if not isinstance(topicos, list) or len(topicos) > 200:
        return _nao("CAMPO_INVALIDO"), None
    for item in topicos:
        if not isinstance(item, dict) or set(item) - CHAVES_TOPICO:
            return _nao("CAMPO_FORA_DO_CONTRATO"), None
        if not _id_ok(item.get("topic_id")) or not _inteiro(item.get("attempted")) or not _inteiro(item.get("correct")):
            return _nao("CAMPO_INVALIDO"), None
    # mesmo o que passou pela forma é conferido contra segredo, dado pessoal, HTML e instrução embutida
    textos = [v for v in relatorio.values() if isinstance(v, str)] + [i["topic_id"] for i in topicos]
    for texto in textos:
        motivo = classificar_texto(texto)
        if motivo:
            return _nao(motivo), None
    try:
        resultado = gp1_ingestion.normalize_external_report(relatorio, convencao)
    except ValueError:
        return _nao("INGESTAO_RECUSADA"), None
    if resultado["decision"] != "normalized":
        return _nao("CONVENCAO_PENDENTE"), None
    evento = dict(resultado["event"])
    evento["source_kind"] = "unknown"  # o esquema não tem "leitura direta"; não inventar valor novo
    return _sim("SAIDA_ACEITA"), evento
