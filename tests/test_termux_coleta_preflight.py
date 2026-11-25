"""Coleta do pré-voo do piloto (roteiro do Termux, só leitura): contrato estático e execução com um `gh` falso. Offline."""
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/termux/coleta_preflight.sh"
TEXTO = SCRIPT.read_text(encoding="utf-8")

FAKE_GH = r'''#!/bin/bash
# gh falso: devolve o que o --jq pediria, a partir de arquivos locais; registra cada chamada
echo "$*" >> "$FAKE_LOG"
case "$1" in auth) exit 0;; esac
args="$*"
b64() { base64 -w0 "$1"; }
case "$args" in
  *"-X "*|*"--method"*|*"PUT"*|*"POST"*|*"DELETE"*|*"PATCH"*) echo "ESCRITA PROIBIDA" >&2; exit 9;;
  *"commits/main --jq .sha"*) git -C "$REPO_ROOT" rev-parse HEAD;;
  *"/check-runs"*) echo '["success", "success"]';;
  *"contents/.github/workflows/promover.yml"*) b64 "$FAKE_FLOW";;
  *"contents/config/modelos_fluxo/promover.yml"*) b64 "$REPO_ROOT/config/modelos_fluxo/promover.yml";;
  *"contents/scripts/promotion_gate.py"*) b64 "$REPO_ROOT/scripts/promotion_gate.py";;
  *"contents/scripts/sinal_emissor.py"*) b64 "$REPO_ROOT/scripts/sinal_emissor.py";;
  *"contents/settings.json"*) b64 "$REPO_ROOT/settings.json";;
  *"contents/consent-v4.json"*) printf '%s' '{}' | base64 -w0;;
  *"--jq .private"*) echo true;;
  *"--jq .forks_count"*) echo 0;;
  *"--jq .fork"*) echo false;;
  *"/collaborators"*) echo dono;;
  *"/invitations"*) ;;
  *) echo "chamada inesperada: $args" >&2; exit 8;;
esac
'''


class ContratoEstaticoTest(unittest.TestCase):
    def test_sintaxe_e_somente_leitura(self):
        r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for proibido in (r"gh\s+variable\s+set", r"gh\s+secret", r"-X\s+(?:PUT|POST|PATCH|DELETE)", r"gh\s+api\s+--method",
                         r"git\s+push", r"settings\.json\s*>", r"github_pat_", r"echo\s+.*TOKEN"):
            self.assertIsNone(re.search(proibido, TEXTO), proibido)

    def test_apaga_o_temporario_e_nao_pede_nem_imprime_token(self):
        self.assertIn("trap 'rm -rf \"$TMP\"' EXIT", TEXTO)
        self.assertIn("chmod 700", TEXTO)
        self.assertIn("o script não lê token", TEXTO)

    def test_confere_o_clone_na_main_e_o_modo(self):
        self.assertIn("BLOQUEADO: o clone não está na main pública", TEXTO)
        r = subprocess.run(["bash", str(SCRIPT), "invalido"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


class ExecucaoComGhFalsoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(self.tmp)]))
        (self.tmp / "gh").write_text(FAKE_GH, encoding="utf-8")
        (self.tmp / "gh").chmod(0o755)
        self.log = self.tmp / "calls.log"
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        modelo = (ROOT / "config/modelos_fluxo/promover.yml").read_text(encoding="utf-8")
        gate = subprocess.run(["sha256sum", str(ROOT / "scripts/promotion_gate.py")], capture_output=True, text=True).stdout.split()[0]
        emi = subprocess.run(["sha256sum", str(ROOT / "scripts/sinal_emissor.py")], capture_output=True, text=True).stdout.split()[0]
        fluxo = modelo.replace("__VALIDADOR_SHA__", head).replace("__VALIDADOR_GATE_SHA256__", gate).replace("__VALIDADOR_EMISSOR_SHA256__", emi)
        (self.tmp / "fluxo.yml").write_text(fluxo, encoding="utf-8")
        self.head = head

    def rodar(self, entrada="2027-07-31\n2027-07-31\n", modo="abertura"):
        env = dict(os.environ, PATH=str(self.tmp) + os.pathsep + os.environ["PATH"], FAKE_LOG=str(self.log),
                   REPO_ROOT=str(ROOT), FAKE_FLOW=str(self.tmp / "fluxo.yml"))
        return subprocess.run(["bash", str(SCRIPT), modo], input=entrada, capture_output=True, text=True, env=env, timeout=60)

    def test_pre_voo_roda_de_ponta_a_ponta_e_so_o_consentimento_falha(self):
        r = self.rodar()
        saida = r.stdout
        self.assertIn("== 9. Pré-voo (abertura) ==", saida, r.stdout + r.stderr)
        corpo = json.loads(saida[saida.index("{"):saida.rindex("}") + 1])
        por_id = {i["id"]: i["resultado"] for i in corpo["itens"]}
        for ok in ("flags", "fluxo_hash", "sha_fixado", "repo_entrada", "repo_dados", "tokens", "ci", "contraprova_gerador"):
            self.assertEqual(por_id[ok], "VERDE", (ok, corpo))
        self.assertEqual(por_id["consentimento_v4"], "VERMELHO")  # o gh falso devolve consentimento vazio: o pré-voo fecha
        self.assertEqual(r.returncode, 1)
        self.assertIn("RESULTADO: VERMELHO", saida)

    def test_nenhuma_chamada_de_escrita_e_nenhum_token_na_saida(self):
        r = self.rodar()
        self.assertNotIn("ESCRITA PROIBIDA", r.stderr)
        chamadas = self.log.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"-X |--method|variable|secret", chamadas))
        self.assertNotRegex(r.stdout + r.stderr, r"github_pat_|ghp_|gho_")

    def test_fluxo_instalado_diferente_do_esperado_fica_vermelho(self):
        fluxo = (self.tmp / "fluxo.yml").read_text(encoding="utf-8") + "# adulterado\n"
        (self.tmp / "fluxo.yml").write_text(fluxo, encoding="utf-8")
        saida = self.rodar().stdout
        corpo = json.loads(saida[saida.index("{"):saida.rindex("}") + 1])
        self.assertEqual({i["id"]: i["resultado"] for i in corpo["itens"]}["fluxo_hash"], "VERMELHO")

    def test_data_de_validade_invalida_para(self):
        r = self.rodar(entrada="amanha\n2027-07-31\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("== 9.", r.stdout)

    def test_token_com_validade_curta_fica_ambar_no_item_tokens(self):
        saida = self.rodar(entrada="2026-12-01\n2027-07-31\n").stdout
        corpo = json.loads(saida[saida.index("{"):saida.rindex("}") + 1])
        self.assertEqual({i["id"]: i["resultado"] for i in corpo["itens"]}["tokens"], "AMBAR")


if __name__ == "__main__":
    unittest.main()
