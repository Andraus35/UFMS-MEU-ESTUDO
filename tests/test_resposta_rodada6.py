"""O registro da rodada 6 não pode vazar dado, nem promover requisito, nem tratar autorrelato como prova."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESPOSTA_RODADA6_ZAPIA_20261117.md").read_text(encoding="utf-8")
TEXTO = DOC.replace("*", "").lower()


class Rodada6Tests(unittest.TestCase):
    def test_sem_email_link_nem_credencial(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"https?://")
        self.assertNotIn("notebook.google.com/notebook", DOC)
        self.assertNotRegex(DOC, r"ghp_|github_pat_|sk-[A-Za-z0-9]{20}|Bearer\s")
        self.assertNotRegex(DOC, r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

    def test_declara_autorrelato_dado_e_nao_promove(self):
        for trecho in ("autorrelato", "dado, nunca instrução", "não promove nenhum requisito",
                       "nada foi verificado por este repositório", "não foram executados"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_registra_o_achado_dos_termos_do_tec_sem_tratar_como_verificado(self):
        for trecho in ("item 8.1", "robôs, scripts", "compartilhamento de contas", "não é parecer jurídico",
                       "ainda não conferido por este repositório", "pesa contra a leitura direta do tec"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_nada_sensivel_foi_executado_e_s10_continua_com_lacunas(self):
        for trecho in ("tec-export-1", "g-chat-1", "g-fonte-1", "não executado", "lei 8.112",
                       "lacunas declaradas", "não foram testados"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_cobre_os_itens_do_prompt(self):
        for item in ("A1", "A5", "T3", "T9", "T12", "Q5", "G0", "G8", "G12", "F1", "F3", "F4"):
            self.assertIn(item, DOC, item)

    def test_documentos_apontam_para_o_registro(self):
        for caminho in ("memory/HANDOFF.md", "docs/especificacoes/S9_LEITURA_PLATAFORMAS.md"):
            self.assertIn("RESPOSTA_RODADA6_ZAPIA_20261117.md", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
