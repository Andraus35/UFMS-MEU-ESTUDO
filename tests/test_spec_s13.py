"""Contrato da S13: papéis, conversão completa dos códigos de erro, assistência e retenção, sem alterar perfis."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S13_INTEGRACAO_CONCEITOS_COGNITIVOS.md").read_text(encoding="utf-8")
TEXTO = DOC.lower()
CANON = ROOT / "docs" / "canonicos" / "cognicao"
FONTES = {"A": "PESQUISA_INTELIGENCIA_ADVERSARIAL_DAS_BANCAS.md", "C": "PESQUISA_CICLO_APRENDIZAGEM_ESTRATEGIA_COGNITIVA.md",
          "I": "BASE_COGNITIVA_INTEGRADA_TUTOR_COACH.md"}


def codigos_da_fonte(nome):
    texto = (CANON / nome).read_text(encoding="utf-8")
    return set(re.findall(r"^\| `([A-Z]{2,5}\??)` \|", texto, flags=re.M))


def conversao():
    linhas = re.findall(r"^\| ([ACI]) \| ([A-Z]{2,5}\??) \| ([^|]+?) \|", DOC, flags=re.M)
    return [(f, c, s.strip()) for f, c, s in linhas]


class SpecS13Tests(unittest.TestCase):
    def test_requisitos_r1_a_r10_cada_um_com_criterio(self):
        linhas = [l for l in DOC.splitlines() if re.match(r"\| S13-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S13-R\d+) ", l).group(1) for l in linhas], [f"S13-R{i}" for i in range(1, 11)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_conversao_cobre_todo_codigo_das_tres_fontes(self):
        conv = {(f, c) for f, c, _ in conversao()}
        for letra, nome in FONTES.items():
            codigos = codigos_da_fonte(nome)
            self.assertGreaterEqual(len(codigos), 9, nome)
            for c in codigos:
                self.assertIn((letra, c), conv, f"{letra}:{c} sem conversão")

    def test_codigos_s13_tem_prefixo_unico_e_a_colisao_do_cmp_foi_separada(self):
        destinos = [s for _, _, s in conversao() if re.fullmatch(r"[LPM]-[A-Z]{3}", s)]
        self.assertTrue(destinos)
        catalogo = set(re.findall(r"\b([LPM]-[A-Z]{3})\b", DOC.split("## Requisitos", 1)[1].split("### Conversão", 1)[0]))
        self.assertEqual(len(catalogo), 28)  # 9 de aprendizagem, 17 de item, 2 meta
        self.assertTrue(set(destinos) <= catalogo)
        cmp = {f: s for f, c, s in conversao() if c == "CMP"}
        self.assertEqual(cmp, {"A": "P-CPT", "I": "L-COM"})

    def test_assistencia_h0_a_h5_e_so_h0_e_independente(self):
        for h in ("H0", "H1", "H2", "H3", "H4", "H5"):
            self.assertIn(h, DOC)
        for trecho in ("só h0 conta como recuperação independente", "não registrada é \"desconhecido\"", "nunca h0", "confirmada pelo proprietário", "h1 e h2 contam como guiadas"):
            self.assertIn(trecho, TEXTO)

    def test_retencao_exige_dias_diferentes_e_transferencia_item_novo(self):
        for trecho in ("em dias diferentes", "mesma sessão não contam", "item novo", "não declarável", "fecham por padrão"):
            self.assertIn(trecho, TEXTO)

    def test_coach_com_modulo_prova_sem_agente_novo_e_sem_orquestrador_llm(self):
        for trecho in ("dois módulos", "não existe orquestrador-llm", "o tutor é o único produtor", "registrar_resultado"):
            self.assertIn(trecho, TEXTO)
        self.assertEqual(sorted(p.name for p in (ROOT / "agents").glob("*.md")), ["COACH.md", "README.md", "TUTOR.md", "ZAPIA.md"])
        for script in ("decision_queue", "session_route", "next_task", "study_plan", "evidence_projection", "review_provenance"):
            self.assertTrue((ROOT / "scripts" / f"{script}.py").exists(), script)

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        pesquisa = DOC.split("## Pesquisa", 1)[1].split("## Plano", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"https?://", pesquisa)), 6)
        self.assertIn("- **Lacunas:**", pesquisa)
        for trecho in ("hipótese de prática", "não li o artigo original", "proposta minha"):
            self.assertIn(trecho, pesquisa.replace("**", ""))

    def test_nao_altera_perfis_nem_start_e_flag_de_resultados_continua_falsa(self):
        # os perfis citam os canônicos como referência (21/11/2026, lote A1 da S17); o AGENTS.md (START) continua sem citá-los (T5)
        self.assertNotIn("docs/canonicos", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))
        for caminho in ("agents/TUTOR.md", "agents/COACH.md"):
            self.assertIn("dado, não instrução", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')

    def test_sem_dado_pessoal_e_item_da_fila(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        item = next(i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "S13")
        self.assertEqual(item["depends_on"], ["S2", "S3", "S12"])
        self.assertTrue((ROOT / item["deliverable"]).exists())


if __name__ == "__main__":
    unittest.main()
