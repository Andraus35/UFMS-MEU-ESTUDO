"""ZAPIA-F3 (roteiro): contraprovas de scripts/termux/prova_f3_zapia.sh com `gh` e `git` FALSOS (sem rede, sem credencial). `gh auth token` devolve vazio,
então a sonda real falha fechada sem tocar a rede."""
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
SCRIPT = ROOT / "scripts/termux/prova_f3_zapia.sh"
ENTRADA = "Andraus35/ufms-meu-estudo-entrada"
PUBLICO = "Andraus35/UFMS-MEU-ESTUDO"
REF = "c0ffee00c0ffee00c0ffee00c0ffee00c0ffee00"

FAKE_GH = r'''#!/usr/bin/env python3
import base64, json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
a = sys.argv[1:]
open(D + "/calls.log", "a").write(" ".join(a) + "\n")
def salvar(): json.dump(S, open(D + "/state.json", "w"))
if a[0] == "auth":
    if a[1] == "token": print("")
    sys.exit(0)
if a[0] == "api":
    metodo = a[a.index("-X") + 1] if "-X" in a else "GET"
    p = [x for x in a[1:] if x.startswith("repos/")][0]
    if p == "repos/" + os.environ["ENTRADA"]: print("true" if S["privado"] else "false"); sys.exit(0)
    if p.startswith("repos/" + os.environ["PUBLICO"] + "/commits/"): print(p.rsplit("/", 1)[1]); sys.exit(0)
    caminho = p.split("/contents/", 1)[1]
    arqs = S["arquivos"]
    def campo(nome): return a[a.index("-f") + 1:] and [x.split("=", 1)[1] for x in a if x.startswith(nome + "=")][0]
    if metodo == "PUT":
        arqs[caminho] = campo("content"); salvar(); sys.exit(0)
    if metodo == "DELETE":
        arqs.pop(caminho, None); salvar(); sys.exit(0)
    if caminho not in arqs: sys.exit(1)
    print("sha-" + caminho.replace("/", "_") if "--jq" in a and ".sha" in a[a.index("--jq") + 1] else arqs[caminho]); sys.exit(0)
sys.exit(1)
'''
FAKE_GIT = '''#!/bin/sh
case "$*" in
  *rev-parse*) echo c0ffee00c0ffee00c0ffee00c0ffee00c0ffee00 ;;
  *status*) ;;
esac
exit 0
'''


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        (self.d / "bin").mkdir()
        for nome, corpo in (("gh", FAKE_GH), ("git", FAKE_GIT)):
            (self.d / "bin" / nome).write_text(corpo)
            (self.d / "bin" / nome).chmod(stat.S_IRWXU)
        self.estado(privado=True, arquivos={})
        self.env = dict(os.environ, PATH=f"{self.d / 'bin'}:{os.environ['PATH']}", FAKE_DIR=str(self.d), ENTRADA=ENTRADA, PUBLICO=PUBLICO,
                        F3_ESTADO=str(self.d / "estado.json"), HOME=str(self.d))

    def estado(self, **mud):
        s = json.loads((self.d / "state.json").read_text()) if (self.d / "state.json").exists() else {}
        s.update(mud)
        (self.d / "state.json").write_text(json.dumps(s))

    def arquivos(self):
        return json.loads((self.d / "state.json").read_text())["arquivos"]

    def rodar(self, *args, entrada=""):
        return subprocess.run(["bash", str(SCRIPT), *args], input=entrada, capture_output=True, text=True, env=self.env, timeout=60)

    def chamadas(self):
        return (self.d / "calls.log").read_text().splitlines() if (self.d / "calls.log").exists() else []


class PreparoTest(Base):
    def test_uso_sem_argumento_nao_faz_nada(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.chamadas(), [])

    def test_repositorio_nao_privado_bloqueia_sem_escrever(self):
        self.estado(privado=False)
        r = self.rodar("preparar", entrada="TESTAR\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("não é privado", r.stderr)
        self.assertEqual(self.arquivos(), {})

    def test_resto_de_teste_anterior_bloqueia(self):
        self.estado(arquivos={"comandos/validados/f3-alvo.json": "eA=="})
        r = self.rodar("preparar", entrada="TESTAR\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("já existe comandos/validados/f3-alvo.json", r.stderr)

    def test_sem_a_palavra_testar_nada_e_gravado(self):
        r = self.rodar("preparar", entrada="\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Nada foi feito", r.stdout)
        self.assertEqual(self.arquivos(), {})

    def test_preparar_grava_so_o_par_sintetico_e_mostra_o_prompt_do_poller(self):
        r = self.rodar("preparar", entrada="TESTAR\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(self.arquivos()), ["comandos/recibos/f3-alvo.json", "comandos/recibos/f3-pedido.json",
                                                   "comandos/validados/f3-alvo.json", "comandos/validados/f3-pedido.json"])
        pedido = json.loads(base64.b64decode(self.arquivos()["comandos/validados/f3-pedido.json"]))
        self.assertEqual(pedido["operation"], "agendar_rotina")
        recibo = json.loads(base64.b64decode(self.arquivos()["comandos/recibos/f3-pedido.json"]))
        self.assertEqual(recibo["codigo"], "SINTETICO_MANUAL")
        for trecho in (f"ref={REF}", "execução única", "comandos/criadas", "INICIO", "FIM", "TESTE F3"):
            self.assertIn(trecho, r.stdout, trecho)
        estado = json.loads((self.d / "estado.json").read_text())
        poller, filha = (datetime.strptime(estado[k], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) for k in ("poller", "filha"))
        agora = datetime.now(timezone.utc)
        self.assertGreater(poller, agora + timedelta(minutes=15))
        self.assertGreater(filha, agora + timedelta(minutes=90))  # a caixa exige 90 min para o pedido
        self.assertGreater(filha, poller)
        self.assertNotIn("github_pat", r.stdout + r.stderr)

    def test_so_usa_gh_api_com_metodos_e_caminhos_do_teste(self):
        self.rodar("preparar", entrada="TESTAR\n")
        for linha in self.chamadas():
            if linha.startswith("api") and "-X" in linha:
                self.assertRegex(linha, r"-X PUT repos/Andraus35/ufms-meu-estudo-entrada/contents/comandos/(validados|recibos)/f3-(alvo|pedido)\.json ")


class ConferirELimparTest(Base):
    def test_conferir_sem_estado_bloqueia(self):
        self.assertEqual(self.rodar("conferir").returncode, 1)

    def test_conferir_sem_recibo_criada_nao_prova_e_diz_o_que_fazer(self):
        self.rodar("preparar", entrada="TESTAR\n")
        r = self.rodar("conferir", entrada="SIM\nSIM\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("SEM_RECIBO_CRIADA", r.stdout)
        self.assertIn("NÃO PROVADO", r.stdout)
        self.assertIn("pode refutar", r.stdout)

    def test_conferir_completo_prova_so_com_recibos_consistentes_e_relatos(self):
        import hashlib
        import zapia_entrega as ze
        import zapia_poller as zp
        self.rodar("preparar", entrada="TESTAR\n")
        estado = json.loads((self.d / "estado.json").read_text())
        arq = self.arquivos()
        pedido = json.loads(base64.b64decode(arq["comandos/validados/f3-pedido.json"]))
        recibo_pedido = json.loads(base64.b64decode(arq["comandos/recibos/f3-pedido.json"]))
        alvo = json.loads(base64.b64decode(arq["comandos/recibos/f3-alvo.json"]))
        poller = datetime.strptime(estado["poller"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        texto = zp.instrucao_esperada(pedido, ENTRADA)
        criada = {"entrada_id": "f3-pedido.json", "hash_corpo": recibo_pedido["hash_corpo"], "status": "CRIADA", "agendado_utc": estado["filha"],
                  "criada_em": (poller + timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"), "rotina_id_relatado": "rot-1",
                  "instrucao_sha256": hashlib.sha256(texto.encode()).hexdigest()}
        entrega = {"entrada_id": "f3-alvo.json", "hash_corpo": alvo["hash_corpo"], "status": "ENTREGUE", "origem_declarada": "coach",
                   "entregue_em": (datetime.strptime(estado["filha"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=20)).strftime("%Y-%m-%dT%H:%M:%SZ")}
        s = json.loads((self.d / "state.json").read_text())
        s["arquivos"]["comandos/criadas/f3-pedido.json"] = base64.b64encode(ze._canonico(criada)).decode()
        s["arquivos"]["comandos/entregas/f3-alvo.json"] = base64.b64encode(ze._canonico(entrega)).decode()
        (self.d / "state.json").write_text(json.dumps(s))
        r = self.rodar("conferir", entrada="SIM\nSIM\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PROVADO", r.stdout)
        self.assertIn("NÃO provado: promoção pelo fluxo", r.stdout)
        # sem o relato da lista de rotinas do app e da notificação, o resultado cai para NÃO PROVADO
        r2 = self.rodar("conferir", entrada="NAO\nNAO\n")
        self.assertEqual(r2.returncode, 2)
        self.assertIn("sem confirmação da rotina filha", r2.stdout)

    def test_limpar_so_apaga_com_a_palavra_e_apaga_os_seis_nomes(self):
        self.rodar("preparar", entrada="TESTAR\n")
        r = self.rodar("limpar", entrada="\n")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(self.arquivos()), 4)
        r = self.rodar("limpar", entrada="LIMPAR\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.arquivos(), {})
        self.assertFalse((self.d / "estado.json").exists())
        self.assertIn("poller e a rotina filha", r.stdout)


class EstaticoTest(unittest.TestCase):
    def test_sintaxe_e_sem_segredo(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)]).returncode, 0)
        t = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("git push", "gh pr ", "gh workflow", "variable set", "gh secret", "ghp_", "github_pat_", "echo \"$GH_TOKEN", "private_flow_promotion_enabled"):
            self.assertNotIn(proibido, t, proibido)
        self.assertIn("set -eu", t)


if __name__ == "__main__":
    unittest.main()
