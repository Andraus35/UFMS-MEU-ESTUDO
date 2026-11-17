"""Contrato da S7: P1 a P9 cobertos, fluxo único, token mínimo, revogação e flag de resultados falsa."""
import json
import re
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S7_PERSISTENCIA_ESCRITOR.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "")


class SpecS7Tests(unittest.TestCase):
    def test_requisitos_r1_a_r12_cada_um_com_criterio(self):
        linhas = [l for l in DOC.splitlines() if re.match(r"\| S7-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S7-R\d+) ", l).group(1) for l in linhas], [f"S7-R{i}" for i in range(1, 13)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_cada_controle_p1_a_p9_aparece_em_algum_requisito(self):
        requisitos = "\n".join(l for l in DOC.splitlines() if re.match(r"\| S7-R\d+ \|", l))
        for p in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"):
            self.assertRegex(requisitos, rf"\b{p}\b", p)

    def test_token_minimo_e_credencial_fora_do_modelo(self):
        for trecho in ("contents em leitura e escrita", "nenhuma outra permissão", "expiração de 30 dias", "por referência", "nunca no chat", "confere", "401"):
            self.assertIn(trecho, TEXTO)
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")

    def test_um_arquivo_por_evento_sem_edicao_e_correcao_como_novo_evento(self):
        for trecho in ("um arquivo próprio", "nunca alterado", "correção é novo evento", "nunca se atualiza evento existente", "hash canônico"):
            self.assertIn(trecho, TEXTO)

    def test_retencao_termina_em_16_02_2027_e_revogacao_apaga_o_repositorio_inteiro(self):
        self.assertEqual(date(2027, 1, 17) + timedelta(days=30), date(2027, 2, 16))
        for trecho in ("16/02/2027", "apagar o repositório privado inteiro", "forks desabilitados", "36 meses", "não elimina"):
            self.assertIn(trecho, TEXTO)

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        pesquisa = DOC.split("## Pesquisa", 1)[1].split("## Plano", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"https?://", pesquisa)), 7)
        self.assertIn("- **Lacunas:**", pesquisa)
        for trecho in ("nada foi provado contra um repositório privado real", "não li o artigo original", "hipótese a verificar", "não consultei jurista"):
            self.assertIn(trecho, pesquisa.replace("**", ""))

    def test_nao_habilita_escrita_nem_altera_perfis_e_nao_cria_rotina_de_escrita(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        for caminho in ("agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md", "AGENTS.md"):
            self.assertNotIn("S7_PERSISTENCIA", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertFalse(list((ROOT / "scripts").glob("private_writer*")))
        self.assertEqual(sorted(p.name for p in (ROOT / "agents").glob("*.md")), ["COACH.md", "README.md", "TUTOR.md", "ZAPIA.md"])

    def test_sem_dado_pessoal_e_na_fila(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        item = next(i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "S7")
        self.assertTrue((ROOT / item["deliverable"]).exists())


if __name__ == "__main__":
    unittest.main()
