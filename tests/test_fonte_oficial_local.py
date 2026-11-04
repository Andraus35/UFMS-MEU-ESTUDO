"""Contrato offline: edital inicial do projeto é fonte oficial de estudo; retificações são separadas."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASH = "c758bb421ad848bf76757f6ece7a7b786e80e45123b80c3e01a13d0985f09675"
BLOB = "a4129cceabd20fc119625d71b1c1599b3ce644e1"

class FonteOficialLocalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads((ROOT / "edital/fontes_oficiais.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "edital/manifest.json").read_text(encoding="utf-8"))

    def test_identidade_imutavel_da_fonte_local(self):
        self.assertEqual(self.manifest["source_pdf_sha256"], HASH)
        self.assertEqual(self.reg["canonical"]["original_pdf_sha256"], HASH)
        self.assertEqual(self.manifest["source_git_blob_sha"], BLOB)
        self.assertEqual(self.reg["canonical"]["source_git_blob_sha"], BLOB)
        self.assertEqual(self.manifest["page_count"], 47)

    def test_fonte_oficial_primaria_esta_explicita(self):
        text = (ROOT / "docs/FONTES.md").read_text(encoding="utf-8")
        self.assertIn("Fonte oficial primária do projeto", text)
        self.assertIn("não condicionar os estudos", text.lower())
        self.assertIn(HASH, text)

    def test_retificacao_nao_substitui_documento_original(self):
        self.assertFalse(self.reg["amendment_policy"]["auto_apply"])
        self.assertEqual(self.reg["amendment_policy"]["source_preservation"], "immutable_original")
        text = (ROOT / "docs/RETIFICACOES_E_PROVENIENCIA.md").read_text(encoding="utf-8")
        self.assertIn("retificações posteriores", text)
        self.assertIn("aplicadas separadamente", text)
        self.assertIn("não requisito de início dos estudos", text)

    def test_alerta_cronologico_nao_foi_reescrito(self):
        alert = next(x for x in self.reg["open_alerts"] if x["id"] == "ALERTA-DOC-01")
        self.assertEqual(alert["result_date_text"], "10/02/2027")
        self.assertEqual(alert["appeal_date_text"], "11 e 12/01/2027")
        self.assertEqual(alert["status"], "unresolved_source_inconsistency")
        self.assertIsNone(alert["resolution_document_id"])

    def test_fonte_remota_nao_substitui_a_local(self):
        obs = self.reg["institutional_pdf_observations"][0]
        self.assertEqual(obs["remote_pdf_equivalence"], "unverified")
        self.assertIsNone(obs["pdf_bytes_sha256"])
        self.assertEqual(self.reg["verified_amendments"], [])

if __name__ == "__main__":
    unittest.main()
