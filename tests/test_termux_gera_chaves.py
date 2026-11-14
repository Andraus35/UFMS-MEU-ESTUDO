"""Contraprovas de scripts/termux/gera_chaves.sh (sem rede; chaves só em diretório temporário)."""
import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "termux" / "gera_chaves.sh"
PUB = re.compile(r"^  (tutor|coach) ([0-9a-f]{64})$", re.M)


class GeraChavesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "keys"

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, keydir=None):
        env = dict(os.environ, KEYDIR=str(keydir or self.dir))
        return subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=60)

    def test_sintaxe_bash_valida_e_arquivo_executavel(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)
        self.assertTrue(SCRIPT.read_text(encoding="utf-8").startswith("#!/data/data/com.termux/files/usr/bin/bash"))

    def test_gera_duas_chaves_0600_em_diretorio_0700_e_imprime_so_publicas(self):
        r = self.run_script()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(stat.S_IMODE(self.dir.stat().st_mode), 0o700)
        pubs = dict(PUB.findall(r.stdout))
        self.assertEqual(set(pubs), {"tutor", "coach"})
        self.assertNotEqual(pubs["tutor"], pubs["coach"])
        for papel in ("tutor", "coach"):
            chave = self.dir / f"{papel}.key"
            self.assertEqual(stat.S_IMODE(chave.stat().st_mode), 0o600)
            segredo = chave.read_text(encoding="utf-8").strip()
            self.assertNotIn(segredo, r.stdout + r.stderr)
            self.assertNotEqual(segredo, pubs[papel])

    def test_nao_sobrescreve_e_reaproveita_a_chave_existente(self):
        primeiro = self.run_script()
        antes = {p: (self.dir / f"{p}.key").read_text(encoding="utf-8") for p in ("tutor", "coach")}
        segundo = self.run_script()
        self.assertEqual(segundo.returncode, 0, segundo.stderr)
        self.assertIn("mantida", segundo.stdout)
        self.assertEqual(dict(PUB.findall(primeiro.stdout)), dict(PUB.findall(segundo.stdout)))
        for p, texto in antes.items():
            self.assertEqual((self.dir / f"{p}.key").read_text(encoding="utf-8"), texto)

    def test_recusa_keydir_dentro_do_repositorio_sem_criar_nada(self):
        dentro = ROOT / "chaves_teste_tmp"
        r = self.run_script(dentro)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("repositório", r.stderr)
        self.assertFalse(dentro.exists())

    def test_chave_existente_com_permissao_aberta_falha_sem_vazar(self):
        self.run_script()
        chave = self.dir / "tutor.key"
        segredo = chave.read_text(encoding="utf-8").strip()
        os.chmod(chave, 0o644)
        r = self.run_script()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("guarda FALHOU", r.stderr)
        self.assertNotIn(segredo, r.stdout + r.stderr)

    def test_symlink_no_lugar_da_chave_e_recusado(self):
        self.dir.mkdir(mode=0o700)
        alvo = Path(self.tmp.name) / "alvo.key"
        alvo.write_text("ab" * 32 + "\n", encoding="utf-8")
        os.chmod(alvo, 0o600)
        (self.dir / "tutor.key").symlink_to(alvo)
        r = self.run_script()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("guarda FALHOU", r.stderr)

    def test_script_nao_toca_em_token_nem_rede(self):
        texto = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("curl", "wget", "GH_TOKEN", "github_pat_", "git push", "gh "):
            self.assertNotIn(proibido, texto)


if __name__ == "__main__":
    unittest.main()
