"""Relatório do ciclo do piloto e semáforo (S11-R4, R10, R11, R13), SEM dado pessoal.

Função pura e fail-closed: não faz rede, não lê credencial, não grava nada e não chama modelo. Recebe o `ciclo` (leituras já feitas,
injetadas) e devolve um relatório de CAMPOS FECHADOS, com o semáforo decidido por regras fixadas antes (S11-R10).

O que o relatório NUNCA leva (S11-R11): valores de desempenho, nomes de tópico com resultado, enunciado, e-mail, token ou link com
identificador de conta. Por isso as etapas usam só ENUMERAÇÕES FECHADAS e as contagens usam só inteiros; o único texto livre curto é
a lista de lacunas, com padrão restrito. O relatório termina com a linha "Não provado:" e a lista (S11-R13) e declara N=1 (S11-R1).

Semáforo (S11-R10, padrão fechado):
- VERMELHO: gatilho vermelho ligado, pré-voo vermelho, janela aberta há mais de 24 h ou ainda aberta no relatório, fechamento sem
  reinstalar o fluxo, F3 ou F4 escritas como PROVADA (relato nunca é prova), qualquer entrada ausente ou malformada, e TUDO que não
  estiver na lista âmbar e não for VERDE.
- ÂMBAR: F5 recusou por formato, readback atrasou, pré-voo ÂMBAR, ou etapa F1 a F7 NÃO PROVADA por falta de registro, sem falha.
- VERDE: os três pré-voos VERDES; F1, F2, F5, F6, F7 PROVADAS; F3 e F4 RELATADAS; F8 NÃO EXERCIDA ou PROVADA; um evento lido de
  volta; janela fechada e fluxo reinstalado; nenhuma etapa NÃO PROVADA.

Limites: prova o que as leituras injetadas dizem; NÃO prova que foram feitas contra a conta real e NÃO liga nem desliga nada.
Códigos de saída da linha de comando: 0 VERDE, 1 VERMELHO (inclui arquivo ilegível), 3 ÂMBAR; 2 é de uso incorreto (argparse).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

VERDE, AMBAR, VERMELHO = "VERDE", "AMBAR", "VERMELHO"
ORDEM = {VERDE: 0, AMBAR: 1, VERMELHO: 2}
JANELA = timedelta(hours=24)
ETAPAS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8")
ESTADOS = ("PROVADA", "RELATADA", "NAO_EXERCIDA", "NAO_PROVADA")
QUEM = ("proprietario", "tutor", "zapia", "fluxo", "gerador")
PROVAS = ("readback", "projecao_check", "validacao_f5", "relato_com_captura", "relato", "justificativa", "nenhuma")
DESCONHECIDOS = ("nenhum", "compreensao", "utilidade", "disponibilidade_de_questoes", "origem_do_comando", "veracidade_do_resultado")
NIVEIS = ("E0", "E1", "E2", "E3", "E4")
PREVOOS = ("abertura", "pos_janela", "repouso")
GATILHOS_VERMELHOS = ("dado_pessoal_no_publico", "escrita_sem_readback_declarada", "flag_do_publico_true", "segredo_exposto",
                      "hash_do_fluxo_diferente", "consentimento_invalido", "evento_fora_de_dados", "repositorio_nao_privado",
                      "fechamento_sem_reinstalar_o_fluxo")
GATILHOS_AMBAR = ("f5_recusou_por_formato", "readback_atrasou")
NAO_PROVADO = ("utilidade pedagógica", "ganho de aprendizagem", "robustez em escala", "leitura automática do TEC",
               "rotina da Zapia (S8)", "homologação da RM-08 e da RM-10")
LACUNAS_PADRAO = ("os fatos F3 e F4 são relato do proprietário", "o repositório não lê a conta real do GitHub",
                  "um caderno não permite concluir eficácia")
TOPO = ("schema", "gerado_em", "n", "semaforo", "motivos", "preflights", "janela", "evento", "contagens", "niveis", "etapas", "lacunas",
        "nao_provado")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
LACUNA = re.compile(r"^[A-Za-zÀ-ÿ ,;:()./-]{3,100}$")
PROIBIDO = re.compile(r"melhorou|melhora\b|ganhou|%|github_pat_|\bgh[pousr]_|\bsk-|-----BEGIN|@[A-Za-z0-9.-]+\.[a-z]{2,}|https?://|\bcpf\b|enunciado|gabarito",
                      re.I)


def _dt(valor):
    if not isinstance(valor, str):
        return None
    try:
        q = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    return q if q.tzinfo is not None else None


def _int(v):
    return type(v) is int and v >= 0


def _fechado(motivo):
    """Resultado mínimo VERMELHO por entrada inválida: nunca traz o conteúdo recebido."""
    return {"semaforo": VERMELHO, "motivos": [motivo]}


def _etapas(ciclo):
    bruto = ciclo.get("etapas")
    if not isinstance(bruto, dict):
        return None, ["etapas_ausentes"]
    linhas, erros = [], []
    for e in ETAPAS:
        r = bruto.get(e)
        if r is None:
            linhas.append({"etapa": e, "estado": "NAO_PROVADA", "quem": "proprietario", "prova": "nenhuma", "desconhecido": "nenhum"})
            continue
        if not (isinstance(r, dict) and r.get("estado") in ESTADOS and r.get("quem") in QUEM and r.get("prova") in PROVAS
                and r.get("desconhecido") in DESCONHECIDOS):
            erros.append(f"etapa_{e}_malformada")
            continue
        linhas.append({"etapa": e, "estado": r["estado"], "quem": r["quem"], "prova": r["prova"], "desconhecido": r["desconhecido"]})
    return linhas, erros


def _decidir(ciclo, etapas, agora):
    """Aplica S11-R10. Devolve (semaforo, motivos). Qualquer coisa fora das regras conhecidas cai em VERMELHO (padrão fechado)."""
    vermelhos, ambares = [], []
    gat = ciclo.get("gatilhos")
    if not isinstance(gat, dict):
        return VERMELHO, ["gatilhos_ausentes"]
    for g in GATILHOS_VERMELHOS + GATILHOS_AMBAR:
        if type(gat.get(g)) is not bool:
            return VERMELHO, [f"gatilho_{g}_ausente_ou_nao_booleano"]
    vermelhos += [g for g in GATILHOS_VERMELHOS if gat[g]]
    ambares += [g for g in GATILHOS_AMBAR if gat[g]]
    pre = ciclo.get("preflights")
    if not isinstance(pre, dict) or any(pre.get(m) not in (VERDE, AMBAR, VERMELHO) for m in PREVOOS):
        return VERMELHO, ["preflights_ausentes_ou_invalidos"]
    for m in PREVOOS:
        (vermelhos if pre[m] == VERMELHO else ambares if pre[m] == AMBAR else []).append(f"preflight_{m}_{pre[m].lower()}")
    janela = ciclo.get("janela")
    aberta = _dt(janela.get("aberta_em")) if isinstance(janela, dict) else None
    fechada = _dt(janela.get("fechada_em")) if isinstance(janela, dict) else None
    if aberta is None:
        return VERMELHO, ["janela_sem_hora_de_abertura"]
    if janela.get("fechada_em") is None:
        vermelhos.append("janela_ainda_aberta_no_relatorio")
        if agora - aberta > JANELA:
            vermelhos.append("janela_aberta_ha_mais_de_24_h")
    elif fechada is None or fechada < aberta:
        return VERMELHO, ["janela_com_fechamento_invalido"]
    elif fechada - aberta > JANELA:
        vermelhos.append("janela_aberta_ha_mais_de_24_h")
    ev = ciclo.get("evento")
    if not (isinstance(ev, dict) and isinstance(ev.get("id"), str) and ID.fullmatch(ev["id"]) and isinstance(ev.get("commit_sha"), str)
            and SHA40.fullmatch(ev["commit_sha"]) and isinstance(ev.get("hash_corpo"), str) and HASH64.fullmatch(ev["hash_corpo"])
            and type(ev.get("readback")) is bool):
        return VERMELHO, ["evento_ausente_ou_malformado"]
    if not ev["readback"]:
        vermelhos.append("evento_sem_readback")
    estado = {l["etapa"]: l["estado"] for l in etapas}
    for e in ("F3", "F4"):
        if estado[e] == "PROVADA":
            vermelhos.append(f"{e}_escrita_como_provada_relato_nao_e_prova")
    for e in ("F1", "F2", "F5", "F6", "F7"):
        if estado[e] == "NAO_PROVADA":
            ambares.append(f"{e}_nao_provada_por_falta_de_registro")
        elif estado[e] != "PROVADA":
            vermelhos.append(f"{e}_estado_inesperado_{estado[e].lower()}")
    for e in ("F3", "F4"):
        if estado[e] == "NAO_PROVADA":
            ambares.append(f"{e}_nao_provada_por_falta_de_registro")
        elif estado[e] not in ("RELATADA", "PROVADA"):
            vermelhos.append(f"{e}_estado_inesperado_{estado[e].lower()}")
    if estado["F8"] == "NAO_PROVADA":
        ambares.append("F8_nao_provada")
    elif estado["F8"] not in ("PROVADA", "NAO_EXERCIDA"):
        vermelhos.append(f"F8_estado_inesperado_{estado['F8'].lower()}")
    if vermelhos:
        return VERMELHO, sorted(set(vermelhos))
    if ambares:
        return AMBAR, sorted(set(ambares))
    return VERDE, ["todas_as_regras_do_verde_cumpridas"]


def gerar_relatorio(ciclo, agora=None):
    """Monta o relatório de campos fechados. Nunca levanta por causa do `ciclo`: entrada ruim vira VERMELHO sem repetir o conteúdo."""
    agora = agora or datetime.now(timezone.utc)
    if agora.tzinfo is None:
        raise ValueError("horário sem fuso")
    base = {"schema": 1, "gerado_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "n": 1}
    try:
        if not isinstance(ciclo, dict):
            return {**base, **_fechado("ciclo_nao_e_objeto")}
        etapas, erros = _etapas(ciclo)
        if erros:
            return {**base, **_fechado(erros[0])}
        semaforo, motivos = _decidir(ciclo, etapas, agora)
        ev, janela, cont, niv = ciclo["evento"], ciclo["janela"], ciclo.get("contagens"), ciclo.get("niveis")
        if not (isinstance(cont, dict) and _int(cont.get("eventos_gravados")) and _int(cont.get("eventos_recusados"))):
            return {**base, **_fechado("contagens_ausentes_ou_invalidas")}
        if not (isinstance(niv, dict) and set(niv) <= set(NIVEIS) and all(_int(v) for v in niv.values())):
            return {**base, **_fechado("niveis_ausentes_ou_invalidos")}
        lacunas = ciclo.get("lacunas", [])
        if not (isinstance(lacunas, list) and len(lacunas) <= 10 and all(isinstance(x, str) and LACUNA.fullmatch(x) for x in lacunas)):
            return {**base, **_fechado("lacunas_invalidas")}
        aberta, fechada = _dt(janela["aberta_em"]), _dt(janela.get("fechada_em"))
        horas = round(((fechada or agora) - aberta).total_seconds() / 3600, 1)
        relatorio = {
            **base, "semaforo": semaforo, "motivos": motivos, "preflights": {m: ciclo["preflights"][m] for m in PREVOOS},
            "janela": {"aberta_em": janela["aberta_em"], "fechada_em": janela.get("fechada_em"), "duracao_horas": horas},
            "evento": {"id": ev["id"], "commit_sha": ev["commit_sha"][:12], "hash_corpo": ev["hash_corpo"][:12], "readback": ev["readback"]},
            "contagens": {"eventos_gravados": cont["eventos_gravados"], "eventos_recusados": cont["eventos_recusados"]},
            "niveis": {k: niv[k] for k in NIVEIS if k in niv}, "etapas": etapas,
            "lacunas": list(LACUNAS_PADRAO) + [x for x in lacunas if x not in LACUNAS_PADRAO], "nao_provado": list(NAO_PROVADO),
        }
        validar_relatorio(relatorio)
        return relatorio
    except (KeyError, TypeError, ValueError, AttributeError):
        return {**base, **_fechado("erro_inesperado_na_montagem")}


def validar_relatorio(r):
    """Recusa campo fora da lista fechada, texto proibido e qualquer promessa de ganho (S11-R1, R11). Levanta ValueError."""
    if not isinstance(r, dict) or set(r) != set(TOPO) and not (set(r) == {"schema", "gerado_em", "n", "semaforo", "motivos"}):
        raise ValueError("campos do relatório fora da lista fechada")
    if r.get("n") != 1 or r.get("schema") != 1:
        raise ValueError("relatório deve declarar n=1 e schema 1")
    texto = json.dumps(r, ensure_ascii=False)
    if PROIBIDO.search(texto):
        raise ValueError("texto proibido no relatório")
    if "etapas" in r:
        if [e["etapa"] for e in r["etapas"]] != list(ETAPAS):
            raise ValueError("as oito etapas devem aparecer, em ordem")
        if r["nao_provado"] != list(NAO_PROVADO):
            raise ValueError("lista Não provado alterada")
        for e in r["etapas"]:
            if set(e) != {"etapa", "estado", "quem", "prova", "desconhecido"}:
                raise ValueError("campos da etapa fora da lista fechada")
    return r


def para_markdown(r):
    """Apresentação derivada do JSON, sem campo novo; termina com a linha "Não provado:" e a lista (S11-R13)."""
    validar_relatorio(r)
    linhas = ["# Relatório do ciclo do piloto", "", f"- Gerado em: {r['gerado_em']} (N={r['n']})", f"- **Semáforo: {r['semaforo']}**",
              "- Motivos: " + ", ".join(r["motivos"])]
    if "etapas" in r:
        linhas += ["- Pré-voos: " + ", ".join(f"{m} {v}" for m, v in r["preflights"].items()),
                   f"- Janela: aberta {r['janela']['aberta_em']}, fechada {r['janela']['fechada_em']}, {r['janela']['duracao_horas']} h",
                   f"- Evento: {r['evento']['id']}, commit {r['evento']['commit_sha']}, hash {r['evento']['hash_corpo']}, readback {r['evento']['readback']}",
                   f"- Contagens: {r['contagens']['eventos_gravados']} gravado(s), {r['contagens']['eventos_recusados']} recusado(s)",
                   "- Níveis (quantidade de tópicos por nível): " + (", ".join(f"{k}: {v}" for k, v in r["niveis"].items()) or "nenhum"),
                   "", "| Etapa | Estado | Quem | Prova | O que segue desconhecido |", "|---|---|---|---|---|"]
        linhas += [f"| {e['etapa']} | {e['estado']} | {e['quem']} | {e['prova']} | {e['desconhecido']} |" for e in r["etapas"]]
        linhas += ["", "Lacunas:"] + [f"- {x}" for x in r["lacunas"]]
    linhas += ["", "Não provado:"] + [f"- {x}" for x in r.get("nao_provado", NAO_PROVADO)]
    return "\n".join(linhas) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ciclo", required=True, help="arquivo JSON com as leituras do ciclo (nenhuma rede é usada aqui)")
    ap.add_argument("--markdown", action="store_true", help="imprime o Markdown derivado em vez do JSON")
    a = ap.parse_args(argv)
    try:
        with open(a.ciclo, encoding="utf-8") as arq:
            ciclo = json.load(arq)
    except (OSError, ValueError):
        ciclo = None
    r = gerar_relatorio(ciclo)
    print(para_markdown(r) if a.markdown else json.dumps(r, ensure_ascii=False, indent=2))
    return {VERDE: 0, AMBAR: 3, VERMELHO: 1}[r["semaforo"]]


if __name__ == "__main__":
    sys.exit(main())
