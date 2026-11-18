"""Contrato da E1: emenda do PRODUCT.md. Decisões D-25 a D-27, emendas marcadas, nada perdido, orçamento de bytes fixado."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
ARQUIVO = (ROOT / "docs" / "governanca" / "ARQUIVO_PRODUCT_EVIDENCIAS_E01_E12_20261118.md").read_text(encoding="utf-8")
REGISTRO = (ROOT / "docs" / "governanca" / "E1_EMENDA_PRODUCT_20261118.md").read_text(encoding="utf-8")
ORCAMENTO_BYTES = 38 * 1024


def bullet(texto, ident):
    m = re.search(rf"^- \*\*{re.escape(ident)}\b.*$", texto, re.M)
    assert m, ident
    return m.group(0)


class EmendaProductTests(unittest.TestCase):
    def test_orcamento_de_bytes_do_product_md_fixado(self):
        self.assertLessEqual(len(PRODUCT.encode("utf-8")), ORCAMENTO_BYTES)

    def test_decisoes_novas_d25_d26_d27(self):
        d25 = bullet(PRODUCT, "D-25").lower()
        for t in ("sessões do app claude na nuvem", "origem do comando não é provada", "único escritor", "ufms-meu-estudo-entrada",
                  "ufms-meu-estudo-dados", "novo evento", "flag", "false", "emenda a d-02", "substitui a d-18"):
            self.assertIn(t, d25, t)
        d26 = bullet(PRODUCT, "D-26").lower()
        for t in ("só pela zapia, como ponte", "open-10", "emenda a d-12", "enviar_prompt_notebook", "não há mcp"):
            self.assertIn(t, d26, t)
        d27 = bullet(PRODUCT, "D-27").lower()
        for t in ("mantém o aceite do risco do d-14", "sem condição nova", "item 8.1", "não verificado", "s9-r8", "s9-r9", "qconcursos"):
            self.assertIn(t, d27, t)

    def test_decisoes_antigas_marcadas_como_emendadas_sem_perder_o_texto(self):
        self.assertIn("emendada pela D-25", bullet(PRODUCT, "D-02"))
        self.assertIn("superada pela D-25", bullet(PRODUCT, "D-18"))
        self.assertIn("emendado pela D-26", bullet(PRODUCT, "D-12"))
        self.assertIn("grava os resultados desde o início", bullet(PRODUCT, "D-02"))
        self.assertIn("rodam no computador do proprietário", bullet(PRODUCT, "D-18"))
        self.assertIn("O Tutor deve acessar o NotebookLM diretamente", bullet(PRODUCT, "D-12"))

    def test_open_09_e_10_atualizados(self):
        self.assertIn("nuvem", bullet(PRODUCT, "OPEN-09"))
        self.assertIn("não é provada", bullet(PRODUCT, "OPEN-09"))
        self.assertIn("resolvido pela D-26", bullet(PRODUCT, "OPEN-10"))

    def test_fluxo_e_requisitos_alinhados_a_d25_e_d26(self):
        self.assertIn("o fluxo de Actions grava", bullet(PRODUCT, "F6"))
        self.assertIn("(D-25)", bullet(PRODUCT, "PR-003"))
        pr12 = bullet(PRODUCT, "PR-012")
        self.assertIn("pela Zapia (D-26)", pr12)
        self.assertNotIn("caminho direto", pr12)
        self.assertNotIn("o Tutor deve acessar o notebooklm diretamente", PRODUCT.replace("O Tutor deve", "o Tutor deve").lower().split("- **d-12", 1)[0])

    def test_nenhum_id_se_perdeu_e_as_evidencias_continuam_definidas(self):
        for i in [f"E-{n:02d}" for n in range(1, 13)]:
            self.assertRegex(PRODUCT, rf"(?m)^- \*\*{i} ", i)
        for i in [f"D-{n:02d}" for n in range(1, 28)]:
            self.assertRegex(PRODUCT, rf"(?m)^- \*\*{i} ", i)
        for i in [f"OPEN-{n:02d}" for n in (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12)]:
            self.assertRegex(PRODUCT, rf"(?m)^- \*\*{i}:", i)

    def test_arquivo_guarda_o_texto_integral_das_doze_evidencias(self):
        for n in range(1, 13):
            ident = f"E-{n:02d}"
            linha = bullet(ARQUIVO, ident)
            self.assertGreater(len(linha), 120, ident)
        self.assertIn("https://www.tecconcursos.com.br/termos-de-uso", ARQUIVO)  # E-12 com seus links
        self.assertIn("Bloomsbury", ARQUIVO)  # E-08
        self.assertIn("36 meses", ARQUIVO)  # E-09
        self.assertIn("sem alteração", ARQUIVO.lower())

    def test_product_aponta_para_o_arquivo_e_mantem_resumo_curto(self):
        self.assertIn("ARQUIVO_PRODUCT_EVIDENCIAS_E01_E12_20261118.md", PRODUCT)
        for n in range(1, 13):
            linha = bullet(PRODUCT, f"E-{n:02d}")
            self.assertLess(len(linha), 330, f"E-{n:02d} voltou a crescer")

    def test_registro_diz_proposta_nao_aprovada_e_o_que_fica_de_fora(self):
        t = REGISTRO.lower().replace("**", "").replace("`", "")
        for trecho in ("proposta aguardando a aprovação do proprietário", "pedido explícito dele", "74 bytes", "nada foi apagado",
                       "não altera agents.md", "s5 nem a s4-r2", "segue sem resposta", "não aprova a ordem de caminhos", "consentimento v4"):
            self.assertIn(trecho, t, trecho)
        self.assertNotRegex(REGISTRO, r"\bPR\s*#\d+")  # estado do ciclo não mora aqui
        self.assertNotRegex(REGISTRO, r"\b[0-9a-f]{40}\b")

    def test_nao_toca_contratos_nem_habilita_escrita(self):
        cfg = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(cfg["storage"]["personal_results_writes_enabled"], False)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", PRODUCT + ARQUIVO + REGISTRO))
        self.assertNotRegex(PRODUCT + ARQUIVO + REGISTRO, r"ghp_|github_pat_[A-Za-z0-9_]{10}|Bearer\s")


if __name__ == "__main__":
    unittest.main()
