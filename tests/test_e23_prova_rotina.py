"""E23: o registro da prova real da rotina agendada diz o que está provado e o que NÃO está, traz a linha do tempo e as lições. Não promove além da prova."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "governanca" / "E23_ZAPIA_ROTINA_TESTE_PROVA_REAL.md"


class RegistroTeste(unittest.TestCase):
    def test_diz_o_que_esta_provado_e_o_que_nao_esta(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("Acordou sozinha", "commands/validados", "traduziu `comandos` para `commands`", "Falha segura correta", "\"ok\": true",
                       "`{\"conferidas\": 1, \"falhas\": {}}`".replace("`", ""), "sem a frase `AUTORIZO`", "O que NÃO está provado", "falta a captura do aparelho",
                       "`rotina_id_relatado`", "confere só o **formato**", "Causa não determinada", "causa do 0 das 00:15", "promoção pelo fluxo",
                       "URLs completos e literais", "github_ufms_repo_token", "SINTETICO_MANUAL", "dois arquivos **vazios**"):
            self.assertIn(trecho, t, trecho)

    def test_nao_registra_token_nem_dado_pessoal(self):
        t = DOC.read_text(encoding="utf-8").lower()
        for ruim in ("ghp_", "github_pat_", "souza.merchan", "bearer "):
            self.assertNotIn(ruim, t)


if __name__ == "__main__":
    unittest.main()
