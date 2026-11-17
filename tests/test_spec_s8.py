"""A S8 (rotina diária do Coach) precisa seguir o modelo das especificações, concordar com o resto e não vazar dado pessoal."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S8 = (ROOT / "docs" / "especificacoes" / "S8_ROTINA_COACH.md").read_text(encoding="utf-8")


class SpecS8Tests(unittest.TestCase):
    def test_segue_o_modelo_na_ordem(self):
        posicoes = [S8.index(t) for t in ("## Objetivo", "## Pesquisa", "## Requisitos", "## Aceite", "## Limites")]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_pesquisa_tem_fontes_com_link_confianca_e_lacunas(self):
        pesquisa = S8[S8.index("## Pesquisa"):S8.index("## Requisitos")]
        self.assertGreaterEqual(len(re.findall(r"\]\(https?://", pesquisa)), 6)
        self.assertRegex(pesquisa, r"\|\s*[ABC]\s*\|")
        self.assertIn("- **Lacunas:**", pesquisa)
        self.assertIn("autorrelato", pesquisa.lower())

    def test_requisitos_s8_r1_a_r9_com_aceite(self):
        tabela = S8[S8.index("## Requisitos"):S8.index("## Aceite")]
        for n in range(1, 10):
            self.assertIn(f"| S8-R{n} |", tabela)
        linhas = [l for l in tabela.splitlines() if l.startswith("| S8-R")]
        self.assertEqual(len(linhas), 9)
        for linha in linhas:
            self.assertGreaterEqual(linha.count("|"), 4)

    def test_limites_do_plano_e_regras_de_seguranca_estao_escritos(self):
        for trecho in ("900 s", "32 execuções por dia", "uma mensagem por dia", "`AUTORIZO`", "sem listar tudo",
                       "não chegam aos jobs", "pesquisa", "Não habilita a escrita de resultados"):
            self.assertIn(trecho.lower(), S8.lower(), trecho)

    def test_decisoes_do_proprietario_de_17_11_2026_estao_registradas(self):
        low = S8.lower().replace("**", "")
        for trecho in ("curta e diz que não há atividade", "no máximo um segundo lembrete", "teto: duas mensagens de rotina por dia",
                       "rotina-aaaa-mm-dd-lembrete2", "só o app", "uma única pergunta", "decisões do proprietário (17/11/2026)",
                       "nenhum job foi criado"):
            self.assertIn(trecho, low, trecho)
        self.assertNotIn("pontos a confirmar pelo proprietário", low)

    def test_nao_contem_horario_nem_ritmo_do_proprietario(self):
        self.assertIsNone(re.search(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", S8))
        self.assertIsNone(re.search(r"\b\d{1,2}\s?h\b", S8))
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", S8))
        self.assertNotRegex(S8, r"github_pat_|ghp_")
        for proibido in ("pomodoro", "04:30", "5h", "15h"):
            self.assertNotIn(proibido, S8.lower())

    def test_nao_cria_nada_e_aponta_o_que_e_outra_tarefa(self):
        self.assertIn("nada aqui cria job, lembrete ou mensagem", S8)
        self.assertIn("outra tarefa", S8)

    def test_concorda_com_esquema_perfis_fila_e_produto(self):
        esquema = json.loads((ROOT / "config" / "agent_command_schema.json").read_text(encoding="utf-8"))
        self.assertIn("consultar_agenda_minima", json.dumps(esquema))
        self.assertIn("consultar_agenda_minima", (ROOT / "agents" / "COACH.md").read_text(encoding="utf-8"))
        fila = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]
        s8 = next(i for i in fila if i["id"] == "S8")
        self.assertEqual(s8["deliverable"], "docs/especificacoes/S8_ROTINA_COACH.md")
        self.assertEqual(s8["depends_on"], ["S3", "S4", "S5"])
        self.assertIn("S8_ROTINA_COACH.md", (ROOT / "PRODUCT.md").read_text(encoding="utf-8"))
        self.assertIn("S8", (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8"))

    def test_s3_deixava_canal_e_frequencia_para_a_operacao(self):
        self.assertIn("Não escolhe canal, horário nem frequência", (ROOT / "docs/especificacoes/S3_COACH.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
