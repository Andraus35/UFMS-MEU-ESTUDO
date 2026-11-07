"""ADR-013: desenho de persistência privada não habilita escrita pessoal."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
DOC = ROOT / "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"


class Adr013Tests(unittest.TestCase):
    def test_controles_p1_a_p9_presentes(self):
        text = DOC.read_text(encoding="utf-8")
        for n in range(1, 10):
            self.assertRegex(text, rf"\|\s*P{n}\s*\|", f"controle P{n} ausente")

    def test_exige_visibilidade_privada_e_token_fora_do_llm(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("private=true", text)
        self.assertIn("Token fora do LLM", text)
        self.assertIn("não habilita", text)

    def test_decisions_registra_adr013_sem_habilitar(self):
        decisions = (ROOT / "memory/DECISIONS.md").read_text(encoding="utf-8")
        self.assertRegex(decisions, r"## ADR-013 ")
        self.assertIn("implementação e habilitação não autorizadas", decisions)

    def test_flag_de_escrita_pessoal_permanece_desabilitada(self):
        settings = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(settings["storage"]["personal_results_writes_enabled"], False)

    def test_estado_de_estudo_permanece_vazio(self):
        current = json.loads((ROOT / "state/CURRENT.json").read_text(encoding="utf-8"))
        self.assertEqual((current["event_count"], current["results_count"]), (0, 0))


    def test_decisoes_do_proprietario_registradas_sem_criar_nada(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Andraus35/ufms-meu-estudo-dados", text)
        self.assertIn("Zapia, como executora, grava desde o início", text)
        self.assertIn("só por comando do Tutor", text)
        self.assertIn("OPEN-02", text)
        self.assertIn("17/01/2027", text)
        self.assertIn("apagar o repositório privado inteiro", text)
        self.assertIn("ainda não foi criado", text)
        self.assertIn("APROVADO pelo proprietário em 07/11/2026", text)
        self.assertIn("mais 30 dias", text)
        self.assertIn("Consentimento v2 (APROVADO pelo proprietário em 07/11/2026, sem ajustes; substitui o v1)", text)
        self.assertIn("SUBSTITUÍDO pelo v2", text)
        self.assertNotIn("RASCUNHO", text)
        self.assertIn("apagar o repositório não elimina as cópias na Zapia nem no Google", text)
        self.assertIn("Versão: v2", text)

    def test_repositorio_privado_difere_do_publico(self):
        from private_persistence_guard import PUBLIC_REPOSITORY, check_destination
        with self.assertRaises(ValueError):
            check_destination(PUBLIC_REPOSITORY, "Andraus35/ufms-meu-estudo-dados")
        self.assertEqual(check_destination("Andraus35/ufms-meu-estudo-dados",
                                           "Andraus35/ufms-meu-estudo-dados"),
                         "Andraus35/ufms-meu-estudo-dados")

if __name__ == "__main__":
    unittest.main()
