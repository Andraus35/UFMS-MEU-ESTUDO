#!/data/data/com.termux/files/usr/bin/bash
# verifica_token.sh: confere o que um token do GitHub consegue fazer neste repositório,
# SEM imprimir o token e SEM criar nada (as sondas de escrita mandam corpo vazio e falham na validação).
# Uso:  bash verifica_token.sh        (cole o token quando pedir; ele não aparece na tela)
# Requer: curl (pkg install curl). Opcional: REPO=dono/repo ISSUE=numero bash verifica_token.sh
set -u
REPO="${REPO:-Andraus35/UFMS-MEU-ESTUDO}"
ISSUE="${ISSUE:-75}"
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
echo "Validade (só fine-grained): $(hdr github-authentication-token-expiration)"

C=$(call GET /rate_limit)
echo "Limite de taxa restante: $(hdr x-ratelimit-remaining) de $(hdr x-ratelimit-limit)"

echo
echo "== Acesso de leitura =="
C=$(call GET "/repos/$REPO"); echo "GET /repos/$REPO: HTTP $C"
C=$(call GET "/user/repos?per_page=100")
echo "Repositórios que o token alcança (HTTP $C):"
grep -o '"full_name": *"[^"]*"' "$TMP/b" | cut -d'"' -f4 | sort -u | sed 's/^/  - /'
echo "Total listado: $(grep -o '"full_name": *"[^"]*"' "$TMP/b" | cut -d'"' -f4 | sort -u | wc -l | tr -d ' ')"

echo
echo "== Sondas de escrita (corpo vazio: não criam nada) =="
C=$(call POST "/repos/$REPO/issues" '{}');                    echo "Criar issue ...........: $(veredito "$C")"
C=$(call POST "/repos/$REPO/issues/$ISSUE/comments" '{}');     echo "Comentar na issue $ISSUE: $(veredito "$C")"
C=$(call PUT  "/repos/$REPO/contents/sonda-nao-existe.txt" '{}'); echo "Gravar arquivo ........: $(veredito "$C")"
C=$(call POST "/repos/$REPO/pulls" '{}');                      echo "Abrir pull request ....: $(veredito "$C")"
echo
echo "Fim. Nada foi gravado no GitHub e o token não foi impresso nem salvo."
