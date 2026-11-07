"""Contraprovas do gate de estrutura do PRODUCT.md e da leitura obrigatória no START de engenharia."""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_gates import ENGINEERING_FILES, check_engineering_bootstrap  # noqa: E402
from bootstrap import run  # noqa: E402
from product_gate import FILE_REF, HEADINGS, validate  # noqa: E402

TEXT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")


class ProductGateTests(unittest.TestCase):
    def make_root(self, text=TEXT):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "PRODUCT.md").write_text(text, encoding="utf-8")
        for ref in set(FILE_REF.findall(TEXT)):
            target = root / ref
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("x", encoding="utf-8")
        return temp, root

    def rejects(self, text, pattern):
        temp, root = self.make_root(text)
        with temp, self.assertRaisesRegex(ValueError, pattern):
            validate(root)

    def test_documento_vigente_e_valido(self):
        info = validate(ROOT)
        self.assertEqual(info["flow_steps"], 9)
        self.assertGreaterEqual(info["requirements"], 9)
        self.assertEqual(len(info["sha256"]), 64)

    def test_arquivo_ausente_vazio_symlink_ou_grande(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "ausente"):
                validate(Path(tmp))
        self.rejects("   \n", "vazio")
        self.rejects(TEXT + "\n" + "x" * (41 * 1024), "tamanho")
        temp, root = self.make_root()
        with temp:
            (root / "PRODUCT.md").unlink()
            (root / "real.md").write_text(TEXT, encoding="utf-8")
            (root / "PRODUCT.md").symlink_to(root / "real.md")
            with self.assertRaisesRegex(ValueError, "redirecionado"):
                validate(root)

    def test_nao_utf8(self):
        temp, root = self.make_root()
        with temp:
            (root / "PRODUCT.md").write_bytes(b"\xff\xfe# PRODUCT")
            with self.assertRaisesRegex(ValueError, "UTF-8"):
                validate(root)

    def test_titulo_cabecalho_e_precedencia(self):
        self.rejects(TEXT.replace("# PRODUCT — UFMS MEU ESTUDO", "# OUTRO", 1), "Título")
        self.rejects(re.sub(r"^Versão:.*$", "Versão: ?", TEXT, flags=re.M), "versão")
        self.rejects(TEXT.replace("`AGENTS.md` (segurança e contrato do agente) > `PRODUCT.md`", "`PRODUCT.md` > `AGENTS.md`", 1),
                     "precedência")

    def test_secoes_ausentes_extras_ou_fora_de_ordem(self):
        self.rejects(TEXT.replace(HEADINGS[9] + "\n", "", 1), "Seções")
        self.rejects(TEXT + "\n## 13. Status atual\n", "Seções")
        a, b = HEADINGS[8], HEADINGS[9]
        self.rejects(TEXT.replace(a, "@@", 1).replace(b, a, 1).replace("@@", b, 1), "Seções")

    def test_nao_vira_segunda_fonte_de_estado(self):
        casos = {
            "SHA": "\nCommit " + "a" * 40 + "\n",
            "próxima tarefa": "\n**Próxima tarefa: RM-09**\n",
            "checkpoint": "\n<!-- GOVERNANCE-CHECKPOINT:START -->\n",
            "frente ativa": "\n- Frente ativa: RM-08\n",
            "número de PR": "\nVer PR #12.\n",
        }
        for nome, extra in casos.items():
            with self.subTest(nome):
                self.rejects(TEXT + extra, "não pode conter")

    def test_fluxo_decisoes_requisitos_e_pontos_em_aberto(self):
        self.rejects(TEXT.replace("- **F5 Validar:**", "- **F6 Validar:**", 1), "Fluxo")
        self.rejects(TEXT.replace("- **D-02 (07/11/2026):**", "- **D-01 (07/11/2026):**", 1), "duplicadas")
        self.rejects(TEXT.replace("- **PR-002 ", "- **PR-001 ", 1), "duplicados")
        self.rejects(TEXT.replace("Aceite: testes com fixtures", "Teste: fixtures", 1), "Aceite")
        self.rejects(TEXT.replace("Elo: RM-09.", "", 1), "Elo")
        self.rejects(TEXT.replace("- **OPEN-02:**", "- **OPEN-01:**", 1), "OPEN")

    def test_referencias_cruzadas_devem_existir(self):
        self.rejects(TEXT.replace("**B7:** PR-007 e PR-008.", "**B7:** PR-099.", 1), "inexistente")
        self.rejects(TEXT.replace("OPEN-01 e OPEN-02", "OPEN-01 e OPEN-77", 1), "OPEN")
        self.rejects(TEXT.replace("(ver D-02)", "(ver D-77)", 1), "decisão")

    def test_nao_afirma_mecanismo_nao_observado(self):
        # A Zapia informou (07/11/2026) que GitHub é API REST e Gemini é interface web, sem MCP.
        self.assertNotIn("por MCP", TEXT)
        self.assertNotIn("pelo conector dela", TEXT)
        self.assertIn("não há MCP de GitHub nem de Notebook", TEXT)
        for ref in ("E-01", "E-03", "E-04", "E-06"):
            self.assertIn(ref, TEXT)

    def test_pr003_permanece_bloqueado_ate_credencial_de_escopo_unico(self):
        self.assertIn("PR-010", TEXT)
        self.assertIn("o PR-003 está bloqueado", TEXT)

    def test_arquivo_citado_inexistente(self):
        temp, root = self.make_root()
        with temp:
            (root / "docs/OPERACAO.md").unlink()
            with self.assertRaisesRegex(ValueError, "não existe"):
                validate(root)


class StartDeEngenhariaTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for rel in ENGINEERING_FILES + ("settings.json", "config/concursos.json", "hooks/before_write.py",
                                         "hooks/after_write.py", "hooks/checkpoint.py"):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        for ref in set(FILE_REF.findall(TEXT)):
            target = root / ref
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("x", encoding="utf-8")
        return temp, root

    def test_engenharia_inclui_product_em_terceiro_com_hash(self):
        receipt = run(ROOT, mode="engineering")
        self.assertEqual(receipt["obrigatorios"], list(ENGINEERING_FILES))
        self.assertEqual(receipt["obrigatorios"][2], "PRODUCT.md")
        self.assertEqual(len(receipt["sha256_dos_arquivos"]["PRODUCT.md"]), 64)

    def test_estudo_nao_inclui_product(self):
        self.assertNotIn("PRODUCT.md", run(ROOT, mode="study")["obrigatorios"])

    def test_product_invalido_bloqueia_engenharia_mas_nao_estudo(self):
        temp, root = self.fixture()
        with temp:
            (root / "PRODUCT.md").write_text(TEXT.replace(HEADINGS[9] + "\n", "", 1), encoding="utf-8")
            with self.assertRaises(ValueError):
                run(root, mode="engineering")
            self.assertEqual(run(root, mode="study")["modo"], "study")

    def test_product_ausente_bloqueia_engenharia(self):
        temp, root = self.fixture()
        with temp:
            (root / "PRODUCT.md").unlink()
            with self.assertRaises((ValueError, OSError)):
                run(root, mode="engineering")

    def test_contrato_de_ordem_em_settings_nao_pode_ser_alterado(self):
        temp, root = self.fixture()
        with temp:
            p = root / "settings.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["bootstrap"]["engineering_mandatory"].remove("PRODUCT.md")
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergentes"):
                check_engineering_bootstrap(root)
            data["bootstrap"]["engineering_mandatory"] = list(ENGINEERING_FILES)
            data["bootstrap"]["engineering_mandatory"][2], data["bootstrap"]["engineering_mandatory"][3] = \
                data["bootstrap"]["engineering_mandatory"][3], data["bootstrap"]["engineering_mandatory"][2]
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergentes"):
                check_engineering_bootstrap(root)

    def test_roadmap_continua_em_segundo_lugar(self):
        self.assertEqual(ENGINEERING_FILES[:2], ("AGENTS.md", "ROADMAP.md"))


if __name__ == "__main__":
    unittest.main()
