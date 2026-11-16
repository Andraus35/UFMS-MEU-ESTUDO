"""O registro do v3 e do plano guardado não pode virar prova indevida nem vazar dado pessoal do plano."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "RESULTADO_PERSISTENCIA_V3_PLANO_20261116.md").read_text(encoding="utf-8")
TEXTO = DOC.replace("*", "").lower()


class ResultadoV3PlanoTests(unittest.TestCase):
    def test_declara_relato_e_ausencia_de_verificacao_independente(self):
        for trecho in ("relato do proprietário", "o agente construtor não viu o repositório privado",
                       "não habilita a escrita automática", "não foi visto", "por relato"):
            self.assertIn(trecho, TEXTO)

    def test_registra_o_blob_do_v3_e_o_que_ficou_pendente(self):
        self.assertIn("d1a72470ebccdc82859557d4b1e5ba16d743d25f", DOC)
        for trecho in ("token", "pendente", "p4", "open-01", "open-02", "confirmação independente"):
            self.assertIn(trecho, TEXTO)

    def test_nao_vaza_dado_do_plano_nem_dado_pessoal(self):
        for proibido in ("2026-11-20", "cb10ea15", "plano-2026"):
            self.assertNotIn(proibido, DOC)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")  # valor de token, não o prefixo
        self.assertIn("omite de propósito", TEXTO)

    def test_registra_o_resultado_do_verificador_de_token_sem_nomes_de_outros_repositorios(self):
        for trecho in ("resultado: diverge", "read-only", "falso positivo", "403", "não entregar à zapia", "16/12/2026", "30 dias", "estava errada"):
            self.assertIn(trecho, TEXTO)
        for alheio in ("inteligencia", "trading", "sot"):
            self.assertNotIn(alheio, TEXTO)
        self.assertNotIn("causa não foi vista", TEXTO)

    def test_hashes_do_start_batem_com_o_repositorio(self):
        import subprocess, sys
        saida = subprocess.run([sys.executable, "scripts/bootstrap.py", "--mode", "study"], cwd=ROOT, capture_output=True, text=True)
        hashes = json.loads(saida.stdout)["sha256_dos_arquivos"]
        # o registro cita os hashes do commit 85dbf66a; AGENTS e CURRENT não mudam com os recibos
        self.assertIn(f"AGENTS.md {hashes['AGENTS.md'][:12]}", DOC)
        self.assertIn(f"state/CURRENT.json {hashes['state/CURRENT.json'][:12]}", DOC)

    def test_documentos_apontam_para_o_registro_e_a_flag_continua_falsa(self):
        for caminho in ("memory/HANDOFF.md", "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"):
            self.assertIn("RESULTADO_PERSISTENCIA_V3_PLANO_20261116.md", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertNotIn("Enquanto o consentimento v3 não for aprovado", (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
