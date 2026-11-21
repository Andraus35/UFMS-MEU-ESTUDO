"""Contrato da S16: rotina de estudo UFMS 2027 (top 10 por matéria). Especificação; não lista o top 10 nem implanta."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S16_ROTINA_ESTUDO_TOP10_UFMS_2027.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Separação", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Pendências", 1)[0]
PENDENCIAS = DOC.split("## Pendências e conflitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}


def req(n):
    return REQUISITOS.split(f"S16-R{n} ", 1)[1].split("| S16-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS16Tests(unittest.TestCase):
    def test_secoes_na_ordem(self):
        pos = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Separação", "## Requisitos", "## Pendências e conflitos",
                                      "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(pos, sorted(pos))

    def test_requisitos_r1_a_r16_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S16-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S16-R\d+) ", l).group(1) for l in linhas], [f"S16-R{i}" for i in range(1, 17)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_link_e_lacunas_honestas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 1)
        self.assertIn("- **Lacunas:**", PESQUISA)
        for trecho in ("não consultei nenhuma página do tec", "percentuais do guia não foram vistos", "denominador",
                       "retificações do edital não foram conferidas", "nada foi implantado"):
            self.assertIn(trecho, PESQUISA.lower().replace("**", ""), trecho)

    def test_regra_do_top10_usa_so_percentual_do_guia_e_nao_amplia(self):
        r4 = req(4)
        for trecho in ("10 assuntos ou subassuntos de maior percentual por matéria", "apenas os percentuais efetivamente apresentados",
                       "do maior para o menor", "não amplia", "não completa o ranking com estimativa"):
            self.assertIn(trecho, r4, trecho)

    def test_origem_caminho_e_pai_filho(self):
        self.assertIn("cargo", req(1)); self.assertIn("caderno de origem", req(1)); self.assertIn("por inferência", req(1))
        self.assertIn("caminho inteiro", req(2))
        for trecho in ("não** soma pai e filho", "probabilidade"):
            self.assertIn(trecho.replace("**", ""), req(3).replace("**", ""), trecho)
        for campo in ("posição", "percentual", "fonte", "data", "filtros", "denominador"):
            self.assertIn(campo, req(5), campo)

    def test_pendencias_e_conflitos_para_o_proprietario(self):
        for pid in ("P1", "P2", "P3", "P4", "P5", "C1", "C2", "C3"):
            self.assertRegex(PENDENCIAS, rf"\| {pid} \|", pid)
        for trecho in ("decidido (21/11/2026): o harness não impõe cronograma", "decidido (21/11/2026): o top 10 por matéria restringe o plano"):
            self.assertIn(trecho, PENDENCIAS.lower().replace("**", ""), trecho)
        for trecho in ("pai e um subassunto", "denominador", "empate no 10º lugar", "menos de 10 itens", "pendencia_aberta",
                       "não inventa regra"):
            self.assertIn(trecho, (PENDENCIAS + REQUISITOS).lower().replace("**", "").replace("`", ""), trecho)

    def test_comandos_de_inicio_e_fim_nao_existem_e_dependem_do_e3(self):
        schema = json.loads((ROOT / "config" / "agent_command_schema.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(schema["destinations"]), sorted(schema["destinations"]))
        for op in schema["destinations"]:
            self.assertNotIn("estudo", op)
        for n in (10, 11):
            for trecho in ("não há comando hoje",):
                self.assertIn(trecho, req(n))
        self.assertIn("estudo de hoje finalizado.", req(11))
        self.assertIn("e3", req(10))

    def test_nao_lista_top10_nem_dado_pessoal_nem_credencial(self):
        self.assertNotRegex(DOC, r"\b\d{1,3}(?:[.,]\d+)?\s?%")  # nenhum percentual inventado
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_|Bearer\s")
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')

    def test_mantem_a_liberacao_da_zapia_e_a_data_da_prova(self):
        self.assertIn("liberação de 21/11/2026 (d-27)", TEXTO)
        self.assertIn("17/01/2027", DOC)
        cfg = json.loads((ROOT / "config" / "concursos.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["prova_data"], "2027-01-17")
        self.assertIs(cfg["retificacoes_verificadas"], False)

    def test_fila_readme_e_nao_altera_contrato(self):
        item = FILA["S16"]
        self.assertEqual(item["deliverable"], "docs/especificacoes/S16_ROTINA_ESTUDO_TOP10_UFMS_2027.md")
        self.assertEqual(item["roadmap_task"], "RM-09")
        self.assertTrue((ROOT / item["deliverable"]).exists())
        self.assertIn("| S16 |", (ROOT / "docs" / "especificacoes" / "README.md").read_text(encoding="utf-8"))
        for caminho in ("AGENTS.md", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md"):
            self.assertNotIn("S16_ROTINA", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
