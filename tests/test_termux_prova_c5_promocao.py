"""C5, segunda metade (roteiro): contraprovas de scripts/termux/prova_c5_promocao.sh e de scripts/c5_entrada_sintetica.py com
`gh` e `curl` FALSOS (sem rede, sem credencial)."""
import base64
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import c5_entrada_sintetica as c5  # noqa: E402
import promotion_gate as pg  # noqa: E402
from core import topic_rows  # noqa: E402

SCRIPT = ROOT / "scripts/termux/prova_c5_promocao.sh"
PUBLIC = "Andraus35/UFMS-MEU-ESTUDO"
ENTRADA = "Andraus35/ufms-meu-estudo-entrada"
DADOS = "Andraus35/ufms-meu-estudo-dados"
TOKEN = "github_pat_ficticio_zapia_token_0123456789"
COMMIT = "c0ffee00c0ffee00c0ffee00c0ffee00c0ffee00"
SHA_FIXADO = "294b9c38e71edce615c47298d1bf993f4cc72c66"

FAKE_GH = r'''#!/usr/bin/env python3
import base64, json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/calls.log", "a").write(" ".join(a) + "\n")
def err(m): sys.stderr.write(m + "\n"); sys.exit(1)
def b64(t): return base64.b64encode(t.encode()).decode()
if a[0] == "auth": sys.exit(0)
if a[0] == "variable": sys.exit(0 if S["variavel"] else 1)
if a[0] == "run" and a[1] == "list":
    print(json.dumps([{"databaseId": 77, "headSha": S["run_sha"], "status": S["run_status"], "conclusion": S["run_conc"]}] if S["tem_run"] else [])); sys.exit(0)
if a[0] == "run" and a[1] == "view":
    print("saida " + ("FLAG_DESLIGADA" if S["log_flag_desligada"] else "PROCESSADO")); sys.exit(0)
if a[0] != "api": err("fake: nao previsto " + " ".join(a))
p = [x for x in a[1:] if x.startswith("repos/")][0]
put = os.path.exists(D + "/entrada_gravada.json")
if p in ("repos/%(E)s", "repos/%(D)s"):
    print("true" if S["privado"] else "false"); sys.exit(0)
if p.endswith("actions/secrets"): print("DADOS_TOKEN" if S["segredo"] else ""); sys.exit(0)
if p == "repos/%(D)s/contents/consent-v4.json":
    if S["consent"]: print("abc"); sys.exit(0)
    err("gh: Not Found (HTTP 404)")
if p.endswith("contents/.github/workflows/promover.yml"):
    if not S["fluxo"]: err("gh: Not Found (HTTP 404)")
    print(b64("jobs:\nenv:\n  VALIDADOR_REPO: x\n  VALIDADOR_SHA: " + S["sha_fixado"] + "\n  VALIDADOR_GATE_SHA256: y\n")); sys.exit(0)
if p.startswith("repos/%(P)s/contents/settings.json"):
    print(b64(json.dumps({"storage": {"personal_results_writes_enabled": S["flag_publica"], "private_flow_promotion_enabled": S["flag_fluxo"]}}))); sys.exit(0)
if p.startswith("repos/%(D)s/git/trees"):
    print(S["eventos"] + (S["promove"] if put else 0)); sys.exit(0)
if p.startswith("repos/%(D)s/commits"):
    print("dados-novo" if (put and S["cabeca_avanca"]) else "dados-base"); sys.exit(0)
if p.startswith("repos/%(D)s/contents/eventos/"):
    if not (put and S["evento_existe"]): err("gh: Not Found (HTTP 404)")
    print(b64(json.dumps({"evento": {"type": "caderno_recomendado", "event_id": "x"}, "envelope": S["envelope"]}))); sys.exit(0)
if p.startswith("repos/%(E)s/contents/fila/entradas/"):
    if put and S["fila_consumida"]: err("gh: Not Found (HTTP 404)")
    print("sha1"); sys.exit(0)
if p.startswith("repos/%(E)s/contents/recibos/"):
    if put and S["recibo"]: print("sha2"); sys.exit(0)
    err("gh: Not Found (HTTP 404)")
err("fake: nao previsto " + p)
''' % {"E": ENTRADA, "D": DADOS, "P": PUBLIC}

FAKE_CURL = r'''#!/usr/bin/env python3
import base64, json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/curl.log", "a").write(" ".join(a) + "\n")
open(D + "/curl_stdin.log", "a").write(sys.stdin.read())
out = a[a.index("-o") + 1]
corpo = json.loads(a[a.index("--data") + 1])
if S["curl_code"] == 201:
    open(D + "/entrada_gravada.json", "wb").write(base64.b64decode(corpo["content"]))
    open(D + "/curl_url.log", "w").write(a[-1])
json.dump({"commit": {"sha": S["commit"]}}, open(out, "w"))
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
        self.estado = {"privado": True, "variavel": True, "segredo": True, "consent": True, "fluxo": True,
                       "sha_fixado": SHA_FIXADO, "flag_fluxo": True, "flag_publica": False, "eventos": 3, "promove": 1,
                       "cabeca_avanca": True, "evento_existe": True,
                       "envelope": {"origem": "tutor", "entregue_por": "zapia", "escritor": "fluxo", "sintetico": True},
                       "fila_consumida": True, "recibo": True, "curl_code": 201, "commit": COMMIT, "run_sha": COMMIT,
                       "tem_run": True, "run_status": "completed", "run_conc": "success", "log_flag_desligada": False}
        self.salvar()

    def salvar(self):
        (self.fake / "state.json").write_text(json.dumps(self.estado))

    def rodar(self, entradas):
        env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake),
               "C5_TENTATIVAS": "2", "C5_INTERVALO": "0"}
        return subprocess.run(["bash", str(SCRIPT)], input="".join(l + "\n" for l in entradas), capture_output=True, text=True,
                              env=env, timeout=90)

    def log(self, nome):
        p = self.fake / nome
        return p.read_text() if p.exists() else ""


class CaminhoFelizTest(Base):
    def test_promocao_conferida_com_a_marca_e_token_so_por_stdin(self):
        r = self.rodar(["PROMOVER", TOKEN])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("segunda metade da C5 conferida", r.stdout)
        for trecho in ("dados ganhou exatamente 1 evento (3 -> 4)", "sintetico=true, escritor=fluxo, entregue_por=zapia",
                       "a cabeça de dados avançou", "a entrada saiu da fila", "recibo em recibos/c5-sintetica-"):
            self.assertIn(trecho, r.stdout)
        entrada = json.loads((self.fake / "entrada_gravada.json").read_text())
        self.assertIs(entrada["sintetico"], True)
        self.assertEqual(entrada["origem"]["escritor"], "zapia")
        self.assertIn("/repos/%s/contents/fila/entradas/c5-sintetica-" % ENTRADA, self.log("curl_url.log"))
        for texto in (r.stdout, r.stderr, self.log("curl.log"), self.log("calls.log")):
            self.assertNotIn(TOKEN, texto)
        self.assertIn(TOKEN, self.log("curl_stdin.log"))
        self.assertIn("flag do fluxo deve voltar a falsa", r.stdout)


class PreCondicoesTest(Base):
    def bloqueia(self, **mud):
        self.estado.update(mud); self.salvar()
        r = self.rodar(["PROMOVER", TOKEN])
        self.assertEqual(r.returncode, 1, str(mud) + r.stdout + r.stderr)
        self.assertEqual(self.log("curl.log"), "", mud)  # nada foi gravado
        return r

    def test_flag_do_fluxo_desligada_no_sha_fixado_bloqueia(self):
        self.assertIn("NÃO está ligada", self.bloqueia(flag_fluxo=False).stderr)
        self.assertIn("NÃO está ligada", self.bloqueia(flag_fluxo="true").stderr)

    def test_flag_publica_ligada_bloqueia(self):
        self.assertIn("personal_results_writes_enabled", self.bloqueia(flag_publica=True).stderr)

    def test_sha_nao_fixado_ou_curto_bloqueia(self):
        self.bloqueia(sha_fixado="__VALIDADOR_SHA__")
        self.bloqueia(sha_fixado="abcdef12")

    def test_repositorio_nao_privado_ou_pecas_ausentes_bloqueiam(self):
        for mud in ({"privado": False}, {"variavel": False}, {"segredo": False}, {"consent": False}, {"fluxo": False}):
            self.setUp()
            self.bloqueia(**mud)


class ContraprovasTest(Base):
    def test_sem_a_frase_nada_e_gravado(self):
        r = self.rodar(["", TOKEN])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.log("curl.log"), "")

    def test_token_vazio_ou_nao_fine_grained_bloqueia_sem_curl(self):
        for tok in ("", "ghp_classico_ficticio"):
            self.setUp()
            r = self.rodar(["PROMOVER", tok])
            self.assertEqual(r.returncode, 1, tok)
            self.assertEqual(self.log("curl.log"), "", tok)

    def test_token_que_nao_grava_bloqueia(self):
        self.estado["curl_code"] = 403; self.salvar()
        r = self.rodar(["PROMOVER", TOKEN])
        self.assertEqual(r.returncode, 1)
        self.assertIn("não grava em entrada", r.stderr)

    def test_fluxo_que_falha_ou_nao_dispara_diverge(self):
        for mud, trecho in (({"run_conc": "failure"}, "não terminou em sucesso"), ({"tem_run": False}, "nenhuma execução do fluxo")):
            self.setUp()
            self.estado.update(mud); self.salvar()
            r = self.rodar(["PROMOVER", TOKEN])
            self.assertEqual(r.returncode, 2, mud)
            self.assertIn(trecho, r.stdout)

    def test_runner_que_parou_na_flag_diverge(self):
        self.estado["log_flag_desligada"] = True; self.salvar()
        r = self.rodar(["PROMOVER", TOKEN])
        self.assertEqual(r.returncode, 2)
        self.assertIn("FLAG_DESLIGADA", r.stdout)

    def test_historico_que_nao_cresceu_ou_cresceu_demais_diverge(self):
        for promove in (0, 2):
            self.setUp()
            self.estado["promove"] = promove; self.salvar()
            r = self.rodar(["PROMOVER", TOKEN])
            self.assertEqual(r.returncode, 2, promove)
            self.assertIn("contagem de eventos em dados inesperada", r.stdout)

    def test_evento_sem_a_marca_de_teste_ou_com_escritor_errado_diverge(self):
        for env in ({"origem": "tutor", "entregue_por": "zapia", "escritor": "fluxo"},
                    {"sintetico": False, "entregue_por": "zapia", "escritor": "fluxo"},
                    {"sintetico": True, "entregue_por": "zapia", "escritor": "zapia"},
                    {"sintetico": True, "entregue_por": "outro", "escritor": "fluxo"}):
            self.setUp()
            self.estado["envelope"] = env; self.salvar()
            r = self.rodar(["PROMOVER", TOKEN])
            self.assertEqual(r.returncode, 2, env)
            self.assertIn("o envelope não tem a marca de teste", r.stdout)

    def test_evento_ausente_cabeca_parada_fila_nao_consumida_ou_sem_recibo_divergem(self):
        for mud, trecho in (({"evento_existe": False}, "não existe em dados"), ({"cabeca_avanca": False}, "cabeça de dados não avançou"),
                            ({"fila_consumida": False}, "ainda está na fila"), ({"recibo": False}, "não achei o recibo")):
            self.setUp()
            self.estado.update(mud); self.salvar()
            r = self.rodar(["PROMOVER", TOKEN])
            self.assertEqual(r.returncode, 2, mud)
            self.assertIn(trecho, r.stdout)


class EntradaSinteticaTest(unittest.TestCase):
    AGORA = datetime(2026, 11, 20, 10, 30, 5, tzinfo=timezone(timedelta(hours=-4)))

    def test_entrada_montada_passa_no_portao_e_grava_o_envelope_marcado(self):
        nome, bruto, caminho = c5.montar(self.AGORA)
        self.assertEqual(nome, "c5-sintetica-20261120T103005.json")
        entrada = json.loads(bruto)
        self.assertIs(entrada["sintetico"], True)
        self.assertEqual(entrada["evento"]["type"], "caderno_recomendado")
        self.assertEqual(caminho, pg.event_path(entrada["evento"]["event_id"]))
        self.assertTrue(caminho.startswith("eventos/2026-11/20261120-"))
        # promoção de ponta a ponta no portão com fakes: grava com a marca no envelope
        sys.path.insert(0, str(ROOT / "tests"))
        import test_promotion_gate as tg  # noqa: E402
        repo = tg.preparar()
        r = pg.promover(bruto, tg.contexto(repo))
        self.assertEqual(r["status"], "COMMITTED", r)
        guardado = json.loads(repo.arquivos[r["path"]])
        self.assertIs(guardado["envelope"]["sintetico"], True)
        self.assertEqual(guardado["evento"], entrada["evento"])

    def test_sem_marca_o_mesmo_evento_vira_evento_comum(self):
        _, bruto, _ = c5.montar(self.AGORA)
        d = json.loads(bruto); d.pop("sintetico")
        sys.path.insert(0, str(ROOT / "tests"))
        import test_promotion_gate as tg
        repo = tg.preparar()
        r = pg.promover(json.dumps(d).encode(), tg.contexto(repo))
        self.assertNotIn("sintetico", json.loads(repo.arquivos[r["path"]])["envelope"])

    def test_nome_e_evento_mudam_por_segundo_e_o_topico_existe(self):
        a = c5.montar(self.AGORA)
        b = c5.montar(self.AGORA + timedelta(seconds=1))
        self.assertNotEqual((a[0], a[2]), (b[0], b[2]))
        self.assertIn(c5.TOPICO, {t["topic_id"] for t in topic_rows(ROOT)})

    def test_cli_escreve_o_arquivo_e_imprime_nome_e_caminho(self):
        saida = Path(tempfile.mkdtemp()) / "e.json"
        r = subprocess.run([sys.executable, str(ROOT / "scripts/c5_entrada_sintetica.py"), "--saida", str(saida)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r"NOME=c5-sintetica-\d{8}T\d{6}\.json\nEVENTO=eventos/\d{4}-\d{2}/\d{8}-[0-9a-f]{12}\.json\n")
        self.assertIs(json.loads(saida.read_text())["sintetico"], True)

    def test_modulo_nao_faz_rede_nem_le_segredo(self):
        fonte = (ROOT / "scripts/c5_entrada_sintetica.py").read_text(encoding="utf-8")
        for proibido in ("import socket", "urllib", "requests", "subprocess", "os.environ", "http.client"):
            self.assertNotIn(proibido, fonte)


class TextoTest(unittest.TestCase):
    def test_script_nao_liga_flag_nem_apaga_dados_e_nomeia_os_tokens(self):
        t = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("NÃO o zapia_dados", t)
        self.assertNotIn("-X DELETE", t)
        self.assertNotIn("personal_results_writes_enabled=true", t)
        self.assertEqual(t.count('"Authorization: Bearer'), 1)  # o único uso do token é a gravação da entrada


if __name__ == "__main__":
    unittest.main()
