"""Trava de regressão: as restrições de acesso da Zapia retiradas em 21/11/2026 não voltam ao repositório."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# padrões montados por partes, para este arquivo não casar com eles
PADROES = (
    re.compile(r"[Tt]ermos? [Dd]e " + r"[Uu]so"),
    re.compile(r"item " + r"8\.1\b"),
    re.compile(r"termos_tec" + r"_registrados"),
    re.compile(r"TERMOS_TEC" + r"_NAO_REGISTRADOS"),
    re.compile(r"REGISTRO_TERMOS" + r"_TEC"),
    re.compile(r"aceite do " + r"risco do D-14"),
)
EXCLUIR_DIRS = {".git", ".specs", "__pycache__", "node_modules"}
EXCLUIR_ARQUIVOS = {"EDITAL_UFMS_152_2026.md", "test_sem_restricoes_de_acesso.py"}  # o edital da UFMS tem o texto oficial do site de inscrição


class SemRestricoesDeAcessoTests(unittest.TestCase):
    def test_nenhuma_mencao_ou_trava_de_acesso_retirada_volta(self):
        achados = []
        for caminho in ROOT.rglob("*"):
            if not caminho.is_file() or caminho.name in EXCLUIR_ARQUIVOS:
                continue
            partes = caminho.relative_to(ROOT).parts
            if set(partes) & EXCLUIR_DIRS or partes[:2] == ("edital", "chunks"):
                continue
            try:
                texto = caminho.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for padrao in PADROES:
                if padrao.search(texto):
                    achados.append((str(caminho.relative_to(ROOT)), padrao.pattern))
        self.assertEqual(achados, [])

    def test_guarda_da_plataforma_continua_liberada_e_sem_cotas(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import platform_read_guard as g
        self.assertEqual(g.PADRAO.habilitadas, frozenset({"tec", "qconcursos"}))
        for nome in ("INTERVALO_MIN_S", "PAGINAS_MAX", "SESSOES_POR_DIA"):
            self.assertFalse(hasattr(g, nome), nome)


if __name__ == "__main__":
    unittest.main()
