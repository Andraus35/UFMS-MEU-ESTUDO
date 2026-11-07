"""Contraprovas do gate dos perfis Tutor e Coach e da separação de responsabilidades."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_gates import check_engineering_bootstrap  # noqa: E402
from agents_gate import COACH_ONLY, FILE_REF, HEADINGS, SHARED, TUTOR_ONLY, validate  # noqa: E402
from bootstrap import run  # noqa: E402

FILES = ("agents/README.md", "agents/TUTOR.md", "agents/COACH.md")
TUTOR = (ROOT / "agents/TUTOR.md").read_text(encoding="utf-8")
COACH = (ROOT / "agents/COACH.md").read_text(encoding="utf-8")


class AgentsGateTests(unittest.TestCase):
    def make_root(self, tutor=TUTOR, coach=COACH, readme=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "agents").mkdir()
        (root / "agents/TUTOR.md").write_text(tutor, encoding="utf-8")
        (root / "agents/COACH.md").write_text(coach, encoding="utf-8")
        (root / "agents/README.md").write_text(readme or (ROOT / "agents/README.md").read_text(encoding="utf-8"),
                                               encoding="utf-8")
        for text in (tutor, coach):
            for ref in set(FILE_REF.findall(text)):
                target = root / ref
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_text("x", encoding="utf-8")
        return temp, root

    def rejects(self, pattern, **kwargs):
        temp, root = self.make_root(**kwargs)
        with temp, self.assertRaisesRegex(ValueError, pattern):
            validate(root)

    def test_perfis_vigentes_sao_validos(self):
        info = validate(ROOT)
        self.assertEqual([r["file"] for r in info["specs"]], ["agents/TUTOR.md", "agents/COACH.md"])

    def test_conjuntos_de_operacoes_sao_disjuntos(self):
        self.assertFalse(TUTOR_ONLY & COACH_ONLY)
        self.assertFalse((TUTOR_ONLY | COACH_ONLY) & SHARED)
        self.assertIn("enviar_prompt_notebook", TUTOR_ONLY)     # só o Tutor produz e envia conteúdo ao notebook
        self.assertIn("criar_lembrete", COACH_ONLY)             # só o Coach cria lembretes

    def test_coach_nao_pode_receber_operacao_exclusiva_do_tutor(self):
        for op in sorted(TUTOR_ONLY):
            with self.subTest(op=op):
                self.rejects("operações diferentes", coach=COACH.replace("- `registrar_acompanhamento`\n",
                                                                         "- `registrar_acompanhamento`\n- `%s`\n" % op))

    def test_tutor_nao_pode_receber_operacao_exclusiva_do_coach(self):
        for op in sorted(COACH_ONLY):
            with self.subTest(op=op):
                self.rejects("operações diferentes", tutor=TUTOR.replace("- `enviar_prompt_notebook`\n",
                                                                         "- `enviar_prompt_notebook`\n- `%s`\n" % op))

    def test_operacao_removida_ou_inventada_ou_duplicada(self):
        self.rejects("operações diferentes", tutor=TUTOR.replace("- `registrar_plano`\n", ""))
        self.rejects("operações diferentes", tutor=TUTOR.replace("- `registrar_plano`\n", "- `apagar_repositorio`\n"))
        self.rejects("duplicada", coach=COACH.replace("- `criar_lembrete`\n", "- `criar_lembrete`\n- `criar_lembrete`\n"))

    def test_estrutura(self):
        self.rejects("Título inválido", tutor=TUTOR.replace("# Tutor (Aragonê)", "# Tutor", 1))
        self.rejects("Seções", tutor=TUTOR.replace(HEADINGS[3] + "\n", "", 1))
        self.rejects("Seções", coach=COACH + "\n## Status atual\n")
        a, b = HEADINGS[1], HEADINGS[2]
        self.rejects("Seções", coach=COACH.replace(a, "@@", 1).replace(b, a, 1).replace("@@", b, 1))

    def test_secao_vazia(self):
        corpo = TUTOR.split(HEADINGS[7])[1]
        self.rejects("Seção vazia", tutor=TUTOR.replace(corpo, "\n\n"))

    def test_clausulas_obrigatorias(self):
        self.rejects("cláusula", tutor=TUTOR.replace("único produtor de conteúdo", "um dos produtores"))
        self.rejects("cláusula", coach=COACH.replace("Não produz conteúdo de revisão", "Produz conteúdo"))
        self.rejects("cláusula", tutor=TUTOR.replace("Não recebe credenciais", "Recebe tokens"))

    def test_sem_estado_nem_segredo(self):
        casos = {"SHA": "\n" + "a" * 40 + "\n", "PR": "\nVer PR #12.\n", "estado": "\n- Frente ativa: RM-08\n",
                 "segredo": "\nghp_" + "A" * 30 + "\n"}
        for nome, extra in casos.items():
            with self.subTest(nome):
                self.rejects("não pode conter", tutor=TUTOR + extra)

    def test_referencia_a_arquivo_inexistente(self):
        temp, root = self.make_root()
        with temp:
            (root / "scripts").mkdir(exist_ok=True)
            texto = (root / "agents/TUTOR.md").read_text(encoding="utf-8") + "\nVer `docs/nao_existe.md`.\n"
            (root / "agents/TUTOR.md").write_text(texto, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inexistente"):
                validate(root)

    def test_readme_obrigatorio_e_referencias(self):
        temp, root = self.make_root()
        with temp:
            (root / "agents/README.md").unlink()
            with self.assertRaises(ValueError):
                validate(root)
        self.rejects("sem referência", readme="# vazio\n")

    def test_arquivo_ausente_grande_vazio_e_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                validate(Path(tmp))
        self.rejects("vazio ou grande", tutor="   \n")
        self.rejects("vazio ou grande", tutor=TUTOR + "x" * (25 * 1024))
        temp, root = self.make_root()
        with temp:
            alvo = root / "real.md"
            alvo.write_text(TUTOR, encoding="utf-8")
            (root / "agents/TUTOR.md").unlink()
            (root / "agents/TUTOR.md").symlink_to(alvo)
            with self.assertRaisesRegex(ValueError, "redirecionado"):
                validate(root)

    def test_start_de_engenharia_executa_o_gate_mas_estudo_nao(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name) / "repo"
        with temp:
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
            self.assertEqual(run(root, mode="engineering")["modo"], "engineering")
            (root / "agents/COACH.md").write_text(COACH.replace("- `criar_lembrete`\n", ""), encoding="utf-8")
            with self.assertRaises(ValueError):
                check_engineering_bootstrap(root)
            with self.assertRaises(ValueError):
                run(root, mode="engineering")
            self.assertEqual(run(root, mode="study")["modo"], "study")


if __name__ == "__main__":
    unittest.main()
