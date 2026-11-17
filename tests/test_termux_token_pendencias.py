"""token_pendencias.sh: conferências do repositório privado e leitura do resultado do verificador, sem tocar no token."""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "termux" / "token_pendencias.sh"

UFMS_STUB = """#!/bin/bash
case "$1" in
 atualizar) echo "clone atualizado (stub)";;
 token)
  if [ "${FAKE_RES:-ok}" = ok ]; then
    echo "Validade (só fine-grained): 2026-12-17 11:35:41 UTC"; echo "Gravar arquivo ........: PODE [OK]"
    echo "RESULTADO: CONFERE com o perfil privado."
  else
    echo "Gravar arquivo ........: NÃO (sem permissão; código 403) [DIVERGE (esperado PODE)]"
    echo "DIVERGE: o token alcança o repositório PRIVADO outro/privado, que não é o designado."
    echo "RESULTADO: DIVERGE (2 ponto(s)) no perfil privado. NÃO entregue este token à Zapia."; exit 1
  fi;;
esac
"""
GH_STUB = """#!/bin/bash
case "$*" in
 "auth status") exit 0;;
 *collaborators*) echo "${FAKE_COLAB:-1}";;
 *"--jq"*) printf '%s\\t%s\\t%s\\t%s\\n' "${FAKE_PRIVATE:-true}" "false" "${FAKE_FORK:-false}" "0";;
esac
"""


class TokenPendenciasTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        (t / "home" / "UFMS-MEU-ESTUDO" / "scripts" / "termux").mkdir(parents=True)
        (t / "bin").mkdir()
        (t / "home" / "UFMS-MEU-ESTUDO" / "scripts" / "termux" / "ufms.sh").write_text(UFMS_STUB)
        gh = t / "bin" / "gh"
        gh.write_text(GH_STUB)
        gh.chmod(0o755)
        self.home = t / "home"

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, com_gh=True, **env):
        e = dict(os.environ, HOME=str(self.home), **env)
        e["PATH"] = (f"{Path(self.tmp.name) / 'bin'}:" if com_gh else "") + "/usr/bin:/bin"
        if not com_gh:
            e["PATH"] = "/usr/bin:/bin"
        return subprocess.run(["bash", str(SCRIPT)], stdin=subprocess.DEVNULL, capture_output=True, text=True, env=e, timeout=60)

    def test_sintaxe_e_nunca_le_nem_imprime_o_token(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)]).returncode, 0)
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("read -rs", texto)
        self.assertNotRegex(texto, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")
        self.assertIn("bash \"$UFMS\" token privado", texto)

    def test_tudo_certo_sai_com_zero_e_mostra_a_data_para_renovar(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULTADO: CONFERE", r.stdout)
        self.assertIn("Renove o token antes de 2026-12-17", r.stdout)
        self.assertIn("repositório PRIVADO (private=true)", r.stdout)
        self.assertIn("só 1 colaborador", r.stdout)
        self.assertIn("Resumo: 0 ponto(s) de atenção", r.stdout)

    def test_forks_colaboradores_e_diverge_geram_atencao_e_saida_diferente_de_zero(self):
        r = self.rodar(FAKE_RES="bad", FAKE_FORK="true", FAKE_COLAB="2")
        self.assertEqual(r.returncode, 1)
        for trecho in ("forks permitidos", "colaboradores: 2", "RESULTADO: DIVERGE", "Contents precisa ser Read and write",
                       "O token alcança outro repositório PRIVADO"):
            self.assertIn(trecho, r.stdout)

    def test_repositorio_nao_privado_e_recusado_com_aviso(self):
        r = self.rodar(FAKE_PRIVATE="false")
        self.assertEqual(r.returncode, 1)
        self.assertIn("private NÃO é true", r.stdout)
        self.assertIn("NÃO grave nada nele", r.stdout)

    def test_sem_gh_pula_a_conferencia_mas_ainda_roda_o_verificador(self):
        r = self.rodar(com_gh=False)
        self.assertIn("gh ausente ou sem login", r.stdout)
        self.assertIn("RESULTADO: CONFERE", r.stdout)

    def test_sem_ufms_sh_para_com_mensagem(self):
        (self.home / "UFMS-MEU-ESTUDO" / "scripts" / "termux" / "ufms.sh").unlink()
        r = self.rodar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("Não achei o ufms.sh", r.stdout)

    def test_arquivo_temporario_do_log_e_removido(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0)
        self.assertFalse(list(Path(self.tmp.name).glob("**/.tok_pend_*")))
        self.assertIsNone(re.search(r"^/tmp/.*tok", r.stdout, flags=re.M))


if __name__ == "__main__":
    unittest.main()
