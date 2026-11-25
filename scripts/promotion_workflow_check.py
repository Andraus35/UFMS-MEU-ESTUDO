"""Teste estático do modelo do fluxo de promoção (S6-R4/R5/R6, tarefa C2).

Confere o TEXTO de `config/modelos_fluxo/promover.yml`; só stdlib, sem rede, sem escrita. Falha fechada: devolve a lista de
violações e o CLI sai com código 1 se houver alguma.

Limites (S6-R13): isto prova o que o arquivo diz, não que o GitHub o execute assim, nem que o fluxo instalado no repositório
`entrada` seja este modelo (conferência do hash instalado é da C3/C5), nem que o `promotion_runner.py` exista. O próprio fluxo
conferir o seu hash não é à prova de quem consegue alterar o arquivo e a execução ao mesmo tempo; o que o impede é a credencial
da Zapia não ter a permissão Workflows (prova real: C5).
"""
import argparse
import re
import sys
from pathlib import Path

try:
    from core import ROOT
except ModuleNotFoundError:
    from scripts.core import ROOT

MODELO = "config/modelos_fluxo/promover.yml"
VALIDADOR_REPO = "Andraus35/UFMS-MEU-ESTUDO"
PLACEHOLDER_SHA = "__VALIDADOR_SHA__"
PLACEHOLDER_GATE = "__VALIDADOR_GATE_SHA256__"
PLACEHOLDER_EMISSOR = "__VALIDADOR_EMISSOR_SHA256__"
TITULO_CAMPAINHA = "SINAL comando-promovido"
TRIGGERS_PERMITIDOS = frozenset({"push", "workflow_dispatch"})
# Contextos que o modelo pode interpolar (só em `env:`, nunca em `run:`); nenhum vem de texto controlável por terceiros.
EXPRESSOES_PERMITIDAS = frozenset({"github.token", "github.sha", "github.run_id", "github.repository",
                                   "secrets.DADOS_TOKEN", "vars.FLUXO_SHA256",
                                   "steps.contar.outputs.promovidos"})
ETAPAS_EM_ORDEM = ("Obter a fila no SHA do evento", "Conferir o hash do próprio fluxo",
                   "Obter o validador do público fixado por SHA",
                   "Promover com o portão (única etapa com o segredo do histórico)",
                   "Promover comandos da caixa (sem o segredo do histórico)",
                   "Contar os comandos promovidos (sem texto de comando)")
_EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PROIBIDOS_TEXTO = (
    (r"\bcurl\b|\bwget\b", "REDE_LIVRE"),
    (r"\bpip3?\s+install\b|\bnpm\b|\bnpx\b", "INSTALACAO_EXTERNA"),
    (r"\|\s*(?:ba)?sh\b", "PIPE_PARA_SHELL"),
    (r"\bgit\s+push\b", "PUSH_FORA_DO_PORTAO"),
    (r"\bset\s+-[a-z]*x|ACTIONS_STEP_DEBUG|ACTIONS_RUNNER_DEBUG", "DEPURACAO_QUE_VAZA_SEGREDO"),
    (r"\bprintenv\b|(?m:^\s*env\s*$)|\bset\s*$", "DESPEJO_DE_AMBIENTE"),
    (r"continue-on-error:\s*true", "BYPASS_CONTINUE_ON_ERROR"),
    (r"(?m)^\s*if:\s*(?:false|\$\{\{\s*false\s*\}\})\s*$", "BYPASS_IF_FALSE"),
    (r"\bset\s+\+e\b", "ERRO_IGNORADO"),
)


def _linhas(texto):
    return [(i + 1, l) for i, l in enumerate(texto.splitlines())]


def _indent(linha):
    return len(linha) - len(linha.lstrip(" "))


def _blocos_run(texto):
    """Devolve, para cada `run:`, (linha_inicial, corpo) — inline ou bloco literal."""
    saida, linhas, i = [], texto.splitlines(), 0
    while i < len(linhas):
        m = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", linhas[i])
        if m:
            base, resto, corpo = len(m.group(1)), m.group(2), []
            if resto.strip() in ("|", ">", "|-", ">-"):
                j = i + 1
                while j < len(linhas) and (not linhas[j].strip() or _indent(linhas[j]) > base):
                    corpo.append(linhas[j])
                    j += 1
                i = j - 1
            else:
                corpo.append(resto)
            saida.append((i + 1, "\n".join(corpo)))
        i += 1
    return saida


def _bloco_toplevel(texto, chave):
    """Linhas filhas do bloco de coluna 0 `chave:` (vazio se for `chave: {}` ou ausente)."""
    linhas, achou, filhos = texto.splitlines(), False, []
    for l in linhas:
        if re.match(r"^" + re.escape(chave) + r":\s*$", l):
            achou = True
            continue
        if achou:
            if l.strip() and _indent(l) == 0:
                break
            filhos.append(l)
    return achou, filhos


def verificar(texto, instanciado=False):
    """Lista de códigos de violação (vazia = o texto cumpre o contrato). `instanciado` exige SHA e hash reais."""
    if not isinstance(texto, str) or not texto.strip():
        return ["TEXTO_VAZIO"]
    v = []
    # gatilhos: só push e workflow_dispatch; nada que rode com entrada de fork, comentário ou issue
    achou, filhos = _bloco_toplevel(texto, "on")
    chaves = {re.match(r"^\s{2}([A-Za-z_]+):", l).group(1) for l in filhos if re.match(r"^\s{2}[A-Za-z_]+:", l)}
    if not achou or not chaves:
        v.append("GATILHO_AUSENTE")
    for c in sorted(chaves - TRIGGERS_PERMITIDOS):
        v.append("GATILHO_PROIBIDO:" + c)
    # permissões: vazias por padrão no topo; por job só contents
    if len(re.findall(r"(?m)^permissions:\s*\{\}\s*$", texto)) != 1:
        v.append("PERMISSOES_PADRAO_NAO_VAZIAS")
    if re.search(r"(?m)^permissions:\s*(?!\{\})\S", texto) or _bloco_toplevel(texto, "permissions")[1]:
        v.append("PERMISSOES_DE_TOPO_COM_CONTEUDO")
    jobs = _jobs(texto)
    if set(jobs) != {"promover", "campainha"}:
        v.append("JOBS_INESPERADOS")
    for nome_job, corpo_job in jobs.items():
        perms = _permissoes_do_job(corpo_job)
        esperado = {"promover": {"contents"}, "campainha": {"issues"}}.get(nome_job, set())
        for chave, valor in perms.items():
            if chave not in esperado or (chave == "issues" and valor != "write") or (chave == "contents" and valor not in ("read", "write")):
                v.append("PERMISSAO_NAO_PERMITIDA:%s:%s=%s" % (nome_job, chave, valor))
        if nome_job in jobs and set(perms) != esperado:
            v.append("PERMISSAO_DO_JOB_INCOMPLETA:" + nome_job)
    if re.search(r"write-all|read-all|id-token|\bworkflows:|\bactions:\s*(?:read|write)|\bpackages:|"
                 r"pull-requests:|\badministration:|\bsecrets:\s*(?:read|write)", texto):
        v.append("PERMISSAO_AMPLA_OU_SENSIVEL")
    # expressões: só a lista fechada e nunca dentro de `run:`
    for n, linha in _linhas(texto):
        for e in _EXPR.findall(linha):
            if e not in EXPRESSOES_PERMITIDAS:
                v.append("EXPRESSAO_NAO_PERMITIDA:" + e)
    for _, corpo in _blocos_run(texto):
        if "${{" in corpo:
            v.append("EXPRESSAO_EM_RUN")
    if not _blocos_run(texto):
        v.append("SEM_ETAPA_RUN")
    # `env:` global sem expressão (o segredo só entra na etapa que o usa)
    _, env_global = _bloco_toplevel(texto, "env")
    if any("${{" in l for l in env_global):
        v.append("EXPRESSAO_NO_ENV_GLOBAL")
    usos_segredo = [l for _, l in _linhas(texto) if "secrets.DADOS_TOKEN" in l]
    if len(usos_segredo) != 1 or _indent(usos_segredo[0]) < 10 or not re.match(r"^\s+DADOS_TOKEN:\s*\$\{\{ secrets\.DADOS_TOKEN \}\}\s*$", usos_segredo[0]):
        v.append("SEGREDO_FORA_DO_ENV_DA_ETAPA")
    # ações de terceiros só por SHA de 40 hex
    for n, linha in _linhas(texto):
        m = re.search(r"\buses:\s*(\S+)", linha)
        if m and not re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", m.group(1)):
            v.append("ACAO_NAO_FIXADA_POR_SHA:" + m.group(1))
    # SHA do validador e hash do portão fixados no próprio arquivo, do repositório público do projeto
    sha = re.findall(r"(?m)^  VALIDADOR_SHA:\s*(\S+)\s*$", texto)
    gate = re.findall(r"(?m)^  VALIDADOR_GATE_SHA256:\s*(\S+)\s*$", texto)
    repo = re.findall(r"(?m)^  VALIDADOR_REPO:\s*(\S+)\s*$", texto)
    if repo != [VALIDADOR_REPO]:
        v.append("VALIDADOR_REPO_DIVERGENTE")
    if len(sha) != 1 or not (_SHA40.fullmatch(sha[0]) or (not instanciado and sha[0] == PLACEHOLDER_SHA)):
        v.append("VALIDADOR_SHA_INVALIDO")
    if len(gate) != 1 or not (_HEX64.fullmatch(gate[0]) or (not instanciado and gate[0] == PLACEHOLDER_GATE)):
        v.append("VALIDADOR_HASH_INVALIDO")
    if re.search(r"(?mi)^\s*[\w-]*(?:ref|branch):\s*\S+|fetch\b[^\n]*\b(?:main|master|HEAD)\b[^\n]*\n|--branch", texto):
        v.append("VALIDADOR_POR_RAMO")
    # etapas obrigatórias, em ordem, com as conferências de hash e de SHA
    nomes = re.findall(r"(?m)^      - name:\s*(.+?)\s*$", texto)
    if [n for n in nomes if n in ETAPAS_EM_ORDEM] != list(ETAPAS_EM_ORDEM):
        v.append("ETAPAS_FORA_DE_ORDEM_OU_AUSENTES")
    por_nome = _etapas(texto)
    corpo_fluxo = por_nome.get(ETAPAS_EM_ORDEM[1], "")
    if "sha256sum" not in corpo_fluxo or "FLUXO_SHA256_ESPERADO" not in corpo_fluxo or "test -n" not in corpo_fluxo:
        v.append("SEM_CONFERENCIA_DO_HASH_DO_FLUXO")
    corpo_val = por_nome.get(ETAPAS_EM_ORDEM[2], "")
    if not ("rev-parse HEAD" in corpo_val and '"$VALIDADOR_SHA"' in corpo_val and "sha256sum scripts/promotion_gate.py" in corpo_val
            and '"$VALIDADOR_GATE_SHA256"' in corpo_val):
        v.append("SEM_CONFERENCIA_DO_VALIDADOR")
    corpo_fila = por_nome.get(ETAPAS_EM_ORDEM[0], "")
    if "rev-parse HEAD" not in corpo_fila or '"$EVENTO_SHA"' not in corpo_fila:
        v.append("SEM_CONFERENCIA_DO_SHA_DO_EVENTO")
    # a promoção chama o portão com o SHA fixado, nunca com o que a fila disser
    promover = por_nome.get(ETAPAS_EM_ORDEM[3], "")
    if "promotion_runner.py" not in promover or '--validador-sha "$VALIDADOR_SHA"' not in promover:
        v.append("PROMOCAO_SEM_SHA_FIXADO")
    # a caixa de comandos roda com o SHA fixado e SEM o segredo do histórico (S6-R6, R8)
    caixa = por_nome.get(ETAPAS_EM_ORDEM[4], "")
    if "command_box_runner.py" not in caixa or '--validador-sha "$VALIDADOR_SHA"' not in caixa:
        v.append("CAIXA_SEM_SHA_FIXADO")
    if "DADOS_TOKEN" in caixa or "secrets." in caixa:
        v.append("CAIXA_COM_SEGREDO_DO_HISTORICO")
    # campainha (ZAPIA-EMISSOR): job próprio, só `issues: write`, só depois da promoção, título fixo e corpo vazio
    emi = re.findall(r"(?m)^  VALIDADOR_EMISSOR_SHA256:\s*(\S+)\s*$", texto)
    if len(emi) != 1 or not (_HEX64.fullmatch(emi[0]) or (not instanciado and emi[0] == PLACEHOLDER_EMISSOR)):
        v.append("EMISSOR_HASH_INVALIDO")
    camp = jobs.get("campainha", "")
    if camp:
        if not re.search(r"(?m)^    needs:\s*promover\s*$", camp):
            v.append("CAMPAINHA_SEM_NEEDS")
        if len(re.findall(r"(?m)^    if:", camp)) != 1 or not re.search(r"(?m)^    if:\s*needs\.promover\.outputs\.promovidos != '0'\s*$", camp):
            v.append("CAMPAINHA_SEM_CONDICAO_DE_PROMOCAO")
        if "secrets." in camp or "DADOS_TOKEN" in camp or "contents:" in camp or "fila_repo" in camp:
            v.append("CAMPAINHA_COM_SEGREDO_OU_FILA")
        etapas_c = _etapas(camp)
        obter = etapas_c.get("Campainha, obter o validador do público fixado por SHA", "")
        if not ('"$VALIDADOR_SHA"' in obter and "rev-parse HEAD" in obter and "sha256sum scripts/sinal_emissor.py" in obter
                and '"$VALIDADOR_EMISSOR_SHA256"' in obter):
            v.append("CAMPAINHA_SEM_CONFERENCIA_DO_EMISSOR")
        abrir = etapas_c.get("Campainha, abrir a issue-sinal (título fixo, corpo vazio)", "")
        if "sinal_emissor.py" not in abrir or "--emitir" not in abrir or "--entrada-repo" not in abrir:
            v.append("CAMPAINHA_SEM_EMISSOR")
        if re.search(r"--(?:titulo|title|corpo|body|texto|nome)\b|\bgh\s+issue\b|\bcurl\b", abrir):
            v.append("CAMPAINHA_COM_TEXTO_LIVRE")
        if len(etapas_c) != 2:
            v.append("CAMPAINHA_COM_ETAPAS_EXTRAS")
    else:
        v.append("CAMPAINHA_AUSENTE")
    saida = re.search(r"(?m)^    outputs:\s*\n\s+promovidos:\s*\$\{\{ steps\.contar\.outputs\.promovidos \}\}\s*$", jobs.get("promover", ""))
    if not saida:
        v.append("PROMOVER_SEM_SAIDA_DE_CONTAGEM")
    contar = por_nome.get(ETAPAS_EM_ORDEM[5], "")
    if "sinal_emissor.py" not in contar or "--contar" not in contar or "GITHUB_OUTPUT" not in contar or "resumo_caixa.json" not in contar:
        v.append("CONTAGEM_FORA_DO_CONTRATO")
    if "resumo_caixa.json" not in caixa:
        v.append("CAIXA_SEM_RESUMO_PARA_CONTAGEM")
    # execução serial e idempotente
    if not re.search(r"(?m)^concurrency:\s*\n\s+group:\s*\S+\s*\n\s+cancel-in-progress:\s*false\s*$", texto):
        v.append("CONCORRENCIA_NAO_SERIAL")
    if not jobs or any(not re.search(r"(?m)^    timeout-minutes:\s*\d+\s*$", c) for c in jobs.values()):
        v.append("SEM_TIMEOUT")
    # vedados em qualquer lugar
    for padrao, codigo in _PROIBIDOS_TEXTO:
        if re.search(padrao, "\n".join(c for _, c in _blocos_run(texto)) or ""):
            v.append(codigo)
    for n, linha in _linhas(texto):
        if re.search(r"\b(?:echo|printf)\b[^\n]*DADOS_TOKEN|DADOS_TOKEN[^\n]*>>?\s*\S", linha) and "run" in texto:
            v.append("SEGREDO_IMPRESSO_OU_GRAVADO")
            break
    return sorted(set(v), key=v.index)


def _jobs(texto):
    """Mapa job -> texto do job (filhos de `jobs:` em coluna 2)."""
    achou, filhos = _bloco_toplevel(texto, "jobs")
    out, nome, buf = {}, None, []
    for l in filhos:
        m = re.match(r"^  ([A-Za-z_][\w-]*):\s*$", l)
        if m:
            if nome is not None:
                out[nome] = "\n".join(buf)
            nome, buf = m.group(1), []
        elif nome is not None:
            buf.append(l)
    if nome is not None:
        out[nome] = "\n".join(buf)
    return out


def _permissoes_do_job(corpo):
    """Chaves e valores do bloco `permissions:` de coluna 4 do job (vazio se ausente)."""
    saida, dentro = {}, False
    for l in corpo.splitlines():
        if re.match(r"^    permissions:\s*$", l):
            dentro = True
            continue
        if dentro:
            m = re.match(r"^      ([\w-]+):\s*(\S+)\s*$", l)
            if not m:
                break
            saida[m.group(1)] = m.group(2)
    return saida


def _etapas(texto):
    """Mapa nome -> texto da etapa (da linha `- name:` até a próxima etapa)."""
    out, nome, buf = {}, None, []
    for linha in texto.splitlines():
        m = re.match(r"^      - name:\s*(.+?)\s*$", linha)
        if m:
            if nome is not None:
                out[nome] = "\n".join(buf)
            nome, buf = m.group(1), []
        elif nome is not None:
            buf.append(linha)
    if nome is not None:
        out[nome] = "\n".join(buf)
    return out


def verificar_arquivo(root=ROOT, instanciado=False):
    return verificar((Path(root) / MODELO).read_text(encoding="utf-8"), instanciado=instanciado)


def main(argv=None):
    p = argparse.ArgumentParser(description="Teste estático do modelo do fluxo de promoção (C2).")
    p.add_argument("--check", action="store_true")
    p.add_argument("--root", default=str(ROOT))
    p.add_argument("--instanciado", action="store_true", help="exige SHA e hash reais no lugar dos marcadores")
    p.add_argument("--arquivo", help="confere este arquivo (o fluxo gerado para instalar) em vez do modelo do repositório")
    a = p.parse_args(argv)
    if a.arquivo:
        violacoes = verificar(Path(a.arquivo).read_text(encoding="utf-8"), instanciado=a.instanciado)
    else:
        violacoes = verificar_arquivo(a.root, a.instanciado)
    if violacoes:
        print("FALHA: " + ", ".join(violacoes))
        return 1
    print("OK: modelo do fluxo de promoção cumpre o contrato estático (S6-R4/R5/R6)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
