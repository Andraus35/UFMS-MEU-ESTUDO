"""E46: o ponto de retomada da sessão de 25 e 26/11/2026 existe, está visível no HANDOFF e traz o que a próxima sessão precisa (decisões, prompts, atos, ordem)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/E46_RETOMADA_PROXIMA_SESSAO_20261125_26.md").read_text(encoding="utf-8")
HANDOFF = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8")
WORKFLOW = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))


class RetomadaE46Test(unittest.TestCase):
    def test_o_handoff_aponta_para_o_registro_logo_no_inicio(self):
        i = HANDOFF.index("E46_RETOMADA_PROXIMA_SESSAO_20261125_26.md")
        self.assertLess(i, 9000)  # visível no começo do arquivo lido no START
        self.assertIn("LEITURA OBRIGATÓRIA DA PRÓXIMA SESSÃO", HANDOFF[i - 80:i])

    def test_o_registro_traz_estado_decisoes_atos_e_ordem(self):
        for trecho in ("b1187c8", "#208", "N1_NAO_PROVADO", "FONTE_NAO_ADICIONADA", "DATA_PARSE_ERROR", "2bef6d04", "DESABILITADO", "27/11/2026 21:55Z",
                       "D-26", "config/propostas_tutor_n1.json", "E44", "E45", "Criar a tarefa S22", "aprovação destacada fica só com o hash",
                       "N1-DIAG-FONTE", "N1-RODADA-4", "E45-CORRETOR", "S22-PROVA-MIN", "--prefixo n1d", "git merge -s ours", "4000", "REVISAO UFMS DIREITO ADM",
                       "não fechar nem comentar issue SINAL com hook habilitado", "Hipótese não provada", "Apêndice A", "Apêndice B", "Apêndice C"):
            self.assertIn(trecho, DOC, trecho)

    def test_os_prompts_prontos_estao_integros(self):
        blocos = re.findall(r"```\n(.*?)\n```", DOC, flags=re.S)
        self.assertGreaterEqual(len(blocos), 3)
        manual = next(b for b in blocos if b.startswith("TESTE MANUAL DE DIAGNÓSTICO"))
        for trecho in ("Execute VOCÊ MESMA", "não pergunte ao Gemini", "NÃO grave nada no GitHub", "COPIE LITERALMENTE os nomes de TODAS as opções",
                       "opção de texto colado", "não consigo ver", "CONTINUE para o passo seguinte", "A administração pública direta e indireta de qualquer dos Poderes"):
            self.assertIn(trecho, manual, trecho)
        self.assertTrue(any(b.startswith("Desative (desabilite) o hook de Gmail 2bef6d04-e272-4b25-b9b9-4d44958cfd73") for b in blocos))
        self.assertTrue(any(b.startswith("Atualize o hook de Gmail existente 2bef6d04-e272-4b25-b9b9-4d44958cfd73") for b in blocos))

    def test_as_proximas_tarefas_estao_na_fila_na_ordem_e_com_o_que_as_bloqueia(self):
        ids = [i["id"] for i in WORKFLOW["work_queue"]]
        fim = ids[-8:-4]  # os 4 últimos itens são do E52 (28/11/2026)
        self.assertEqual(fim, ["N1-DIAG-FONTE", "N1-RODADA-4", "E45-CORRETOR", "S22-PROVA-MIN"])
        fila = {i["id"]: i for i in WORKFLOW["work_queue"]}
        self.assertTrue(fila["N1-DIAG-FONTE"]["blocking_inputs"])
        self.assertEqual(fila["N1-RODADA-4"]["depends_on"], ["N1-DIAG-FONTE"])
        self.assertTrue(any("Criar a tarefa S22" in b for b in fila["S22-PROVA-MIN"]["blocking_inputs"]))
        for i in fila.values():
            self.assertIn("roadmap_task", i)

    def test_o_workflow_cabe_no_limite_do_start(self):
        self.assertLess(len((ROOT / "state/WORKFLOW.json").read_bytes()), 64 * 1024)

    def test_o_registro_nao_guarda_segredo_nem_dado_pessoal_alem_do_que_ja_e_publico_no_projeto(self):
        self.assertNotRegex(DOC, r"ghp_|github_pat_|Bearer\s+[A-Za-z0-9]|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")


if __name__ == "__main__":
    unittest.main()
