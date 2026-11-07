"""Consistência entre plano, regras, configuração e documento de pesquisa."""
import inspect
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import study_plan  # noqa: E402

PLANO = (ROOT / "docs/pedagogia/PLANO_DE_ESTUDOS_METODO_4_2_E_REVISAO_7_15_30.md").read_text(encoding="utf-8")
PESQUISA = (ROOT / "docs/pedagogia/ESTADO_DA_ARTE_TUTOR_COACH_20261107.md").read_text(encoding="utf-8")
SETTINGS = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")


class PlanoEPesquisaTests(unittest.TestCase):
    def test_plano_cita_o_padrao_do_settings(self):
        d = SETTINGS["study"]["owner_default_plan"]
        self.assertEqual(d["review_intervals_days"], [7, 15, 30])
        self.assertEqual(d["max_minutes_per_discipline_theory"], 120)
        self.assertIn("D+7, D+15 e D+30", PLANO)
        self.assertIn("120 minutos por disciplina", PLANO)
        self.assertIn("study.owner_default_plan", PLANO)

    def test_plano_documenta_todos_os_parametros_do_gerador(self):
        parametros = set(inspect.signature(study_plan.generate_plan).parameters)
        for nome in parametros - {"defaults", "topics"}:
            self.assertIn(nome, PLANO, nome)

    def test_flags_de_imposicao_seguem_falsas_e_o_padrao_e_ajustavel(self):
        self.assertIs(SETTINGS["study"]["fixed_schedule"], False)
        self.assertIs(SETTINGS["study"]["fixed_repetition_intervals"], False)
        self.assertIs(SETTINGS["study"]["owner_default_plan"]["adjustable_with_justification"], True)

    def test_regras_nao_contradizem_mais_o_padrao_do_proprietario(self):
        for rel in ("AGENTS.md", "rules/STUDY.md", "rules/CORE.md", "docs/METHOD.md"):
            texto = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("D-11", texto, rel)
        self.assertNotIn("disponibilidade e prazo do concurso; nenhum intervalo universal.",
                         (ROOT / "rules/STUDY.md").read_text(encoding="utf-8"))
        self.assertNotIn("referência opcional", (ROOT / "rules/STUDY.md").read_text(encoding="utf-8"))

    def test_pesquisa_tem_fontes_e_declara_limites(self):
        urls = set(re.findall(r"https?://[^\s)\]]+", PESQUISA))
        self.assertGreaterEqual(len(urls), 12)
        for trecho in ("Não é revisão sistemática", "não consegui ler a ajuda oficial",
                       "não foram verificados", "Nenhuma fonte desta pesquisa comprova a eficácia do Método 4.2",
                       "Gemini Notebook"):
            self.assertIn(trecho, PESQUISA)
        self.assertIn("19/02/2018", PESQUISA)
        self.assertIn("não menciona", PESQUISA)             # o 4.2 não menciona 7, 15 e 30

    def test_pesquisa_nao_atribui_ao_4_2_a_revisao_em_7_15_30(self):
        self.assertIn("Decisão do proprietário", PLANO)
        self.assertNotRegex(PLANO, r"Método 4\.2[^.\n]{0,80}prescreve[^.\n]{0,40}7, 15 e 30")

    def test_product_registra_decisoes_e_pontos_em_aberto_da_criacao_dos_agentes(self):
        for ref in ("D-11", "D-12", "PR-014", "PR-015", "PR-016", "OPEN-10", "OPEN-11", "E-11"):
            self.assertIn(ref, PRODUCT)
        self.assertIn("O conteúdo é produzido apenas pelo Tutor", PRODUCT)
        self.assertIn("prioridade ao acesso direto", PRODUCT)


if __name__ == "__main__":
    unittest.main()
