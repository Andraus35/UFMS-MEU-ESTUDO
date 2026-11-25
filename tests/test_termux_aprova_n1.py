"""Roteiro aprova_n1.sh com `gh` FALSO (sem rede, sem credencial) e chave sintética em pasta temporária."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import aprovacao_comando as ap  # noqa: E402
import command_box  # noqa: E402
import zapia_n1_prep as prep  # noqa: E402

SCRIPT = ROOT / "scripts/termux/aprova_n1.sh"
FAKE_GH = r'''#!/usr/bin/env python3
import base64, json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/calls.log", "a").write(" ".join(a) + "\n")
if a[0] == "auth":
    sys.exit(0)
if a[0] == "api":
    p = [x for x in a[1:] if x.startswith("repos/")][0]
    if p == "repos/Andraus35/ufms-meu-estudo-entrada":
        print("true" if S["privado"] else "false"); sys.exit(0)
    caminho = p.split("/contents/", 1)[1]
    arq = D + "/repo/" + caminho
    if "-X" in a and "PUT" in a:
        if S["put_falha"]:
            sys.exit(1)
        dados = base64.b64decode([x for x in a if x.startswith("content=")][0][len("content="):])
        if S["corrompe"]:
            dados += b"x"
        os.makedirs(os.path.dirname(arq), exist_ok=True)
        open(arq, "wb").write(dados); sys.exit(0)
    if os.path.isdir(arq):
        for n in sorted(os.listdir(arq)): print(n)
        sys.exit(0)
    if not os.path.exists(arq):
        sys.exit(1)
    if "--jq" in a:
        print(base64.b64encode(open(arq, "rb").read()).decode())
    sys.exit(0)
sys.exit(1)
'''


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        os.chmod(self.tmp, 0o700)
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin/gh").write_text(FAKE_GH)
        (self.tmp / "bin/gh").chmod(0o755)
        self.fake = self.tmp / "fake"
        (self.fake / "repo/comandos/validados").mkdir(parents=True)
        (self.fake / "state.json").write_text(json.dumps({"privado": True, "put_falha": False, "corrompe": False}))
        m = prep.montar(datetime.now(timezone.utc))
        self.hashes = {}
        for i in m["itens"]:
            (self.fake / "repo/comandos/validados" / i["nome"]).write_bytes(i["comando_bytes"])
            self.hashes[i["nome"]] = i["hash_corpo"]
        self.chave = self.tmp / "chaves" / "proprietario"

    def roda(self, passo, entrada=""):
        env = {**os.environ, "PATH": f"{self.tmp / 'bin'}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake), "UFMS_CHAVE": str(self.chave), "HOME": str(self.tmp)}
        return subprocess.run(["bash", str(SCRIPT), passo], input=entrada, capture_output=True, text=True, env=env, timeout=60)

    def calls(self):
        p = self.fake / "calls.log"
        return p.read_text() if p.exists() else ""

    def pub(self):
        import agent_keys
        from ed25519_pure import public_key
        return public_key(bytes.fromhex(self.chave.read_text().strip())).hex()


class ChaveTest(Base):
    def test_gera_chave_fora_do_repo_com_modo_0600_e_nao_sobrescreve(self):
        r = self.roda("chave")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(stat.S_IMODE(self.chave.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.chave.parent.stat().st_mode), 0o700)
        segredo = self.chave.read_text().strip()
        self.assertNotIn(segredo, r.stdout + r.stderr)  # a privada nunca é impressa
        self.assertIn(self.pub(), r.stdout)
        antes = self.chave.read_text()
        self.assertEqual(self.roda("chave").returncode, 1)
        self.assertEqual(self.chave.read_text(), antes)

    def test_passo_invalido(self):
        self.assertEqual(self.roda("apagar").returncode, 2)


class AprovarTest(Base):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.roda("chave").returncode, 0)

    def test_sem_a_frase_nao_assina_nem_grava(self):
        for entrada in ("\n", "aprovo n1\n"):
            r = self.roda("aprovar", entrada)
            self.assertEqual(r.returncode, 1)
        self.assertNotIn("PUT", self.calls())

    def test_mostra_o_prompt_e_com_a_frase_grava_aprovacoes_que_verificam(self):
        r = self.roda("aprovar", "APROVO N1\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Tópico:", r.stdout)  # o proprietário lê o prompt antes de aprovar
        pasta = self.fake / "repo/comandos/aprovacoes"
        self.assertEqual(len(list(pasta.iterdir())), 3)
        for nome, h in self.hashes.items():
            a = json.loads((pasta / (nome.replace(".json", "") + ".aprovacao.json")).read_text())
            self.assertIsNone(ap.verificar(a, h, self.pub()), nome)
        self.assertEqual(self.calls().count("-X PUT"), 3)
        self.assertNotIn(self.chave.read_text().strip(), r.stdout + r.stderr)

    def test_sem_chave_repo_publico_e_sem_comandos_bloqueiam(self):
        self.chave.unlink()
        self.assertEqual(self.roda("aprovar", "APROVO N1\n").returncode, 1)
        self.assertNotIn("PUT", self.calls())
        self.assertEqual(self.roda("chave").returncode, 0)
        (self.fake / "state.json").write_text(json.dumps({"privado": False, "put_falha": False, "corrompe": False}))
        self.assertEqual(self.roda("aprovar", "APROVO N1\n").returncode, 1)
        (self.fake / "state.json").write_text(json.dumps({"privado": True, "put_falha": False, "corrompe": False}))
        shutil.rmtree(self.fake / "repo/comandos/validados")
        (self.fake / "repo/comandos/validados").mkdir()
        self.assertEqual(self.roda("aprovar", "APROVO N1\n").returncode, 1)

    def test_nao_sobrescreve_e_falhas_de_gravacao_dao_divergencia(self):
        (self.fake / "repo/comandos/aprovacoes").mkdir(parents=True)
        (self.fake / "repo/comandos/aprovacoes/n1-fonte.aprovacao.json").write_text("antiga")
        r = self.roda("aprovar", "APROVO N1\n")
        self.assertEqual(r.returncode, 2)
        self.assertEqual((self.fake / "repo/comandos/aprovacoes/n1-fonte.aprovacao.json").read_text(), "antiga")
        shutil.rmtree(self.fake / "repo/comandos/aprovacoes")
        (self.fake / "state.json").write_text(json.dumps({"privado": True, "put_falha": True, "corrompe": False}))
        self.assertEqual(self.roda("aprovar", "APROVO N1\n").returncode, 2)
        (self.fake / "state.json").write_text(json.dumps({"privado": True, "put_falha": False, "corrompe": True}))
        self.assertEqual(self.roda("aprovar", "APROVO N1\n").returncode, 2)


class EstaticosTest(unittest.TestCase):
    def test_script_sem_segredo_flag_nem_fila(self):
        t = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("personal_results_writes_enabled", "fila/entradas", "curl", "-X DELETE", "TOKEN", "cat \"$CHAVE\"", "echo \"$SEGREDO"):
            self.assertNotIn(proibido, t, proibido)
        self.assertIn("APROVO N1", t)
        self.assertEqual(t.count("-X PUT"), 1)


if __name__ == "__main__":
    unittest.main()
