"""E10: prorrogação do hook de entrega final (decisão do proprietário de 20/11/2026): prazo, registro e limites."""
import json
import re
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "hooks"))
import entrega_final as ef  # noqa: E402

DOC = (ROOT / "docs" / "governanca" / "E10_PRORROGACAO_HOOK_ENTREGA_FINAL.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
HOOK = (ROOT / ".claude" / "hooks" / "entrega_final.py").read_text(encoding="utf-8")


class E10Tests(unittest.TestCase):
    def test_prazo_prorrogado_para_18_12_2026(self):
        self.assertEqual(ef.PRAZO, date(2026, 12, 18))
        self.assertIn("18/12", ef.contagem(date(2026, 12, 1)))
        self.assertNotIn("20/11", ef.contagem(date(2026, 12, 1)))

    def test_o_hook_nao_fica_permanente(self):
        self.assertLess(ef.PRAZO, date(2027, 1, 1))  # a prorrogação tem teto: renovar é nova decisão dele
        self.assertIn("Depois de 18/12 não faz nada", HOOK)

    def test_registro_diz_a_decisao_e_a_mudanca(self):
        for trecho in ("20/11/2026", "prorrogar o hook de entrega final até o fim do piloto", "18/12/2026", "vencimento relatado dos tokens",
                       "teto seguro", "o merge do pr é a aprovação expressa dele", "decisões dele"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_registro_declara_que_o_hook_e_lembrete_e_nao_controle(self):
        for trecho in ("falha aberto", "lembrete de entrega", "não controle", "só lê e avisa", "não substitui isso", "s14-r17"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_so_o_hook_de_entrega_muda_settings_e_contratos_ficam_intocados(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        comandos = [h["command"] for g in settings["hooks"]["Stop"] for h in g["hooks"]]
        proprios = [c for c in comandos if "claude_context_guard.py" not in c]  # o hook geral entrou na E12-B
        self.assertEqual(len(proprios), 2)
        self.assertTrue(any("entrega_final.py" in c for c in comandos))
        self.assertIn("não altera .claude/settings.json", TEXTO)

    def test_o_hook_continua_so_lendo(self):
        for proibido in ("urllib", "requests", "socket", "write_text", "write_bytes", "open(", "GITHUB_TOKEN", "merge_pull_request", '"git", "push"'):
            self.assertNotIn(proibido, HOOK, proibido)

    def test_mensagens_nao_citam_mais_o_prazo_antigo(self):
        self.assertIsNone(re.search(r"para 20/11\"", HOOK))
        self.assertIsNone(re.search(r"hoje é 20/11", HOOK))


if __name__ == "__main__":
    unittest.main()
