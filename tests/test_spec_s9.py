"""Contrato da S9: leitura direta das plataformas. Exportação primeiro (TEC), Qconcursos sem automação, sem conversor sem amostra."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S9_LEITURA_PLATAFORMAS.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Decisões a registrar", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]


class SpecS9Tests(unittest.TestCase):
    def test_requisitos_r1_a_r10_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S9-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S9-R\d+) ", l).group(1) for l in linhas], [f"S9-R{i}" for i in range(1, 11)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 7)
        self.assertIn("- **Lacunas:**", PESQUISA)
        sem_negrito = PESQUISA.replace("**", "")
        for trecho in ("não confirmei", "nenhum desenho foi testado", "formato real das colunas", "relato"):
            self.assertIn(trecho, sem_negrito.lower(), trecho)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)

    def test_insumos_do_proprietario_registrados_como_afirmacao_e_lacuna(self):
        for trecho in ("exportação do desempenho em csv ou excel", "não sei / não conferi", "viu a zapia",
                       "afirmações dele, não verificadas", "lacuna declarada"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_ordem_dos_caminhos_exportacao_primeiro_e_qconcursos_pode_ser_lido(self):
        r1 = REQUISITOS.split("S9-R1 ", 1)[1].split("| S9-R2 ", 1)[0].lower().replace("**", "")
        for trecho in ("linha de base e o primeiro caminho", "complemento condicionado", "pode ler", "entrada manual"):
            self.assertIn(trecho, r1, trecho)

    def test_somente_leitura_e_lista_fechada_impostas_fora_do_navegador(self):
        r2 = REQUISITOS.split("S9-R2 ", 1)[1].split("| S9-R3 ", 1)[0].lower().replace("**", "")
        for trecho in ("somente leitura", "lista fechada", "proibido", "fora do navegador", "file://"):
            self.assertIn(trecho, r2, trecho)

    def test_credencial_nunca_ao_modelo_nem_ao_repositorio(self):
        r3 = REQUISITOS.split("S9-R3 ", 1)[1].split("| S9-R4 ", 1)[0].lower().replace("**", "")
        for trecho in ("nunca", "cookie", "conta exclusiva", "encerrar a sessão", "não é verificável"):
            self.assertIn(trecho, r3, trecho)

    def test_sem_cota_imposta_pelo_harness(self):
        r4 = REQUISITOS.split("S9-R4 ", 1)[1].split("| S9-R5 ", 1)[0].lower().replace("**", "")
        for trecho in ("sem cota", "não limita", "não paralelizar", "sem repetição automática"):
            self.assertIn(trecho, r4, trecho)

    def test_zapia_liberada_sem_condicao_previa(self):
        r8 = REQUISITOS.split("S9-R8 ", 1)[1].split("| S9-R9 ", 1)[0].lower().replace("**", "")
        for trecho in ("liberou a zapia", "livremente", "nenhuma condição prévia", "21/11/2026"):
            self.assertIn(trecho, r8, trecho)

    def test_primeira_leitura_nao_depende_de_aprovacao_adicional(self):
        r9 = REQUISITOS.split("S9-R9 ", 1)[1].split("| S9-R10 ", 1)[0].lower().replace("**", "")
        self.assertIn("não depende de aprovação adicional", r9)

    def test_nao_ha_conversor_sem_amostra_nem_modulo_de_leitura_ainda(self):
        # a L2 entrou por decisão do proprietário (18/11/2026): o ÚNICO conversor é scripts/tec_export_converter.py, que só vê o objeto
        # já carregado (não lê arquivo bruto, não grava, sem rede); qualquer outro conversor ou leitor direto continua proibido
        for padrao in ("*conversor*", "*export_tec*", "*exportacao_tec*", "*leitura_direta*", "*platform_reader*"):
            self.assertEqual(list((ROOT / "scripts").glob(padrao)), [], padrao)
        self.assertEqual(sorted(p.name for p in (ROOT / "scripts").glob("*convert*")), ["tec_export_converter.py"])
        ids = {i["id"] for i in FILA}
        self.assertNotIn("L3", ids)
        l2 = next((i for i in FILA if i["id"] == "L2"), None)  # L2 entrou na fila por decisão dele (18/11/2026), com a amostra real; ainda sem arquivo
        self.assertIsNotNone(l2)
        self.assertEqual(l2["deliverable"], "scripts/tec_export_converter.py")
        l1 = next((i for i in FILA if i["id"] == "L1"), None)  # a L1 entrou na fila por decisão do proprietário (17/11/2026)
        self.assertIsNotNone(l1)
        self.assertEqual(l1["deliverable"], "scripts/platform_read_guard.py")
        self.assertEqual(l1["depends_on"], ["S9"])

    def test_nao_habilita_escrita_nao_tem_dado_pessoal_nem_credencial(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")

    def test_nao_altera_contrato_e_e_item_da_fila_entregue(self):
        for caminho in ("AGENTS.md", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md"):
            self.assertNotIn("S9_LEITURA", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        item = next(i for i in FILA if i["id"] == "S9")
        self.assertEqual(item["deliverable"], "docs/especificacoes/S9_LEITURA_PLATAFORMAS.md")
        self.assertTrue((ROOT / item["deliverable"]).exists())

    def test_decisao_final_e_do_proprietario_por_pr(self):
        for trecho in ("só vira decisão", "aprovação humana", "propostas ao proprietário", "ainda não aprovadas"):
            self.assertIn(trecho, TEXTO, trecho)


if __name__ == "__main__":
    unittest.main()
