#!/data/data/com.termux/files/usr/bin/bash
# ufms.sh: ferramenta única do PROPRIETÁRIO no Termux para o projeto UFMS MEU ESTUDO.
# Uso:  bash ufms.sh {preparar|atualizar|diagnostico|token [privado|publico]|plano|ajuda}
#   preparar     instala git, python, gh, curl e coreutils e clona (ou atualiza) o repositório PÚBLICO do projeto
#   atualizar    põe o clone em main, só por fast-forward e só se não houver alteração local
#   diagnostico  relatório SEM segredos para colar no chat: START de estudo, ciclo, flag de escrita pessoal,
#                repositório privado de dados e consentimento (leitura apenas)
#   token        confere um token do GitHub (perfil privado por padrão): chama verifica_token.sh
#   plano        gera LOCALMENTE o plano padrão (Método 4.2 e revisões em 7, 15 e 30 dias) com study_plan.py,
#                salvo FORA do repositório, em modo 0600. O Tutor decide os ajustes (D-23); nada vai ao GitHub
# Garantias: nenhum subcomando lê, imprime ou guarda token (o `gh` usa a credencial do seu aparelho); nada é
# gravado no repositório público nem no privado; a escrita de resultados continua desabilitada.
set -u

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "${UFMS_DIR:-}" ]; then RAIZ="$UFMS_DIR"
elif [ -f "$SELF/../../AGENTS.md" ] && [ -f "$SELF/../study_plan.py" ]; then RAIZ="$(cd "$SELF/../.." && pwd)"
else RAIZ="$HOME/UFMS-MEU-ESTUDO"; fi
REMOTO="https://github.com/Andraus35/UFMS-MEU-ESTUDO.git"
if [ "${UFMS_TESTE:-}" = "1" ] && [ -n "${UFMS_REMOTE:-}" ]; then REMOTO="$UFMS_REMOTE"; fi
PRIVADO="Andraus35/ufms-meu-estudo-dados"

erro() { echo "$*" >&2; exit 1; }
exigir_clone() {
  { [ -f "$RAIZ/AGENTS.md" ] && [ -f "$RAIZ/scripts/study_plan.py" ]; } \
    || erro "Não achei o clone em $RAIZ. Rode antes: bash ufms.sh preparar"
}
curto() { printf '%s' "$1" | cut -c1-12; }

# leitura: imprime o valor e devolve 0; 2 se não existe (404); 1 em outro erro.
ler() {
  local out
  if out="$(gh api "$@" 2>&1)"; then printf '%s' "$out"; return 0; fi
  case "$out" in *404*|*"Not Found"*) return 2;; *) return 1;; esac
}

atualizar_clone() {
  [ -z "$(git -C "$RAIZ" status --porcelain 2>/dev/null)" ] \
    || erro "Há alterações locais em $RAIZ; não vou mexer. Veja 'git status' e resolva antes."
  git -C "$RAIZ" fetch -q origin main || erro "Não consegui buscar o repositório (rede?)."
  git -C "$RAIZ" checkout -q main || erro "Não consegui trocar para main."
  git -C "$RAIZ" merge -q --ff-only origin/main || erro "Não é fast-forward; não vou forçar nada."
}

cmd_preparar() {
  if [ "${UFMS_SEM_PKG:-}" != "1" ] && command -v pkg >/dev/null 2>&1; then
    pkg install -y git python gh curl coreutils || erro "A instalação de pacotes falhou."
  fi
  for c in git python; do command -v "$c" >/dev/null 2>&1 || erro "Falta o comando $c."; done
  if [ -d "$RAIZ/.git" ]; then
    atualizar_clone
    echo "[preparar] clone atualizado em $RAIZ"
  else
    [ ! -e "$RAIZ" ] || erro "$RAIZ existe e não é um clone; não vou sobrescrever."
    git clone -q "$REMOTO" "$RAIZ" || erro "O clone falhou."
    echo "[preparar] clone criado em $RAIZ"
  fi
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    echo "[preparar] gh já está logado."
  else
    echo "[preparar] falta o login do gh: rode 'gh auth login' (a credencial fica só no seu aparelho)."
  fi
}

cmd_atualizar() {
  exigir_clone
  atualizar_clone
  echo "[atualizar] $RAIZ em main, HEAD $(curto "$(git -C "$RAIZ" rev-parse HEAD)")"
}

cmd_diagnostico() {
  exigir_clone
  echo "=== UFMS diagnóstico (sem segredos; pode colar no chat) ==="
  local head branch limpo
  head="$(git -C "$RAIZ" rev-parse HEAD 2>/dev/null || echo desconhecido)"
  branch="$(git -C "$RAIZ" rev-parse --abbrev-ref HEAD 2>/dev/null || echo desconhecido)"
  if [ -z "$(git -C "$RAIZ" status --porcelain 2>/dev/null)" ]; then limpo="sim"; else limpo="NÃO (há alterações locais)"; fi
  echo "clone: branch $branch, HEAD $(curto "$head"), limpo: $limpo"
  if [ "${UFMS_SEM_REDE:-}" != "1" ]; then
    local remoto
    remoto="$(git -C "$RAIZ" ls-remote origin main 2>/dev/null | cut -f1)"
    if [ -n "$remoto" ]; then
      if [ "$remoto" = "$head" ]; then echo "main remota: $(curto "$remoto"), igual ao clone: sim"
      else echo "main remota: $(curto "$remoto"), igual ao clone: NÃO (rode: bash ufms.sh atualizar)"; fi
    else echo "main remota: não consegui ler (rede?)"; fi
  fi
  if (cd "$RAIZ" && python scripts/bootstrap.py --mode study >"${TMPDIR:-/tmp}/ufms_boot.$$" 2>&1); then
    echo "START de estudo (bootstrap): OK"
    python - "${TMPDIR:-/tmp}/ufms_boot.$$" <<'PY'
import json, sys
try:
    dados = json.load(open(sys.argv[1], encoding="utf-8"))
    for nome, h in dados["sha256_dos_arquivos"].items():
        print(f"  {nome} {h[:12]}")
except Exception:
    print("  (não consegui ler os hashes)")
PY
  else
    echo "START de estudo (bootstrap): FALHOU"
  fi
  rm -f "${TMPDIR:-/tmp}/ufms_boot.$$"
  (cd "$RAIZ" && python scripts/next_task.py 2>/dev/null) | python -c '
import json, sys
try:
    d = json.load(sys.stdin)
    c = d["ciclo"]
    print("ciclo: PR #%s, tarefa %s, estado %s" % (c.get("pr"), c.get("tarefa"), c.get("estado")))
    print("fila: proximo =", d["fila"].get("proximo"))
except Exception:
    print("ciclo: não consegui ler (next_task.py)")
'
  python - "$RAIZ/settings.json" <<'PY'
import json, sys
def achar(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "personal_results_writes_enabled":
                return v
            r = achar(v)
            if r is not None:
                return r
    elif isinstance(x, list):
        for v in x:
            r = achar(v)
            if r is not None:
                return r
    return None
try:
    v = achar(json.load(open(sys.argv[1], encoding="utf-8")))
except Exception:
    v = None
if v is False:
    print("escrita de resultados pessoais: DESABILITADA (settings.json: false)")
elif v is True:
    print("ATENÇÃO: personal_results_writes_enabled está true em settings.json")
else:
    print("escrita de resultados pessoais: não achei a flag")
PY
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    echo "gh: logado"
    local vis rc sha
    vis="$(ler "repos/$PRIVADO" --jq '.private')"; rc=$?
    if [ "$rc" -eq 0 ]; then
      if [ "$vis" = "true" ]; then echo "repositório privado de dados: existe, private=true"
      else echo "ATENÇÃO: o repositório de dados existe e NÃO é privado (private=$vis)"; fi
      sha="$(ler "repos/$PRIVADO/contents/consent.json" --jq '.sha')"; rc=$?
      if [ "$rc" -eq 0 ]; then echo "consentimento v2 (consent.json): presente, blob $(curto "$sha")"
      elif [ "$rc" -eq 2 ]; then echo "consentimento v2 (consent.json): AUSENTE"
      else echo "consentimento v2: não consegui verificar"; fi
    elif [ "$rc" -eq 2 ]; then echo "repositório privado de dados: não existe"
    else echo "repositório privado de dados: não consegui verificar"; fi
  else
    echo "gh: NÃO logado (rode: gh auth login)"
  fi
  echo "=== fim do diagnóstico ==="
}

cmd_token() {
  exigir_clone
  local perfil="${1:-privado}"
  case "$perfil" in privado|publico) ;; *) erro "Perfil deve ser privado ou publico.";; esac
  PERFIL="$perfil" bash "$RAIZ/scripts/termux/verifica_token.sh"
}

cmd_plano() {
  exigir_clone
  local padrao_inicio inicio minutos descanso cargo exame saida_dir arquivo args
  padrao_inicio="$(python -c '
import datetime
d = datetime.date.today()
d += datetime.timedelta(days=(7 - d.weekday()) % 7 or 7)
print(d)')"
  exame="$(python - "$RAIZ/config/concursos.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["prova_data"])
PY
)" || erro "Não consegui ler a data da prova em config/concursos.json."
  printf 'Data de início (AAAA-MM-DD) [%s]: ' "$padrao_inicio"; read -r inicio || inicio=""
  [ -n "$inicio" ] || inicio="$padrao_inicio"
  printf 'Minutos de estudo por dia (número, ex.: 240): '; read -r minutos || minutos=""
  printf 'Dia de descanso (segunda a domingo) [domingo]: '; read -r descanso || descanso=""
  printf 'Cargo (523, 324 ou ambos) [ambos]: '; read -r cargo || cargo=""
  [ -n "$descanso" ] || descanso="domingo"
  [ -n "$cargo" ] || cargo="ambos"

  local dia
  case "$(printf '%s' "$descanso" | tr 'A-Z' 'a-z')" in
    segunda|0) dia=0;; terça|terca|1) dia=1;; quarta|2) dia=2;; quinta|3) dia=3;;
    sexta|4) dia=4;; sábado|sabado|5) dia=5;; domingo|6) dia=6;;
    *) erro "Dia de descanso inválido: $descanso";;
  esac
  case "$minutos" in ''|*[!0-9]*) erro "Minutos deve ser um número inteiro.";; esac
  [ "$minutos" -ge 30 ] && [ "$minutos" -le 720 ] || erro "Minutos fora do razoável (30 a 720)."
  case "$cargo" in 523|324) args=(--cargo "$cargo");; ambos) args=();; *) erro "Cargo deve ser 523, 324 ou ambos.";; esac
  python - "$inicio" <<'PY' || erro "Data de início inválida: use AAAA-MM-DD."
import datetime, sys
datetime.date.fromisoformat(sys.argv[1])
PY

  saida_dir="${UFMS_PLANO_DIR:-$HOME/ufms-plano}"
  case "$(python -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$saida_dir")/" in
    "$(python -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$RAIZ")"/*) erro "A pasta do plano não pode ficar dentro do repositório.";;
  esac
  mkdir -p "$saida_dir" && chmod 700 "$saida_dir"
  arquivo="$saida_dir/plano-$inicio-$cargo.json"
  [ ! -e "$arquivo" ] || arquivo="$saida_dir/plano-$inicio-$cargo-$(date +%H%M%S).json"
  umask 077
  (cd "$RAIZ" && python scripts/study_plan.py --start "$inicio" --exam "$exame" --daily-minutes "$minutos" \
      --rest-weekday "$dia" ${args[@]+"${args[@]}"}) >"$arquivo" 2>"$arquivo.erro" \
    || { echo "O gerador recusou os parâmetros:" >&2; cat "$arquivo.erro" >&2; rm -f "$arquivo" "$arquivo.erro"; exit 1; }
  rm -f "$arquivo.erro"
  chmod 600 "$arquivo"
  python - "$arquivo" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
dias = d["days"]
print("Plano gerado:", len(dias), "dias, de", dias[0]["date"], "a", dias[-1]["date"])
nomes = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
for dia in dias[:7]:
    itens = ", ".join(f'{i["disciplina"]} {i["minutes"]}min' for i in dia["items"]) or "descanso"
    print(f'  {dia["date"]} {nomes[dia["weekday"]]} [{dia["kind"]}] {itens}')
PY
  echo
  echo "Salvo em: $arquivo (modo 0600, FORA do repositório)."
  echo "É o plano PADRÃO (Método 4.2 e revisões em 7, 15 e 30 dias); o Tutor ajusta com tópicos estudados e prioridades."
  echo "Não coloque este arquivo em repositório público. Leve-o à sessão de estudo do Tutor."
}

case "${1:-ajuda}" in
  preparar)    cmd_preparar;;
  atualizar)   cmd_atualizar;;
  diagnostico) cmd_diagnostico;;
  token)       shift; cmd_token "${1:-privado}";;
  plano)       cmd_plano;;
  ajuda|-h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//';;
  *) echo "Comando desconhecido: $1" >&2; echo "Use: bash ufms.sh ajuda" >&2; exit 2;;
esac
