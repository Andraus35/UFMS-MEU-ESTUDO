import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import doc_cohesion  # noqa: E402


class DocCohesionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "repo"
        self.addCleanup(shutil.rmtree, self.tmp.parent, True)
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

    def _append(self, rel, text):
        p = self.tmp / rel
        p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")

    def _fails(self, code):
        with self.assertRaises(ValueError) as ctx:
            doc_cohesion.validate(self.tmp)
        self.assertIn(code, str(ctx.exception))

    def test_repositorio_real_passa(self):
        self.assertEqual(doc_cohesion.validate(ROOT)["result"], "PASS")

    def test_copia_integra_passa(self):
        self.assertEqual(doc_cohesion.validate(self.tmp)["result"], "PASS")

    def test_c1_caminho_inexistente(self):
        self._append("docs/PLATFORMS.md", "\nVer `docs/nao_existe.md`.\n")
        self._fails("C1")

    def test_c1_ignora_bloco_de_codigo_e_placeholders(self):
        self._append("docs/PLATFORMS.md", "\n```\n`docs/nao_existe.md`\n```\nExemplo `docs/<nome>.md` e `scripts/*.py`.\n")
        self.assertEqual(doc_cohesion.validate(self.tmp)["result"], "PASS")

    def test_c2_link_relativo_quebrado(self):
        self._append("docs/PLATFORMS.md", "\n[x](nao_existe.md)\n")
        self._fails("C2")

    def test_c3_id_nao_definido(self):
        self._append("docs/PLATFORMS.md", "\nVer D-99.\n")
        self._fails("C3")

    def test_c3_tarefa_fora_do_roadmap(self):
        self._append("docs/PLATFORMS.md", "\nVer RM-77.\n")
        self._fails("C3")

    def test_c3_workflow_aponta_tarefa_inexistente(self):
        p = self.tmp / "state/WORKFLOW.json"
        w = json.loads(p.read_text(encoding="utf-8"))
        w["next_task_after_merge"] = "RM-88"
        p.write_text(json.dumps(w), encoding="utf-8")
        self._fails("C3")

    def test_c4_id_duplicado(self):
        self._append("PRODUCT.md", "\n- **D-01 (x):** duplicado.\n")
        self._fails("C4")

    def test_c5_intervalos_divergentes(self):
        p = self.tmp / "settings.json"
        s = json.loads(p.read_text(encoding="utf-8"))
        s["study"]["owner_default_plan"]["review_intervals_days"] = [1, 7, 30]
        p.write_text(json.dumps(s), encoding="utf-8")
        self._fails("C5")

    def test_c5_agenda_fixa_ligada(self):
        p = self.tmp / "settings.json"
        s = json.loads(p.read_text(encoding="utf-8"))
        for v in s.values():
            if isinstance(v, dict) and "fixed_schedule" in v:
                v["fixed_schedule"] = True
        p.write_text(json.dumps(s), encoding="utf-8")
        self._fails("C5")

    def test_c6_frase_superada(self):
        self._append("docs/PLATFORMS.md", "\nNão acessar conta privada por bots.\n")
        self._fails("C6")

    def test_c6_frase_emendada_nao_dispara(self):
        self._append("docs/PLATFORMS.md", "\nFora do padrão do proprietário, nenhum intervalo universal.\n")
        self.assertEqual(doc_cohesion.validate(self.tmp)["result"], "PASS")

    def _spec(self, body):
        d = self.tmp / "docs/especificacoes"
        d.mkdir(parents=True, exist_ok=True)
        (d / "S9_teste.md").write_text(body, encoding="utf-8")

    def test_c7_especificacao_sem_pesquisa(self):
        self._spec("# S9\n\n## Objetivo\nx\n\n## Requisitos\ny\n")
        self._fails("C7")

    def test_c7_pesquisa_sem_link(self):
        self._spec("# S9\n\n## Pesquisa\n- fonte sem link\n- **Lacunas:** nenhuma\n\n## Requisitos\ny\n")
        self._fails("C7")

    def test_c7_pesquisa_sem_lacunas(self):
        self._spec("# S9\n\n## Pesquisa\n- https://exemplo.org (confiança B)\n\n## Requisitos\ny\n")
        self._fails("C7")

    def test_c7_pesquisa_completa_passa(self):
        self._spec("# S9\n\n## Pesquisa\n- https://exemplo.org (confiança B)\n- **Lacunas:** página bloqueada.\n\n## Requisitos\ny\n")
        self.assertEqual(doc_cohesion.validate(self.tmp)["result"], "PASS")

    def _queue(self, mutate):
        p = self.tmp / "state/WORKFLOW.json"
        w = json.loads(p.read_text(encoding="utf-8"))
        mutate(w["work_queue"])
        p.write_text(json.dumps(w), encoding="utf-8")

    def test_c8_item_sem_campo(self):
        self._queue(lambda q: q[0].pop("deliverable"))
        self._fails("C8")

    def test_c8_tarefa_fora_do_roadmap(self):
        self._queue(lambda q: q[0].update(roadmap_task="RM-77"))
        self._fails("C8")

    def test_c8_dependencia_inexistente_ou_posterior(self):
        self._queue(lambda q: q[0].update(depends_on=["S9"]))
        self._fails("C8")
        self._queue(lambda q: q[0].update(depends_on=["S2"]))
        self._fails("C8")

    def test_c8_entrega_fora_de_especificacoes(self):
        self._queue(lambda q: q[0].update(deliverable="docs/outro/S1.md"))
        self._fails("C8")

    def test_c8_id_repetido(self):
        self._queue(lambda q: q[1].update(id=q[0]["id"]))
        self._fails("C8")

    def test_c0_documento_normativo_ausente(self):
        (self.tmp / "docs/PLATFORMS.md").unlink()
        self._fails("C0")


if __name__ == "__main__":
    unittest.main()
