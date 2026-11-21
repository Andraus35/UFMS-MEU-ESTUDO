"""RG: o recibo de START (RS) ligado ao verificador de entrega (GE), S14-R3. Repositório Git sintético; uma contraprova por recusa."""
import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import delivery_receipt_binding as b  # noqa: E402
import start_receipt as r  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name) / "contrato"
        cls.repo.mkdir()
        git(cls.repo, "init", "-q")
        for nome in r.ARQUIVOS["engineering"]:
            (cls.repo / nome).parent.mkdir(parents=True, exist_ok=True)
            (cls.repo / nome).write_text("conteudo de " + nome + "\n", encoding="utf-8")
        git(cls.repo, "add", "-A")
        git(cls.repo, "commit", "-q", "-m", "um")
        cls.sha = git(cls.repo, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def envelope(self, tipo="ORIENTACAO", papel="tutor", recibo=None, **mud):
        env = {"tipo": tipo, "papel": papel, "sha_contrato": self.sha,
               "recibo": recibo if recibo is not None else r.emitir(self.repo, self.sha, "tutor" if papel == "zapia" else papel),
               "corpo": "Vamos revisar o assunto de hoje com calma.", "alegacoes": []}
        env.update(mud)
        return env

    def cli(self, env, *args):
        arq = Path(self.tmp.name) / "envelope.json"
        arq.write_text(json.dumps(env), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "delivery_gate.py"), "--envelope", str(arq), "--sha-contrato", self.sha,
                               "--modo", "bloqueio", *args], capture_output=True, text=True, timeout=60)
        return proc.returncode, json.loads(proc.stdout)


class RecibosEsperado(Base):
    def test_tutor_e_coach_recebem_o_recibo_de_estudo_do_rs(self):
        for papel in ("tutor", "coach"):
            self.assertEqual(b.recibo_esperado(self.repo, self.sha, papel), r.emitir(self.repo, self.sha, papel))
            self.assertEqual(len(b.recibo_esperado(self.repo, self.sha, papel)["hashes"]), 4)

    def test_so_tutor_e_coach_tem_start_definido(self):
        self.assertEqual(b.PAPEIS_COM_START, ("tutor", "coach"))

    def test_papel_sem_start_definido_ou_invalido_devolve_none(self):
        for papel in ("zapia", "engineer", "auditor", "admin", "", None, 7):
            self.assertIsNone(b.recibo_esperado(self.repo, self.sha, papel), repr(papel))

    def test_sha_ruim_ou_inexistente_ou_checkout_ruim_devolve_none(self):
        for sha in ("", "abc", None, "0" * 40, "g" * 40):
            self.assertIsNone(b.recibo_esperado(self.repo, sha, "tutor"), repr(sha))
        self.assertIsNone(b.recibo_esperado(Path(self.tmp.name) / "nao_existe", self.sha, "tutor"))

    def test_arquivo_do_start_ausente_na_revisao_devolve_none(self):
        git(self.repo, "rm", "-q", "state/CURRENT.json")
        git(self.repo, "commit", "-q", "-m", "sem current")
        sem = git(self.repo, "rev-parse", "HEAD")
        try:
            self.assertIsNone(b.recibo_esperado(self.repo, sem, "tutor"))
        finally:
            git(self.repo, "reset", "-q", "--hard", self.sha)


class LigacaoNoVerificadorDeEntrega(Base):
    def test_recibo_correto_e_aceito(self):
        codigo, res = self.cli(self.envelope(), "--root-contrato", str(self.repo))
        self.assertEqual((codigo, res["decisao"], res["motivos"], res["avisos"]), (0, "ACEITA", [], []))

    def test_hash_adulterado_e_recusado(self):
        rec = r.emitir(self.repo, self.sha, "tutor")
        rec["hashes"]["AGENTS.md"] = "0" * 64
        codigo, res = self.cli(self.envelope(recibo=rec), "--root-contrato", str(self.repo))
        self.assertEqual((codigo, res["decisao"], res["motivos"]), (1, "RECUSADA", ["recibo_diferente_do_esperado"]))

    def test_recibo_de_engenharia_nao_vale_para_entrega_de_estudo(self):
        codigo, res = self.cli(self.envelope(recibo=r.emitir(self.repo, self.sha, "engineer")), "--root-contrato", str(self.repo))
        self.assertEqual((codigo, res["motivos"]), (1, ["recibo_diferente_do_esperado"]))

    def test_sha_antigo_no_recibo_e_recusado(self):
        rec = r.emitir(self.repo, self.sha, "tutor")
        rec["sha"] = "1" * 40
        codigo, res = self.cli(self.envelope(recibo=rec), "--root-contrato", str(self.repo))
        self.assertEqual((codigo, res["motivos"]), (1, ["recibo_diferente_do_esperado"]))

    def test_sem_a_ligacao_o_recibo_fica_nao_conferido(self):
        codigo, res = self.cli(self.envelope())
        self.assertEqual((codigo, res["decisao"], res["avisos"]), (3, "AVISO", ["recibo_nao_conferido_contra_o_repositorio"]))

    def test_efeito_externo_sem_a_ligacao_e_recusado(self):
        env = self.envelope("COMANDO", "coach", corpo="", estruturado={"operacao": "enviar_mensagem", "params": {"texto": "Revisão pendente."}})
        codigo, res = self.cli(env)
        self.assertEqual((codigo, res["motivos"]), (1, ["recibo_nao_conferido_contra_o_repositorio"]))
        codigo, res = self.cli(env, "--root-contrato", str(self.repo))
        self.assertEqual((codigo, res["decisao"]), (0, "ACEITA"))

    def test_papel_sem_start_fica_nao_conferido_mesmo_com_a_ligacao(self):
        env = self.envelope("LEMBRETE", "zapia", corpo="Falta o caderno.", estruturado={"atividade_id": "UFMS-002"})
        _, res = self.cli(env, "--root-contrato", str(self.repo))
        self.assertIn("recibo_nao_conferido_contra_o_repositorio", res["motivos"])

    def test_checkout_inexistente_nao_aceita_efeito(self):
        env = self.envelope("COMANDO", "coach", corpo="", estruturado={"operacao": "enviar_mensagem", "params": {"texto": "Revisão pendente."}})
        codigo, res = self.cli(env, "--root-contrato", str(Path(self.tmp.name) / "nao_existe"))
        self.assertEqual((codigo, res["motivos"]), (1, ["recibo_nao_conferido_contra_o_repositorio"]))

    def test_envelope_sem_papel_nao_derruba_a_linha_de_comando(self):
        env = self.envelope()
        env.pop("papel")
        codigo, res = self.cli(env, "--root-contrato", str(self.repo))
        self.assertEqual(codigo, 1)
        self.assertIn("campos_do_envelope_fora_da_lista_fechada", res["motivos"])


class RepositorioReal(unittest.TestCase):
    def test_recibo_do_head_real_e_aceito_na_linha_de_comando(self):
        sha = git(ROOT, "rev-parse", "HEAD")
        env = {"tipo": "ORIENTACAO", "papel": "tutor", "sha_contrato": sha, "recibo": r.emitir(ROOT, sha, "tutor"),
               "corpo": "Vamos revisar o assunto de hoje com calma.", "alegacoes": []}
        with tempfile.TemporaryDirectory() as pasta:
            arq = Path(pasta) / "e.json"
            arq.write_text(json.dumps(env), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "delivery_gate.py"), "--envelope", str(arq), "--sha-contrato", sha,
                                   "--modo", "bloqueio", "--root-contrato", str(ROOT)], capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["decisao"], "ACEITA")


class SemRedeNemEscrita(unittest.TestCase):
    def test_modulo(self):
        arvore = ast.parse((ROOT / "scripts" / "delivery_receipt_binding.py").read_text(encoding="utf-8"))
        importados = {n.names[0].name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import)}
        importados |= {n.module.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(importados, {"start_receipt"})
        chamadas = {n.func.attr for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse(chamadas & {"write_text", "write_bytes", "unlink", "mkdir", "rename", "replace"}, chamadas)


if __name__ == "__main__":
    unittest.main()
