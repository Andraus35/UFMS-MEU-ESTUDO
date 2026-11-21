"""Contrato da S18: IMC do Coach. Especificação e texto proposto; não aplica nada em agents/."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S18_INTELIGENCIA_MOTIVACIONAL_COACH.md").read_text(encoding="utf-8")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## O Manual do Imparável", 1)[0]
MANUAL = DOC.split("## O Manual do Imparável", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Texto para `agents/COACH.md`", 1)[0]


def req(n):
    return REQUISITOS.split(f"S18-R{n} ", 1)[1].split("| S18-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS18Tests(unittest.TestCase):
    def test_secoes_na_ordem(self):
        pos = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## O Manual do Imparável", "## Requisitos", "## Texto para `agents/COACH.md`", "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(pos, sorted(pos))

    def test_requisitos_r1_a_r13_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S18-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S18-R\d+) ", l).group(1) for l in linhas], [f"S18-R{i}" for i in range(1, 14)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3)

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 6)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)
        self.assertIn("- **Lacunas:**", PESQUISA)
        for t in ("resumos", "não li", "não encontrei", "anexado depois", "nada foi implantado"):
            self.assertIn(t, PESQUISA.lower().replace("**", ""), t)

    def test_canonico_com_hash_no_manifesto(self):
        man = json.loads((ROOT / "docs/canonicos/MANIFESTO.json").read_text(encoding="utf-8"))
        d = next(x for x in man["documentos"] if x["id"] == "IMC-COACH-001")
        self.assertEqual(hashlib.sha256((ROOT / d["path"]).read_bytes()).hexdigest(), d["sha256"])
        self.assertIn(d["path"], DOC)

    def test_imc_capacidade_interna_comportamento_e_gates(self):
        for t in ("não é um quarto agente", "não é psicoterapia", "tutor"):
            self.assertIn(t, req(1), t)
        for t in ("g-mot-01 a 05", "capacidade, oportunidade, motivação, custo e bem-estar"):
            self.assertIn(t, req(2), t)
        for t in ("proposta", "escala validada", "colisão"):
            self.assertIn(t, req(3), t)

    def test_intervencoes_ciclos_e_protocolos(self):
        for t in ("imc-01 a imc-22", "indicador observável", "g-mot-19"):
            self.assertIn(t, req(4), t)
        for t in ("diário", "semanal", "fase", "reentrada", "simulado ruim", "ansiedade de prova", "sobrecarga", "g-mot-10", "s8"):
            self.assertIn(t, req(5), t)

    def test_seguranca_privacidade_e_autonomia(self):
        for t in ("g-mot-15", "g-mot-14", "risco imediato", "g-mot-11, 12"):
            self.assertIn(t, req(6), t)
        for t in ("sensível", "repositório público", "g-mot-17"):
            self.assertIn(t, req(7), t)
        for t in ("g-mot-08, 09, 16, 21", "dependência emocional"):
            self.assertIn(t, req(8), t)

    def test_eficacia_contratos_gates_e_manual(self):
        for t in ("g-mot-07", "n-of-1", "g-mot-18", "hipótese"):
            self.assertIn(t, req(9), t)
        for t in ("coach/imc → tutor", "tutor → coach", "orquestrador", "g-mot-13"):
            self.assertIn(t, req(10), t)
        for t in ("g-mot-01 a 22", "não implementados"):
            self.assertIn(t, req(11).replace("`", ""), t)
        for t in ("texto integral só no privado", "citação curta", "conferidas na fonte", "dado, não instrução"):
            self.assertIn(t, req(12), t)
        self.assertIn("só índice, página e citação curta", MANUAL)
        self.assertIn("não está no repositório público", DOC)
        idx = (ROOT / "docs/referencias/MANUAL_DO_IMPARAVEL_INDICE.md").read_text(encoding="utf-8")
        self.assertIn("52965cb8da34c301f41913fd4c2efe404e5d80af44d122c1f323ca63e09314ac", idx)
        self.assertIn("978-85-69303-55-8", idx)
        self.assertIn("não está neste repositório público", idx)
        self.assertIn("pasta privada do Drive do proprietário", idx)
        self.assertIn("sem link nem ID neste repositório", idx)
        self.assertIn("Coach não o lê", idx)
        self.assertNotRegex(idx, r"drive\.google\.com|15qMFRsz")
        self.assertFalse(list(ROOT.rglob("Manual-do-imparavel*.pdf")))

    def test_texto_aplicado_pela_b1_e_flag_false(self):
        self.assertIn("NÃO aplicado", DOC)
        coach = (ROOT / "agents/COACH.md").read_text(encoding="utf-8")
        self.assertIn("Aplicar a IMC, capacidade interna do Coach", coach)  # aplicado pela B1
        self.assertIn("INTELIGENCIA_MOTIVACIONAL_COMPORTAMENTAL_DO_COACH.md", coach)
        self.assertIn("MANUAL_DO_IMPARAVEL_INDICE.md", coach)
        self.assertIn("nunca vai ao repositório público", coach)
        self.assertNotIn("IMC-COACH-001", (ROOT / "agents/TUTOR.md").read_text(encoding="utf-8"))
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertIn("| S18 |", (ROOT / "docs/especificacoes/README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
