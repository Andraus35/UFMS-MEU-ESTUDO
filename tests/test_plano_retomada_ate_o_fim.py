"""O plano de retomada diz por onde começar e como esgotar pendências, fila e roadmap; sem estado volátil."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "PLANO_DE_RETOMADA_ATE_O_FIM_20261121.md").read_text(encoding="utf-8")
T = DOC.replace("**", "").replace("`", "").lower()
HANDOFF = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")


class PlanoRetomadaTests(unittest.TestCase):
    def test_comeca_pelo_bootstrap_confere_o_github_e_nao_infere_por_memoria(self):
        for trecho in ("0. por onde começar", "bootstrap.py --mode engineering", "next_task.py", "confirmar no github autenticado",
                       "não inferir por memória", "record_merge_receipt.py", "primeiro commit", "single_flow_gate.py --check"):
            self.assertIn(trecho, T, trecho)

    def test_fila_em_ordem_com_lotes_a_a_f_e_criterio_de_esgotado(self):
        pos = [DOC.index(f"**Lote {c},") for c in "ABCDEF"]
        self.assertEqual(pos, sorted(pos))
        for trecho in ("t1:", "t2:", "t3:", "pendencia_aberta", "teto de 15", "p9", "pj", "cm", "n1", "decisão f3",
                       "4. quando a sessão pode dizer", "antes disso, continuar o próximo lote"):
            self.assertIn(trecho, T, trecho)

    def test_mapa_separa_o_que_e_da_sessao_do_proprietario_e_o_que_ja_foi_feito(self):
        for trecho in ("já feitos pelo proprietário", "p1 a p8", "renovar `zapia_dados`".replace("`", ""), "18/12/2026", "04/12/2026",
                       "rm-08", "rm-09", "rm-10", "bloqueado"):
            self.assertIn(trecho, T, trecho)

    def test_regras_permanentes_e_liberacao_da_zapia(self):
        for trecho in ("uma tarefa → uma branch → um pr draft", "arquivos de contrato", "a zapia está liberada", "não reintroduzir",
                       "flag personal_results_writes_enabled segue false", "merge -s ours"):
            self.assertIn(trecho, T, trecho)

    def test_sem_estado_volatil_dado_pessoal_nem_credencial(self):
        self.assertNotRegex(DOC, r"\b[0-9a-f]{40}\b")
        self.assertNotRegex(DOC, r"\bPR\s*#\d+")
        self.assertNotRegex(DOC, r"\b[0-9a-f]{7}\b(?=`)")
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_|Bearer\s")

    def test_handoff_aponta_o_plano_e_nao_afirma_pendentes_atos_que_ja_foram_feitos(self):
        self.assertIn("PLANO_DE_RETOMADA_ATE_O_FIM_20261121.md", HANDOFF)
        self.assertIn("Pendências reais do proprietário", HANDOFF)
        self.assertNotIn("**Atos que só o proprietário pode fazer (bloqueiam o RM-08", HANDOFF)

    def test_arquivo_citado_no_plano_existe(self):
        for nome in re.findall(r"`((?:scripts|tests|docs|config)/[\w./-]+\.(?:py|md|json))`", DOC):
            self.assertTrue((ROOT / nome).is_file() or "tests/test_sem_restricoes" in nome, nome)


if __name__ == "__main__":
    unittest.main()
