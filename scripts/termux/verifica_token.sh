#!/data/data/com.termux/files/usr/bin/bash
# verifica_token.sh: confere o que um token do GitHub consegue fazer neste repositório,
# SEM imprimir o token e SEM criar nada (as sondas de escrita mandam corpo vazio e falham na validação).
# Uso:  bash verifica_token.sh        (cole o token quando pedir; ele não aparece na tela)
# Requer: curl (pkg install curl). Opcional: REPO=dono/repo ISSUE=numero bash verifica_token.sh
# Perfis (variável PERFIL): "publico" (padrão, token do projeto: criar issue PODE, comentar PODE, gravar arquivo NÃO,
# abrir PR NÃO) e "privado" (token da Zapia para o repositório de dados: gravar arquivo PODE, issue/comentário/PR NÃO,
# escrita no repositório público NÃO). Nos dois: token fine-grained, COM expiração e alcançando 1 repositório (PR-010).
# Cada sonda é comparada com o esperado; o fim imprime RESULTADO e sai com código 1 se algo divergir.
set -u
PERFIL="${PERFIL:-publico}"
case "$PERFIL" in
  publico) REPO="${REPO:-Andraus35/UFMS-MEU-ESTUDO}"; ESP_ISSUE=PODE; ESP_COMENT=PODE; ESP_ARQ=NAO; ESP_PR=NAO;;
  privado) REPO="${REPO:-Andraus35/ufms-meu-estudo-dados}"; ESP_ISSUE=NAO; ESP_COMENT=NAO; ESP_ARQ=PODE; ESP_PR=NAO;;
  *) echo "PERFIL deve ser publico ou privado."; exit 1;;
esac
PUBLICO="${PUBLICO:-Andraus35/UFMS-MEU-ESTUDO}"
ISSUE="${ISSUE:-75}"
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
echo "Repositórios que o token alcança (HTTP $C):"
grep -o '"full_name": *"[^"]*"' "$TMP/b" | cut -d'"' -f4 | sort -u | sed 's/^/  - /'
TOTAL="$(grep -o '"full_name": *"[^"]*"' "$TMP/b" | cut -d'"' -f4 | sort -u | wc -l | tr -d ' ')"
echo "Total listado: $TOTAL"
if [ "$TOTAL" != "1" ]; then echo "DIVERGE: o token deve alcançar exatamente 1 repositório (alcança $TOTAL)."; DIVERGENCIAS=$((DIVERGENCIAS+1)); fi

echo
echo "== Sondas de escrita (corpo vazio: não criam nada) =="
C=$(call POST "/repos/$REPO/issues" "$VAZIO");                    confere "$ESP_ISSUE" "$C"; echo "Criar issue ...........: $(veredito "$C") [$CONF]"
C=$(call POST "/repos/$REPO/issues/$ISSUE/comments" "$VAZIO");     confere "$ESP_COMENT" "$C"; echo "Comentar na issue $ISSUE: $(veredito "$C") [$CONF]"
C=$(call PUT  "/repos/$REPO/contents/sonda-nao-existe.txt" "$VAZIO"); confere "$ESP_ARQ" "$C"; echo "Gravar arquivo ........: $(veredito "$C") [$CONF]"
C=$(call POST "/repos/$REPO/pulls" "$VAZIO");                      confere "$ESP_PR" "$C"; echo "Abrir pull request ....: $(veredito "$C") [$CONF]"
if [ "$PERFIL" = "privado" ]; then
  C=$(call PUT "/repos/$PUBLICO/contents/sonda-nao-existe.txt" "$VAZIO"); confere NAO "$C"
  echo "Gravar no repositório PÚBLICO: $(veredito "$C") [$CONF]"
fi
echo
if [ "$DIVERGENCIAS" -eq 0 ]; then echo "RESULTADO: CONFERE com o perfil $PERFIL."
else echo "RESULTADO: DIVERGE ($DIVERGENCIAS ponto(s)) no perfil $PERFIL. NÃO entregue este token à Zapia."; fi
echo "Fim. Nada foi gravado no GitHub e o token não foi impresso nem salvo."
[ "$DIVERGENCIAS" -eq 0 ] || exit 1
