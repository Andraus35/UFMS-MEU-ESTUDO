"""Contrato da S22: tarefas agendadas do Claude como gatilho dos agentes. Especificação; não cria, agenda nem testa nada."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S22_TAREFAS_AGENDADAS_CLAUDE_GATILHO.md").read_text(encoding="utf-8")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Onde se encaixa", 1)[0]
ENCAIXE = DOC.split("## Onde se encaixa", 1)[1].split("## Requisitos", 1)[0]
REQ = DOC.split("## Requisitos", 1)[1].split("## Matriz", 1)[0]
MATRIZ = DOC.split("## Matriz gatilho", 1)[1].split("## Aceite", 1)[0]
T = DOC.lower().replace("**", "").replace("`", "")


def req(n):
    return REQ.split(f"S22-R{n} ", 1)[1].split("| S22-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS22Tests(unittest.TestCase):
    def test_secoes_na_ordem(self):
        pos = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Onde se encaixa", "## Requisitos", "## Matriz gatilho", "## Aceite", "## Limites")]
        self.assertEqual(pos, sorted(pos))

    def test_requisitos_r1_a_r11_cada_um_com_criterio(self):
        linhas = [l for l in REQ.splitlines() if re.match(r"\| S22-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S22-R\d+) ", l).group(1) for l in linhas], [f"S22-R{i}" for i in range(1, 12)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3)

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 2)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)
        self.assertIn("- **Lacunas:**", PESQUISA)
        for t in ("pontualidade real", "nada foi testado", "não existe"):
            self.assertIn(t, PESQUISA.lower().replace("**", ""), t)

    def test_encaixe_tem_o_fluxo_e_os_donos(self):
        for t in ("tarefa agendada", "start", "caixa", "fluxo", "campainha", "zapia", "gates"):
            self.assertIn(t, ENCAIXE.lower(), t)

    def test_gatilho_so_acorda_e_a_entrega_e_da_zapia(self):
        r1 = req(1)
        for t in ("só acorda", "não fala com o estudante", "tec", "gemini"):
            self.assertIn(t, r1, t)
        self.assertIn("entrega no minuto", T)
        self.assertIn("zapia", req(2))

    def test_prova_s15_r4_sem_efeito_e_sem_dado_pessoal(self):
        r6 = req(6)
        for t in ("3 dias", "só grava um carimbo", "sem dado pessoal", "atraso e perda", "o proprietário ajusta"):
            self.assertIn(t, r6, t)

    def test_escopo_do_token_e_risco_declarado(self):
        r5 = req(5)
        for t in ("só do repositório entrada", "sem permissão de workflows", "não provada", "não limita por pasta"):
            self.assertIn(t, r5, t)

    def test_push_nao_adotado_e_despertar_perdido_seguro(self):
        self.assertIn("não adotado", req(9))
        self.assertIn("rajada", req(7))

    def test_matriz_nao_deixa_a_tarefa_falar_com_as_plataformas(self):
        linha = next(l for l in MATRIZ.splitlines() if l.startswith("| Tarefa agendada do Claude"))
        self.assertIn("não pode", MATRIZ.lower())
        self.assertIn("falar com estudante, tec ou gemini", linha.lower())

    def test_nada_foi_criado_e_sem_dado_pessoal_nem_credencial(self):
        for t in ("nada foi criado, agendado, ligado ou testado", "pontualidade das tarefas agendadas do claude é desconhecida"):
            self.assertIn(t, T, t)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_[A-Za-z0-9_]{10}|Bearer\s")

    def test_fila_aponta_para_a_especificacao_e_s21_fica_reservada(self):
        item = next(i for i in json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "S22")
        self.assertEqual(item["deliverable"], "docs/especificacoes/S22_TAREFAS_AGENDADAS_CLAUDE_GATILHO.md")
        self.assertTrue((ROOT / item["deliverable"]).exists())
        self.assertIn("S21", (ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))

    def test_indice_do_readme_lista_a_s22(self):
        self.assertRegex((ROOT / "docs/especificacoes/README.md").read_text(encoding="utf-8"), r"\| S22 \|")


if __name__ == "__main__":
    unittest.main()
