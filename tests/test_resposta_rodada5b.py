"""O registro da rodada 5b da Zapia não pode virar prova indevida, e a D-22 não pode virar autorização de leitura."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESPOSTA_RODADA5B_ZAPIA_20261115.md").read_text(encoding="utf-8")
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")


class Rodada5bTests(unittest.TestCase):
    def test_declara_autorrelato_e_nao_promove_requisito(self):
        for trecho in ("autorrelato", "não promove nenhum requisito", "NAO_EXECUTADO", "sem comprovante"):
            self.assertIn(trecho.lower(), DOC.lower(), trecho)

    def test_hash_do_arquivo_do_v4_confere(self):
        esperado = hashlib.sha256(b"arquivo-v4-ok").hexdigest()
        self.assertIn(esperado, DOC)
        self.assertEqual(len(b"arquivo-v4-ok"), 13)

    def test_limites_do_cron_batem_com_a_conta(self):
        self.assertEqual(1440 // 15, 96)   # 15 min: 96 execuções por dia
        self.assertEqual(1440 // 32, 45)   # 32 por dia: intervalo mínimo de 45 min
        for trecho in ("96 execuções", "32", "45 minutos", "900 s"):
            self.assertIn(trecho, DOC)

    def test_sem_dado_pessoal_nem_credencial(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")

    def test_v6_e_v9_nao_aparecem_como_aprovados(self):
        texto = DOC.replace("*", "").lower()
        self.assertIn("recusado pelo agendador", texto)
        self.assertIn("bloqueado", texto)
        self.assertIn("inexistente", texto)

    def test_d22_dispensa_consulta_sem_autorizar_leitura(self):
        d22 = next(l for l in PRODUCT.splitlines() if l.startswith("- **D-22"))
        for trecho in ("dispensa a consulta ao suporte do TEC", "relato, não verificado", "Não implementa nem autoriza leitura",
                       "D-14", "D-15", "PR-017", "aprovação expressa"):
            self.assertIn(trecho, d22)

    def test_documentos_que_dependiam_da_consulta_foram_ajustados(self):
        for caminho in ("docs/PLATFORMS.md", "docs/especificacoes/S4_OPERACAO.md", "memory/HANDOFF.md"):
            texto = (ROOT / caminho).read_text(encoding="utf-8")
            self.assertIn("D-22", texto, caminho)
        plataformas = (ROOT / "docs" / "PLATFORMS.md").read_text(encoding="utf-8")
        self.assertNotIn("exige consulta ao suporte do TEC (OPEN-12) e aprovação do proprietário", plataformas)


if __name__ == "__main__":
    unittest.main()
