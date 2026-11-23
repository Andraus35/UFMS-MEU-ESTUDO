"""E26: emenda aditiva que exclui o AUTORIZO por mensagem das automações entre agentes, Zapia, TEC e Gemini. Texto antigo preservado, travas declaradas, limites da plataforma e o que continua exigindo frase."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E26 = ROOT / "docs" / "governanca" / "E26_EMENDA_FIM_DO_AUTORIZO_NAS_AUTOMACOES.md"
SPECS = ("S5_ZAPIA", "S6_EXECUCAO_CANAL", "S8_ROTINA_COACH", "S14_RUNTIME_OPERACIONAL", "S15_ORQUESTRACAO_FLUXO_ROTINA_TEMPO",
         "S19_ZAPIA_INTERFACE_AGENDAMENTOS_GATILHOS", "S20_AUTOMACAO_PONTA_A_PONTA_ZAPIA")


class EmendaTeste(unittest.TestCase):
    def test_o_texto_da_emenda_traz_o_que_muda_as_travas_e_os_limites(self):
        t = E26.read_text(encoding="utf-8")
        for trecho in ("emenda **aditiva**", "autorização permanente", "escopo fechado", "Caixa de comandos", "Recibo de mesmo hash", "Teste sem efeito antes",
                       "Parada", "leitura de e-mail", "E-07", "flags", "consentimento v4", "janela PJ", "CAPTCHA", "Risco aceito por ele",
                       "entra em vigor com o merge", "não altera `AGENTS.md`"):
            self.assertIn(trecho.lower(), t.lower(), trecho)

    def test_cada_especificacao_tem_aviso_no_topo_e_secao_no_fim_e_preserva_o_texto_antigo(self):
        for s in SPECS:
            t = (ROOT / "docs" / "especificacoes" / f"{s}.md").read_text(encoding="utf-8")
            self.assertIn("**Emenda E26 (23/11/2026):**", t[:1500], s)
            self.assertIn("## Emenda do AUTORIZO (E26, 23/11/2026)", t, s)
            if s != "S5_ZAPIA":  # na S5 a E2 deve ser a última seção (teste da E2); a E26 vem antes dela
                self.assertTrue(t.rstrip().endswith("não é removido."), s)
            else:
                self.assertLess(t.index("## Emenda do AUTORIZO (E26"), t.index("## Emenda E2 (18/11/2026)"))
            self.assertIn("AUTORIZO", t.split("## Emenda do AUTORIZO (E26")[0], s)  # o texto antigo continua lá (aditiva)

    def test_product_md_tem_a_d29_e_mantem_o_e_mail(self):
        t = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
        self.assertIn("**D-31 (23/11/2026):**", t)
        self.assertIn("E26_EMENDA_FIM_DO_AUTORIZO_NAS_AUTOMACOES.md", t)
        self.assertIn("**Mantém** `AUTORIZO` para ler e-mail (E-07)", t)
        self.assertLessEqual(len(t.encode("utf-8")), 38 * 1024)

    def test_agents_md_nao_cita_a_frase_e_a_operacao_foi_aplicada_pelo_lote_apl(self):
        self.assertNotIn("AUTORIZO", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))  # a E26 não precisou mudar o AGENTS.md
        for rel in ("agents/ZAPIA.md", "agents/TUTOR.md", "agents/COACH.md", "scripts/command_params_schema.py", "scripts/agents_gate.py"):
            self.assertIn("agendar_rotina", (ROOT / rel).read_text(encoding="utf-8"), rel)  # ZAPIA-APL


if __name__ == "__main__":
    unittest.main()
