"""Volta do N1 (E41, lote VOLTA-N1): Zapia -> conferência -> relatório do Tutor -> entrada do Coach -> proposta do Coach pela caixa. OFFLINE.

Função determinística, sem rede, sem escrita e sem LLM. Lê as respostas que a Zapia gravou em `comandos/respostas/<nome>` do checkout de `entrada`
(DADO NÃO CONFIÁVEL), confere cada uma com `notebook_response_check` (forma, hash, citação aberta, contraprova e, na questão C1, a âncora do gabarito) e devolve:

  - `relatorio_tutor`: só códigos, estados e booleanos (NUNCA o texto do Notebook), para o Tutor verificar contra a fonte (S10-R7b);
  - `entrada_coach`: o que o Coach pode receber (sem texto do Notebook, sem dado do aluno);
  - `avaliar_proposta_coach`: a proposta do Coach (comando `enviar_mensagem`) só passa se vier pela caixa (`command_box`) e se NÃO repassar texto da
    resposta do Notebook nem afirmar o que o relatório não sustenta.

Confiança: `B` (autorrelato da Zapia) ou `B+captura` quando o proprietário traz o registro de captura (relógio visível) — captura é ato dele; o código só a
registra, não a verifica. Limites: não prova que a resposta veio do Notebook nem que o gabarito do Notebook acertou; a autoria do comando é declarada (S6-R7).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

try:
    import agent_commands
    import aprovacao_comando
    import command_box
    import content_filters
    import notebook_response_check as nrc
    import subagent_harness
except ModuleNotFoundError:  # uso como pacote
    from scripts import agent_commands, aprovacao_comando, command_box, content_filters, subagent_harness
    from scripts import notebook_response_check as nrc

PRONTO = "PRONTO_PARA_O_TUTOR"
NAO_PROVADO = "N1_NAO_PROVADO"
_JANELA_ECO = 25  # tamanho mínimo (caracteres) de trecho da resposta do Notebook que a proposta do Coach não pode repetir


def _norm(texto) -> str:
    base = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"\s+", " ", base).strip()


def validar_captura(captura):
    """Registro de captura (ato do proprietário): `{relogio_visivel: true, descricao: texto curto sem dado pessoal}`. None se válido, senão o código."""
    if captura is None:
        return None
    if not isinstance(captura, dict) or set(captura) != {"relogio_visivel", "descricao"}:
        return "CAPTURA_FORA_DO_FORMATO"
    if captura["relogio_visivel"] is not True:
        return "CAPTURA_SEM_RELOGIO"
    d = captura["descricao"]
    if not isinstance(d, str) or not d.strip() or len(d) > 200 or agent_commands.scan_text(d, html=True) or content_filters.tem_url(d) or agent_commands.texto_de_questao(d):
        return "CAPTURA_DESCRICAO_INVALIDA"
    return None


def processar(meta: dict, fonte_texto: str, respostas: dict, captura=None, aprovacoes=None, chave_publica=None) -> dict:
    """`meta`: o meta.json do kit; `respostas`: nome -> bytes (ou None se a Zapia ainda não gravou). Devolve o relatório (sem o texto do Notebook)."""
    erro_captura = validar_captura(captura)
    itens, algum_parado, algum_pendente, aprov_ruim = [], False, False, False
    for nome in sorted(meta["itens"]):
        info = meta["itens"][nome]
        bruto = respostas.get(nome)
        linha = {"comando": nome, "contraprova": bool(info["contraprova"]), "tem_gabarito": info.get("ancora_gabarito") is not None}
        if not bruto:
            linha.update(estado="PENDENTE", conferencia=None)
            algum_pendente = True
        else:
            esperado = {"nome": nome, "hash_corpo": info["hash_corpo"], "fonte_nome": meta["fonte_nome"]}
            codigo = nrc.conferir(bruto, esperado, fonte_texto, contraprova=bool(info["contraprova"]), ancora_gabarito=info.get("ancora_gabarito"))
            try:
                estado = json.loads(bytes(bruto).decode("utf-8")).get("estado")
            except (ValueError, UnicodeDecodeError, AttributeError):
                estado = None
            if codigo is None and estado == "PARADO":
                linha.update(estado="PARADO", conferencia="PARADA_REGISTRADA")
                algum_parado = True
            else:
                linha.update(estado="CONFERIDA" if codigo is None else "RECUSADA", conferencia=codigo)
        if aprovacoes is None:
            linha["autoria"] = "declarada"
        else:  # limite 3: aprovação destacada do proprietário sobre o hash do comando (chave fora do modelo); verificada offline
            motivo = aprovacao_comando.verificar(aprovacoes.get(nome), info["hash_corpo"], chave_publica)
            linha["autoria"] = "aprovada_pelo_proprietario" if motivo is None else "APROVACAO_RECUSADA:" + motivo
            aprov_ruim = aprov_ruim or motivo is not None
        itens.append(linha)
    todos_ok = all(i["estado"] == "CONFERIDA" for i in itens)
    return {
        "veredito": PRONTO if todos_ok and erro_captura is None and not aprov_ruim else NAO_PROVADO,
        "confianca": "B+captura" if captura is not None and erro_captura is None else "B",
        "captura": "ausente" if captura is None else (erro_captura or "registrada"),
        "pendentes": sum(1 for i in itens if i["estado"] == "PENDENTE"), "parados": sum(1 for i in itens if i["estado"] == "PARADO"),
        "relatorio_tutor": itens,
        "ressalvas": ["autorrelato da Zapia", "gabarito conferido só pela citação da âncora, não pela resposta do Notebook", "verificação contra a fonte é do Tutor (S10-R7b)"]
                     + (["há resposta pendente"] if algum_pendente else []) + (["há resposta PARADA: o teste não foi provado"] if algum_parado else []),
    }


def entrada_coach(relatorio: dict) -> dict:
    """Só o que o Coach pode receber: contagens e veredito. Sem texto do Notebook, sem dado do aluno (E0), sem desempenho."""
    itens = relatorio["relatorio_tutor"]
    return {"origem": "relatorio_tutor_n1", "veredito": relatorio["veredito"], "confianca": relatorio["confianca"],
            "conferidas": sum(1 for i in itens if i["estado"] == "CONFERIDA"), "total": len(itens), "pendentes": relatorio["pendentes"],
            "parados": relatorio["parados"], "dado_do_aluno": False}


def _texto_da_resposta(bruto) -> str:
    try:
        r = json.loads(bytes(bruto).decode("utf-8"))
        return f"{r.get('texto_literal', '')} {r.get('citacao_trecho', '')}"
    except (ValueError, UnicodeDecodeError, AttributeError):
        return ""


def avaliar_proposta_coach(proposta, respostas: dict, agora_utc=None) -> dict:
    """Proposta do Coach (comando `enviar_mensagem`) pela CAIXA, mais a guarda de eco: não pode repetir trecho (>= 25 caracteres) do que o Notebook respondeu."""
    if not isinstance(proposta, dict) or proposta.get("origin") != "coach" or proposta.get("operation") != "enviar_mensagem":
        return {"status": "RECUSADA", "codigo": "PROPOSTA_NAO_E_DO_COACH", "etapa": "guarda"}  # a volta só aceita mensagem do Coach
    texto = ((proposta or {}).get("params") or {}).get("texto") if isinstance(proposta, dict) else None
    if isinstance(texto, str):
        alvo = _norm(texto)
        for bruto in respostas.values():
            fonte = _norm(_texto_da_resposta(bruto)) if bruto else ""
            for i in range(0, max(0, len(fonte) - _JANELA_ECO + 1)):
                if fonte[i:i + _JANELA_ECO] in alvo:
                    return {"status": "RECUSADA", "codigo": "ECO_DO_NOTEBOOK", "etapa": "guarda"}
    return subagent_harness.avaliar("coach-n1.json", proposta, subagent_harness.contexto_sintetico(**({"agora": agora_utc} if agora_utc else {})))


def _ler_aprovacoes(pasta: Path, meta: dict) -> dict:
    saida = {}
    for nome in meta["itens"]:
        arq = Path(pasta) / (nome.replace(".json", "") + ".aprovacao.json")
        try:
            saida[nome] = json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saida[nome] = None
    return saida


def _ler_respostas(entrada: Path, meta: dict) -> dict:
    saida = {}
    for nome in meta["itens"]:
        p = Path(entrada) / "comandos" / "respostas" / nome
        saida[nome] = p.read_bytes() if p.is_file() else None
    return saida


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Volta do N1 (offline): confere as respostas e prepara o relatório do Tutor e a entrada do Coach.")
    p.add_argument("--entrada", required=True, help="checkout local de `entrada`")
    p.add_argument("--meta", required=True)
    p.add_argument("--fonte", required=True)
    p.add_argument("--captura", help="JSON {relogio_visivel, descricao} trazido pelo proprietário")
    p.add_argument("--aprovacoes", help="pasta com <nome>.aprovacao.json do proprietário (aprovacao_comando.py aprovar)")
    p.add_argument("--publica", help="chave pública do proprietário (hexadecimal), exigida com --aprovacoes")
    p.add_argument("--proposta-coach", help="JSON do comando enviar_mensagem proposto pelo Coach")
    a = p.parse_args(argv)
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    respostas = _ler_respostas(Path(a.entrada), meta)
    captura = json.loads(Path(a.captura).read_text(encoding="utf-8")) if a.captura else None
    aprov = _ler_aprovacoes(Path(a.aprovacoes), meta) if a.aprovacoes else None
    rel = processar(meta, Path(a.fonte).read_text(encoding="utf-8"), respostas, captura, aprov, a.publica)
    saida = {"relatorio": rel, "entrada_coach": entrada_coach(rel)}
    if a.proposta_coach:
        saida["proposta_coach"] = avaliar_proposta_coach(json.loads(Path(a.proposta_coach).read_text(encoding="utf-8")), respostas, datetime.now(timezone.utc))
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return 0 if rel["veredito"] == PRONTO else 2


if __name__ == "__main__":
    sys.exit(main())
