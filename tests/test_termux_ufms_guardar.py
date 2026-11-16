"""Contraprovas de `ufms.sh consentir-v3` e `ufms.sh guardar-plano` (gh falso, sem rede, sem credencial)."""
import base64
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import private_persistence_guard as guard  # noqa: E402

SCRIPT = ROOT / "scripts" / "termux" / "ufms.sh"
ADR = ROOT / "docs" / "governanca" / "ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"

FAKE_GH = r'''#!/usr/bin/env python3
import base64, hashlib, json, os, pathlib, sys
D = pathlib.Path(os.environ["FAKE_DIR"])
args = sys.argv[1:]
with open(D / "calls.log", "a", encoding="utf-8") as f:
    f.write(" ".join(args) + "\n")
def nao_achou():
    sys.stderr.write("gh: Not Found (HTTP 404)\n"); sys.exit(1)
if args[0] == "auth":
    sys.exit(1 if (D / "noauth").exists() else 0)
a = args[1:]
metodo = "GET"
if a[0] == "-X":
    metodo, a = a[1], a[2:]
caminho, resto = a[0], a[1:]
arquivos = D / "arquivos"; arquivos.mkdir(exist_ok=True)
def chave(p): return arquivos / p.replace("/", "__")
if metodo == "PUT":
    corpo = {}
    if "--input" in resto:
        corpo = json.loads(pathlib.Path(resto[resto.index("--input") + 1]).read_text(encoding="utf-8"))
    for i, x in enumerate(resto):
        if x == "-f" and resto[i + 1].startswith("content="):
            corpo["content"] = resto[i + 1][len("content="):]
    if (D / "put_falha").exists():
        sys.stderr.write("gh: Server Error (HTTP 500)\n"); sys.exit(1)
    p = caminho.split("/contents/", 1)[1]
    chave(p).write_text(corpo["content"], encoding="utf-8")
    sys.exit(0)
if "/contents/" in caminho:
    p = caminho.split("/contents/", 1)[1]
    if not chave(p).exists():
        nao_achou()
    conteudo = chave(p).read_text(encoding="utf-8")
    if ".sha" in " ".join(resto):
        print("fakesha-" + hashlib.sha1(conteudo.encode()).hexdigest())
    elif os.environ.get("FAKE_READBACK_BAD") and p.startswith(os.environ["FAKE_READBACK_BAD"]):
        print("AAAA")
    else:
        print(conteudo)
    sys.exit(0)
if (D / "error500").exists():
    sys.stderr.write("gh: Server Error (HTTP 500)\n"); sys.exit(1)
if not (D / "existe").exists():
    nao_achou()
print((D / "privado").read_text(encoding="utf-8"), end="")
'''

PLANO = {"parameters": {"method": "4.2", "start_date": "2026-11-16", "exam_date": "2027-01-17", "daily_minutes": 240,
                        "rest_weekday": 6}, "days": [{"date": "2026-11-16", "weekday": 0, "kind": "teoria", "items": []}]}


def consentimento_v3(**mudancas):
    c = {"version": "v3", "scope": "resultados_estudo", "inclui": ["resultados_estudo", "plano_estudo"],
         "granted_at": "2026-11-15T12:00:00+00:00", "revoked_at": None, "text": "t", "text_sha256": "x"}
    c.update(mudancas)
    return c


class ConsentirEGuardarTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
        self.estado = self.dir / "estado"
        self.estado.mkdir()
        self.planos = self.dir / "planos"
        self.planos.mkdir()
        self.repo_existe(True)

    def tearDown(self):
        self.tmp.cleanup()

    def repo_existe(self, privado):
        (self.estado / "existe").touch()
        (self.estado / "privado").write_text("true" if privado else "false", encoding="utf-8")

    def rodar(self, *args, entrada="", **env):
        ambiente = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_DIR=str(self.estado), UFMS_DIR=str(ROOT),
                        UFMS_PLANO_DIR=str(self.planos), UFMS_SEM_PKG="1", UFMS_SEM_REDE="1", TMPDIR=str(self.dir))
        ambiente.update(env)
        return subprocess.run(["bash", str(SCRIPT), *args], input=entrada, env=ambiente, capture_output=True, text=True,
                              timeout=120)

    def arquivo_remoto(self, caminho):
        p = self.estado / "arquivos" / caminho.replace("/", "__")
        return p if p.exists() else None

    def guardado(self, caminho):
        p = self.arquivo_remoto(caminho)
        return base64.b64decode(p.read_text(encoding="utf-8")) if p else None

    def chamadas(self):
        p = self.estado / "calls.log"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def semear(self, caminho, conteudo):
        (self.estado / "arquivos").mkdir(exist_ok=True)
        (self.estado / "arquivos" / caminho.replace("/", "__")).write_text(
            base64.b64encode(conteudo if isinstance(conteudo, bytes) else conteudo.encode()).decode(), encoding="utf-8")

    def plano(self, nome="plano-2026-11-16-ambos.json", dados=None):
        p = self.planos / nome
        p.write_text(json.dumps(dados or PLANO, ensure_ascii=False), encoding="utf-8")
        return p

    # consentir-v3 --------------------------------------------------------------------------------------------
    def test_consentir_v3_registra_arquivo_valido_sem_tocar_no_v2(self):
        self.semear("consent.json", "ORIGINAL-V2")
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        c = json.loads(self.guardado("consent-v3.json"))
        self.assertEqual(guard.check_consent(c), "v3")
        self.assertIn("plano_estudo", c["inclui"])
        self.assertIn("resultados_estudo", c["inclui"])
        self.assertIsNone(c["revoked_at"])
        self.assertEqual(c["text_sha256"], hashlib.sha256(c["text"].encode("utf-8")).hexdigest())
        self.assertIn(c["text"], ADR.read_text(encoding="utf-8"))
        self.assertIn("plano de estudos", c["text"])
        self.assertEqual(self.guardado("consent.json"), b"ORIGINAL-V2")
        self.assertNotIn("contents/consent.json", self.chamadas().replace("consent-v3.json", ""))
        self.assertIn("readback", r.stdout)
        self.assertIn("DESABILITADA", r.stdout)

    def test_consentir_v3_so_com_a_frase_exata(self):
        for resposta in ("\n", "sim\n", "CONSINTO v2\n", "consinto v3\n", "CONSINTO\n", ""):
            r = self.rodar("consentir-v3", entrada=resposta)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("NÃO registrado", r.stdout)
            self.assertIsNone(self.arquivo_remoto("consent-v3.json"), resposta)

    def test_consentir_v3_bloqueia_repositorio_publico_inexistente_ou_erro(self):
        self.repo_existe(False)
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("NÃO é privado", r.stderr)
        self.assertIsNone(self.arquivo_remoto("consent-v3.json"))
        (self.estado / "existe").unlink()
        self.assertEqual(self.rodar("consentir-v3", entrada="CONSINTO v3\n").returncode, 1)
        (self.estado / "error500").touch()
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n")
        self.assertEqual(r.returncode, 1)
        self.assertIsNone(self.arquivo_remoto("consent-v3.json"))

    def test_consentir_v3_nao_sobrescreve_e_trata_readback_e_falha_de_gravacao(self):
        self.semear("consent-v3.json", "ORIGINAL-V3")
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n")
        self.assertEqual(r.returncode, 0)
        self.assertIn("mantido", r.stdout)
        self.assertEqual(self.guardado("consent-v3.json"), b"ORIGINAL-V3")
        (self.estado / "arquivos" / "consent-v3.json").unlink()
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n", FAKE_READBACK_BAD="consent-v3")
        self.assertEqual(r.returncode, 1)
        self.assertIn("PENDENTE (P6)", r.stderr)
        (self.estado / "arquivos" / "consent-v3.json").unlink()
        (self.estado / "put_falha").touch()
        r = self.rodar("consentir-v3", entrada="CONSINTO v3\n")
        self.assertEqual(r.returncode, 1)
        self.assertIsNone(self.arquivo_remoto("consent-v3.json"))

    # guardar-plano -------------------------------------------------------------------------------------------
    def destino(self, arquivo):
        h = hashlib.sha256(arquivo.read_bytes()).hexdigest()
        return f"planos/plano-2026-11-16-{h[:8]}.json"

    def test_guardar_plano_grava_no_privado_com_readback_e_sem_imprimir_o_conteudo(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        plano = self.plano()
        r = self.rodar("guardar-plano", str(plano))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        destino = self.destino(plano)
        self.assertEqual(self.guardado(destino), plano.read_bytes())
        self.assertIn(destino, r.stdout)
        self.assertIn("readback", r.stdout)
        self.assertIn("DESABILITADA", r.stdout)
        self.assertNotIn("teoria", r.stdout + r.stderr)
        self.assertIn("--input", self.chamadas())        # o conteúdo não passa pela linha de comando
        self.assertNotIn("content=", self.chamadas())
        self.assertNotIn("UFMS-MEU-ESTUDO/contents", self.chamadas())

    def test_guardar_plano_usa_o_mais_recente_por_padrao(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        antigo = self.plano("plano-2026-11-16-ambos.json")
        os.utime(antigo, (1, 1))
        novo = self.plano("plano-2026-11-23-ambos.json", dict(PLANO, parameters=dict(PLANO["parameters"], start_date="2026-11-23")))
        r = self.rodar("guardar-plano")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        h = hashlib.sha256(novo.read_bytes()).hexdigest()[:8]
        self.assertIsNotNone(self.arquivo_remoto(f"planos/plano-2026-11-23-{h}.json"))

    def test_guardar_plano_exige_consentimento_v3_valido_que_cubra_o_plano(self):
        plano = self.plano()
        r = self.rodar("guardar-plano", str(plano))
        self.assertEqual(r.returncode, 1)
        self.assertIn("Falta o consentimento v3", r.stderr)
        for ruim in (consentimento_v3(inclui=["resultados_estudo"]), consentimento_v3(revoked_at="2026-11-16T00:00:00+00:00"),
                     consentimento_v3(version="v2"), consentimento_v3(scope="outro"),
                     consentimento_v3(granted_at="2999-01-01T00:00:00+00:00"), consentimento_v3(granted_at="2026-11-15T12:00:00")):
            self.semear("consent-v3.json", json.dumps(ruim))
            r = self.rodar("guardar-plano", str(plano))
            self.assertEqual(r.returncode, 1, ruim)
            self.assertIn("BLOQUEADO (P3)", r.stderr)
            self.assertIsNone(self.arquivo_remoto(self.destino(plano)), ruim)
        self.semear("consent-v3.json", "isto nao e json")
        self.assertEqual(self.rodar("guardar-plano", str(plano)).returncode, 1)

    def test_guardar_plano_so_no_repositorio_privado(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        plano = self.plano()
        self.repo_existe(False)
        r = self.rodar("guardar-plano", str(plano))
        self.assertEqual(r.returncode, 1)
        self.assertIn("NÃO é privado", r.stderr)
        self.assertIsNone(self.arquivo_remoto(self.destino(plano)))
        (self.estado / "noauth").touch()
        self.assertEqual(self.rodar("guardar-plano", str(plano)).returncode, 1)

    def test_guardar_plano_e_idempotente_e_conteudo_novo_vira_arquivo_novo(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        plano = self.plano()
        self.assertEqual(self.rodar("guardar-plano", str(plano)).returncode, 0)
        r = self.rodar("guardar-plano", str(plano))
        self.assertEqual(r.returncode, 0)
        self.assertIn("já está guardado", r.stdout)
        self.assertEqual(self.chamadas().count("-X PUT"), 1)
        plano.write_text(json.dumps(dict(PLANO, days=PLANO["days"] + [{"date": "2026-11-17", "weekday": 1, "kind": "teoria",
                                                                       "items": []}])), encoding="utf-8")
        self.assertEqual(self.rodar("guardar-plano", str(plano)).returncode, 0)
        self.assertEqual(self.chamadas().count("-X PUT"), 2)

    def test_guardar_plano_recusa_arquivo_que_nao_e_plano_antes_de_qualquer_rede(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        casos = {"vazio.json": "", "texto.json": "isto nao e json", "lista.json": "[]",
                 "sem_dias.json": json.dumps({"parameters": {"start_date": "2026-11-16"}}),
                 "sem_data.json": json.dumps({"parameters": {}, "days": []}),
                 "email.json": json.dumps(dict(PLANO, nota="fale com fulano@example.com")),
                 "gigante.json": json.dumps(dict(PLANO, lixo="x" * 950000))}
        for nome, texto in casos.items():
            p = self.planos / nome
            p.write_text(texto, encoding="utf-8")
            r = self.rodar("guardar-plano", str(p))
            self.assertEqual(r.returncode, 1, nome)
        self.assertNotIn("-X PUT", self.chamadas())
        self.assertEqual(self.chamadas(), "")             # nem chegou a falar com o GitHub
        r = self.rodar("guardar-plano", str(self.planos / "nao_existe.json"))
        self.assertEqual(r.returncode, 1)

    def test_guardar_plano_sem_plano_local_e_readback_divergente(self):
        self.semear("consent-v3.json", json.dumps(consentimento_v3()))
        r = self.rodar("guardar-plano")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Gere antes", r.stderr)
        r = self.rodar("guardar-plano", str(self.plano()), FAKE_READBACK_BAD="planos/")
        self.assertEqual(r.returncode, 1)
        self.assertIn("PENDENTE (P6)", r.stderr)

    def test_documentos_e_texto_do_v3(self):
        adr = ADR.read_text(encoding="utf-8")
        secao = adr.split("## Consentimento v3", 1)[1].split("\n## ", 1)[0]
        citacoes = [l for l in secao.splitlines() if l.startswith("> ")]
        self.assertEqual(len(citacoes), 1)
        self.assertTrue(citacoes[0].endswith("Versão: v3."))
        self.assertIn("PROPOSTO", adr)
        self.assertIn("consent-v3.json", adr)
        for caminho in ("memory/HANDOFF.md", "docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md"):
            texto = (ROOT / caminho).read_text(encoding="utf-8")
            self.assertIn("guardar-plano", texto, caminho)
        self.assertIn("D-24", (ROOT / "PRODUCT.md").read_text(encoding="utf-8"))
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')


if __name__ == "__main__":
    unittest.main()
