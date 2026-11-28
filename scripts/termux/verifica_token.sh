#!/data/data/com.termux/files/usr/bin/bash
# verifica_token.sh: confere o que um token do GitHub consegue fazer neste repositório,
# SEM imprimir o token e SEM criar nada (as sondas de escrita mandam corpo vazio e falham na validação).
# Uso:  bash verifica_token.sh        (cole o token quando pedir; ele não aparece na tela)
# Requer: curl (pkg install curl). Opcional: REPO=dono/repo ISSUE=numero bash verifica_token.sh
# Perfis (variável PERFIL; "privado_issues" é o token da Zapia no `entrada` depois da emenda E54): "publico" (padrão, token do projeto: criar issue PODE, comentar PODE, gravar arquivo NÃO,
# abrir PR NÃO) e "privado" (token da Zapia para o repositório de dados: gravar arquivo PODE, issue/comentário/PR NÃO,
# escrita no repositório público NÃO). Nos dois: token fine-grained, COM expiração e sem alcançar outros repositórios PRIVADOS nem escrever em outros (PR-010; os públicos qualquer token lê).
# Cada sonda é comparada com o esperado; o fim imprime RESULTADO e sai com código 1 se algo divergir.
set -u
PERFIL="${PERFIL:-publico}"
case "$PERFIL" in
  publico) REPO="${REPO:-Andraus35/UFMS-MEU-ESTUDO}"; ESP_ISSUE=PODE; ESP_COMENT=PODE; ESP_ARQ=NAO; ESP_PR=NAO;;
  privado) REPO="${REPO:-Andraus35/ufms-meu-estudo-dados}"; ESP_ISSUE=NAO; ESP_COMENT=NAO; ESP_ARQ=PODE; ESP_PR=NAO;;
  # E54 (emenda da S6-R6, 28/11/2026): token da Zapia no `entrada`: gravar arquivo PODE e Issues PODE (só para abrir `RESP eng-NNNN`); comentar acompanha Issues
  # (a API não separa), então a proibição de comentar é do prompt, não da permissão; pull request NÃO; escrita em qualquer outro repositório NÃO.
  privado_issues) REPO="${REPO:-Andraus35/ufms-meu-estudo-entrada}"; ESP_ISSUE=PODE; ESP_COMENT=PODE; ESP_ARQ=PODE; ESP_PR=NAO;;
  *) echo "PERFIL deve ser publico, privado ou privado_issues."; exit 1;;
esac
PRIV=0; case "$PERFIL" in privado|privado_issues) PRIV=1;; esac
PUBLICO="${PUBLICO:-Andraus35/UFMS-MEU-ESTUDO}"
ISSUE_PADRAO=75  # issue do repositório PÚBLICO; no perfil privado_issues o repositório é o entrada, onde existe a #12 (a #75 não existe lá: 404 enganoso, achado de 28/11/2026)
[ "$PERFIL" = "privado_issues" ] && ISSUE_PADRAO=12
ISSUE="${ISSUE:-$ISSUE_PADRAO}"
VAZIO='{}'
DIVERGENCIAS=0
API="https://api.github.com"
command -v curl >/dev/null 2>&1 || { echo "Instale o curl: pkg install curl"; exit 1; }

printf 'Cole o token e tecle Enter (não aparece na tela): '
read -rs TOKEN
echo
[ -n "$TOKEN" ] || { echo "Token vazio."; exit 1; }
case "$TOKEN" in
  github_pat_*) TIPO="fine-grained (prefixo github_pat_)";;
  ghp_*)        TIPO="classic (prefixo ghp_)";;
  gho_*|ghu_*|ghs_*) TIPO="OAuth ou app (prefixo ${TOKEN:0:4})";;
  *)            TIPO="formato desconhecido";;
esac

TMP="$(mktemp -d)"; chmod 700 "$TMP"
trap 'rm -rf "$TMP"; unset TOKEN' EXIT

# call METODO CAMINHO [CORPO]: grava cabeçalhos em $TMP/h e corpo em $TMP/b; imprime o código HTTP.
# O token vai por stdin (-K -), nunca na linha de comando (não aparece em "ps").
call() {
  local m="$1" p="$2" d="${3-}"
  if [ -n "$d" ]; then
    printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -X "$m" -D "$TMP/h" -o "$TMP/b" \
      -w '%{http_code}' -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' \
      -H 'Content-Type: application/json' --data "$d" "$API$p" 2>/dev/null || printf '000'
  else
    printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -sS -K - -X "$m" -D "$TMP/h" -o "$TMP/b" \
      -w '%{http_code}' -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28' \
      "$API$p" 2>/dev/null || printf '000'
  fi
}
# confere ESPERADO(PODE|NAO) CODIGO: define CONF e conta divergências (sem subshell).
confere() {
  local real
  case "$2" in 422) real=PODE;; 401|403|404) real=NAO;; *) real=OUTRO;; esac
  if [ "$real" = "$1" ]; then CONF="OK"; else CONF="DIVERGE (esperado $1)"; DIVERGENCIAS=$((DIVERGENCIAS+1)); fi
}
hdr() { grep -i "^$1:" "$TMP/h" 2>/dev/null | tr -d '\r' | head -1 | cut -d' ' -f2-; }
veredito() { case "$1" in 422) echo "PODE (a validação falhou depois da autorização; nada foi criado)";;
  200|201|204) echo "ATENÇÃO: a sonda foi aceita (código $1); verifique o repositório";;
  401) echo "NÃO (token inválido ou expirado)";; 403|404) echo "NÃO (sem permissão; código $1)";; 000) echo "SEM REDE";; *) echo "indefinido (código $1)";; esac; }

echo
echo "== Token =="
echo "Tipo: $TIPO"
C=$(call GET /user)
echo "GET /user: HTTP $C"
if [ "$C" = "200" ]; then
  echo "Conta: $(grep -o '"login": *"[^"]*"' "$TMP/b" | head -1 | cut -d'"' -f4)"
else
  echo "Mensagem: $(grep -o '"message": *"[^"]*"' "$TMP/b" | head -1 | cut -d'"' -f4)"
fi
echo "Escopos (só classic): $(hdr x-oauth-scopes)"
EXPIRA="$(hdr github-authentication-token-expiration)"
echo "Validade (só fine-grained): $EXPIRA"
case "$TIPO" in
  fine-grained*) if [ -z "$EXPIRA" ]; then echo "DIVERGE: token SEM expiração (PR-010 e D-09 exigem expiração)."; DIVERGENCIAS=$((DIVERGENCIAS+1)); fi;;
  *) echo "DIVERGE: o token não é fine-grained (PR-010 exige escopo único por repositório)."; DIVERGENCIAS=$((DIVERGENCIAS+1));;
esac

C=$(call GET /rate_limit)
echo "Limite de taxa restante: $(hdr x-ratelimit-remaining) de $(hdr x-ratelimit-limit)"

echo
echo "== Acesso de leitura =="
C=$(call GET "/repos/$REPO"); echo "GET /repos/$REPO: HTTP $C"
C=$(call GET "/user/repos?per_page=100")
# Qualquer token lê TODOS os repositórios públicos (o GitHub avisa isso na página do token), então os públicos
# aparecem nesta lista sem serem alcance. O que conta é: (1) repositórios PRIVADOS alcançados e (2) onde dá para ESCREVER.
LISTA="$(python - "$TMP/b" 2>/dev/null <<'PY'
import json, sys
try:
    dados = json.load(open(sys.argv[1], encoding="utf-8"))
    for r in dados:
        print("privado" if r.get("private") else "publico", r["full_name"])
except Exception:
    sys.exit(1)
PY
)"; LISTA_RC=$?
PRIVADOS=""; PUBLICOS=""; NPUB=0; REPO_MINUSC="$(printf '%s' "$REPO" | tr 'A-Z' 'a-z')"
if [ "$C" != "200" ] || [ "$LISTA_RC" -ne 0 ]; then
  echo "Repositórios que o token alcança: não consegui ler a lista (HTTP $C; precisa do python)."
  echo "DIVERGE: não consegui classificar os repositórios alcançados."; DIVERGENCIAS=$((DIVERGENCIAS+1))
else
  while read -r tipo nome; do
    [ -n "$nome" ] || continue
    if [ "$tipo" = "privado" ]; then PRIVADOS="$PRIVADOS $nome"; else PUBLICOS="$PUBLICOS $nome"; NPUB=$((NPUB+1)); fi
  done <<EOF_LISTA
$LISTA
EOF_LISTA
  echo "Repositórios PRIVADOS que o token alcança (HTTP $C):"
  if [ -z "$PRIVADOS" ]; then echo "  (nenhum)"; else for n in $PRIVADOS; do echo "  - $n"; done; fi
  echo "Repositórios públicos listados: $NPUB (qualquer token lê os públicos; não contam como alcance)"
  # privados permitidos: só o designado, se ele for privado (perfil privado); nenhum no perfil público
  for n in $PRIVADOS; do
    if [ "$PRIV" = 1 ] && [ "$(printf '%s' "$n" | tr 'A-Z' 'a-z')" = "$REPO_MINUSC" ]; then continue; fi
    echo "DIVERGE: o token alcança o repositório PRIVADO $n, que não é o designado."; DIVERGENCIAS=$((DIVERGENCIAS+1))
  done
  if [ "$PRIV" = 1 ]; then
    case " $(printf '%s' "$PRIVADOS" | tr 'A-Z' 'a-z') " in *" $REPO_MINUSC "*) ;;
      *) echo "DIVERGE: o token não alcança o repositório designado $REPO."; DIVERGENCIAS=$((DIVERGENCIAS+1));; esac
  fi
fi

echo
echo "== Sondas de escrita (corpo vazio: não criam nada) =="
C=$(call POST "/repos/$REPO/issues" "$VAZIO");                    confere "$ESP_ISSUE" "$C"; echo "Criar issue ...........: $(veredito "$C") [$CONF]"
C=$(call POST "/repos/$REPO/issues/$ISSUE/comments" "$VAZIO");     confere "$ESP_COMENT" "$C"; echo "Comentar na issue $ISSUE: $(veredito "$C") [$CONF]"
[ "$C" = "404" ] && echo "  (404 pode ser issue inexistente em $REPO, não falta de permissão: rode de novo com ISSUE=<número de uma issue que exista>)"
C=$(call PUT  "/repos/$REPO/contents/sonda-nao-existe.txt" "$VAZIO"); confere "$ESP_ARQ" "$C"; echo "Gravar arquivo ........: $(veredito "$C") [$CONF]"
C=$(call POST "/repos/$REPO/pulls" "$VAZIO");                      confere "$ESP_PR" "$C"; echo "Abrir pull request ....: $(veredito "$C") [$CONF]"
if [ "$PRIV" = 1 ]; then
  C=$(call PUT "/repos/$PUBLICO/contents/sonda-nao-existe.txt" "$VAZIO"); confere NAO "$C"
  echo "Gravar no repositório PÚBLICO: $(veredito "$C") [$CONF]"
fi
# escrita em QUALQUER outro repositório listado (a lista de públicos inclui os seus outros projetos)
OUTROS=0
for n in $PUBLICOS $PRIVADOS; do
  nl="$(printf '%s' "$n" | tr 'A-Z' 'a-z')"
  [ "$nl" = "$REPO_MINUSC" ] && continue
  [ "$PRIV" = 1 ] && [ "$nl" = "$(printf '%s' "$PUBLICO" | tr 'A-Z' 'a-z')" ] && continue   # já sondado acima
  OUTROS=$((OUTROS+1)); [ "$OUTROS" -le 20 ] || break
  C=$(call PUT "/repos/$n/contents/sonda-nao-existe.txt" "$VAZIO"); confere NAO "$C"
  echo "Gravar em $n: $(veredito "$C") [$CONF]"
done
echo
if [ "$DIVERGENCIAS" -eq 0 ]; then echo "RESULTADO: CONFERE com o perfil $PERFIL."
else echo "RESULTADO: DIVERGE ($DIVERGENCIAS ponto(s)) no perfil $PERFIL. NÃO entregue este token à Zapia."; fi
echo "Fim. Nada foi gravado no GitHub e o token não foi impresso nem salvo."
[ "$DIVERGENCIAS" -eq 0 ] || exit 1
