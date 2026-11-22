"""Verificador de ENTREGA do runtime (S14-R5 a R8, R11, R13, R17): envelope fechado, alegações declaradas e verificadas.

Regra do proprietário (19/11/2026): o LLM é LIVRE na cognição; as ENTREGAS são condicionadas por mecanismos determinísticos. Este
módulo NÃO avalia o raciocínio nem a qualidade pedagógica: confere FORMA, PROVENIÊNCIA, PERMISSÃO, PRIVACIDADE e as ALEGAÇÕES que a
própria entrega declara (citação do edital contra os chunks do repositório; dado e nível do aluno contra a projeção fechada).

Função pura e fail-closed: sem rede, sem credencial, sem modelo. As leituras (edital, projeção, SHA fixado) chegam INJETADAS em
`contexto`. Só `carregar_edital` e `main` leem arquivo; só `gravar_registro` escreve (e só fora do repositório).

Classes de garantia (S14): o que este verificador recusa é ENFORÇADO quando roda no portão ou na rotina da Zapia e apenas
VERIFICÁVEL quando é rodado por quem quiser sobre o chat direto: nada aqui impõe o uso. NÃO GATEÁVEL: afirmação não numérica e não
declarada, interpretação do edital além do literal, adequação pedagógica (avaliação offline e amostra, S14-R12 e R14).

Modos (S14-R11): `sombra` avisa e registra (entrega inválida de texto livre passa com AVISO); `bloqueio` recusa. Os tipos com EFEITO
EXTERNO (COMANDO, LEMBRETE enviado pela Zapia e PROMPT_NOTEBOOK enviado ao Notebook) são SEMPRE bloqueio, e tipo desconhecido ou
envelope malformado também (não se sabe se tem efeito); nesses tipos um recibo não conferido contra o repositório também recusa
(S14-R3). Códigos de saída da linha de comando: 0 ACEITA, 1 RECUSADA, 3 AVISO, 4 falha ao gravar o registro (a decisão já foi
impressa); 2 é de uso incorreto (argparse).
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import agent_commands
import command_idempotency
import command_params_schema
import delivery_receipt_binding
import gates_mot
import notebook_prompt_validator
from private_persistence_guard import PersistenceBlocked
from session_read_guard import check_projection, conferir_idade

ROOT = Path(__file__).resolve().parents[1]
ACEITA, AVISO, RECUSADA = "ACEITA", "AVISO", "RECUSADA"
MODOS = ("sombra", "bloqueio")
TIPOS = ("ORIENTACAO", "RECOMENDACAO_CADERNO", "LEMBRETE", "COMANDO", "PROMPT_NOTEBOOK")
PAPEIS = ("tutor", "coach", "zapia")
TOPO_OBRIGATORIO = {"tipo", "papel", "sha_contrato", "recibo", "corpo", "alegacoes"}
TOPO = TOPO_OBRIGATORIO | {"estruturado"}
MAX_CORPO, MAX_LEMBRETE, MAX_ALEGACOES = 6000, 500, 50
SHA40 = re.compile(r"^[0-9a-f]{40}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")
NIVEIS = ("E0", "E1", "E2", "E3", "E4")
PRESCRICAO_DIAS = (7, 15, 30)  # padrão do D-11
PLATAFORMAS = ("TEC", "Qconcursos")
DIFICULDADES = ("facil", "medio", "dificil")
CAMPOS_CADERNO = {"atividade_id", "plataforma", "filtros", "assunto", "dificuldade", "quantidade", "justificativa"}
# S7-R1 e S6: quem pode assinar cada operação de comando
ORIGEM_DA_OPERACAO = {"registrar_resultado": ("tutor",), "registrar_exportacao_desempenho": ("tutor",), "registrar_plano": ("tutor",),
                      "registrar_acompanhamento": ("coach",), "enviar_mensagem": ("tutor", "coach"),
                      "ler_arquivo_repositorio": ("tutor", "coach"), "enviar_prompt_notebook": ("tutor",),
                      "criar_lembrete": ("coach",), "consultar_agenda_minima": ("coach",)}  # GAP-A2: as duas operações da agenda entram na tabela
RISCO_DA_OPERACAO = {"enviar_mensagem": "ROTINA_AUTORIZADA", "ler_arquivo_repositorio": "ORIENTACAO", "enviar_prompt_notebook": "ROTINA_AUTORIZADA",
                     "criar_lembrete": "ROTINA_AUTORIZADA", "consultar_agenda_minima": "ROTINA_AUTORIZADA"}

TIPOS_COM_EFEITO = ("COMANDO", "LEMBRETE", "PROMPT_NOTEBOOK")
FORMATO_PROMPT = ("prompt", "prompt_sha256")  # AT-2: formato ÚNICO do que a Zapia recebe (o rascunho de 5 campos é a forma de AUTORIA do Tutor, via `preparar`)
PREFIXOS_DE_ID = ("UFMS", "TEC", "QC", "CAD", "CADERNO")  # prefixos dos ids de atividade do projeto; outro hífen-número (COVID-19) não é id
_URL = re.compile(r"https?://|\bwww\.", re.I)
_QUESTAO = re.compile(r"enunciado\s*:|enunciado\s+d[aeo]s?\s+quest|gabarito\s+(?:é|e|oficial|da)\b|alternativa\s+[a-e]\s+(?:é|e|est[áa]|correta|incorreta)\b", re.I)
_DISPONIB = re.compile(r"dispon[ií]ve(?:l|is)|\bh[áa]\s+\d+\s+quest|\bexistem?\s+\d+\s+quest"
                       r"|\b(?:h[áa]|existem?|temos|tem)\s+(?:\w+\s+){0,2}?(?:cadernos?|quest(?:[õo]es|[ãa]o))\s+(?:prontos?|suficientes?|dispon\w+|de sobra)\b", re.I)  # AC-7
# AC-7: também "40٪", "quarenta por cento", "taxa de 0.4", "12 de 20 acertos" e "12/20" (fração fora de data: o segundo número passa de 12)
_PERCENTUAL = re.compile(r"\d+(?:[.,]\d+)?\s*[%٪％]|\bpor\s+cento\b|\b(?:taxa|aproveitamento|índice|indice)\s+de\s+\d*[.,]?\d+\b"
                         r"|\b\d+\s+de\s+\d+\s*(?:acertos?|erros?|quest(?:[õo]es|[ãa]o))\b|(?<![\d/])(?:[0-9]|[1-9]\d{1,2})/(?:1[3-9]|[2-9]\d|\d{3})(?![\d/])", re.I)
_DESEMPENHO = re.compile(r"\b(?:acertou|errou|acertos?|erros?|nota)\b\D{0,12}\d+", re.I)
# contagem ANTES da palavra, atribuída ao aluno por marcador na mesma frase ("você teve 12 acertos"); sem marcador ("os 3 erros comuns") não casa
_DESEMPENHO_ATRIBUIDO = re.compile(r"\b(?:voc[êe]|seu|sua|seus|suas|teve|tive|fez|obteve|tem)\b[^.!?\n]{0,40}?\b\d+\s*(?:acertos?|erros?|pontos?)\b", re.I)
_PAGINA = re.compile(r"p[áa]g(?:ina|\.)?\s*(\d{1,3})", re.I)
_DISPOSITIVO = re.compile(r"\b(?:art(?:igo)?\.?|inciso|item)\s*\d+", re.I)
_NIVEL = re.compile(r"\bE[0-4]\b")
_ID = re.compile(r"\b(?:" + "|".join(PREFIXOS_DE_ID) + r")-\d{1,6}\b", re.I)
_PRESCRICAO = re.compile(r"(\d+)\s*(quest(?:[õo]es|[ãa]o)|dias?)\b", re.I)
_ID_VALIDO = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_TEXTO_CURTO = re.compile(r"^[^\x00-\x1f]{1,200}$")


def _norm(texto):
    if not isinstance(texto, str):
        return ""
    base = unicodedata.normalize("NFKC", texto).lower()
    return re.sub(r"\s+", " ", base).strip()


def carregar_edital(root=ROOT):
    """Lê os chunks do edital já no repositório: {página: texto normalizado}. Única leitura de arquivo do módulo além de `main`."""
    paginas = {}
    for arq in sorted((Path(root) / "edital" / "chunks").glob("p*-c*.md")):
        texto = arq.read_text(encoding="utf-8")
        achou = re.search(r"^page:\s*(\d+)\s*$", texto, re.M)
        if achou:
            corpo = texto.split("\n---\n", 1)[-1] if texto.startswith("---") else texto
            paginas[int(achou.group(1))] = paginas.get(int(achou.group(1)), "") + " " + _norm(corpo)
    return paginas


def _recibo(recibo, contexto, motivos, avisos, efeito):
    if not (isinstance(recibo, dict) and set(recibo) == {"sha", "hashes"} and isinstance(recibo["sha"], str) and SHA40.fullmatch(recibo["sha"])
            and isinstance(recibo["hashes"], dict) and recibo["hashes"]
            and all(isinstance(k, str) and 1 <= len(k) <= 60 and isinstance(v, str) and HASH64.fullmatch(v) for k, v in recibo["hashes"].items())):
        motivos.append("recibo_ausente_ou_malformado")
        return
    esperado = contexto.get("recibo_esperado")
    if esperado is None:
        # a conferência contra o repositório é a tarefa RS: em tipo com efeito externo, não decidir é recusar (S14-R3 e R17)
        (motivos if efeito else avisos).append("recibo_nao_conferido_contra_o_repositorio")
    elif recibo != esperado:
        motivos.append("recibo_diferente_do_esperado")


def _alegacoes(alegacoes, contexto, motivos):
    """Verifica cada alegação declarada contra a fonte. Devolve o que foi declarado, para cruzar com o corpo."""
    declarado = {"paginas": set(), "citou": False, "niveis": set(), "ids": set()}
    if not (isinstance(alegacoes, list) and len(alegacoes) <= MAX_ALEGACOES):
        motivos.append("alegacoes_invalidas")
        return declarado
    edital, proj = contexto.get("edital") or {}, contexto.get("projecao")
    niveis = {i["topico"]: i["nivel"] for i in proj.get("niveis", [])} if isinstance(proj, dict) else None
    pend = {i["atividade_id"] for i in proj.get("pendencias", [])} if isinstance(proj, dict) else None
    revs = {(i["topico"], i["vence_em"]) for i in proj.get("revisoes", [])} if isinstance(proj, dict) else None
    for a in alegacoes:
        t = a.get("tipo") if isinstance(a, dict) else None
        if t == "citacao_edital":
            if not (set(a) == {"tipo", "pagina", "trecho"} and type(a["pagina"]) is int and isinstance(a["trecho"], str)
                    and 12 <= len(a["trecho"]) <= 300):
                motivos.append("alegacao_malformada")
            elif a["pagina"] not in edital:
                motivos.append("citacao_edital_pagina_sem_chunk")
            elif _norm(a["trecho"]) not in edital[a["pagina"]]:
                motivos.append("citacao_edital_trecho_inexistente")
            else:
                declarado["paginas"].add(a["pagina"])
                declarado["citou"] = True
        elif t == "dado_aluno":
            if not (set(a) == {"tipo", "campo", "valor"} and a["campo"] in ("pendencia", "revisao", "nivel") and isinstance(a["valor"], str)
                    and _TEXTO_CURTO.fullmatch(a["valor"])):
                motivos.append("alegacao_malformada")
            elif proj is None:
                motivos.append("dado_aluno_sem_projecao")
            elif a["campo"] == "pendencia" and a["valor"] in pend:
                declarado["ids"].add(a["valor"])
            elif a["campo"] == "revisao" and tuple(a["valor"].split("|", 1)) in revs:
                pass
            elif a["campo"] == "nivel" and tuple(a["valor"].split("|", 1))[0] in niveis and niveis[a["valor"].split("|", 1)[0]] == a["valor"].split("|", 1)[-1]:
                declarado["niveis"].add(a["valor"].split("|", 1)[-1])
            else:
                motivos.append("dado_aluno_inexistente_na_projecao")
        elif t == "nivel_evidencia":
            if not (set(a) == {"tipo", "topico", "nivel"} and isinstance(a["topico"], str) and a["nivel"] in NIVEIS):
                motivos.append("alegacao_malformada")
            elif proj is None:
                motivos.append("nivel_sem_projecao")
            elif niveis.get(a["topico"], "E0") != a["nivel"]:  # tópico fora da lista = sem tentativa = E0
                motivos.append("nivel_diferente_da_projecao")
            else:
                declarado["niveis"].add(a["nivel"])
        elif t == "inferencia":
            if not (set(a) == {"tipo", "texto"} and isinstance(a["texto"], str) and _TEXTO_CURTO.fullmatch(a["texto"])):
                motivos.append("alegacao_malformada")
        else:
            motivos.append("alegacao_tipo_desconhecido")
    return declarado


def _corpo(corpo, estruturado, declarado, contexto, motivos, avisos):
    """Privacidade (R8) e fatos não declarados (R6) no texto livre. Nunca repete o conteúdo nas saídas."""
    if agent_commands.scan_text(corpo, html=True):
        motivos.append("corpo_com_segredo_ou_dado_pessoal")
    if _URL.search(corpo):
        motivos.append("url_fora_da_lista")
    if _QUESTAO.search(corpo):
        motivos.append("enunciado_de_questao")
    if notebook_prompt_validator.instrucao_embutida(corpo):
        motivos.append("instrucao_embutida_no_corpo")
    if _DISPONIB.search(corpo):
        motivos.append("disponibilidade_de_questoes_afirmada")
    if _PERCENTUAL.search(corpo) or _DESEMPENHO.search(corpo) or _DESEMPENHO_ATRIBUIDO.search(corpo):
        motivos.append("dado_de_desempenho_nao_verificavel")  # a projeção fechada não traz desempenho: nada o confirma
    if any(f["gate"] != "FORMA" for f in gates_mot.verificar_mensagem(corpo)["falhas"]):
        motivos.append("frase_proibida_gmot")  # AC-5: os gates lexicais G-MOT agora valem na entrega (heurística; não pega toda paráfrase)
    for pagina in _PAGINA.findall(corpo):
        if int(pagina) not in declarado["paginas"]:
            motivos.append("pagina_citada_sem_alegacao")
    if _DISPOSITIVO.search(corpo) and not declarado["citou"]:
        motivos.append("dispositivo_citado_sem_alegacao")
    for nivel in set(_NIVEL.findall(corpo)):
        if nivel not in declarado["niveis"]:
            motivos.append("nivel_sem_alegacao")
    proj = contexto.get("projecao")
    conhecidos = set(declarado["ids"]) | ({i["atividade_id"] for i in proj.get("pendencias", [])} if isinstance(proj, dict) else set())
    if isinstance(estruturado, dict) and isinstance(estruturado.get("atividade_id"), str):
        conhecidos.add(estruturado["atividade_id"])
    conhecidos_norm = {c.upper() for c in conhecidos}
    for ident in set(_ID.findall(corpo)):
        if ident.upper() not in conhecidos_norm:
            motivos.append("id_sem_alegacao")
    quantidade = estruturado.get("quantidade") if isinstance(estruturado, dict) else None
    for numero, unidade in _PRESCRICAO.findall(corpo):
        if unidade.lower().startswith("quest"):
            if quantidade is None or int(numero) != quantidade:
                avisos.append("quantidade_diferente_do_campo_estruturado")
        elif int(numero) not in PRESCRICAO_DIAS:
            avisos.append("prazo_fora_do_padrao_d11")


def _caderno(est, contexto, motivos, avisos):
    if not (isinstance(est, dict) and set(est) == CAMPOS_CADERNO and isinstance(est["atividade_id"], str) and _ID_VALIDO.fullmatch(est["atividade_id"])
            and est["plataforma"] in PLATAFORMAS and est["dificuldade"] in DIFICULDADES and type(est["quantidade"]) is int and 1 <= est["quantidade"] <= 200
            and isinstance(est["filtros"], list) and 1 <= len(est["filtros"]) <= 8 and all(isinstance(f, str) and _TEXTO_CURTO.fullmatch(f) for f in est["filtros"])
            and isinstance(est["assunto"], str) and _TEXTO_CURTO.fullmatch(est["assunto"])
            and isinstance(est["justificativa"], str) and 1 <= len(est["justificativa"]) <= 500):
        motivos.append("recomendacao_de_caderno_fora_da_lista_fechada")
        return
    extra = " ".join([est["justificativa"], est["assunto"], *est["filtros"]])
    if _DISPONIB.search(extra):
        motivos.append("disponibilidade_de_questoes_afirmada")
    if agent_commands.scan_text(extra, html=True) or _URL.search(extra) or _QUESTAO.search(extra) or notebook_prompt_validator.instrucao_embutida(extra):
        motivos.append("campo_estruturado_com_conteudo_proibido")
    topicos = contexto.get("topicos")
    if topicos is not None and est["assunto"] not in topicos:
        avisos.append("assunto_fora_da_lista_de_topicos")


def _ids_do_lembrete(est):
    """Lista de atividades do LEMBRETE (GA-4): `atividade_ids` (1 a 5, sem repetição) ou a forma antiga `atividade_id`; None se malformado."""
    if isinstance(est, dict) and set(est) == {"atividade_ids"} and command_idempotency.lista_de_atividades_valida(est["atividade_ids"]):
        return list(est["atividade_ids"])
    if isinstance(est, dict) and set(est) == {"atividade_id"} and isinstance(est["atividade_id"], str):
        return [est["atividade_id"]]
    return None


def _lembrete(est, corpo, contexto, motivos):
    proj = contexto.get("projecao")
    if len(corpo) > MAX_LEMBRETE:
        motivos.append("lembrete_acima_do_limite")
    pend = {i["atividade_id"] for i in proj.get("pendencias", [])} if isinstance(proj, dict) else None
    ids = _ids_do_lembrete(est)
    if not (ids is not None and pend is not None and set(ids) <= pend):  # toda atividade da lista tem de estar pendente
        motivos.append("lembrete_sem_atividade_pendente")  # S8-R2: só lembra atividade pendente


def _ids_ordenados(est):
    ids = _ids_do_lembrete(est)
    return sorted(ids) if ids is not None else None


def _comando(est, papel, contexto, motivos):
    schema = agent_commands.load_schema()
    if papel == "zapia":
        motivos.append("zapia_nao_emite_comando")  # a Zapia só executa o comando válido (S5-R3)
    if not (isinstance(est, dict) and set(est) == {"operacao", "params"} and isinstance(est["operacao"], str) and isinstance(est["params"], dict)):
        motivos.append("comando_fora_da_lista_fechada")
        return None
    op = est["operacao"]
    if op not in schema["destinations"] or op not in ORIGEM_DA_OPERACAO:
        motivos.append("operacao_fora_da_tabela")
        return None
    if papel in PAPEIS and papel != "zapia" and papel not in ORIGEM_DA_OPERACAO[op]:
        motivos.append("papel_nao_pode_emitir_a_operacao")
    if agent_commands._scan_params(est["params"], schema):
        motivos.append("comando_com_parametro_proibido")
    if command_params_schema.validar_params(op, est["params"]):
        motivos.append("comando_com_params_fora_do_esquema")  # GA-1: o mesmo esquema fechado do validador
    elif op == "criar_lembrete":
        _vinculo_lembrete(est["params"], contexto, motivos)
    elif op == "enviar_prompt_notebook" and not notebook_prompt_validator.conferir_parametros(est["params"]).ok:
        motivos.append("comando_prompt_notebook_invalido")  # AT-1: o mesmo hash, forma canônica e filtros do validador e da caixa
    texto = est["params"].get("texto")
    if isinstance(texto, str) and len(texto) > MAX_LEMBRETE:
        motivos.append("mensagem_acima_do_limite")  # AC-7: o mesmo teto de 500 caracteres do LEMBRETE
    if isinstance(texto, str):  # GA-2: o texto livre dos params passa pelos MESMOS filtros do corpo (identificadores e prompt do Notebook têm validação própria)
        _corpo(texto, None, {"paginas": set(), "ids": [], "citou": False, "niveis": set()}, {}, motivos, [])
    return op


def _vinculo_lembrete(params, contexto, motivos):
    """GA-4 e AC-2: o COMANDO `criar_lembrete` referencia o hash de um LEMBRETE já verificado; o hash é RECALCULADO a partir do corpo e dos ids
    que o verificador guardou, e os ids do comando têm de ser exatamente os do lembrete. `lembretes_verificados`: {hash: {"corpo", "atividade_ids"}}."""
    verificados = contexto.get("lembretes_verificados")
    h = params["lembrete_sha256"]
    if isinstance(verificados, (set, frozenset, list, tuple)):
        motivos.append("comando_vinculo_sem_ids_verificados")  # forma antiga: só hashes, não prova quais atividades o lembrete cobre
    elif not (isinstance(verificados, dict) and h in verificados):
        motivos.append("comando_sem_vinculo_com_lembrete")
    else:
        reg = verificados[h]
        if not (isinstance(reg, dict) and set(reg) == {"corpo", "atividade_ids"} and isinstance(reg["corpo"], str)
                and command_idempotency.lista_de_atividades_valida(reg["atividade_ids"])):
            motivos.append("comando_vinculo_sem_ids_verificados")
        elif command_idempotency.hash_lembrete(reg["corpo"], reg["atividade_ids"]) != h:
            motivos.append("comando_vinculo_hash_nao_confere")
        elif sorted(params["atividade_ids"]) != sorted(reg["atividade_ids"]):
            motivos.append("comando_lembrete_ids_diferentes_do_lembrete")
    proj = contexto.get("projecao")
    pend = {i["atividade_id"] for i in proj.get("pendencias", [])} if isinstance(proj, dict) else None
    if pend is None or not set(params["atividade_ids"]) <= pend:
        motivos.append("comando_lembrete_atividade_nao_pendente")


def _prompt_notebook(est, papel, motivos):
    if papel != "tutor":
        motivos.append("prompt_notebook_so_do_tutor")  # o Notebook é ferramenta do Tutor (S10)
    if isinstance(est, dict) and set(est) == set(notebook_prompt_validator.CAMPOS):
        motivos.append("prompt_notebook_forma_nao_canonica")  # AT-2: o rascunho de 5 campos passa por `preparar` antes de ir à Zapia
        return
    if not notebook_prompt_validator.conferir_parametros(est).ok:
        motivos.append("prompt_notebook_invalido")


def _estrutura(env, motivos):
    if not isinstance(env, dict):
        motivos.append("envelope_nao_e_objeto")
        return False
    if not TOPO_OBRIGATORIO <= set(env) <= TOPO:
        motivos.append("campos_do_envelope_fora_da_lista_fechada")
        return False
    if env["tipo"] not in TIPOS:
        motivos.append("tipo_desconhecido")
        return False
    if env["papel"] not in PAPEIS:
        motivos.append("papel_desconhecido")
    if not isinstance(env["corpo"], str) or len(env["corpo"]) > MAX_CORPO:
        motivos.append("corpo_acima_do_limite_ou_nao_texto")
        return False
    return True


def _idade_da_projecao(tipo, op, contexto, agora, motivos, avisos):
    """AC-1 (S15-R5): decisão de PRAZO (LEMBRETE e COMANDO criar_lembrete) exige projeção de até 24 h com instante; as demais entregas só avisam
    acima de 72 h. Projeção no futuro ou sem `gerado_em` recusa em qualquer tipo. Sem projeção, nada muda."""
    proj = contexto.get("projecao")
    if not isinstance(proj, dict):
        return
    uso = "prazo" if tipo == "LEMBRETE" or (tipo == "COMANDO" and op == "criar_lembrete") else "orientacao"
    r = conferir_idade(proj, agora, uso)
    if r["decisao"] == "RECUSA":
        motivos.append({"PROJECAO_VELHA_PARA_PRAZO": "projecao_velha_para_prazo", "PROJECAO_SEM_INSTANTE": "projecao_sem_instante_para_prazo",
                        "PROJECAO_NO_FUTURO": "projecao_no_futuro", "PROJECAO_SEM_GERADO_EM": "projecao_do_contexto_invalida"}.get(r["codigo"], "projecao_nao_confere"))
    elif r["decisao"] == "AVISO":
        avisos.append("projecao_defasada")


def _verificar(env, contexto, agora=None):
    motivos, avisos, op = [], [], None
    if not _estrutura(env, motivos):
        return motivos, avisos, None
    tipo, papel, est = env["tipo"], env["papel"], env.get("estruturado")
    if not (isinstance(env["sha_contrato"], str) and SHA40.fullmatch(env["sha_contrato"])) or env["sha_contrato"] != contexto.get("sha_contrato"):
        motivos.append("sha_diferente_do_fixado")  # S14-R2: o contrato em produção é o SHA fixado
    _recibo(env["recibo"], contexto, motivos, avisos, tipo in TIPOS_COM_EFEITO)
    if tipo in ("COMANDO", "PROMPT_NOTEBOOK") and env["corpo"] != "":
        motivos.append("corpo_deve_ser_vazio_neste_tipo")
    if tipo not in ("COMANDO", "PROMPT_NOTEBOOK") and not env["corpo"].strip():
        motivos.append("corpo_vazio")
    declarado = _alegacoes(env["alegacoes"], contexto, motivos)
    if env["corpo"]:
        _corpo(env["corpo"], est, declarado, contexto, motivos, avisos)
    if tipo == "RECOMENDACAO_CADERNO":
        _caderno(est, contexto, motivos, avisos)
    elif tipo == "LEMBRETE":
        _lembrete(est, env["corpo"], contexto, motivos)
    elif tipo == "COMANDO":
        op = _comando(est, papel, contexto, motivos)
    elif tipo == "PROMPT_NOTEBOOK":
        _prompt_notebook(est, papel, motivos)
    elif tipo == "ORIENTACAO" and est is not None:
        motivos.append("orientacao_nao_tem_campo_estruturado")
    _idade_da_projecao(tipo, op, contexto, agora, motivos, avisos)
    return motivos, avisos, op


def _risco(tipo, op):
    if tipo == "COMANDO":
        return RISCO_DA_OPERACAO.get(op, "SENSIVEL")
    return {"ORIENTACAO": "ORIENTACAO", "RECOMENDACAO_CADERNO": "ORIENTACAO", "LEMBRETE": "ROTINA_AUTORIZADA", "PROMPT_NOTEBOOK": "ROTINA_AUTORIZADA"}.get(tipo, "SENSIVEL")


def verificar_entrega(envelope, contexto, modo="sombra", agora=None):
    """Decide ACEITA, AVISO ou RECUSADA. Nunca levanta por causa do envelope e nunca repete o conteúdo recebido."""
    if modo not in MODOS:
        raise ValueError("modo inválido")
    agora = agora or datetime.now(timezone.utc)
    if agora.tzinfo is None:
        raise ValueError("horário sem fuso")
    contexto = contexto if isinstance(contexto, dict) else {}
    proj = contexto.get("projecao")
    if proj is not None:
        try:
            check_projection(proj)
        except PersistenceBlocked:
            contexto = {**contexto, "projecao": None}
            projecao_invalida = True
        else:
            projecao_invalida = False
    else:
        projecao_invalida = False
    try:
        motivos, avisos, op = _verificar(envelope, contexto, agora)
    except Exception as exc:  # erro inesperado: fecha, nunca derruba
        motivos, avisos, op = ["erro_inesperado_na_verificacao_" + type(exc).__name__], [], None
    if projecao_invalida:
        motivos.append("projecao_do_contexto_invalida")
    extras = contexto.get("motivos_extras")
    if isinstance(extras, list):
        motivos.extend(x for x in extras if x in ("envelope_ilegivel", "projecao_ilegivel"))
    tipo = envelope.get("tipo") if isinstance(envelope, dict) and envelope.get("tipo") in TIPOS else None
    efeito = tipo is None or tipo in TIPOS_COM_EFEITO  # tipo desconhecido ou envelope malformado: não se sabe se tem efeito, então é bloqueio
    modo_efetivo = "bloqueio" if efeito else modo
    motivos, avisos = sorted(set(motivos)), sorted(set(avisos))
    if motivos and modo_efetivo == "bloqueio":
        decisao = RECUSADA
    elif motivos or avisos:
        decisao = AVISO
    else:
        decisao = ACEITA
    resultado = {"decisao": decisao, "modo_efetivo": modo_efetivo, "tipo": tipo, "classe_de_risco": _risco(tipo, op),
                 "motivos": motivos, "avisos": avisos, "gerado_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if tipo == "LEMBRETE" and not motivos:  # GA-4: o hash que o COMANDO `criar_lembrete` deve citar (texto e conjunto de atividades)
        resultado["lembrete_sha256"] = command_idempotency.hash_lembrete(envelope["corpo"], _ids_do_lembrete(envelope.get("estruturado")))
        resultado["lembrete_atividade_ids"] = _ids_ordenados(envelope.get("estruturado"))  # AC-2: o que o hash cobre, para o vínculo do COMANDO
    return resultado


def montar_registro(resultado, envelope):
    """Registro da entrega (S14-R13): só tipo, decisão, modo, códigos de motivo e prefixo do SHA; NUNCA o conteúdo."""
    sha = envelope.get("sha_contrato") if isinstance(envelope, dict) else None
    registro = {"tipo": resultado["tipo"], "decisao": resultado["decisao"], "modo": resultado["modo_efetivo"], "motivos": resultado["motivos"],
                "avisos": resultado["avisos"], "sha_contrato": sha[:12] if isinstance(sha, str) and SHA40.fullmatch(sha) else None,
                "gerado_em": resultado["gerado_em"]}
    texto = json.dumps(registro, ensure_ascii=False)
    if re.search(r"github_pat_|\bgh[pousr]_|-----BEGIN|@[A-Za-z0-9.-]+\.[a-z]{2,}|https?://", texto):
        raise ValueError("registro com padrão de segredo ou dado pessoal")
    return registro


def gravar_registro(caminho, registro):
    """Acrescenta UMA linha JSON a um arquivo LOCAL fora do repositório (S14-R13: antes do piloto o registro é efêmero e privado)."""
    destino = Path(caminho).resolve()
    if ROOT in (destino, *destino.parents):
        raise ValueError("o registro não pode ficar dentro do repositório")
    with open(destino, "a", encoding="utf-8") as arq:
        arq.write(json.dumps(registro, ensure_ascii=False) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--envelope", required=True, help="arquivo JSON com a entrega (nenhuma rede é usada aqui)")
    ap.add_argument("--projecao", help="arquivo JSON com a projeção fechada (opcional)")
    ap.add_argument("--sha-contrato", required=True, help="SHA do contrato fixado em produção (S14-R2)")
    ap.add_argument("--root-contrato", help="checkout Git do contrato: o recibo esperado é recalculado nele, no SHA fixado (S14-R3); sem isto o recibo fica não conferido")
    ap.add_argument("--modo", choices=MODOS, default="sombra")
    ap.add_argument("--registro", help="arquivo local, FORA do repositório, onde acrescentar o registro da entrega")
    a = ap.parse_args(argv)
    envelope, projecao, extras = None, None, []
    try:
        with open(a.envelope, encoding="utf-8") as arq:
            envelope = json.load(arq)
    except (OSError, ValueError):
        extras.append("envelope_ilegivel")
    if a.projecao:
        try:
            with open(a.projecao, encoding="utf-8") as arq:
                projecao = json.load(arq)
        except (OSError, ValueError):
            extras.append("projecao_ilegivel")  # o envelope válido continua sendo avaliado; só a projeção ficou de fora
    contexto = {"sha_contrato": a.sha_contrato, "edital": carregar_edital(), "projecao": projecao, "motivos_extras": extras}
    if a.root_contrato:  # RS ligado ao GE: sem papel válido ou com falha ao calcular, fica None (não conferido, fail-closed)
        papel = envelope.get("papel") if isinstance(envelope, dict) else None
        contexto["recibo_esperado"] = delivery_receipt_binding.recibo_esperado(a.root_contrato, a.sha_contrato, papel)
    resultado = verificar_entrega(envelope, contexto, a.modo)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if a.registro:
        try:
            gravar_registro(a.registro, montar_registro(resultado, envelope))
        except (OSError, ValueError) as exc:
            print("falha ao gravar o registro: " + type(exc).__name__, file=sys.stderr)
            return 4  # a decisão já foi impressa; 4 não se confunde com RECUSADA (1) nem com uso incorreto (2)
    return {ACEITA: 0, AVISO: 3, RECUSADA: 1}[resultado["decisao"]]


if __name__ == "__main__":
    sys.exit(main())
