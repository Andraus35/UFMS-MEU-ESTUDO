"""Pré-voo do piloto (S11-R2, S11-R10): conferência SOMENTE LEITURA, tudo ou nada, com LEITURAS INJETADAS.

Função pura e fail-closed: não faz rede, não lê credencial, não grava nada e não chama modelo. Quem tem a credencial de leitura (o
proprietário no Termux, ou o teste com fixtures sintéticas) entrega as leituras já feitas; este módulo só DECIDE. Leitura ausente,
malformada ou indisponível conta como VERMELHO (fecha por padrão).

Três modos (S11-R2, R3, R12): `abertura` (as duas flags falsas, repouso), `pos_janela` (depois de mesclar a janela e reinstalar o
fluxo: a flag do fluxo VERDADEIRA no SHA fixado, a do público SEMPRE falsa) e `repouso` (depois do fechamento e da reinstalação:
as duas falsas e o hash do fluxo conferido).

Cada item devolve VERDE, AMBAR ou VERMELHO (S11-R10). O resultado geral é o PIOR dos itens e só é VERDE se todos forem VERDES
(tudo ou nada). Gatilhos VERMELHOS valem mesmo no pré-voo, antes de qualquer escrita. A saída traz só identificadores, booleanos e
prefixos de 12 caracteres de hash: nunca segredo, token ou dado pessoal (a saída é varrida antes de sair).

Códigos de saída da linha de comando: 0 VERDE, 1 VERMELHO (inclui arquivo ilegível), 3 ÂMBAR; 2 é de uso incorreto (argparse).

Limites: prova o que as leituras injetadas dizem; NÃO prova que elas foram feitas contra o GitHub real (isso é o roteiro do Termux,
ato do proprietário) e NÃO liga nem desliga nenhuma flag.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

from private_persistence_guard import PersistenceBlocked
from projection_generator import gerar_projecao
from session_read_guard import check_consent_v4

MODOS = ("abertura", "pos_janela", "repouso")
VERDE, AMBAR, VERMELHO = "VERDE", "AMBAR", "VERMELHO"
ORDEM = {VERDE: 0, AMBAR: 1, VERMELHO: 2}
JANELA = timedelta(hours=24)
MARGEM = timedelta(days=7)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
HASH64 = re.compile(r"^[0-9a-f]{64}$")
SEGREDO = re.compile(r"github_pat_|\bgh[pousr]_[A-Za-z0-9]|\bsk-[A-Za-z0-9]|-----BEGIN|@[A-Za-z0-9.-]+\.[a-z]{2,}|https?://", re.I)
REPOS = ("entrada", "dados")


def _item(ident, resultado, motivo):
    return {"id": ident, "resultado": resultado, "motivo": motivo}


def _bool(valor):
    return valor if isinstance(valor, bool) else None


def _dt(valor):
    if not isinstance(valor, str):
        return None
    try:
        quando = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    return quando if quando.tzinfo is not None else None


def _flags(leituras, modo):
    f = leituras.get("flags")
    if not isinstance(f, dict):
        return _item("flags", VERMELHO, "leitura das flags ausente")
    publico, fluxo = _bool(f.get("personal_results_writes_enabled")), _bool(f.get("private_flow_promotion_enabled_no_sha_fixado"))
    if publico is None or fluxo is None:
        return _item("flags", VERMELHO, "flag ausente ou não booleana")
    if publico:
        return _item("flags", VERMELHO, "flag do público ligada (nunca liga)")
    esperado = modo == "pos_janela"
    if fluxo != esperado:
        return _item("flags", VERMELHO, f"flag do fluxo no SHA fixado deveria ser {str(esperado).lower()} no modo {modo}")
    return _item("flags", VERDE, f"flags conforme o modo {modo}")


def _sha(valor):
    return valor if isinstance(valor, str) and SHA40.fullmatch(valor) else None


def _fluxo(leituras):
    f = leituras.get("fluxo")
    if not isinstance(f, dict):
        return _item("fluxo_hash", VERMELHO, "leitura do fluxo ausente")
    instalado, esperado = f.get("hash_instalado"), f.get("hash_esperado")
    if not (isinstance(instalado, str) and isinstance(esperado, str) and HASH64.fullmatch(instalado) and HASH64.fullmatch(esperado)):
        return _item("fluxo_hash", VERMELHO, "hash do fluxo ausente ou malformado")
    # o hash esperado é o do modelo gerado PARA o SHA fixado: sem essa amarra, um esperado velho conferiria com um instalado velho
    if _sha(f.get("hash_esperado_sha")) is None or f.get("hash_esperado_sha") != f.get("sha_fixado"):
        return _item("fluxo_hash", VERMELHO, "hash esperado calculado para outro SHA que não o fixado (ou sem SHA declarado)")
    if instalado != esperado:
        return _item("fluxo_hash", VERMELHO, f"hash do fluxo diferente do esperado ({instalado[:12]} contra {esperado[:12]})")
    return _item("fluxo_hash", VERDE, f"hash do fluxo igual ao esperado ({instalado[:12]})")


def _sha_fixado(leituras):
    f = leituras.get("fluxo") if isinstance(leituras.get("fluxo"), dict) else {}
    fixado, main = _sha(f.get("sha_fixado")), _sha(leituras.get("main_sha"))
    if fixado is None or main is None:
        return _item("sha_fixado", VERMELHO, "SHA fixado ou HEAD da main ausente ou malformado")
    if fixado != main:
        return _item("sha_fixado", VERMELHO, f"SHA fixado {fixado[:12]} diferente do HEAD da main {main[:12]}: reinstalar o fluxo (ATUALIZAR)")
    return _item("sha_fixado", VERDE, f"SHA fixado igual ao HEAD da main ({main[:12]})")


def _repos(leituras):
    r = leituras.get("repositorios")
    if not isinstance(r, dict):
        return [_item("repositorios", VERMELHO, "leitura dos repositórios ausente")]
    itens = []
    for nome in REPOS:
        d = r.get(nome)
        if not isinstance(d, dict):
            itens.append(_item(f"repo_{nome}", VERMELHO, "leitura do repositório ausente"))
            continue
        privado, fork = _bool(d.get("private")), _bool(d.get("fork"))
        forks, colab, convites = d.get("forks_count"), d.get("colaboradores"), d.get("convites")
        if privado is None or fork is None or any(type(x) is not int or x < 0 for x in (forks, colab, convites)):
            itens.append(_item(f"repo_{nome}", VERMELHO, "campos do repositório ausentes ou malformados"))
        elif not privado:
            itens.append(_item(f"repo_{nome}", VERMELHO, "repositório NÃO privado"))
        elif fork or forks > 0 or colab > 1 or convites > 0:
            itens.append(_item(f"repo_{nome}", AMBAR, "fork, colaborador extra ou convite a corrigir"))
        else:
            itens.append(_item(f"repo_{nome}", VERDE, "privado, sem forks e sem convites"))
    return itens


def _consentimento(leituras, agora):
    try:
        versao = check_consent_v4(leituras.get("consentimento"), agora)
    except PersistenceBlocked as exc:
        return _item("consentimento_v4", VERMELHO, str(exc)[:120])
    return _item("consentimento_v4", VERDE, f"consentimento {versao} íntegro")


def _tokens(leituras, agora):
    t = leituras.get("tokens")
    if not isinstance(t, list) or not t:
        return _item("tokens", VERMELHO, "leitura da validade dos tokens ausente")
    curtos = []
    for token in t:
        nome = token.get("nome") if isinstance(token, dict) else None
        expira = _dt(token.get("expira_em")) if isinstance(token, dict) else None
        if not (isinstance(nome, str) and re.fullmatch(r"[A-Za-z0-9_ -]{1,40}", nome)) or expira is None:
            return _item("tokens", VERMELHO, "token sem nome válido ou sem data de expiração com fuso")
        if expira <= agora:
            return _item("tokens", VERMELHO, "token já expirado: " + nome)
        if expira - agora <= JANELA + MARGEM:  # "maior que a janela mais 7 dias": exatamente 8 dias NÃO basta
            curtos.append(nome)
    if curtos:
        return _item("tokens", AMBAR, "validade menor que a janela mais 7 dias: " + ", ".join(sorted(curtos)))
    return _item("tokens", VERDE, "validade maior que a janela mais 7 dias")


def _ci(leituras):
    c = leituras.get("ci")
    if not isinstance(c, dict):
        return _item("ci", VERMELHO, "leitura da CI ausente")
    head, main = _sha(c.get("head_sha")), _sha(leituras.get("main_sha"))
    concl = c.get("conclusoes")
    if head is None or main is None or not isinstance(concl, list) or not concl or not all(isinstance(x, str) for x in concl):
        return _item("ci", VERMELHO, "leitura da CI malformada")
    if head != main:
        return _item("ci", AMBAR, "CI lida em outro SHA que não o HEAD da main")
    if any(x != "success" for x in concl):
        return _item("ci", AMBAR, "CI do HEAD não está toda verde")
    return _item("ci", VERDE, f"CI verde no HEAD ({head[:12]})")


def _contraprova_gerador(agora):
    """S11-R2(h): a função `gerar_projecao` chamada direto SEM consentimento v4 deve LEVANTAR; se não levantar, o guarda falhou."""
    for consentimento in (None, {"version": "v3"}):
        try:
            gerar_projecao([], [], consentimento, agora)
        except PersistenceBlocked:
            continue
        return _item("contraprova_gerador", VERMELHO, "o gerador NÃO recusou sem consentimento v4")
    return _item("contraprova_gerador", VERDE, "o gerador recusa sem consentimento v4 (ausente e v3)")


def _janela(leituras, modo, agora):
    if modo != "pos_janela":
        return None
    aberta = _dt(leituras.get("janela_aberta_em"))
    if aberta is None:
        return _item("janela", VERMELHO, "hora de abertura da janela ausente ou sem fuso")
    if aberta > agora:
        return _item("janela", VERMELHO, "abertura da janela no futuro")
    if agora - aberta > JANELA:
        return _item("janela", VERMELHO, "janela aberta há mais de 24 h")
    return _item("janela", VERDE, "janela aberta há menos de 24 h")


def executar(leituras, modo, agora=None):
    """Decide o pré-voo. Nunca levanta por causa das leituras: tudo que não conferir vira item VERMELHO."""
    agora = agora or datetime.now(timezone.utc)
    if modo not in MODOS:
        raise ValueError("modo inválido")
    if agora.tzinfo is None:
        raise ValueError("horário sem fuso")
    if not isinstance(leituras, dict):
        leituras = {}
    itens = []
    for ident, fn in (("flags", lambda: _flags(leituras, modo)), ("fluxo_hash", lambda: _fluxo(leituras)),
                      ("sha_fixado", lambda: _sha_fixado(leituras)), ("repositorios", lambda: _repos(leituras)),
                      ("consentimento_v4", lambda: _consentimento(leituras, agora)), ("tokens", lambda: _tokens(leituras, agora)),
                      ("ci", lambda: _ci(leituras)), ("contraprova_gerador", lambda: _contraprova_gerador(agora)),
                      ("janela", lambda: _janela(leituras, modo, agora))):
        try:
            produzido = fn()
        except Exception as exc:  # leitura que quebra a conferência fecha em VERMELHO, nunca derruba o relatório
            produzido = {"id": ident, "resultado": VERMELHO, "motivo": "erro inesperado na conferência (" + type(exc).__name__ + ")"}
        if produzido is None:
            continue
        itens.extend(produzido if isinstance(produzido, list) else [produzido])
    pior = max((i["resultado"] for i in itens), key=ORDEM.get)
    saida = {"modo": modo, "resultado": pior, "itens": itens, "gerado_em": agora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if SEGREDO.search(json.dumps(saida, ensure_ascii=False)):
        # item literal, sem passar pelo auxiliar que pode ter carregado o segredo: o descarte nunca repete o conteúdo descartado
        return {"modo": modo, "resultado": VERMELHO, "gerado_em": saida["gerado_em"],
                "itens": [{"id": "saida", "resultado": VERMELHO, "motivo": "a saída continha padrão de segredo e foi descartada"}]}
    return saida


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--modo", choices=MODOS, required=True)
    ap.add_argument("--leituras", required=True, help="arquivo JSON com as leituras já feitas (nenhuma rede é usada aqui)")
    a = ap.parse_args(argv)
    try:
        with open(a.leituras, encoding="utf-8") as arq:
            leituras = json.load(arq)
    except (OSError, ValueError):
        leituras = None
    saida = executar(leituras, a.modo)
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return {VERDE: 0, AMBAR: 3, VERMELHO: 1}[saida["resultado"]]  # 2 é o código de uso incorreto do argparse: nunca é AMBAR


if __name__ == "__main__":
    sys.exit(main())
