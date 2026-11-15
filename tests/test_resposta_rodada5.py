"""O registro da rodada 5 da Zapia não pode virar prova indevida nem carregar dado pessoal."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESPOSTA_RODADA5_ZAPIA_20261115.md").read_text(encoding="utf-8")
PROMPTS = (ROOT / "docs" / "governanca" / "PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md").read_text(encoding="utf-8")
CORPO_V7 = "UFMS-V7 teste de escrita validada 2026-11-15T05:16:43Z"


class Rodada5Tests(unittest.TestCase):
    def test_declara_autorrelato_parcial_e_limite_de_autoria(self):
        for trecho in ("autorrelato", "PARCIAL", "não distingue a Zapia do proprietário", "NAO_EXECUTADO",
                       "Google Drive", "Outlook", "não promove nenhum requisito"):
            self.assertIn(trecho.lower(), DOC.lower(), trecho)

    def test_hash_do_corpo_do_v7_confere_com_o_texto_registrado(self):
        self.assertIn(CORPO_V7, DOC)
        esperado = hashlib.sha256(CORPO_V7.encode("utf-8")).hexdigest()
        self.assertIn(esperado, DOC)

    def test_sem_dado_pessoal_nem_credencial(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")

    def test_nenhum_teste_nao_executado_aparece_como_aprovado(self):
        linha = next(l for l in DOC.splitlines() if l.startswith("| V3, V4"))
        self.assertIn("NAO_EXECUTADO", linha)

    def test_prompt_de_validacao_nao_manda_publicar_o_relatorio_na_issue(self):
        self.assertIn("NÃO publique o relatório completo na issue", PROMPTS)
        self.assertNotIn("Publique o relatório como comentário(s)", PROMPTS)


if __name__ == "__main__":
    unittest.main()
