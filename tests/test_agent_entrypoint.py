"""Contraprovas de START dos agentes com escopo somente leitura."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_entrypoint import ReadOnlyAgentBroker, StartBlocked, verify_start

HEAD = "d" * 40
COPIES = (
    "AGENTS.md", "ROADMAP.md", "PRODUCT.md", "memory/HANDOFF.md", "state/CURRENT.json",
    "state/WORKFLOW.json", "settings.json", "config/concursos.json",
    "hooks/before_write.py", "hooks/after_write.py", "hooks/checkpoint.py",
    "docs/governanca/CAPACIDADES_ZAPIA_VERIFICADAS.md",
)


class AgentEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.head_patch = patch("agent_entrypoint._git_head", return_value=HEAD)
        self.clean_patch = patch("agent_entrypoint._git_clean", return_value=None)
        self.head_mock = self.head_patch.start()
        self.clean_mock = self.clean_patch.start()
        self.addCleanup(self.head_patch.stop)
        self.addCleanup(self.clean_patch.stop)

    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name in COPIES:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        return temp, root

    def test_study_roles_require_four_documents(self):
        for role in ("tutor", "coach"):
            with self.subTest(role=role):
                broker = ReadOnlyAgentBroker(ROOT, HEAD, role)
                receipt = broker.request("start")
                self.assertEqual(len(receipt["mandatory"]), 4)
                self.assertEqual(receipt["role"], role)
                self.assertFalse(receipt["external_effects_enabled"])
                self.assertNotIn("state/WORKFLOW.json", receipt["mandatory"])

    def test_engineering_roles_require_workflow(self):
        for role in ("engineer", "auditor"):
            with self.subTest(role=role):
                broker = ReadOnlyAgentBroker(ROOT, HEAD, role)
                receipt = broker.request("start")
                self.assertEqual(len(receipt["mandatory"]), 6)
                self.assertEqual(receipt["mandatory"][2], "PRODUCT.md")
                current = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
                self.assertEqual(receipt["task"], current["active"]["task_id"])
                self.assertEqual(receipt["pr"], current["active"]["pr_number"])
                self.assertIn("state/WORKFLOW.json", receipt["mandatory"])

    def test_fresh_text_is_supplied_with_sha(self):
        broker = ReadOnlyAgentBroker(ROOT, HEAD, "engineer")
        prompt = broker.model_context()
        self.assertEqual(set(prompt["documents"]), set(broker.request("start")["mandatory"]))
        self.assertIn("uma tarefa", prompt["documents"]["AGENTS.md"])
        self.assertIn(json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))["active"]["task_id"], prompt["documents"]["state/WORKFLOW.json"])
        import hashlib
        for name, content in prompt["documents"].items():
            self.assertEqual(hashlib.sha256(content.encode("utf-8")).hexdigest(), prompt["sha256"][name])

    def test_unknown_role_fails(self):
        for role in ("copilot-write", "", None, "admin"):
            with self.subTest(role=role), self.assertRaisesRegex(StartBlocked, "Papel"):
                ReadOnlyAgentBroker(ROOT, HEAD, role)

    def test_rejects_untrusted_or_stale_head(self):
        with self.assertRaisesRegex(StartBlocked, "SHA"):
            verify_start(ROOT, "", "engineering")
        self.head_mock.return_value = "f" * 40
        with self.assertRaisesRegex(StartBlocked, "HEAD"):
            ReadOnlyAgentBroker(ROOT, HEAD, "tutor")

    def test_rejects_dirty_checkout(self):
        self.clean_mock.side_effect = StartBlocked("Checkout alterado")
        with self.assertRaisesRegex(StartBlocked, "alterado"):
            ReadOnlyAgentBroker(ROOT, HEAD, "engineer")

    def test_missing_workflow_denies_engineering_but_not_study(self):
        tmp, root = self.fixture()
        with tmp:
            (root / "state/WORKFLOW.json").unlink()
            with self.assertRaisesRegex(StartBlocked, "START local"):
                ReadOnlyAgentBroker(root, HEAD, "engineer")
            self.assertEqual(ReadOnlyAgentBroker(root, HEAD, "coach").request("start")["mode"], "study")

    def test_corrupt_workflow_and_missing_roadmap_fail(self):
        for name, content in (("state/WORKFLOW.json", "{}"), ("ROADMAP.md", "")):
            with self.subTest(name=name):
                tmp, root = self.fixture()
                with tmp:
                    (root / name).write_text(content, encoding="utf-8")
                    with self.assertRaises(StartBlocked):
                        ReadOnlyAgentBroker(root, HEAD, "engineer")

    def test_stale_receipt_is_not_reusable_even_if_git_is_mocked(self):
        tmp, root = self.fixture()
        with tmp:
            broker = ReadOnlyAgentBroker(root, HEAD, "coach")
            (root / "memory/HANDOFF.md").write_text(
                (root / "memory/HANDOFF.md").read_text(encoding="utf-8") + "\nTAMPERED",
                encoding="utf-8")
            with self.assertRaisesRegex(StartBlocked, "mudaram após START"):
                broker.request("inspect")
            with self.assertRaisesRegex(StartBlocked, "mudaram após START"):
                broker.model_context()

    def test_write_actions_are_never_authorized(self):
        broker = ReadOnlyAgentBroker(ROOT, HEAD, "coach")
        for action in ("github.write", "merge", "calendar.create", "zapia.send",
                       "private.store", "execute", "delete", "admin"):
            with self.subTest(action=action), self.assertRaisesRegex(
                    StartBlocked, "Operações externas"):
                broker.request(action)
        self.assertEqual(broker.request("inspect")["status"], "start_verified")

    def test_model_context_rejects_redirected_symlink(self):
        tmp, root = self.fixture()
        with tmp:
            broker = ReadOnlyAgentBroker(root, HEAD, "tutor")
            path = root / "AGENTS.md"
            path.unlink()
            path.symlink_to(root / "ROADMAP.md")
            with self.assertRaises(StartBlocked):
                broker.model_context()

    def test_rejects_invalid_mode(self):
        with self.assertRaisesRegex(StartBlocked, "Modo"):
            verify_start(ROOT, HEAD, "admin")


class CanalNoStartTests(AgentEntrypointTests):
    """E55: resumo do canal de engenharia no recibo do START (opcional, só leitura); herda só a montagem do HEAD simulado."""

    def run(self, result=None):
        if self._testMethodName.startswith("test_canal_"):
            return super().run(result)
        return unittest.TestResult() if result is None else result

    def entrada(self, **extra):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name) / "comandos" / "engenharia"
        for sub in ("pedidos", "respostas", "registro"):
            (base / sub).mkdir(parents=True)
        for i in ("eng-0001", "eng-0002", "eng-0003"):
            (base / "pedidos" / f"{i}.json").write_text("{}", encoding="utf-8")
        (base / "respostas" / "eng-0001.json").write_text(json.dumps({"itens": [{"rotulo": "x", "valor": "SEGREDO-NA-RESPOSTA-12345"}]}), encoding="utf-8")
        (base / "respostas" / "eng-0002.json").write_text("{}", encoding="utf-8")
        (base / "registro" / "eng-0001.json").write_text(json.dumps({"veredito": "ACEITA", "estado_da_resposta": "RESPONDIDO"}), encoding="utf-8")
        (base / "registro" / "eng-0002.json").write_text(json.dumps({"veredito": "RECUSADA", "codigo": "FORMATO"}), encoding="utf-8")
        for k, v in extra.items():
            (base / k).write_text(v, encoding="utf-8")
        return Path(temp.name)

    def test_canal_sem_clone_o_recibo_nao_muda(self):
        antes = ReadOnlyAgentBroker(ROOT, HEAD, "engineer").request("start")
        self.assertNotIn("canal", antes)

    def test_canal_resumo_traz_so_ids_e_codigos(self):
        e = self.entrada()
        r = ReadOnlyAgentBroker(ROOT, HEAD, "engineer", entrada=e).request("start")
        c = r["canal"]
        self.assertTrue(c["disponivel"])
        self.assertEqual((c["aceitas"], c["recusadas"], c["aguardando_resposta"]), (["eng-0001"], {"eng-0002": "FORMATO"}, ["eng-0003"]))
        self.assertNotIn("SEGREDO-NA-RESPOSTA", json.dumps(r))  # o conteúdo das respostas nunca entra no START
        self.assertIn("nunca o texto das respostas", c["limite"])
        self.assertFalse(r["external_effects_enabled"])

    def test_canal_nao_altera_hashes_nem_a_lista_obrigatoria(self):
        e = self.entrada()
        base = ReadOnlyAgentBroker(ROOT, HEAD, "tutor").request("start")
        com = ReadOnlyAgentBroker(ROOT, HEAD, "tutor", entrada=e).request("start")
        self.assertEqual((base["mandatory"], base["sha256"]), (com["mandatory"], com["sha256"]))

    def test_canal_ausente_ou_corrompido_nao_derruba_o_start(self):
        r = ReadOnlyAgentBroker(ROOT, HEAD, "engineer", entrada="/nao/existe").request("start")
        self.assertEqual(r["status"], "start_verified")
        self.assertFalse(r["canal"]["disponivel"])
        e = self.entrada()
        (e / "comandos/engenharia/registro/eng-0001.json").write_text("{nao e json", encoding="utf-8")
        r = ReadOnlyAgentBroker(ROOT, HEAD, "engineer", entrada=e).request("start")
        self.assertEqual(r["status"], "start_verified")
        self.assertFalse(r["canal"]["disponivel"])

    def test_canal_parada_ativa_aparece_e_nenhuma_escrita_e_liberada(self):
        e = self.entrada(PARAR="x")
        b = ReadOnlyAgentBroker(ROOT, HEAD, "engineer", entrada=e)
        self.assertTrue(b.request("start")["canal"]["parada_ativa"])
        with self.assertRaises(StartBlocked):
            b.request("write")
        antes = sorted(p.name for p in (e / "comandos/engenharia/registro").iterdir())
        b.request("inspect")
        self.assertEqual(antes, sorted(p.name for p in (e / "comandos/engenharia/registro").iterdir()))  # só leitura

    def test_canal_lista_e_limitada(self):
        e = self.entrada()
        for n in range(150):
            (e / "comandos/engenharia/pedidos" / f"eng-{n + 10:04d}.json").write_text("{}", encoding="utf-8")
        c = ReadOnlyAgentBroker(ROOT, HEAD, "engineer", entrada=e).request("start")["canal"]
        self.assertLessEqual(len(c["aguardando_resposta"]), 100)


if __name__ == "__main__":
    unittest.main()
