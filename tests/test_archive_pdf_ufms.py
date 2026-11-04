"""Testes offline de arquivamento e readback independente de PDFs."""
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
from archive_pdf_ufms import archive_response, verify_archive, evidence_dir, live, URL
from probe_pdf_ufms import MAX_BYTES

def fixture_pdf(suffix=b""):
    return b"%PDF-1.4\n" + b"Simulacao de documento\n"*200 + suffix + b"\n%%EOF\n"

class HttpResponse(io.BytesIO):
    def __init__(self,body,ctype="application/pdf",url=URL,length=None,status=200):
        super().__init__(body)
        self.status=status
        self.headers={"Content-Type":ctype}
        if length is not None:
            self.headers["Content-Length"]=str(length)
        self.url=url
    def geturl(self):
        return self.url
    def __enter__(self):
        return self
    def __exit__(self,*args):
        self.close()

class ArchiveOfficialPdfTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.pdf=fixture_pdf()
        self.sha=hashlib.sha256(self.pdf).hexdigest()

    def archive(self,data=None,expected=None,**kwargs):
        return archive_response(HttpResponse(data if data is not None else self.pdf,**kwargs),
                                expected or self.sha,self.folder)

    def test_arquivo_e_recibo_imutaveis_apos_gravacao(self):
        item=self.archive()
        self.assertEqual(item["status"],"archived_digest_match")
        self.assertEqual(item["sha256"],self.sha)
        receipt=verify_archive(item["receipt_path"])
        self.assertEqual(receipt["sha256_remote_bytes"],self.sha)
        self.assertEqual(receipt["bytes_read"],len(self.pdf))
        self.assertTrue(receipt["archived_pdf_bytes"])
        self.assertFalse(receipt["archived_official_pdf"])
        self.assertFalse(receipt["normative_revision_verified"])
        self.assertEqual(receipt["acquisition"],"offline_fixture")
        self.assertEqual(Path(item["pdf_path"]).read_bytes(),self.pdf)

    def test_hash_divergente_fica_arquivado_com_alerta(self):
        item=self.archive(data=fixture_pdf(b"versao diferente"))
        self.assertEqual(item["status"],"archived_digest_mismatch")
        d=verify_archive(item["receipt_path"])
        self.assertEqual(d["comparison_status"],"digest_mismatch")
        self.assertFalse(d["normative_revision_verified"])

    def test_arquivo_existente_nao_e_sobrescrito(self):
        item=self.archive()
        with self.assertRaises(FileExistsError):
            self.archive()
        self.assertEqual(Path(item["pdf_path"]).read_bytes(),self.pdf)
        self.assertEqual(len(list(self.folder.iterdir())),2)

    def test_adulteracao_dos_bytes_falha_no_readback(self):
        item=self.archive()
        Path(item["pdf_path"]).write_bytes(fixture_pdf(b"mutacao"))
        with self.assertRaisesRegex(ValueError,"adulterado"):
            verify_archive(item["receipt_path"])

    def test_adulteracao_da_metadata_falha(self):
        item=self.archive()
        path=Path(item["receipt_path"])
        data=json.loads(path.read_text(encoding="utf-8"))
        data["comparison_status"]="digest_mismatch"
        path.write_text(json.dumps(data),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"inconsistente"):
            verify_archive(path)

    def test_proveniencia_falsamente_promovida_falha(self):
        item=self.archive()
        path=Path(item["receipt_path"])
        data=json.loads(path.read_text(encoding="utf-8"))
        data["archived_official_pdf"]=True
        path.write_text(json.dumps(data),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"inconsistente"):
            verify_archive(path)

    def test_tipo_html_recusado_sem_arquivo(self):
        with self.assertRaisesRegex(ValueError,"Content-Type"):
            self.archive(data=b"<html>blocked</html>"*100,ctype="text/html")
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_pdf_sem_eof_recusado_e_temp_removido(self):
        with self.assertRaisesRegex(ValueError,"incompleto"):
            self.archive(data=b"%PDF-1.4\n"+b"x"*2048)
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_tamanho_declarado_excessivo_falha(self):
        with self.assertRaisesRegex(ValueError,"Content-Length"):
            self.archive(length=MAX_BYTES+1)
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_caminho_relativo_e_recusado(self):
        with self.assertRaisesRegex(ValueError,"absoluto"):
            evidence_dir("evidencias-relativas")

    def test_symlink_do_destino_e_recusado(self):
        shortcut=self.folder.parent/(self.folder.name+"-link")
        shortcut.symlink_to(self.folder,target_is_directory=True)
        self.addCleanup(lambda:shortcut.unlink(missing_ok=True))
        with self.assertRaisesRegex(ValueError,"symlink"):
            evidence_dir(shortcut)

    def test_evidencia_dentro_repo_e_recusada(self):
        with self.assertRaisesRegex(ValueError,"árvore do repositório"):
            evidence_dir(ROOT)

    def test_observacao_https_direta_registra_modo_sem_adocao(self):
        expected=json.loads((ROOT/"edital/manifest.json").read_text(encoding="utf-8"))["source_pdf_sha256"]
        result=archive_response(HttpResponse(self.pdf),expected,self.folder,acquisition="direct_https")
        item=verify_archive(result["receipt_path"])
        self.assertTrue(item["archived_official_pdf"])
        self.assertFalse(item["normative_revision_verified"])
        self.assertEqual(item["comparison_status"],"digest_mismatch")

    def test_redirect_resulta_em_inconclusao_sem_arquivos(self):
        opener=Mock()
        opener.open.return_value=HttpResponse(self.pdf,url="https://outra-pagina.example/documento.pdf")
        with self.assertRaisesRegex(ValueError,"Redirecionamento"):
            live(self.folder,opener=opener)
        self.assertEqual(list(self.folder.iterdir()),[])

    def test_pasta_documental_nao_e_criada_automaticamente(self):
        missing=self.folder/"nova"
        with self.assertRaisesRegex(ValueError,"existente"):
            self.archive_response_for_invalid_folder(missing)
        self.assertFalse(missing.exists())

    def archive_response_for_invalid_folder(self,path):
        return archive_response(HttpResponse(self.pdf),self.sha,path)

if __name__=="__main__":
    unittest.main()
