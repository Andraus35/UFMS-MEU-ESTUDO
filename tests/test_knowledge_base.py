"""RAG determinístico do Tutor e do Coach: manifesto, hashes, broker e rota de estudo."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import knowledge_gate as kg  # noqa: E402
import session_route as sr  # noqa: E402
from agent_entrypoint import ReadOnlyAgentBroker, StartBlocked  # noqa: E402

HEAD = "d" * 40


class KnowledgeBaseTests(unittest.TestCase):
    def tmp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        shutil.copytree(ROOT / "docs/plataformas", root / "docs/plataformas")
        shutil.copytree(ROOT / "config", root / "config")
        shutil.copytree(ROOT / "agents", root / "agents")
        return root

    def test_repositorio_real_aprovado(self):
        self.assertEqual(kg.check(ROOT), [])
        for role in ("tutor", "coach"):
            ids = {d["id"] for d in kg.load_for_role(ROOT, role)}
            self.assertEqual(ids, {"KB-TEC", "KB-GEMINI"})

    def test_conteudo_essencial_dos_insumos(self):
        texto = {d["id"]: d["text"] for d in kg.load_for_role(ROOT, "tutor")}
        for frase in ("pontuação líquida", "Português ficou em 28", "TESTADO", "NÃO VERIFICADO", "repetição espaçada"):
            self.assertIn(frase, texto["KB-TEC"])
        for frase in ("Paráfrase", "imparcialidade", "correção mínima", "Não delegar sem conferência"):
            self.assertIn(frase, texto["KB-GEMINI"])

    def test_documento_alterado_sem_manifesto_e_recusado(self):
        root = self.tmp()
        p = root / "docs/plataformas/TEC_CONCURSOS_AUDITORIA_20261116.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nlinha injetada\n", encoding="utf-8")
        self.assertTrue(kg.check(root))
        with self.assertRaises(kg.KnowledgeError):
            kg.load_for_role(root, "tutor")

    def test_documento_ausente_symlink_ou_fora_do_diretorio(self):
        root = self.tmp()
        (root / "docs/plataformas/GEMINI_NOTEBOOK_AUDITORIA_20261116.md").unlink()
        self.assertTrue(kg.check(root))
        root = self.tmp()
        m = json.loads((root / kg.MANIFEST).read_text(encoding="utf-8"))
        m["documentos"][0]["path"] = "AGENTS.md"
        (root / kg.MANIFEST).write_text(json.dumps(m), encoding="utf-8")
        with self.assertRaises(kg.KnowledgeError):
            kg.load_manifest(root)
        root = self.tmp()
        alvo = root / "docs/plataformas/TEC_CONCURSOS_AUDITORIA_20261116.md"
        alvo.unlink()
        alvo.symlink_to(root / "docs/plataformas/GEMINI_NOTEBOOK_AUDITORIA_20261116.md")
        self.assertTrue(kg.check(root))

    def test_manifesto_malformado_e_papel_invalido(self):
        root = self.tmp()
        m = json.loads((root / kg.MANIFEST).read_text(encoding="utf-8"))
        m["documentos"][0]["roles"] = ["engineer"]
        (root / kg.MANIFEST).write_text(json.dumps(m), encoding="utf-8")
        with self.assertRaises(kg.KnowledgeError):
            kg.load_manifest(root)
        with self.assertRaises(kg.KnowledgeError):
            kg.load_for_role(ROOT, "engineer")

    def test_perfil_sem_referencia_ao_documento_e_recusado(self):
        root = self.tmp()
        p = root / "agents/TUTOR.md"
        p.write_text(p.read_text(encoding="utf-8").replace("TEC_CONCURSOS_AUDITORIA_20261116.md", "x.md"), encoding="utf-8")
        self.assertTrue(any("TUTOR.md" in e for e in kg.check(root)))

    def test_broker_entrega_a_base_a_tutor_e_coach_e_nao_a_engenharia(self):
        with patch("agent_entrypoint._git_head", return_value=HEAD), patch("agent_entrypoint._git_clean", return_value=None):
            for role in ("tutor", "coach"):
                b = ReadOnlyAgentBroker(ROOT, HEAD, role)
                ctx = b.model_context()
                self.assertEqual(set(ctx["knowledge"]), {d["path"] for d in kg.load_for_role(ROOT, role)})
                self.assertEqual(ctx["knowledge_sha256"], b.request("start")["knowledge_sha256"])
            self.assertNotIn("knowledge", ReadOnlyAgentBroker(ROOT, HEAD, "engineer").model_context())

    def test_broker_bloqueia_quando_a_base_diverge(self):
        with patch("agent_entrypoint._git_head", return_value=HEAD), patch("agent_entrypoint._git_clean", return_value=None), \
                patch("agent_entrypoint.load_for_role", side_effect=kg.KnowledgeError("x")):
            b = ReadOnlyAgentBroker(ROOT, HEAD, "tutor")
            with self.assertRaises(StartBlocked):
                b.model_context()
            with self.assertRaises(StartBlocked):
                b.request("start")

    def test_rota_de_estudo_inclui_base_e_verificacao(self):
        r = sr.build(ROOT, "study")
        ids = [s["id"] for s in r["etapas"]]
        self.assertLess(ids.index("ST5"), ids.index("ST5B"))
        self.assertLess(ids.index("ST5B"), ids.index("ST6"))
        kb = next(s for s in r["etapas"] if s["id"] == "ST5B")
        self.assertEqual({d["id"] for d in kb["documentos"]}, {"KB-TEC", "KB-GEMINI"})
        self.assertTrue(any(s.get("comando") == "python scripts/knowledge_gate.py --check" for s in r["etapas"]))


if __name__ == "__main__":
    unittest.main()
