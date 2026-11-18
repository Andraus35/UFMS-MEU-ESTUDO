"""Conversor offline da entrega de desempenho do TEC pela Zapia (L2; S9-R6, R7; emenda E2). Falha fechada.

Recebe a ENTREGA já lida como JSON (um objeto Python) e devolve um RETRATO validado EM MEMÓRIA: nada é gravado, nenhum evento é
criado, nenhum arquivo é lido ou escrito, não há rede. O arquivo bruto nunca entra no repositório (S9-R6); este módulo só vê o
objeto que o chamador (a sessão do Tutor ou do Coach, a partir da fila `entrada`) já carregou.

O que o contrato exige (ver `docs/governanca/CONTRATO_ENTREGA_DESEMPENHO_TEC_20261118.md`): `linhas` com as colunas do relatório
do TEC (código, profundidade, título, questões, acertos, erros, peso; os percentuais do TEC são opcionais e só informativos),
`recorte` (período e filtros), `pontuacao` declarada, `gerado_em`, `totais_declarados` e `procedimento` (relato de como a Zapia
extraiu o dado; é AUTORRELATO: o módulo confere a forma e nunca o prova). Recusa análise de conteúdo (D-10, D-23), texto livre
fora dos campos previstos, instrução embutida, dado pessoal e segredo. **Recalcula** o derivado (taxa de acerto bruto, resíduo
dos pais) e confere os totais declarados contra as linhas.

Decisões do proprietário (18/11/2026): a pontuação (normal ou líquida) é DECLARADA por exportação pelo Tutor ou pelo Coach e
NUNCA inferida do arquivo; sem declaração a decisão é `pending_clarification`, sem retrato.

Limites: heurístico no filtro de texto (reaproveita o da L1); não prova que a Zapia extraiu o que diz, nem que os números são os
do TEC (a conferência de totais pega erro de transcrição, não falsificação); o formato real que a Zapia entregará não foi visto
(a Z1 espera resposta); a hierarquia aceita pai com soma dos filhos MENOR (resíduo no pai), nunca MAIOR.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

try:
    import agent_commands
    import notebook_prompt_validator
    import platform_read_guard
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands, notebook_prompt_validator, platform_read_guard

VERSAO = "1.0"
MAX_LINHAS = 5000
MAX_CONTAGEM = 10_000_000
MAX_TITULO = 200
MAX_TEXTO = 300
MAX_ITENS = 30
CODIGO = re.compile(r"\d{1,3}(?:\.\d{1,3}){0,6}")
SOLICITANTES = frozenset({"tutor", "coach", "proprietario"})
DECLARANTES = frozenset({"tutor", "coach", "proprietario"})
PONTUACOES = frozenset({"normal", "liquida"})
PERIODOS = frozenset({"desde_o_inicio", "intervalo", "nao_declarado"})
FILTROS = ("materia", "banca", "pasta", "dificuldade")
VALORES_FILTRO = frozenset({"todos", "selecao", "nao_declarado"})
CHEGADA = frozenset({"baixou_direto", "por_email_lido_pela_zapia", "encaminhado_pelo_proprietario", "nao_obteve", "outro"})
EXIBIR = frozenset({"apenas_resolvidas", "todas", "nao_declarado"})
# o que NÃO entra: análise é do Tutor e do Coach (D-10, D-23); questão e comentário são texto de terceiros
CHAVES_DE_ANALISE = frozenset({"analise", "analises", "achados", "sinais", "sinais_principais", "classificacao", "interpretacao",
                               "recomendacao", "recomendacoes", "resumo", "conclusao", "comentario", "comentarios", "enunciado",
                               "questao", "questoes_texto", "gabarito", "insights", "diagnostico"})
RAIZ = frozenset({"schema_version", "plataforma", "solicitante", "gerado_em", "recorte", "pontuacao", "exibir", "linhas",
                  "totais_declarados", "procedimento"})
LINHA = frozenset({"codigo", "profundidade", "titulo", "questoes", "acertos", "erros", "peso", "acertos_pct_tec", "erros_pct_tec"})
RECORTE = frozenset({"periodo", "filtros"})
PERIODO = frozenset({"tipo", "inicio", "fim"})
PONTUACAO = frozenset({"valor", "declarado_por"})
TOTAIS = frozenset({"questoes", "acertos", "erros", "materias", "linhas"})
PROCEDIMENTO = frozenset({"telas", "passos", "filtros_visiveis", "chaves_visiveis", "hora", "avisos_do_tec", "parou_por_aviso",
                          "conferencias", "como_chegou_o_arquivo"})
_DATA = re.compile(r"\d{4}-\d{2}-\d{2}")


class Recusa(Exception):
    """Recusa da entrega INTEIRA: só código e, quando há, o número da linha (nunca o texto)."""

    def __init__(self, codigo, linha=None):
        super().__init__(codigo)
        self.codigo, self.linha = codigo, linha


def _recusa(codigo, linha=None):
    raise Recusa(codigo, linha)


def _inteiro(v, codigo="CONTAGEM_INVALIDA", linha=None, minimo=0):
    if type(v) is not int or v < minimo or v > MAX_CONTAGEM:
        _recusa(codigo, linha)
    return v


def _texto(v, limite, codigo, linha=None):
    if not isinstance(v, str) or not v.strip() or v != v.strip() or len(v) > limite:
        _recusa(codigo, linha)
    if any(ord(c) < 32 or ord(c) == 127 or 0x200B <= ord(c) <= 0x200F or 0x202A <= ord(c) <= 0x202E or 0x2066 <= ord(c) <= 0x2069
           or ord(c) == 0xFEFF for c in v):
        _recusa("CARACTERE_INVISIVEL", linha)
    return v


def _limpo(texto, codigo, linha=None):
    """Segredo, dado pessoal, HTML e instrução embutida (filtro heurístico da L1)."""
    if (platform_read_guard.classificar_texto(texto) or platform_read_guard.classificar_texto(texto.replace(".", " "))
            or notebook_prompt_validator.instrucao_embutida(texto)):
        _recusa(codigo, linha)


_PROIBIDAS = None


def _proibidas():
    global _PROIBIDAS
    if _PROIBIDAS is None:
        _PROIBIDAS = frozenset(x.lower() for x in agent_commands.load_schema()["forbidden_param_keys"])
    return _PROIBIDAS


def _chaves(obj, permitidas, codigo, linha=None):
    if not isinstance(obj, dict):
        _recusa(codigo, linha)
    for k in obj:
        if not isinstance(k, str):
            _recusa(codigo, linha)
        if k.strip().lower() in CHAVES_DE_ANALISE:
            _recusa("ANALISE_NAO_ACEITA", linha)
        if k.strip().lower() in _proibidas():
            _recusa("CAMPO_PROIBIDO", linha)
    if set(obj) - permitidas:
        _recusa("CAMPO_FORA_DO_CONTRATO", linha)


def _data(v, codigo):
    if not isinstance(v, str) or not _DATA.fullmatch(v):
        _recusa(codigo)
    try:
        return date.fromisoformat(v)
    except ValueError:
        _recusa(codigo)


def _momento(v, codigo):
    if not isinstance(v, str):
        _recusa(codigo)
    try:
        t = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        _recusa(codigo)
    if t.utcoffset() is None:
        _recusa(codigo)
    return t


def _recorte(r):
    _chaves(r, RECORTE, "RECORTE_INVALIDO")
    if set(r) != RECORTE:
        _recusa("RECORTE_INVALIDO")
    p = r["periodo"]
    _chaves(p, PERIODO, "RECORTE_INVALIDO")
    if p.get("tipo") not in PERIODOS:
        _recusa("RECORTE_INVALIDO")
    if p["tipo"] == "intervalo":
        if set(p) != PERIODO or _data(p["inicio"], "RECORTE_INVALIDO") > _data(p["fim"], "RECORTE_INVALIDO"):
            _recusa("RECORTE_INVALIDO")
    elif set(p) != {"tipo"}:
        _recusa("RECORTE_INVALIDO")
    f = r["filtros"]
    _chaves(f, frozenset(FILTROS), "RECORTE_INVALIDO")
    if set(f) != set(FILTROS) or any(f[k] not in VALORES_FILTRO for k in FILTROS):
        _recusa("RECORTE_INVALIDO")
    return {"periodo": dict(p), "filtros": dict(f)}


def _lista(v, codigo, obrigatoria=False):
    if not isinstance(v, list) or len(v) > MAX_ITENS or (obrigatoria and not v):
        _recusa(codigo)
    for item in v:
        _limpo(_texto(item, MAX_TEXTO, codigo), "PROCEDIMENTO_CONTEUDO_RECUSADO")
    return list(v)


def _procedimento(p, agora):
    _chaves(p, PROCEDIMENTO, "PROCEDIMENTO_INVALIDO")
    if set(p) != PROCEDIMENTO:
        _recusa("PROCEDIMENTO_INVALIDO")
    out = {"telas": _lista(p["telas"], "PROCEDIMENTO_INVALIDO", True), "passos": _lista(p["passos"], "PROCEDIMENTO_INVALIDO", True),
           "filtros_visiveis": _lista(p["filtros_visiveis"], "PROCEDIMENTO_INVALIDO"),
           "chaves_visiveis": _lista(p["chaves_visiveis"], "PROCEDIMENTO_INVALIDO"),
           "avisos_do_tec": _lista(p["avisos_do_tec"], "PROCEDIMENTO_INVALIDO"),
           "conferencias": _lista(p["conferencias"], "PROCEDIMENTO_INVALIDO")}
    if _momento(p["hora"], "PROCEDIMENTO_INVALIDO") > agora + timedelta(minutes=5):
        _recusa("DATA_NO_FUTURO")
    if type(p["parou_por_aviso"]) is not bool or p["como_chegou_o_arquivo"] not in CHEGADA:
        _recusa("PROCEDIMENTO_INVALIDO")
    if out["avisos_do_tec"] and not p["parou_por_aviso"]:
        _recusa("AVISO_SEM_PARADA")  # S5-R13(f): ao primeiro aviso a Zapia para
    if p["parou_por_aviso"] or p["como_chegou_o_arquivo"] == "nao_obteve":
        _recusa("ENTREGA_INTERROMPIDA")
    out.update({"hora": p["hora"], "parou_por_aviso": False, "como_chegou_o_arquivo": p["como_chegou_o_arquivo"]})
    return out


def _linha(n, raw):
    _chaves(raw, LINHA, "LINHA_INVALIDA", n)
    obrigatorias = {"codigo", "profundidade", "titulo", "questoes", "acertos", "erros", "peso"}
    if not obrigatorias <= set(raw):
        _recusa("LINHA_INVALIDA", n)
    codigo = raw["codigo"]
    if codigo is not None and (not isinstance(codigo, str) or not CODIGO.fullmatch(codigo)):
        _recusa("CODIGO_INVALIDO", n)
    esperado = 1 if codigo is None else len(codigo.split(".")) + 1  # matéria = 1; "01" = 2; "01.02" = 3 (como a coluna "Prof." do TEC)
    if type(raw["profundidade"]) is not int or raw["profundidade"] != esperado:
        _recusa("PROFUNDIDADE_INCOERENTE", n)
    titulo = _texto(raw["titulo"], MAX_TITULO, "TITULO_INVALIDO", n)
    _limpo(titulo, "TITULO_RECUSADO", n)
    q, a, e = (_inteiro(raw[k], linha=n) for k in ("questoes", "acertos", "erros"))
    _inteiro(raw["peso"], linha=n)
    if a + e != q:
        _recusa("CONTAGEM_INCOERENTE", n)
    pct = {}
    for k in ("acertos_pct_tec", "erros_pct_tec"):
        if k in raw:
            if type(raw[k]) is not int or not 0 <= raw[k] <= 100:
                _recusa("PERCENTUAL_INVALIDO", n)
            pct[k] = raw[k]
    return {"codigo": codigo, "profundidade": esperado, "titulo": titulo, "questoes": q, "acertos": a, "erros": e,
            "peso": raw["peso"], **pct}


def _hierarquia(linhas):
    """Confere a árvore em profundidade: cada código tem o pai imediato antes dele, sem pular nível nem repetir código dentro da
    matéria. Devolve `{índice do pai: [índices dos filhos]}`. A soma dos filhos pode ser MENOR que o pai (resíduo), nunca MAIOR."""
    pilha = []  # (código ou None para a matéria, nº de segmentos, índice)
    filhos, vistos, materia = {}, set(), -1
    for n, l in enumerate(linhas, 1):
        cod = l["codigo"]
        if cod is None:
            materia, pilha = n - 1, [(None, 0, n - 1)]
            continue
        if not pilha:
            _recusa("FILHO_SEM_PAI", n)
        d = len(cod.split("."))
        if (materia, cod) in vistos:
            _recusa("CODIGO_REPETIDO", n)
        vistos.add((materia, cod))
        while pilha and pilha[-1][1] >= d:
            pilha.pop()
        pai_cod = ".".join(cod.split(".")[:-1]) or None
        if not pilha or pilha[-1][1] != d - 1 or pilha[-1][0] != pai_cod:
            _recusa("FILHO_SEM_PAI", n)
        filhos.setdefault(pilha[-1][2], []).append(n - 1)
        pilha.append((cod, d, n - 1))
    for pai_i, lista in filhos.items():
        for campo in ("questoes", "acertos", "erros"):
            if sum(linhas[i][campo] for i in lista) > linhas[pai_i][campo]:
                _recusa("SOMA_DOS_FILHOS_MAIOR_QUE_O_PAI", pai_i + 1)
    return filhos


def _pct(num, den):
    return None if den == 0 else round(100.0 * num / den, 1)


def converter(entrega, agora=None):
    """Valida a entrega e devolve `{"decisao": ..., ...}`. Nunca levanta: recusa vira `{"decisao": "recusada", "codigo", "linha"}`.

    `agora` (datetime com fuso) é injetado nos testes; por padrão é o relógio UTC. Decisões: `validado` (com `retrato`),
    `pending_clarification` (sem pontuação declarada, sem retrato) e `recusada`."""
    agora = agora or datetime.now(timezone.utc)
    try:
        return _converter(entrega, agora)
    except Recusa as r:
        return {"decisao": "recusada", "codigo": r.codigo, "linha": r.linha, "retrato": None}
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError):
        return {"decisao": "recusada", "codigo": "ENTREGA_INVALIDA", "linha": None, "retrato": None}


def _converter(e, agora):
    _chaves(e, RAIZ, "ENTREGA_INVALIDA")
    faltam = RAIZ - set(e) - {"exibir"}
    if faltam:
        if faltam == {"pontuacao"}:
            # só a pontuação falta: ainda confere o resto para dizer o que mais está errado, mas não devolve retrato
            e = {**e, "pontuacao": None}
        else:
            _recusa("ENTREGA_INVALIDA")
    if e["schema_version"] != VERSAO or e["plataforma"] != "tec":
        _recusa("VERSAO_OU_PLATAFORMA_INVALIDA")
    if e["solicitante"] not in SOLICITANTES:
        _recusa("SOLICITANTE_INVALIDO")
    gerado = _momento(e["gerado_em"], "DATA_INVALIDA")
    if gerado > agora + timedelta(minutes=5):
        _recusa("DATA_NO_FUTURO")
    recorte = _recorte(e["recorte"])
    exibir = e.get("exibir", "nao_declarado")
    if exibir not in EXIBIR:
        _recusa("EXIBIR_INVALIDO")
    procedimento = _procedimento(e["procedimento"], agora)
    linhas_brutas = e["linhas"]
    if not isinstance(linhas_brutas, list) or not linhas_brutas or len(linhas_brutas) > MAX_LINHAS:
        _recusa("LINHAS_INVALIDAS")
    linhas = [_linha(n, raw) for n, raw in enumerate(linhas_brutas, 1)]
    if linhas[0]["codigo"] is not None:
        _recusa("FILHO_SEM_PAI", 1)
    filhos = _hierarquia(linhas)
    materias = [l for l in linhas if l["codigo"] is None]
    tot = {"questoes": sum(m["questoes"] for m in materias), "acertos": sum(m["acertos"] for m in materias),
           "erros": sum(m["erros"] for m in materias), "materias": len(materias), "linhas": len(linhas)}
    d = e["totais_declarados"]
    _chaves(d, TOTAIS, "TOTAIS_INVALIDOS")
    if set(d) != TOTAIS or any(type(d[k]) is not int for k in TOTAIS):
        _recusa("TOTAIS_INVALIDOS")
    if any(d[k] != tot[k] for k in TOTAIS):
        _recusa("TOTAL_DIVERGENTE")
    p = e["pontuacao"]
    if p is None:
        return {"decisao": "pending_clarification", "codigo": "PONTUACAO_NAO_DECLARADA", "linha": None, "retrato": None}
    _chaves(p, PONTUACAO, "PONTUACAO_INVALIDA")
    if set(p) != PONTUACAO or p["valor"] not in PONTUACOES or p["declarado_por"] not in DECLARANTES:
        _recusa("PONTUACAO_INVALIDA")
    # derivado recalculado; percentuais do TEC só informam consistência, nunca mandam
    com_pct = [l for l in linhas if "acertos_pct_tec" in l]
    consistentes = sum(1 for l in com_pct if l["questoes"] and abs(round(100.0 * l["acertos"] / l["questoes"]) - l["acertos_pct_tec"]) <= 1)
    avisos = []
    if com_pct and consistentes == len(com_pct) and p["valor"] == "liquida":
        avisos.append("PONTUACAO_LIQUIDA_DECLARADA_MAS_PERCENTUAIS_SAO_RAZOES_SIMPLES")
    if com_pct and consistentes == 0 and p["valor"] == "normal":
        avisos.append("PONTUACAO_NORMAL_DECLARADA_MAS_PERCENTUAIS_NAO_SAO_RAZOES_SIMPLES")
    nao_declarado = recorte["periodo"]["tipo"] == "nao_declarado" or any(v == "nao_declarado" for v in recorte["filtros"].values())
    if nao_declarado:
        avisos.append("RECORTE_NAO_DECLARADO")
    if exibir == "nao_declarado":
        avisos.append("EXIBIR_NAO_DECLARADO")
    saida = []
    for i, l in enumerate(linhas):
        em_filhos = filhos.get(i, [])
        item = {"codigo": l["codigo"], "profundidade": l["profundidade"], "titulo": l["titulo"], "questoes": l["questoes"],
                "acertos": l["acertos"], "erros": l["erros"], "peso": l["peso"], "acerto_bruto_pct": _pct(l["acertos"], l["questoes"])}
        if em_filhos:
            item["residuo_no_pai"] = {c: l[c] - sum(linhas[j][c] for j in em_filhos) for c in ("questoes", "acertos", "erros")}
        saida.append(item)
    return {"decisao": "validado", "codigo": "OK", "linha": None, "retrato": {
        "plataforma": "tec", "solicitante": e["solicitante"], "gerado_em": e["gerado_em"], "recorte": recorte,
        "pontuacao": {"valor": p["valor"], "declarado_por": p["declarado_por"], "origem": "declarada"},
        "exibir": exibir, "comparavel": not nao_declarado and exibir != "nao_declarado", "totais_recalculados": tot,
        "linhas": saida, "procedimento": procedimento, "procedimento_e_autorrelato": True, "avisos": avisos,
        "persistido": False}}
