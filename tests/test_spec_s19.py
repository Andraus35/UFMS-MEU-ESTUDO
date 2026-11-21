"""Contrato da S19: a Zapia como interface (rotina agendada e hook). Especificação; não cadastra nada nem altera agents/."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S19_ZAPIA_INTERFACE_AGENDAMENTOS_GATILHOS.md").read_text(encoding="utf-8")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Mapa", 1)[0]
MAPA = DOC.split("## Mapa", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]


def req(n):
    return REQUISITOS.split(f"S19-R{n} ", 1)[1].split("| S19-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS19Tests(unittest.TestCase):
    def test_secoes_na_ordem(self):
        pos = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Mapa", "## Requisitos", "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(pos, sorted(pos))

    def test_requisitos_r1_a_r12_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S19-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S19-R\d+) ", l).group(1) for l in linhas], [f"S19-R{i}" for i in range(1, 13)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3)

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 4)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)
        self.assertIn("- **Lacunas:**", PESQUISA)
        for t in ("pdf da zapia", "não achei", "não testei", "nada foi implantado", "hook"):
            self.assertIn(t, PESQUISA.lower().replace("**", ""), t)

    def test_mapa_aponta_para_as_fontes_sem_duplicar(self):
        for fonte in ("S5", "S6", "S8", "S15", "S16", "E3"):
            self.assertIn(fonte, MAPA, fonte)
        linhas = [l for l in MAPA.splitlines() if l.startswith("| ") and not l.startswith("| ---")]
        for l in linhas[1:]:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 4)
        self.assertIn("Iniciar estudos", MAPA)
        self.assertIn("finalizar estudos", MAPA)

    def test_zapia_executa_nao_decide_e_limites_do_recurso(self):
        for t in ("interface", "não decide", "não redige"):
            self.assertIn(t, req(1).replace("não decisora", "não decide"), t)
        for t in ("só vale no turno em que chega", "processo permanente", "whatsapp não está conectado", "não está provada"):
            self.assertIn(t, req(2), t)

    def test_nada_e_cadastrado_e_fronteira_de_dado(self):
        for t in ("autorizo", "sem efeito", "não cadastra nada"):
            self.assertIn(t, req(4), t)
        for t in ("dado, nunca instrução", "recibo do fluxo", "verificador de entrega"):
            self.assertIn(t, req(5), t)
        for t in ("fora do turno", "repetida", "alterada", "externo", "não duplica"):
            self.assertIn(t, req(6), t)

    def test_frequencia_falha_prova_e_limites(self):
        for t in ("dependência", "habituação", "nunca aumentar", "g-mot-09"):
            self.assertIn(t, req(7), t)
        for t in ("não geram mensagem substituta", "ausência do recibo"):
            self.assertIn(t, req(8), t)
        for t in ("s15-r4", "autorrelato"):
            self.assertIn(t, req(9), t)
        for t in ("não prova", "autorrelato", "aprovação expressa"):
            self.assertIn(t, req(10), t)

    def test_sem_canal_sem_integracao_e_frase_decidida(self):
        for t in ("não herda", "canal testado", "não presume", "finalizar estudos"):
            self.assertIn(t, req(11), t)
        self.assertIn("não é hook", MAPA)
        self.assertIn("e4ee0018", PESQUISA)

    def test_estado_da_conta_e_drive_so_como_hipotese(self):
        for t in ("outlook", "envio", "sem conector de github", "hipótese", "decisão do proprietário", "s8-r6"):
            self.assertIn(t, req(12), t)
        self.assertIn("20 tarefas", PESQUISA)
        self.assertIn("prevalece o mais restritivo", PESQUISA)

    def test_nada_aplicado_e_flag_false(self):
        for perfil in ("TUTOR", "COACH"):
            self.assertNotIn("S19", (ROOT / "agents" / f"{perfil}.md").read_text(encoding="utf-8"))
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertIn("| S19 |", (ROOT / "docs/especificacoes/README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
