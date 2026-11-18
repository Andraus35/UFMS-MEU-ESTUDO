"""V4: o texto do consentimento v4 é só proposta, cita o app Claude e não habilita nada."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/E5_CONSENTIMENTO_V4_PROPOSTA_20261118.md").read_text(encoding="utf-8")
ADR = (ROOT / "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md").read_text(encoding="utf-8")


class ConsentimentoV4Tests(unittest.TestCase):
    def texto(self):
        return "\n".join(l for l in DOC.splitlines() if l.startswith(">"))

    def test_e_proposta_e_nao_registra_nem_habilita(self):
        for t in ("PROPOSTO", "não registra", "não habilita", "`personal_results_writes_enabled` segue `false`", "ainda não existe"):
            self.assertIn(t, DOC, t)
        self.assertIn("Consentimento v4 (PROPOSTO", ADR)

    def test_texto_cita_app_claude_leitura_somente_de_projecoes_e_limites(self):
        t = self.texto()
        for trecho in ("app Claude", "somente leitura", "projeções", "nunca o histórico bruto", "texto de questões",
                       "identificador de conta", "ufms-meu-estudo-entrada", "ufms-meu-estudo-dados", "16/02/2027",
                       "não elimina as cópias na Zapia, no Google nem no app Claude", "Versão: v4", "não foi verificada"):
            self.assertIn(trecho, t, trecho)

    def test_nao_autoriza_coisas_proibidas(self):
        t = self.texto()
        for trecho in ("CPF", "credenciais", "exports brutos", "capturas de tela"):
            self.assertIn(trecho, t, trecho)
        self.assertIn("Não autorizo registrar", t)

    def test_flag_continua_falsa_e_fila_tem_o_item(self):
        s = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(s["storage"]["personal_results_writes_enabled"], False)
        w = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        v4 = next(i for i in w["work_queue"] if i["id"] == "V4")
        self.assertEqual(v4["deliverable"], "docs/governanca/E5_CONSENTIMENTO_V4_PROPOSTA_20261118.md")


if __name__ == "__main__":
    unittest.main()
