"""RS: recibo de START verificável (S14-R2, R3). Repositório Git sintético; uma contraprova por recusa."""
import ast
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import start_receipt as r  # noqa: E402
import delivery_gate  # noqa: E402
from bootstrap import run as bootstrap_run  # noqa: E402


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        git(cls.repo, "init", "-q")
        for modo in r.ARQUIVOS.values():
            for nome in modo:
                (cls.repo / nome).parent.mkdir(parents=True, exist_ok=True)
                (cls.repo / nome).write_text("conteudo de " + nome + "\n", encoding="utf-8")
        git(cls.repo, "add", "-A")
        git(cls.repo, "commit", "-q", "-m", "um")
        cls.sha = git(cls.repo, "rev-parse", "HEAD")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def recibo(self, papel="engineer"):
        return r.emitir(self.repo, self.sha, papel)

    def motivos(self, recibo, sha=..., papel=None):
        return r.verificar(recibo, self.repo, self.sha if sha is ... else sha, papel)["motivos"]


class Emissao(Base):
    def test_estudo_tem_quatro_e_engenharia_seis_arquivos(self):
        self.assertEqual(len(self.recibo("tutor")["hashes"]), 4)
        self.assertEqual(len(self.recibo("coach")["hashes"]), 4)
        self.assertEqual(len(self.recibo("engineer")["hashes"]), 6)
        self.assertEqual(len(self.recibo("auditor")["hashes"]), 6)

    def test_formato_fechado_sha_e_hashes(self):
        rec = self.recibo()
        self.assertEqual(set(rec), {"sha", "hashes"})
        self.assertEqual(rec["sha"], self.sha)

    def test_papel_invalido_recusa_a_emissao(self):
        with self.assertRaises(r.ReciboInvalido) as c:
            r.emitir(self.repo, self.sha, "zapia")
        self.assertEqual(c.exception.motivo, "papel_invalido")

    def test_sha_invalido_ou_inexistente_recusa_a_emissao(self):
        for sha in ("", "abc", None, "g" * 40, "0" * 40):
            with self.assertRaises(r.ReciboInvalido, msg=repr(sha)):
                r.emitir(self.repo, sha, "tutor")

    def test_lista_igual_a_do_bootstrap_real(self):
        for modo in ("study", "engineering"):
            self.assertEqual(list(r.ARQUIVOS[modo]), bootstrap_run(ROOT, mode=modo)["obrigatorios"], modo)

    def test_recibo_do_broker(self):
        resp = {"status": "start_verified", "head": self.sha, "sha256": self.recibo("tutor")["hashes"]}
        self.assertEqual(r.recibo_do_broker(resp), self.recibo("tutor"))
        for ruim in (None, {}, {"status": "outro", "head": self.sha, "sha256": {}}):
            with self.assertRaises(r.ReciboInvalido):
                r.recibo_do_broker(ruim)


class Verificacao(Base):
    def test_recibo_valido_com_e_sem_papel(self):
        for papel, modo in (("tutor", "study"), ("engineer", "engineering")):
            for p in (papel, None):
                res = r.verificar(self.recibo(papel), self.repo, self.sha, p)
                self.assertTrue(res["valido"], res)
                self.assertEqual(res["modo"], modo)

    def test_recibo_ausente_ou_malformado_recusa(self):
        ruins = [None, {}, [], "x", {"sha": self.sha}, {"hashes": {"AGENTS.md": "a" * 64}},
                 {"sha": self.sha, "hashes": {}}, {"sha": self.sha, "hashes": "x"},
                 {"sha": self.sha, "hashes": {"AGENTS.md": "curto"}}, {"sha": "curto", "hashes": {"AGENTS.md": "a" * 64}},
                 {**self.recibo(), "extra": 1}]
        for ruim in ruins:
            self.assertIn("recibo_ausente_ou_malformado", self.motivos(ruim), repr(ruim))

    def test_hash_adulterado_recusa(self):
        rec = self.recibo()
        rec["hashes"]["PRODUCT.md"] = "0" * 64
        self.assertEqual(self.motivos(rec), ["hash_divergente:PRODUCT.md"])

    def test_um_byte_a_mais_em_qualquer_arquivo_recusa(self):
        for nome in r.ARQUIVOS["engineering"]:
            rec = self.recibo()
            rec["hashes"][nome] = r.hashlib.sha256(b"conteudo de " + nome.encode() + b"\n!").hexdigest()
            self.assertEqual(self.motivos(rec), ["hash_divergente:" + nome])

    def test_sha_errado_recusa(self):
        self.assertEqual(self.motivos(self.recibo(), sha="1" * 40), ["sha_diferente_do_fixado"])
        rec = self.recibo()
        rec["sha"] = "1" * 40
        self.assertEqual(self.motivos(rec), ["sha_diferente_do_fixado"])

    def test_sha_fixado_ausente_ou_invalido_recusa(self):
        for sha in ("", None, "abc", "G" * 40):
            self.assertIn("sha_fixado_ausente_ou_invalido", self.motivos(self.recibo(), sha=sha), repr(sha))

    def test_sha_inexistente_no_repositorio_recusa(self):
        rec = {"sha": "0" * 40, "hashes": self.recibo()["hashes"]}
        self.assertEqual(self.motivos(rec, sha="0" * 40), ["revisao_ou_arquivo_inexistente"])

    def test_papel_invalido_recusa(self):
        for papel in ("zapia", "admin", ""):
            self.assertEqual(self.motivos(self.recibo(), papel=papel), ["papel_invalido"], papel)

    def test_recibo_de_estudo_nao_vale_para_engenharia_e_vice_versa(self):
        self.assertEqual(self.motivos(self.recibo("tutor"), papel="engineer"), ["arquivos_diferentes_dos_do_papel"])
        self.assertEqual(self.motivos(self.recibo("engineer"), papel="coach"), ["arquivos_diferentes_dos_do_papel"])

    def test_arquivo_faltando_ou_extra_ou_estranho_recusa(self):
        falta = self.recibo()
        falta["hashes"].pop("state/WORKFLOW.json")
        extra = self.recibo()
        extra["hashes"]["README.md"] = "a" * 64
        estranho = self.recibo("tutor")
        estranho["hashes"]["../fora"] = estranho["hashes"].pop("AGENTS.md")
        for rec in (falta, extra, estranho):
            self.assertIn("arquivos_diferentes_dos_do_start", self.motivos(rec))

    def test_confere_a_revisao_nao_a_arvore_de_trabalho(self):
        rec = self.recibo()
        (self.repo / "AGENTS.md").write_text("alterado sem commit\n", encoding="utf-8")
        try:
            self.assertEqual(self.motivos(rec), [], "árvore suja não muda o recibo da revisão fixada")
        finally:
            git(self.repo, "checkout", "--", "AGENTS.md")

    def test_nova_revisao_invalida_o_recibo_antigo(self):
        rec = self.recibo()
        (self.repo / "ROADMAP.md").write_text("mudou\n", encoding="utf-8")
        git(self.repo, "commit", "-q", "-am", "dois")
        novo = git(self.repo, "rev-parse", "HEAD")
        try:
            self.assertEqual(self.motivos(rec, sha=novo), ["sha_diferente_do_fixado"])
            self.assertEqual(self.motivos({"sha": novo, "hashes": rec["hashes"]}, sha=novo), ["hash_divergente:ROADMAP.md"])
            self.assertEqual(self.motivos(rec), [], "o recibo antigo segue válido para a revisão antiga")
        finally:
            git(self.repo, "reset", "-q", "--hard", self.sha)

    def test_nao_prova_compreensao_e_declara_o_limite(self):
        res = r.verificar(self.recibo(), self.repo, self.sha)
        self.assertIs(res["compreensao_comprovada"], False)
        self.assertIn("NÃO prova que o modelo leu ou compreendeu", res["limite"])
        self.assertIn("nem quem emitiu", res["limite"])
        self.assertIs(r.verificar(None, self.repo, self.sha)["compreensao_comprovada"], False)

    def test_recibo_adulterado_nao_devolve_modo_nem_valido(self):
        rec = self.recibo()
        rec["hashes"]["AGENTS.md"] = "0" * 64
        res = r.verificar(rec, self.repo, self.sha)
        self.assertFalse(res["valido"])
        self.assertIsNone(res["modo"])


class IntegracaoComOGE(Base):
    """O recibo emitido é o formato que o verificador de entrega aceita; o esperado vem do repositório (S14-R3)."""

    def test_recibo_emitido_passa_na_forma_e_na_conferencia_do_ge(self):
        rec = self.recibo("tutor")
        for esperado, tipo_com_efeito in ((rec, True), (None, False)):
            motivos, avisos = [], []
            delivery_gate._recibo(rec, {"recibo_esperado": esperado}, motivos, avisos, tipo_com_efeito)
            self.assertEqual(motivos if esperado else [], [])
        adulterado = copy.deepcopy(rec)
        adulterado["hashes"]["AGENTS.md"] = "0" * 64
        motivos = []
        delivery_gate._recibo(adulterado, {"recibo_esperado": rec}, motivos, [], True)
        self.assertEqual(motivos, ["recibo_diferente_do_esperado"])


class RepositorioReal(unittest.TestCase):
    def test_recibo_do_head_real_verifica_para_os_dois_modos(self):
        sha = git(ROOT, "rev-parse", "HEAD")
        for papel in ("tutor", "engineer"):
            rec = r.emitir(ROOT, sha, papel)
            self.assertTrue(r.verificar(rec, ROOT, sha, papel)["valido"], papel)


class LinhaDeComando(Base):
    def cli(self, *args, entrada=None):
        buf = io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(entrada or "")
        try:
            with redirect_stdout(buf):
                codigo = r.main(["--root", str(self.repo), *args])
        finally:
            sys.stdin = old
        return codigo, buf.getvalue()

    def test_emitir_e_verificar(self):
        codigo, saida = self.cli("emitir", "--sha", self.sha, "--role", "tutor")
        self.assertEqual(codigo, 0)
        codigo, saida2 = self.cli("verificar", "--sha", self.sha, "--role", "tutor", entrada=saida)
        self.assertEqual(codigo, 0)
        self.assertTrue(json.loads(saida2)["valido"])

    def test_verificar_recusa_com_codigo_1(self):
        rec = self.recibo("tutor")
        rec["hashes"]["AGENTS.md"] = "0" * 64
        codigo, saida = self.cli("verificar", "--sha", self.sha, entrada=json.dumps(rec))
        self.assertEqual(codigo, 1)
        self.assertFalse(json.loads(saida)["valido"])

    def test_recibo_ausente_ou_json_invalido_recusa(self):
        for entrada in ("", "não é json"):
            codigo, saida = self.cli("verificar", "--sha", self.sha, entrada=entrada)
            self.assertEqual(codigo, 1)
            self.assertIn("recibo_ausente_ou_malformado", json.loads(saida)["motivos"])

    def test_emitir_sem_papel_e_uso_incorreto(self):
        with self.assertRaises(SystemExit) as c:
            self.cli("emitir", "--sha", self.sha)
        self.assertEqual(c.exception.code, 2)

    def test_emitir_com_sha_ruim_recusa(self):
        codigo, _ = self.cli("emitir", "--sha", "abc", "--role", "tutor")
        self.assertEqual(codigo, 1)


class SemRedeNemEscrita(unittest.TestCase):
    def test_modulo_sem_rede_credencial_ou_escrita(self):
        arvore = ast.parse((ROOT / "scripts" / "start_receipt.py").read_text(encoding="utf-8"))
        importados = {n.names[0].name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import)}
        importados |= {n.module.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
        self.assertFalse(importados & {"socket", "urllib", "http", "requests", "ssl", "ftplib", "smtplib"}, importados)
        chamadas = {n.func.attr for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse(chamadas & {"write_text", "write_bytes", "unlink", "mkdir", "rename", "replace"}, chamadas)
        self.assertNotIn("open", {n.func.id for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)})


if __name__ == "__main__":
    unittest.main()
