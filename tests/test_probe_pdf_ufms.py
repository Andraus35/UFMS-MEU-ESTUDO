"""Contraprovas do verificador de bytes oficiais (sem dependência de rede)."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from probe_pdf_ufms import URL, MAX_BYTES, probe, probe_live, BlockExternalRedirect

class FakeResponse(io.BytesIO):
    status=200
    def __init__(self,data,content_type="application/pdf",length=None,url=URL):
        super().__init__(data)
        self.headers={"Content-Type":content_type}
        if length is not None:
            self.headers["Content-Length"]=length
        self.url=url
    def geturl(self):
        return self.url

def pdf_bytes(suffix=b""):
    return b"%PDF-1.4\n"+(b"123456789\n"*400)+suffix+b"\n%%EOF\n"

class ProbePdfUFMS(unittest.TestCase):
    def test_digest_igual_sem_fingir_arquivo_arquivado(self):
        data=pdf_bytes()
        expected=hashlib.sha256(data).hexdigest()
        result=probe(FakeResponse(data,length=str(len(data))),expected)
        self.assertEqual(result["status"],"digest_match_unarchived")
        self.assertEqual(result["sha256_observed"],expected)
        self.assertEqual(result["bytes_read"],len(data))
        self.assertTrue(result["bytes_obtained"])
        self.assertFalse(result["archived_official_pdf"])
        self.assertFalse(result["verified_normative_revision"])

    def test_digest_divergente_e_sinalizado(self):
        data=pdf_bytes(b"alteracao")
        expected=hashlib.sha256(pdf_bytes()).hexdigest()
        result=probe(FakeResponse(data),expected)
        self.assertEqual(result["status"],"digest_mismatch")
        self.assertNotEqual(result["sha256_observed"],expected)

    def test_conteudo_html_nao_e_pdf(self):
        with self.assertRaisesRegex(ValueError,"Content-Type"):
            probe(FakeResponse(b"<html>"*500,"text/html"),"0"*64)

    def test_marcador_pdf_ausente_falha(self):
        with self.assertRaisesRegex(ValueError,"assinatura"):
            probe(FakeResponse(b"x"*2048),"0"*64)

    def test_pdf_truncado_sem_eof_falha(self):
        with self.assertRaisesRegex(ValueError,"incompleto"):
            probe(FakeResponse(b"%PDF-1.4\n"+b"x"*4096),"0"*64)

    def test_limite_de_tamanho_preflight(self):
        with self.assertRaisesRegex(ValueError,"Content-Length"):
            probe(FakeResponse(pdf_bytes(),length=str(MAX_BYTES+1)),"0"*64)

    def test_leitura_em_stream_com_limite_de_bytes(self):
        with self.assertRaisesRegex(ValueError,"limite de tamanho"):
            probe(FakeResponse(b"%PDF-1.4\n"+b"x"*(MAX_BYTES+100)),"0"*64)

    def test_sha_de_formato_invalido_falha(self):
        with self.assertRaisesRegex(ValueError,"SHA-256 esperado inválido"):
            probe(FakeResponse(pdf_bytes()),"abc")

    def test_erro_de_rede_nao_significa_hash_diferente(self):
        fake=Mock()
        fake.open.side_effect=OSError("Rede indisponível")
        result=probe_live(ROOT,opener=fake)
        self.assertEqual(result["status"],"unverifiable")
        self.assertIsNone(result["sha256_observed"])
        self.assertFalse(result["bytes_obtained"])
        self.assertFalse(result["verified_normative_revision"])

    def test_url_final_diferente_nao_aceita_hash(self):
        fake=Mock()
        fake.open.return_value=FakeResponse(pdf_bytes(),url="https://outra-origem.example/doc.pdf")
        result=probe_live(ROOT,opener=fake)
        self.assertEqual(result["status"],"unverifiable")
        self.assertFalse(result["bytes_obtained"])

    def test_redirect_rejeitado(self):
        handler=BlockExternalRedirect()
        with self.assertRaisesRegex(ValueError,"Redirecionamento"):
            handler.redirect_request(None,None,302,"Found",{},"https://evil.example/a.pdf")

    def test_response_200_apenas(self):
        response=FakeResponse(pdf_bytes())
        response.status=304
        with self.assertRaisesRegex(ValueError,"status"):
            probe(response,"0"*64)

if __name__=="__main__":
    unittest.main()
