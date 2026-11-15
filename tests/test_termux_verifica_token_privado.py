"""Contraprovas do perfil privado de scripts/termux/verifica_token.sh com um `curl` falso (sem rede nem token real)."""
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "termux" / "verifica_token.sh"
PRIVADO = "Andraus35/ufms-meu-estudo-dados"
PUBLICO = "Andraus35/UFMS-MEU-ESTUDO"
TOKEN = "github_pat_SENTINELA0123456789abcdefABCDEF"

FAKE_CURL = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
stdin = sys.stdin.read()
log = os.environ["FAKE_LOG"]
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"argv": args, "stdin": stdin}) + "\n")
method, hfile, ofile, url = "GET", None, None, args[-1]
for i, a in enumerate(args):
    if a == "-X": method = args[i + 1]
    if a == "-D": hfile = args[i + 1]
    if a == "-o": ofile = args[i + 1]
path = url.replace("https://api.github.com", "")
codes = json.loads(os.environ["FAKE_CODES"])
code = str(codes.get(method + " " + path, codes.get("default", "404")))
headers = "HTTP/2 " + code + "\r\n"
if os.environ.get("FAKE_EXPIRY"):
    headers += "github-authentication-token-expiration: " + os.environ["FAKE_EXPIRY"] + "\r\n"
headers += "x-ratelimit-remaining: 4999\r\nx-ratelimit-limit: 5000\r\n"
body = "{}"
if path == "/user": body = json.dumps({"login": "dono-teste"})
if path.startswith("/user/repos"):
    body = json.dumps([{"full_name": r} for r in os.environ.get("FAKE_REPOS", "").split(",") if r])
if hfile: open(hfile, "w").write(headers)
if ofile: open(ofile, "w").write(body)
sys.stdout.write(code)
'''

CODIGOS_PRIVADO = {"GET /user": 200, "GET /rate_limit": 200, f"GET /repos/{PRIVADO}": 200, "GET /user/repos?per_page=100": 200,
                   f"POST /repos/{PRIVADO}/issues": 403, f"POST /repos/{PRIVADO}/issues/75/comments": 403,
                   f"PUT /repos/{PRIVADO}/contents/sonda-nao-existe.txt": 422, f"POST /repos/{PRIVADO}/pulls": 403,
                   f"PUT /repos/{PUBLICO}/contents/sonda-nao-existe.txt": 403}
CODIGOS_PUBLICO = {"GET /user": 200, "GET /rate_limit": 200, f"GET /repos/{PUBLICO}": 200, "GET /user/repos?per_page=100": 200,
                   f"POST /repos/{PUBLICO}/issues": 422, f"POST /repos/{PUBLICO}/issues/75/comments": 422,
                   f"PUT /repos/{PUBLICO}/contents/sonda-nao-existe.txt": 403, f"POST /repos/{PUBLICO}/pulls": 403}


class VerificaTokenPrivadoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        curl = self.bin / "curl"
        curl.write_text(FAKE_CURL, encoding="utf-8")
        curl.chmod(curl.stat().st_mode | stat.S_IXUSR)
        self.log = self.dir / "curl.log"

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, codigos, repos, expira="2026-12-15 12:00:00 -0400", perfil="privado", token=TOKEN):
        env = dict(os.environ, FAKE_LOG=str(self.log), FAKE_CODES=json.dumps(codigos), FAKE_REPOS=repos,
                   FAKE_EXPIRY=expira or "", PATH=f"{self.bin}:{os.environ['PATH']}")
        if perfil:
            env["PERFIL"] = perfil
        else:
            env.pop("PERFIL", None)
        return subprocess.run(["bash", str(SCRIPT)], input=token + "\n", env=env, capture_output=True, text=True, timeout=60)

    def test_privado_conforme_passa_com_codigo_zero(self):
        r = self.rodar(CODIGOS_PRIVADO, PRIVADO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULTADO: CONFERE com o perfil privado", r.stdout)
        self.assertIn("Gravar no repositório PÚBLICO", r.stdout)
        self.assertNotIn("DIVERGE", r.stdout)

    def test_token_sem_expiracao_diverge(self):
        r = self.rodar(CODIGOS_PRIVADO, PRIVADO, expira="")
        self.assertEqual(r.returncode, 1)
        self.assertIn("SEM expiração", r.stdout)
        self.assertIn("RESULTADO: DIVERGE", r.stdout)

    def test_token_que_alcanca_mais_de_um_repositorio_diverge(self):
        r = self.rodar(CODIGOS_PRIVADO, f"{PRIVADO},{PUBLICO}")
        self.assertEqual(r.returncode, 1)
        self.assertIn("exatamente 1 repositório", r.stdout)

    def test_escrita_aceita_no_repositorio_publico_diverge(self):
        r = self.rodar(dict(CODIGOS_PRIVADO, **{f"PUT /repos/{PUBLICO}/contents/sonda-nao-existe.txt": 422}), PRIVADO)
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"Gravar no repositório PÚBLICO.*DIVERGE \(esperado NAO\)")

    def test_issue_pr_ou_falta_de_escrita_no_privado_divergem(self):
        for mudanca in ({f"POST /repos/{PRIVADO}/issues": 422}, {f"POST /repos/{PRIVADO}/pulls": 422},
                        {f"PUT /repos/{PRIVADO}/contents/sonda-nao-existe.txt": 403}):
            with self.subTest(mudanca=mudanca):
                r = self.rodar(dict(CODIGOS_PRIVADO, **mudanca), PRIVADO)
                self.assertEqual(r.returncode, 1)
                self.assertIn("DIVERGE (esperado", r.stdout)

    def test_token_classic_diverge(self):
        r = self.rodar(CODIGOS_PRIVADO, PRIVADO, token="ghp_SENTINELA0123456789abcdefABCDEF0123")
        self.assertEqual(r.returncode, 1)
        self.assertIn("não é fine-grained", r.stdout)

    def test_perfil_publico_continua_igual_e_confere(self):
        r = self.rodar(CODIGOS_PUBLICO, PUBLICO, perfil=None)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("RESULTADO: CONFERE com o perfil publico", r.stdout)
        self.assertNotIn("PÚBLICO: ", r.stdout.replace("Gravar no repositório PÚBLICO", "X"))

    def test_perfil_publico_com_escrita_de_arquivo_diverge(self):
        r = self.rodar(dict(CODIGOS_PUBLICO, **{f"PUT /repos/{PUBLICO}/contents/sonda-nao-existe.txt": 422}), PUBLICO,
                       perfil="publico")
        self.assertEqual(r.returncode, 1)

    def test_perfil_invalido_para_antes_de_pedir_o_token(self):
        r = self.rodar(CODIGOS_PRIVADO, PRIVADO, perfil="qualquer")
        self.assertEqual(r.returncode, 1)
        self.assertIn("PERFIL deve ser", r.stdout)
        self.assertFalse(self.log.exists())

    def test_o_token_nunca_aparece_na_saida_nem_na_linha_de_comando(self):
        r = self.rodar(CODIGOS_PRIVADO, PRIVADO)
        self.assertNotIn("SENTINELA", r.stdout + r.stderr)
        entradas = [json.loads(l) for l in self.log.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(entradas)
        for e in entradas:
            self.assertNotIn("SENTINELA", " ".join(e["argv"]))      # nunca na linha de comando
            self.assertIn("SENTINELA", e["stdin"])                 # só por stdin (-K -)
        self.assertEqual(sum(1 for e in entradas if "PUT" in e["argv"]), 2)  # sondas de escrita de arquivo
        for e in entradas:
            if "--data" in e["argv"]:
                self.assertEqual(e["argv"][e["argv"].index("--data") + 1], "{}")  # corpo vazio, nada é criado


    def test_documentos_apontam_para_o_perfil_privado_e_exigem_validade(self):
        roteiro = (ROOT / "docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md").read_text(encoding="utf-8")
        handoff = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8")
        for texto in (roteiro, handoff):
            self.assertIn("PERFIL=privado", texto)
        for trecho in ("Contents: Read and write", "Validade obrigatória", "nenhuma outra", "formulário seguro", "nunca vai no chat"):
            self.assertIn(trecho, roteiro)
        self.assertIn("indefinido", handoff)
        configuracao = (ROOT / "settings.json").read_text(encoding="utf-8")
        self.assertRegex(configuracao, r'"personal_results_writes_enabled":\s*false')


if __name__ == "__main__":
    unittest.main()
