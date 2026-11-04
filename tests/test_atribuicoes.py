"""Contraprovas de atribuições do Anexo IV: limites, proveniência e isolamento."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from index_atribuicoes import build, locate, validate
from search_edital import load, search, search_atribuicao

class AtribuicoesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((ROOT/"edital/atribuicoes_index.json").read_text(encoding="utf-8"))
        cls.chunks={c["id"]:c for c in load(ROOT)}

    def test_identidade_e_indice_reconstrutivel(self):
        self.assertEqual(validate(ROOT),2)
        self.assertEqual(build(ROOT),self.index)
        self.assertEqual(self.index["annex"],"IV")
        self.assertEqual(self.index["classification"],"derived_non_normative")
        manifest=json.loads((ROOT/"edital/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(self.index["source_git_blob_sha"],manifest["source_git_blob_sha"])
        self.assertEqual(self.index["source_pdf_sha256"],manifest["source_pdf_sha256"])

    def test_offets_hash_e_texto_literal(self):
        for entry in self.index["entries"]:
            with self.subTest(cargo=entry["cargo"]):
                chunk=self.chunks[entry["chunk_id"]]
                literal=locate(entry,chunk)
                a,b=entry["chunk_char_start"],entry["chunk_char_end"]
                self.assertEqual(chunk["body"][a:b],literal["text"])
                self.assertEqual(entry["page_char_start"],chunk["char_start"]+a)
                self.assertEqual(entry["page_char_end"],chunk["char_start"]+b)
                self.assertEqual(entry["characters"],len(literal["text"]))
                self.assertEqual(entry["literal_sha256"],hashlib.sha256(
                    literal["text"].encode("utf-8")).hexdigest())
                self.assertTrue(literal["text"].lstrip().startswith(entry["heading"]))
                self.assertIn(entry["first_text"],literal["text"])
                self.assertTrue(literal["text"].endswith(entry["last_text"]))

    def test_recuperacao_523_sem_campus_producao_cultural_ou_endodontia(self):
        data=search_atribuicao("523",ROOT,full=True)
        self.assertEqual((data["page"],data["chunk_id"]),(23,"p23-c01"))
        self.assertIn("governança",data["text"])
        self.assertIn("gestão de riscos",data["text"])
        self.assertNotIn("(Campus)",data["text"])
        self.assertNotIn("Produção Cultural",data["text"])
        self.assertNotIn("Endodontia",data["text"])

    def test_recuperacao_324_sem_veterinaria_ou_ti(self):
        data=search_atribuicao("324",ROOT,full=True)
        self.assertEqual((data["page"],data["chunk_id"]),(28,"p28-c02"))
        self.assertIn("secretarias acadêmicas",data["text"])
        self.assertIn("assistência estudantil",data["text"])
        self.assertNotIn("hospital veterinário",data["text"])
        self.assertNotIn("Tecnologia da Informação",data["text"])
        self.assertNotIn("Edital 6775306",data["text"])

    def test_roteamento_por_intencao_sem_misturar_anexos(self):
        for cargo in ("523","324"):
            with self.subTest(cargo=cargo):
                hits=search("Quais as atribuições do cargo "+cargo+"?",root=ROOT,full=True)
                self.assertEqual(len(hits),1)
                self.assertEqual(hits[0]["route"],"anexo_iv_atribuicoes_literal")
                self.assertEqual(hits[0]["cargo"],cargo)
                self.assertEqual(hits[0]["source_sha"],self.index["source_git_blob_sha"])
        with self.assertRaisesRegex(ValueError,"mistura atribuições e requisitos"):
            search("Quais as atribuições e requisitos do cargo 523?",root=ROOT)
        with self.assertRaisesRegex(ValueError,"não indexado"):
            search_atribuicao("524",ROOT)

    def test_busca_lexical_com_cargo_isola_anexo_iv(self):
        for cargo,expected_page,excluded in (
            ("523",23,"Produção Cultural"),
            ("324",28,"hospital veterinário"),
        ):
            with self.subTest(cargo=cargo):
                hits=search("gestão apoio atividades institucionais",cargo=cargo,
                            root=ROOT,full=True,limit=15)
                for hit in hits:
                    if hit["page"]==expected_page:
                        self.assertNotIn(excluded,hit.get("text",""))
                for hit in hits:
                    if 20<=hit["page"]<=28:
                        self.assertEqual(hit["page"],expected_page)
        # Especialidade vizinha não pode aparecer nas páginas do Anexo IV.
        hits=search("atendimento veterinário experimentos biológicos",cargo="324",
                    root=ROOT,full=True)
        self.assertFalse(any(20<=h["page"]<=28 and
                             "hospital veterinário" in h.get("text","") for h in hits))

    def test_mutacao_de_offsets_detectada(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"edital").mkdir()
            (root/"EDITAL_UFMS_152_2026.md").symlink_to(ROOT/"EDITAL_UFMS_152_2026.md")
            (root/"edital/manifest.json").symlink_to(ROOT/"edital/manifest.json")
            (root/"edital/chunks").symlink_to(ROOT/"edital/chunks",target_is_directory=True)
            bad=copy.deepcopy(self.index)
            bad["entries"][0]["chunk_char_start"]+=1
            (root/"edital/atribuicoes_index.json").write_text(
                json.dumps(bad,ensure_ascii=False),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Índice de atribuições divergente"):
                validate(root)

    def test_recorte_economico(self):
        whole=(ROOT/"EDITAL_UFMS_152_2026.md").read_text(encoding="utf-8")
        for cargo in ("523","324"):
            text=search_atribuicao(cargo,ROOT,full=True)["text"]
            self.assertLess(len(text),len(whole)//100)

if __name__=="__main__":
    unittest.main()
