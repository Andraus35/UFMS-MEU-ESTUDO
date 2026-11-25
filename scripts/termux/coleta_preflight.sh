#!/data/data/com.termux/files/usr/bin/bash
# Coleta SOMENTE LEITURA das leituras do pré-voo do piloto e roda scripts/piloto_preflight.py (S11-R2). Ato do proprietário, no Termux.
# Não grava nada no GitHub, não liga flag, não imprime token. As leituras ficam num arquivo local temporário (modo 0600) que o
# próprio script apaga ao sair; a saída do pré-voo traz só identificadores, booleanos e prefixos de hash.
# Uso (a partir do clone atualizado na main):  bash scripts/termux/coleta_preflight.sh [abertura|pos_janela|repouso]
set -euo pipefail

MODO="${1:-abertura}"
case "$MODO" in abertura|pos_janela|repouso) ;; *) echo "Modo inválido: $MODO (abertura, pos_janela ou repouso)"; exit 2;; esac

PUBLICO="Andraus35/UFMS-MEU-ESTUDO"
ENTRADA="Andraus35/ufms-meu-estudo-entrada"
DADOS="Andraus35/ufms-meu-estudo-dados"
WF=".github/workflows/promover.yml"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

command -v gh >/dev/null || { echo "Falta o gh (pkg install gh)."; exit 1; }
command -v python >/dev/null || { echo "Falta o python (pkg install python)."; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh não está logado (gh auth login)."; exit 1; }

TMP="$(mktemp -d)"; chmod 700 "$TMP"
trap 'rm -rf "$TMP"' EXIT
ler() { gh api "$@"; }            # só GET: nenhum -X aqui
conteudo() { ler "repos/$1/contents/$2${3:+?ref=$3}" --jq .content | base64 -d; }

echo "== 1. HEAD da main pública e do clone =="
MAIN="$(ler "repos/$PUBLICO/commits/main" --jq .sha)"
HEAD_LOCAL="$(git -C "$ROOT" rev-parse HEAD)"
echo "main pública: ${MAIN:0:12}  clone: ${HEAD_LOCAL:0:12}"
[ "$MAIN" = "$HEAD_LOCAL" ] || { echo "BLOQUEADO: o clone não está na main pública. Rode: bash scripts/termux/ufms.sh atualizar"; exit 1; }

echo "== 2. Fluxo instalado em entrada =="
conteudo "$ENTRADA" "$WF" > "$TMP/instalado.yml"
HASH_INST="$(sha256sum "$TMP/instalado.yml" | cut -d' ' -f1)"
SHA_FIX="$(sed -n 's/^  VALIDADOR_SHA: \([0-9a-f]\{40\}\)$/\1/p' "$TMP/instalado.yml" | head -n1)"
[ -n "$SHA_FIX" ] || { echo "BLOQUEADO: não achei VALIDADOR_SHA no fluxo instalado."; exit 1; }
echo "SHA fixado no fluxo: ${SHA_FIX:0:12}  hash instalado: ${HASH_INST:0:12}"

echo "== 3. Hash esperado para o SHA fixado (modelo, portão e emissor lidos NESSE SHA) =="
conteudo "$PUBLICO" config/modelos_fluxo/promover.yml "$SHA_FIX" > "$TMP/modelo.yml"
GATE_H="$(conteudo "$PUBLICO" scripts/promotion_gate.py "$SHA_FIX" | sha256sum | cut -d' ' -f1)"
EMI_H="$(conteudo "$PUBLICO" scripts/sinal_emissor.py "$SHA_FIX" 2>/dev/null | sha256sum | cut -d' ' -f1 || true)"
python - "$TMP/modelo.yml" "$TMP/esperado.yml" "$SHA_FIX" "$GATE_H" "$EMI_H" <<'PY'
import sys
modelo, saida, sha, gate, emi = sys.argv[1:6]
t = open(modelo, encoding="utf-8").read()
for marcador, valor in (("__VALIDADOR_SHA__", sha), ("__VALIDADOR_GATE_SHA256__", gate), ("__VALIDADOR_EMISSOR_SHA256__", emi)):
    if marcador in t:
        t = t.replace(marcador, valor)
open(saida, "w", encoding="utf-8", newline="\n").write(t)
PY
HASH_ESP="$(sha256sum "$TMP/esperado.yml" | cut -d' ' -f1)"
echo "hash esperado: ${HASH_ESP:0:12}"

echo "== 4. Flags =="
PUB_FLAG="$(python - "$ROOT/settings.json" <<'PY'
import json, sys
print(str(json.load(open(sys.argv[1], encoding="utf-8"))["storage"]["personal_results_writes_enabled"]).lower())
PY
)"
FLUXO_FLAG="$(conteudo "$PUBLICO" settings.json "$SHA_FIX" | python -c "import json,sys; print(str(json.load(sys.stdin)['storage'].get('private_flow_promotion_enabled') is True).lower())")"
echo "personal_results_writes_enabled=$PUB_FLAG  private_flow_promotion_enabled(no SHA fixado)=$FLUXO_FLAG"

echo "== 5. Repositórios privados =="
repo_json() {  # private, fork, forks_count, colaboradores, convites
  local r="$1" p f fc co cv
  p="$(ler "repos/$r" --jq .private)"; f="$(ler "repos/$r" --jq .fork)"; fc="$(ler "repos/$r" --jq .forks_count)"
  co="$(ler "repos/$r/collaborators" --paginate --jq '.[].login' | wc -l | tr -d ' ')"
  cv="$(ler "repos/$r/invitations" --paginate --jq '.[].id' | wc -l | tr -d ' ')"
  printf '{"private": %s, "fork": %s, "forks_count": %s, "colaboradores": %s, "convites": %s}' "$p" "$f" "$fc" "$co" "$cv"
}
REPO_E="$(repo_json "$ENTRADA")"; REPO_D="$(repo_json "$DADOS")"

echo "== 6. Consentimento v4 (arquivo no repositório privado dados) =="
conteudo "$DADOS" consent-v4.json > "$TMP/consent-v4.json" || { echo "consent-v4.json ausente"; echo '{}' > "$TMP/consent-v4.json"; }

echo "== 7. Validade dos tokens (você informa; o script não lê token) =="
printf 'Validade do token zapia_dados (AAAA-MM-DD): '; read -r V1
printf 'Validade do token zapia token (AAAA-MM-DD): '; read -r V2

echo "== 8. CI do HEAD da main =="
CI="$(ler "repos/$PUBLICO/commits/$MAIN/check-runs" --jq '[.check_runs[].conclusion // "pendente"]')"

python - "$TMP/leituras.json" "$MAIN" "$HASH_INST" "$HASH_ESP" "$SHA_FIX" "$PUB_FLAG" "$FLUXO_FLAG" "$REPO_E" "$REPO_D" \
  "$TMP/consent-v4.json" "$V1" "$V2" "$CI" <<'PY'
import json, re, sys
saida, main, inst, esp, sha, pub, fluxo, re_, rd, consent, v1, v2, ci = sys.argv[1:14]
def data(v):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        sys.exit("data de validade inválida: use AAAA-MM-DD")
    return v + "T23:59:59+00:00"
leituras = {
  "main_sha": main,
  "flags": {"personal_results_writes_enabled": pub == "true", "private_flow_promotion_enabled_no_sha_fixado": fluxo == "true"},
  "fluxo": {"hash_instalado": inst, "hash_esperado": esp, "hash_esperado_sha": sha, "sha_fixado": sha},
  "repositorios": {"entrada": json.loads(re_), "dados": json.loads(rd)},
  "consentimento": json.load(open(consent, encoding="utf-8")),
  "tokens": [{"nome": "zapia_dados", "expira_em": data(v1)}, {"nome": "zapia token", "expira_em": data(v2)}],
  "ci": {"head_sha": main, "conclusoes": json.loads(ci)},
}
open(saida, "w", encoding="utf-8").write(json.dumps(leituras, ensure_ascii=False))
PY
chmod 600 "$TMP/leituras.json"

echo "== 9. Pré-voo ($MODO) =="
set +e
python "$ROOT/scripts/piloto_preflight.py" --modo "$MODO" --leituras "$TMP/leituras.json"
RC=$?
set -e
case "$RC" in
  0) echo "RESULTADO: VERDE";; 3) echo "RESULTADO: ÂMBAR (corrigir antes de pedir a janela)";; 1) echo "RESULTADO: VERMELHO (parar)";; *) echo "RESULTADO: erro de uso ($RC)";;
esac
exit "$RC"
