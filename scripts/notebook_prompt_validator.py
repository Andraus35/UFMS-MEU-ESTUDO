"""Validador offline do prompt do Tutor ao Gemini Notebook (N2; S10-R3, S2-R7; fecha o PR-002). Falha fechada.

O Tutor escreve o prompt (D-23); este módulo só **confere** antes de a Zapia enviá-lo (comando `enviar_prompt_notebook`).
Sem rede, sem Zapia, sem Google, sem gravação, sem credencial. Devolve **só código e nome do campo**, nunca o texto do
prompt. Na dúvida recusa o prompt inteiro: nada é limpo em silêncio. Um prompt aceito sai em texto canônico, montado
pelo próprio módulo a partir dos campos, para que o que se envia seja exatamente o que foi validado.

Contrato (S10-R3): cinco campos de texto, todos obrigatórios e nenhum a mais: `topico`, `lacuna`, `metodo`,
`exigencia_fonte` e `formato_saida`. Proibido: dado pessoal, CPF, e-mail, credencial, token, exportação bruta, captura
de tela, texto integral de questão, desempenho individual, endereço da web e HTML. Tamanho total no limite do esquema
de comandos (2000 caracteres).

Limites: o filtro de instrução embutida, dado pessoal e desempenho é **heurístico** (reaproveita o da L1) e aceita falso
positivo; não prova que o Tutor escreveu o prompt (E-04), nem que a Zapia o envia como validado, nem a fidelidade do
Notebook. A qualidade pedagógica do prompt é revisão humana.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from dataclasses import dataclass

try:
    import agent_commands
    import platform_read_guard
except ModuleNotFoundError:  # pragma: no cover - uso como pacote
    from scripts import agent_commands, platform_read_guard

CAMPOS = ("topico", "lacuna", "metodo", "exigencia_fonte", "formato_saida")
LIMITES = {"topico": 120, "lacuna": 400, "metodo": 400, "exigencia_fonte": 300, "formato_saida": 300}
ROTULOS = {"topico": "Tópico", "lacuna": "Lacuna", "metodo": "Método", "exigencia_fonte": "Exigência de fonte",
           "formato_saida": "Formato de saída"}
# nomes de campo que denunciam dado que não pode ir ao Google (além dos proibidos pelo esquema de comandos)
CHAVES_PROIBIDAS_EXTRA = frozenset({
    "cpf", "email", "e-mail", "nome", "telefone", "desempenho", "acertos", "erros", "resultado", "nota", "captura", "screenshot",
    "exportacao", "exportação", "export", "enunciado", "comentario", "comentário", "html", "questao", "questão", "alternativas",
    "gabarito", "arquivo", "anexo", "url", "link",
})
_INVISIVEIS = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff\u00ad]")  # zero-width, bidi, soft hyphen
_CONTROLE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_URL = re.compile(r"(?:https?|ftp|file|data|javascript):|\bwww\.|//[a-z0-9.-]+\.[a-z]{2,}", re.I)
_DESEMPENHO = re.compile(
    r"\b(?:meu|minha|meus|minhas|my)\s+(?:desempenho|nota|notas|acertos?|erros?|resultados?|score|percentual)\b"
    r"|\b(?:acertei|errei|gabaritei)\b|\b\d+\s*(?:acertos?|erros?)\b|\b\d+\s*%\s*(?:de\s+)?(?:acerto|erro|aproveitamento)",
    re.I)
# complementa o filtro da L1 com ordens de esquecer/substituir regras e de revelar o sistema (heurístico; ver os limites no topo)
_INSTRUCAO_EXTRA = re.compile(
    r"\besquec\w* (?:tudo|todas?|as|os|suas?|seus?|o que)\b|\bforget (?:everything|all|your|the|previous)\b|\bdesconsidere\b|\bdesconsiderem\b"
    r"|\bfrom now on\b|\bde agora em diante\b|\breveal\b.{0,30}\b(?:prompt|instructions?|rules)\b"
    r"|\brevel\w+\b.{0,30}\b(?:prompt|instruc\w*|regras)\b|\bdeveloper mode\b|\bmodo desenvolvedor\b|\bnovo papel\b|\bnew role\b",
    re.I | re.S)
_ALTERNATIVA = re.compile(r"(?m)^\s*\(?[A-Ea-e][\).:]\s+\S")
_ALTERNATIVA_NA_LINHA = re.compile(r"(?:^|(?<=\s))\(?[A-Ea-e]\)\s+\S")  # "(A) x (B) y" na mesma linha
_TAG = re.compile(r"<\s*/?\s*[A-Za-z!?][^>]{0,200}>?")  # qualquer marca parecida com HTML, não só a lista do filtro do esquema
_LETRAS_SEPARADAS = re.compile(r"\b(?:[a-z][.\-_*]){3,}[a-z]\b")
_QUEBRA = re.compile(r"[\r\n\t\u2028\u2029\x0b\x0c\x85]")
PARAMETRO_PROMPT = "prompt"
PARAMETRO_HASH = "prompt_sha256"


@dataclass(frozen=True)
class Resultado:
    ok: bool
    codigo: str  # só código; nunca eco do texto do prompt
    campo: str | None = None
    texto: str | None = None  # prompt canônico, só quando ok


def _recusa(codigo, campo=None):
    return Resultado(False, codigo, campo, None)


def _norm(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()
    base = _LETRAS_SEPARADAS.sub(lambda m: re.sub(r"[.\-_*]", "", m.group(0)), base)  # i.g.n.o.r.e vira ignore
    return re.sub(r"\s+", " ", base)


def _checa_chaves(prompt):
    proibidas = {k.lower() for k in agent_commands.load_schema()["forbidden_param_keys"]} | CHAVES_PROIBIDAS_EXTRA
    for chave in prompt:
        if not isinstance(chave, str):
            return _recusa("PROMPT_INVALIDO")
        if chave.strip().lower() in proibidas:
            return _recusa("CAMPO_PROIBIDO", chave[:40] if re.fullmatch(r"[\w-]{1,40}", chave) else None)
    extras = sorted(k for k in prompt if k not in CAMPOS)
    if extras:
        return _recusa("CAMPO_FORA_DO_CONTRATO", extras[0] if re.fullmatch(r"[\w-]{1,40}", extras[0]) else None)
    return None


def _checa_texto(campo, valor):
    if not isinstance(valor, str):
        return _recusa("CAMPO_NAO_TEXTO", campo)
    if not valor.strip():
        return _recusa("CAMPO_VAZIO", campo)
    if valor != valor.strip():
        return _recusa("CAMPO_COM_BORDA", campo)  # sem espaço nas pontas: o texto validado é o texto enviado
    if len(valor) > LIMITES[campo]:
        return _recusa("CAMPO_LONGO_DEMAIS", campo)
    if _INVISIVEIS.search(valor) or _CONTROLE.search(valor):
        return _recusa("CARACTERE_INVISIVEL", campo)
    if _URL.search(valor):
        return _recusa("URL_PROIBIDA", campo)
    if _TAG.search(valor):
        return _recusa("HTML_BRUTO", campo)
    if _DESEMPENHO.search(_norm(valor)):
        return _recusa("DESEMPENHO_INDIVIDUAL", campo)
    if len(_ALTERNATIVA.findall(valor)) >= 2 or len(_ALTERNATIVA_NA_LINHA.findall(valor)) >= 3:
        return _recusa("QUESTAO_INTEGRAL", campo)
    if _QUEBRA.search(valor):
        return _recusa("CAMPO_MULTILINHA", campo)  # um campo por linha: o texto montado se confere de volta sem ambiguidade
    if _INSTRUCAO_EXTRA.search(_norm(valor).replace("-", " ").replace("_", " ").replace(".", " ")):
        return _recusa("INSTRUCAO_EMBUTIDA", campo)
    # segredo, dado pessoal, HTML bruto e instrução embutida, no texto original e no texto sem ofuscação de letras
    motivo = platform_read_guard.classificar_texto(valor) or platform_read_guard.classificar_texto(_norm(valor))
    if motivo:
        return _recusa({"PARAMS_SEGREDO": "SEGREDO", "PARAMS_DADO_PESSOAL": "DADO_PESSOAL", "PARAMS_HTML_BRUTO": "HTML_BRUTO",
                        "INSTRUCAO_EMBUTIDA": "INSTRUCAO_EMBUTIDA"}.get(motivo, "CONTEUDO_RECUSADO"), campo)
    return None


def _checa_exigencias(prompt):
    fonte = _norm(prompt["exigencia_fonte"])
    if "nao consta" not in fonte or not any(t in fonte for t in ("cite", "citar", "citacao", "trecho")):
        return _recusa("SEM_EXIGENCIA_DE_FONTE", "exigencia_fonte")  # S10-R3: citar o trecho e dizer "não consta nas fontes"
    metodo = _norm(prompt["metodo"])
    if "pergunt" not in metodo and "questoes de recuperacao" not in metodo and "questao de recuperacao" not in metodo:
        return _recusa("METODO_SEM_PERGUNTAS", "metodo")  # S2-R3: perguntas de recuperação, não resumo para reler
    return None


def instrucao_embutida(texto: str) -> bool:
    """True se o texto tem instrução embutida, no original ou sem ofuscação de letras (`i.g.n.o.r.e`). Filtro HEURÍSTICO da N2
    (inclui os padrões de esquecer, revelar e modo de desenvolvedor), reaproveitado pelo conversor da L2."""
    if not isinstance(texto, str):
        return False
    norm = _norm(texto)
    if _INSTRUCAO_EXTRA.search(norm.replace("-", " ").replace("_", " ").replace(".", " ")):
        return True
    return bool(platform_read_guard.classificar_texto(texto) == "INSTRUCAO_EMBUTIDA" or platform_read_guard.classificar_texto(norm) == "INSTRUCAO_EMBUTIDA")


def montar(prompt: dict) -> str:
    """Texto canônico do prompt, montado dos campos; só chamar depois de `validar` aceitar."""
    return "\n".join(f"{ROTULOS[c]}: {prompt[c]}" for c in CAMPOS)


def validar(prompt) -> Resultado:
    """Confere o prompt do Tutor. Ordem fixa; a primeira falha para e devolve só o código e o campo."""
    if not isinstance(prompt, dict):
        return _recusa("PROMPT_INVALIDO")
    erro = _checa_chaves(prompt)
    if erro:
        return erro
    for campo in CAMPOS:
        if campo not in prompt:
            return _recusa("CAMPO_AUSENTE", campo)
    for campo in CAMPOS:
        erro = _checa_texto(campo, prompt[campo])
        if erro:
            return erro
    erro = _checa_exigencias(prompt)
    if erro:
        return erro
    texto = montar(prompt)
    # o texto montado também passa pelo filtro inteiro (um campo inofensivo não pode compor algo recusado) e pelo limite
    if len(texto) > agent_commands.load_schema()["limits"]["max_param_string_chars"]:
        return _recusa("PROMPT_LONGO_DEMAIS")
    motivo = platform_read_guard.classificar_texto(texto)
    if motivo:
        return _recusa("CONTEUDO_RECUSADO")
    return Resultado(True, "PROMPT_ACEITO", None, texto)


def hash_agrupado(texto: str) -> str:
    """SHA-256 do texto em UTF-8, em oito grupos de oito hexadecimais separados por hífen.

    Os grupos evitam uma sequência de 11 dígitos que o filtro de CPF do esquema de comandos recusaria por engano."""
    h = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return "-".join(h[i:i + 8] for i in range(0, 64, 8))


def preparar(prompt):
    """Valida o prompt e monta os `params` do comando `enviar_prompt_notebook`: `{"prompt": texto, "prompt_sha256": hash}`.

    Devolve `(Resultado, params)`; em recusa, `params` é None. O hash permite a quem recebe o comando conferir que o texto é
    o que foi validado (ver `conferir_parametros`)."""
    r = validar(prompt)
    if not r.ok:
        return r, None
    return r, {PARAMETRO_PROMPT: r.texto, PARAMETRO_HASH: hash_agrupado(r.texto)}


def _desmontar(texto):
    """Inverso exato de `montar`; None se o texto não tiver a forma canônica."""
    linhas = texto.split("\n")
    if len(linhas) != len(CAMPOS):
        return None
    campos = {}
    for campo, linha in zip(CAMPOS, linhas):
        prefixo = ROTULOS[campo] + ": "
        if not linha.startswith(prefixo):
            return None
        campos[campo] = linha[len(prefixo):]
    return campos


def conferir_parametros(params) -> Resultado:
    """Lado de quem RECEBE o comando (a caixa de comandos): os `params` devem ser exatamente `prompt` e `prompt_sha256`, o hash
    deve bater, e o texto deve ser a forma canônica de um prompt que o validador aceita. Prompt editado depois de validado,
    hash trocado, campo a mais ou texto fora da forma canônica são recusados. Devolve só código."""
    if not isinstance(params, dict):
        return _recusa("PARAMS_INVALIDOS")
    if set(params) != {PARAMETRO_PROMPT, PARAMETRO_HASH}:
        return _recusa("PARAMS_FORA_DO_CONTRATO")
    texto, marca = params[PARAMETRO_PROMPT], params[PARAMETRO_HASH]
    if not isinstance(texto, str) or not isinstance(marca, str):
        return _recusa("PARAMS_INVALIDOS")
    if not hmac.compare_digest(marca.encode("utf-8"), hash_agrupado(texto).encode("utf-8")):
        return _recusa("HASH_DIVERGENTE")
    campos = _desmontar(texto)
    if campos is None:
        return _recusa("FORMA_NAO_CANONICA")
    r = validar(campos)
    if not r.ok:
        return r
    if r.texto != texto:
        return _recusa("FORMA_NAO_CANONICA")
    return r
