"""Contraprovas do registro de proveniência: integridade, anomalia e falha segura."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_fontes_oficiais import validate, _official_url

class FontesOficiaisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(
            (ROOT/"edital/fontes_oficiais.json").read_text(encoding="utf-8"))

    def _mutate(self,change):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"edital").mkdir()
            (root/"edital/manifest.json").symlink_to(ROOT/"edital/manifest.json")
            (root/"EDITAL_UFMS_152_2026.md").symlink_to(
                ROOT/"EDITAL_UFMS_152_2026.md")
            data=copy.deepcopy(self.registry)
            change(data)
            (root/"edital/fontes_oficiais.json").write_text(
                json.dumps(data,ensure_ascii=False),encoding="utf-8")
            return validate(root)

    def test_fonte_original_e_alerta_presentes(self):
        obs,amendments,alerts=validate(ROOT)
        self.assertEqual((obs,amendments,alerts),(1,0,1))
        self.assertEqual(self.registry["open_alerts"][0]["appeal_date_text"],
                         "11 e 12/01/2027")
        self.assertEqual(self.registry["open_alerts"][0]["result_date_text"],
                         "10/02/2027")
        self.assertFalse(self.registry["amendment_policy"]["auto_apply"])

    def test_nao_confunde_documento_local_com_remoto(self):
        rec=self.registry["publication_observations"][0]
        self.assertEqual(rec["remote_pdf_equivalence"],"unverified")
        self.assertIsNone(rec["download_bytes_sha256"])
        self.assertFalse(rec["verified_amendment_found"])

    def test_proibe_importacao_automatica(self):
        with self.assertRaisesRegex(ValueError,"automática"):
            self._mutate(lambda d:d["amendment_policy"].__setitem__(
                "auto_apply",True))

    def test_mudanca_do_hash_original_falha(self):
        with self.assertRaisesRegex(ValueError,"SHA-256 original"):
            self._mutate(lambda d:d["canonical"].__setitem__(
                "original_pdf_sha256","0"*64))

    def test_datas_e_alerta_nao_podem_ser_corrigidos_sem_fonte(self):
        with self.assertRaisesRegex(ValueError,"Data de recurso"):
            self._mutate(lambda d:d["open_alerts"][0].__setitem__(
                "appeal_date_text","11 e 12/02/2027"))
        with self.assertRaisesRegex(ValueError,"Alerta encerrado"):
            def resolved(d):
                d["open_alerts"][0]["status"]="resolved"
                d["open_alerts"][0]["resolution_document_id"]="RET-001"
            self._mutate(resolved)

    def test_equivalencia_remota_sem_bytes_e_rejeitada(self):
        with self.assertRaisesRegex(ValueError,"sem hash exato"):
            self._mutate(lambda d:d["publication_observations"][0].__setitem__(
                "remote_pdf_equivalence","verified"))

    def test_publicacao_referencia_dominios_permitidos(self):
        self.assertTrue(_official_url(
            "https://portal.concurso.fundacaofapec.org.br/edital/ver/22"))
        self.assertTrue(_official_url("https://boletimoficial.ufms.br/"))
        self.assertFalse(_official_url("http://portal.concurso.fundacaofapec.org.br/"))
        self.assertFalse(_official_url("https://boletimoficial.ufms.br.evil.example/"))
        self.assertFalse(_official_url("https://example.org/retificacao.pdf"))

    def test_retirar_alerta_nao_elimina_pendencia(self):
        with self.assertRaisesRegex(ValueError,"Alerta cronológico"):
            self._mutate(lambda d:d.__setitem__("open_alerts",[]))

    def test_retirar_restricao_de_cobertura_falha(self):
        with self.assertRaisesRegex(ValueError,"exaustiva"):
            self._mutate(lambda d:d["last_check"].__setitem__("exhaustive",True))

if __name__=="__main__":
    unittest.main()
