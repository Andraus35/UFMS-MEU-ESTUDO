"""Contrato da S20: automação ponta a ponta (Tutor e Coach acionam a Zapia). Especificação; não implanta nada nem altera agents/."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S20_AUTOMACAO_PONTA_A_PONTA_ZAPIA.md").read_text(encoding="utf-8")
GAPS = (ROOT / "docs" / "governanca" / "FILA_GAPS_E_DIVERGENCIAS_20261121.md").read_text(encoding="utf-8")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Mapa", 1)[0]
MAPA = DOC.split("## Mapa", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}


def req(n):
    return REQUISITOS.split(f"S20-R{n} ", 1)[1].split("| S20-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS20Tests(unittest.TestCase):
    def test_secoes_na_ordem(self):
        pos = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Mapa", "## Decisões que são do proprietário", "## Requisitos", "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(pos, sorted(pos))

    def test_requisitos_r1_a_r12_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S20-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S20-R\d+) ", l).group(1) for l in linhas], [f"S20-R{i}" for i in range(1, 13)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3)

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 5)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)
        self.assertIn("- **Lacunas:**", PESQUISA)
        for t in ("não foram lidos por inteiro", "não verifiquei", "não achei", "não testei", "nada foi implantado"):
            self.assertIn(t, PESQUISA.lower().replace("**", ""), t)

    def test_mapa_p1_a_p8_e_decisoes_d1_a_d3(self):
        for p in range(1, 9):
            self.assertRegex(MAPA, rf"\| P{p} \|")
        decisoes = DOC.split("## Decisões que são do proprietário", 1)[1].split("## Requisitos", 1)[0]
        for d in ("D1", "D2", "D3"):
            self.assertIn(f"| {d} |", decisoes)
        for t in ("whatsapp", "gmail", "conector de github", "drive"):
            self.assertIn(t, decisoes.lower(), t)

    def test_honestidade_gates_fora_do_modelo_e_fila_unica(self):
        for t in ("não está garantida", "caminho manual"):
            self.assertIn(t, req(1), t)
        for t in ("só emitem comando", "fora do modelo", "sem aprovação"):
            self.assertIn(t, req(2), t)
        for t in ("fila entrada", "texto livre não é comando", "drive não é canal"):
            self.assertIn(t, req(3), t)

    def test_entrega_gatilho_autorizo_e_notebook(self):
        for t in ("prova sem efeito", "recibo", "nada é considerado entregue"):
            self.assertIn(t, req(4), t)
        for t in ("melhor esforço", "60 dias", "monitoramento externo", "ausência do recibo"):
            self.assertIn(t, req(5), t)
        for t in ("autorizo", "mais restritivo"):
            self.assertIn(t, req(6), t)
        for t in ("só transporta", "dado não confiável", "verifica", "sem laço"):
            self.assertIn(t, req(7), t)

    def test_privacidade_falha_fases_decisoes_e_limites(self):
        for t in ("dado pessoal", "flag false", "consentimento v4"):
            self.assertIn(t, req(8), t)
        self.assertIn("não geram envio substituto", req(9))
        for f in ("f0", "f1", "f2", "f3", "f4", "f5"):
            self.assertIn(f, req(10))
        self.assertIn("nenhuma fase começa sem a anterior", req(10))
        for t in ("d1", "d2", "d3", "não adota"):
            self.assertIn(t, req(11), t)
        for t in ("não prova", "autorrelato"):
            self.assertIn(t, req(12), t)

    def test_fila_de_gaps_no_workflow_em_serie_e_documentada(self):
        lotes = ["GAP-A", "GAP-B", "GAP-C", "GAP-D", "GAP-E"]
        self.assertEqual(FILA["HOOKR"]["depends_on"], ["S20"])  # correção do hook entra logo depois do S20
        self.assertEqual(FILA["GAP-A"]["depends_on"], ["HOOKR"])
        for ant, atual in zip(lotes, lotes[1:]):
            self.assertEqual(FILA[atual]["depends_on"], [ant])
        for l in lotes:
            self.assertRegex(FILA[l]["deliverable"], r"^scripts/[a-z_]+\.py$")
            self.assertFalse((ROOT / FILA[l]["deliverable"]).exists(), l)  # ainda não feitos: viram pendentes
            self.assertIn(FILA[l]["deliverable"], GAPS)
        for gid in ("GA-1", "GA-2", "GB-1", "GC-1", "GD-1", "GE-1", "G-1", "G-6"):
            self.assertIn(f"| {gid} |", GAPS)
        self.assertIn("não foram reproduzidos", GAPS)

    def test_nada_aplicado_e_flag_false(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC + GAPS))
        self.assertIn("| S20 |", (ROOT / "docs/especificacoes/README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
