"""C5 (roteiro): contraprovas de scripts/termux/prova_c5.sh com `gh` e `curl` FALSOS (sem rede, sem credencial)."""
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/termux/prova_c5.sh"
ENTRADA = "Andraus35/ufms-meu-estudo-entrada"
DADOS = "Andraus35/ufms-meu-estudo-dados"
TOKEN = "github_pat_ficticio_zapia_token_0123456789"
COMMIT = "c0ffee00c0ffee00c0ffee00c0ffee00c0ffee00"

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/calls.log", "a").write(" ".join(a) + "\n")
def err(m): sys.stderr.write(m + "\n"); sys.exit(1)
j = " ".join(a)
if a[0] == "auth": sys.exit(0)
if a[0] == "variable": sys.exit(0 if S["variavel"] else 1)
if a[0] == "run" and a[1] == "list":
    seq = S.get("run_sequencia")  # lista de [status, conclusão] consumida a cada consulta; a conclusão vem VAZIA enquanto roda
    if seq:
        n = int(open(D + "/seq_n").read()) if os.path.exists(D + "/seq_n") else 0
        open(D + "/seq_n", "w").write(str(n + 1))
        st, co = seq[min(n, len(seq) - 1)]
    else:
        st, co = S["run_status"], S["run_conc"]
    print(json.dumps([{"databaseId": 77, "headSha": S["run_sha"], "status": st, "conclusion": co}] if S["tem_run"] else [])); sys.exit(0)
if a[0] == "run" and a[1] == "view":
    print("saida {\"estado\": \"FLAG_DESLIGADA\"}" if S["log_flag"] else "saida sem flag"); sys.exit(0)
if a[0] == "api":
    if "-X" in a and "DELETE" in a: sys.exit(0 if S["delete_ok"] else 1)
    p = [x for x in a[1:] if x.startswith("repos/")][0]
    if p == "repos/" + "%s": print("true"); sys.exit(0)
    if p.endswith("actions/secrets"):
        print("DADOS_TOKEN" if S["segredo"] else ""); sys.exit(0)
    if "contents/.github/workflows" in p:
        if S["fluxo"]: print("promover.yml"); sys.exit(0)
        err("gh: Not Found (HTTP 404)")
    if p.startswith("repos/%s/commits"):
        print(S["dados_sha"]); sys.exit(0)
    if "contents/fila/entradas/" in p: print("abc123"); sys.exit(0)
    if p == "repos/%s": print("true"); sys.exit(0)
err("fake: nao previsto " + j)
''' % (ENTRADA, DADOS, ENTRADA)

FAKE_CURL = r'''#!/usr/bin/env python3
import json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/curl.log", "a").write(" ".join(a) + "\n")
open(D + "/curl_stdin.log", "a").write(sys.stdin.read())
out = a[a.index("-o") + 1]
json.dump({"commit": {"sha": S["commit"]}}, open(out, "w"))
if S["dados_muda"]:
    S["dados_sha"] = "dados-mudou"; json.dump(S, open(D + "/state.json", "w"))
sys.stdout.write(str(S["curl_code"]))
'''


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.bin = self.tmp / "bin"; self.bin.mkdir()
        self.fake = self.tmp / "fake"; self.fake.mkdir()
        for nome, codigo in (("gh", FAKE_GH), ("curl", FAKE_CURL)):
            (self.bin / nome).write_text(codigo)
            (self.bin / nome).chmod((self.bin / nome).stat().st_mode | stat.S_IXUSR)
        self.estado = {"variavel": True, "segredo": True, "fluxo": True, "dados_sha": "dados-base", "dados_muda": False,
                       "curl_code": 201, "commit": COMMIT, "run_sha": COMMIT, "tem_run": True, "run_status": "completed",
                       "run_conc": "success", "log_flag": True, "delete_ok": True}
        self.salvar()

    def salvar(self):
        (self.fake / "state.json").write_text(json.dumps(self.estado))

    def rodar(self, entradas):
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake),
               "C5_TENTATIVAS": "2", "C5_INTERVALO": "0"}
        return subprocess.run(["bash", str(SCRIPT)], input="".join(l + "\n" for l in entradas), capture_output=True, text=True,
                              env=env, timeout=60)

    def log(self, nome):
        p = self.fake / nome
        return p.read_text() if p.exists() else ""


class CaminhoFelizTest(Base):
    def test_prova_conferida_e_token_so_por_stdin(self):
        r = self.rodar(["PROVAR", TOKEN, "LIMPAR"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("primeira metade da C5 conferida", r.stdout)
        self.assertIn("FLAG_DESLIGADA", r.stdout)
        self.assertIn("-X PUT", self.log("curl.log"))
        self.assertIn("fila/entradas/c5-sintetica-", self.log("curl.log"))
        for texto in (r.stdout, r.stderr, self.log("curl.log"), self.log("calls.log")):
            self.assertNotIn(TOKEN, texto)  # o token nunca aparece em argumento nem na tela
        self.assertIn(TOKEN, self.log("curl_stdin.log"))  # entrou por stdin (config do curl)
        self.assertIn("DELETE", self.log("calls.log"))


    def test_espera_com_conclusao_vazia_enquanto_o_fluxo_roda_nao_derruba_o_script(self):
        # prova real de 18/11/2026: `$3: unbound variable` quando a conclusão vem vazia (fluxo ainda rodando)
        self.estado["run_sequencia"] = [["in_progress", ""], ["queued", ""], ["completed", "success"]]
        self.salvar()
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake), "C5_TENTATIVAS": "5", "C5_INTERVALO": "0"}
        r = subprocess.run(["bash", str(SCRIPT)], input="PROVAR\n" + TOKEN + "\nLIMPAR\n", capture_output=True, text=True, env=env, timeout=90)
        self.assertNotIn("unbound variable", r.stderr + r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("fluxo concluído com sucesso", r.stdout)

    def test_token_com_caractere_fora_do_padrao_bloqueia_sem_curl(self):
        # `read` já apara espaço e tabulação nas pontas; sobram o CR de colagem, o caractere invisível e o espaço no meio
        for tok in (TOKEN + "\r", TOKEN + "\u200b", "github_pat_com espaco_no_meio_123456"):
            self.setUp()
            r = self.rodar(["PROVAR", tok])
            self.assertEqual(r.returncode, 1, repr(tok))
            self.assertIn("fora do padrão", r.stderr, repr(tok))
            self.assertEqual(self.log("curl.log"), "", repr(tok))


class ContraprovasTest(Base):
    def test_sem_a_frase_nada_e_gravado(self):
        r = self.rodar(["", TOKEN])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.log("curl.log"), "")

    def test_pre_condicoes_ausentes_bloqueiam(self):
        for chave in ("variavel", "segredo", "fluxo"):
            self.setUp()
            self.estado[chave] = False; self.salvar()
            r = self.rodar(["PROVAR", TOKEN])
            self.assertEqual(r.returncode, 1, chave)
            self.assertEqual(self.log("curl.log"), "", chave)

    def test_token_nao_fine_grained_ou_vazio_bloqueia_sem_curl(self):
        for tok in ("", "ghp_classico_ficticio"):
            self.setUp()
            r = self.rodar(["PROVAR", tok])
            self.assertEqual(r.returncode, 1, tok)
            self.assertEqual(self.log("curl.log"), "", tok)

    def test_token_que_nao_grava_bloqueia(self):
        self.estado["curl_code"] = 403; self.salvar()
        r = self.rodar(["PROVAR", TOKEN])
        self.assertEqual(r.returncode, 1)
        self.assertIn("não grava em entrada", r.stderr)

    def test_fluxo_sem_sucesso_diverge(self):
        self.estado["run_conc"] = "failure"; self.salvar()
        r = self.rodar(["PROVAR", TOKEN, ""])
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("não terminou em sucesso", r.stdout)

    def test_gatilho_que_nao_dispara_diverge(self):
        self.estado["tem_run"] = False; self.salvar()
        r = self.rodar(["PROVAR", TOKEN, ""])
        self.assertEqual(r.returncode, 2)
        self.assertIn("nenhuma execução do fluxo", r.stdout)

    def test_log_sem_flag_desligada_diverge(self):
        self.estado["log_flag"] = False; self.salvar()
        r = self.rodar(["PROVAR", TOKEN, ""])
        self.assertEqual(r.returncode, 2)
        self.assertIn("não mostra FLAG_DESLIGADA", r.stdout)

    def test_dados_que_muda_diverge_e_manda_nao_avancar(self):
        self.estado["dados_muda"] = True; self.salvar()
        r = self.rodar(["PROVAR", TOKEN, ""])
        self.assertEqual(r.returncode, 2)
        self.assertIn("dados mudou", r.stdout)
        self.assertIn("não avance para a C6", r.stderr)

    def test_sem_limpar_mantem_o_arquivo_e_nao_apaga(self):
        r = self.rodar(["PROVAR", TOKEN, ""])
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("DELETE", self.log("calls.log"))

    def test_falha_ao_remover_vira_divergencia(self):
        self.estado["delete_ok"] = False; self.salvar()
        r = self.rodar(["PROVAR", TOKEN, "LIMPAR"])
        self.assertEqual(r.returncode, 2)


class TextoTest(unittest.TestCase):
    def test_nao_habilita_escrita_e_nomeia_os_tokens(self):
        t = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("NÃO o zapia_dados", t)
        self.assertIn("continua DESABILITADA", t)
        self.assertNotIn("personal_results_writes_enabled=true", t)
        self.assertEqual(t.count('"Authorization: Bearer'), 1)  # o único uso do token é a gravação sintética


if __name__ == "__main__":
    unittest.main()
