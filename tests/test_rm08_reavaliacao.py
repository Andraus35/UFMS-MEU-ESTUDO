"""A reavaliação do RM-08 mantém o bloqueio, aponta os insumos que faltam e não promove nenhum gate."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RM08_REAVALIACAO_20261121.md").read_text(encoding="utf-8")
T = DOC.replace("**", "").replace("`", "").lower()


class Rm08ReavaliacaoTests(unittest.TestCase):
    def test_mantem_o_bloqueio_e_nao_promove_gates(self):
        for trecho in ("permanece bloqueado", "não homologa gp-3, gq-d, gq-c, gq-o nem gp-4", "não habilita build",
                       "continua bloqueado", "não é auditoria independente"):
            self.assertIn(trecho, T, trecho)

    def test_cobre_todos_os_bloqueadores_da_baseline(self):
        for trecho in ("reauditoria gq-d", "gq-c", "gq-o", "gp-3", "persistência e replay", "ciclo tutor–coach"):
            self.assertIn(trecho, T, trecho)

    def test_lista_os_insumos_do_proprietario_sem_assumir_insumo_novo(self):
        for trecho in ("eventos reais de estudo", "consentimento v4", "repositório privado", "nenhum insumo novo foi assumido"):
            self.assertIn(trecho, T, trecho)

    def test_estado_de_dados_confere_com_o_repositorio(self):
        atual = json.loads((ROOT / "state" / "CURRENT.json").read_text(encoding="utf-8"))
        self.assertEqual((atual["evidence_level"], atual["event_count"], atual["results_count"]), ("E0", 0, 0))
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(settings["storage"]["personal_results_writes_enabled"], False)
        self.assertIn("personal_results_writes_enabled=false", T)

    def test_roadmap_continua_com_rm08_bloqueado(self):
        linha = next(l for l in (ROOT / "ROADMAP.md").read_text(encoding="utf-8").splitlines() if l.startswith("| RM-08 |"))
        self.assertIn("bloqueado", linha)

    def test_sem_dado_pessoal_credencial_nem_estado_do_ciclo(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_|Bearer\s|https?://")


if __name__ == "__main__":
    unittest.main()
