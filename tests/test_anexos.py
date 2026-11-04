"""Contraprovas da separação jurídica entre os Anexos III, IV e V."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from search_edital import search, search_anexo, search_programa, load

class AnnexSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((ROOT/"edital/topic_index.json").read_text(encoding="utf-8"))
        cls.manifest=json.loads((ROOT/"edital/manifest.json").read_text(encoding="utf-8"))
        cls.cases=json.loads((ROOT/"tests/fixtures/annex_cases.json").read_text(encoding="utf-8"))["cases"]
        cls.chunks={x["id"]:x for x in load(ROOT)}

    def test_21_contraprovacoes_de_roteamento(self):
        for c in self.cases:
            with self.subTest(query=c["query"]):
                if c["kind"]=="conflict":
                    with self.assertRaisesRegex(ValueError,"mistura"):
                        search(c["query"],root=ROOT,full=True)
                    continue
                hits=search(c["query"],root=ROOT,full=True)
                self.assertEqual(len(hits),1)
                hit=hits[0]
                self.assertEqual(hit["cargo"],c["cargo"])
                self.assertEqual(hit["annex"],c["annex"])
                self.assertEqual(hit["source_sha"],self.manifest["source_git_blob_sha"])
                if c["annex"]=="III":
                    self.assertEqual(hit["route"],"quadro_vagas_derived_verified_anchors")
                    self.assertEqual(hit["page"],15 if c["cargo"]=="523" else 18)
                    self.assertIn("text",hit)
                    self.assertIn("qualification", " ".join(
                        x["field"] for x in hit["field_evidence"]))
                elif c["annex"]=="IV":
                    self.assertEqual(hit["route"],"anexo_iv_atribuicoes_literal")
                    self.assertEqual(hit["page"],23 if c["cargo"]=="523" else 28)
                    self.assertIn("text",hit)
                else:
                    self.assertEqual(hit["route"],"anexo_v_programa_literal")
                    self.assertEqual(hit["area"],c["area"])
                    total=14 if c["cargo"]=="523" else 13
                    count=4 if c["area"]=="gerais" else (
                        total-4 if c["area"]=="especificos" else total)
                    self.assertEqual(hit["num_topics"],count)

    def test_seletor_explicito_seis_fontes(self):
        for cargo in ("523","324"):
            for annex in ("III","IV","V"):
                with self.subTest(cargo=cargo,annex=annex):
                    found=search("",cargo=cargo,anexo=annex,root=ROOT,full=True)
                    self.assertEqual(len(found),1)
                    self.assertEqual(found[0]["cargo"],cargo)
                    self.assertEqual(found[0]["annex"],annex)
                    self.assertEqual(found[0]["source_sha"],
                                     self.manifest["source_git_blob_sha"])

    def test_programa_inteiro_e_referencias_literais(self):
        for cargo,quantity,pages in (("523",14,{29,35,36}),("324",13,{29,45})):
            with self.subTest(cargo=cargo):
                data=search_programa(cargo,ROOT,full=True)
                self.assertEqual(data["num_topics"],quantity)
                self.assertEqual(len({t["topic_id"] for t in data["topics"]}),quantity)
                self.assertEqual({t["area"] for t in data["topics"]},
                                 {"gerais","especificos"})
                self.assertEqual({loc["page"] for topic in data["topics"]
                                  for loc in topic["locations"]},pages)
                self.assertEqual(sum(t["area"]=="gerais" for t in data["topics"]),4)
                for topic in data["topics"]:
                    self.assertTrue(topic["topic_id"].startswith(("GER-",cargo+"-")))
                    for loc in topic["locations"]:
                        chunk=self.chunks[loc["chunk_id"]]
                        a,b=loc["chunk_char_start"],loc["chunk_char_end"]
                        self.assertEqual(chunk["body"][a:b],loc["text"])
                        self.assertEqual(loc["page_char_start"],chunk["char_start"]+a)
                        self.assertEqual(loc["page_char_end"],chunk["char_start"]+b)
                        self.assertLess(len(loc["excerpt"]),181)

    def test_areas_nao_omitem_nem_misturam_disciplinas(self):
        for cargo,specific_count in (("523",10),("324",9)):
            common=search_programa(cargo,ROOT,area="gerais")
            specific=search_programa(cargo,ROOT,area="especificos")
            self.assertEqual(common["num_topics"],4)
            self.assertEqual(specific["num_topics"],specific_count)
            self.assertTrue(all(t["area"]=="gerais" for t in common["topics"]))
            self.assertTrue(all(t["area"]=="especificos" for t in specific["topics"]))
            self.assertTrue(all(t["topic_id"].startswith(cargo+"-")
                                for t in specific["topics"]))
            self.assertFalse({t["topic_id"] for t in common["topics"]}.intersection(
                             {t["topic_id"] for t in specific["topics"]}))

    def test_conflitos_de_filtros_falham_seguro(self):
        with self.assertRaisesRegex(ValueError,"Informe --cargo"):
            search("",anexo="III",root=ROOT)
        with self.assertRaisesRegex(ValueError,"somente para Anexo V"):
            search("",anexo="IV",cargo="523",area="especificos",root=ROOT)
        with self.assertRaisesRegex(ValueError,"incompatível"):
            search("",anexo="III",cargo="523",topic="523-01",root=ROOT)
        with self.assertRaisesRegex(ValueError,"separadamente"):
            search("",anexo="V",cargo="523",topic="523-01",root=ROOT)
        with self.assertRaisesRegex(ValueError,"Cargo da consulta contradiz"):
            search("Anexo III do cargo 523",cargo="324",root=ROOT)
        with self.assertRaisesRegex(ValueError,"Cargo não indexado"):
            search_anexo("524","III",root=ROOT)
        with self.assertRaisesRegex(ValueError,"sem consulta textual"):
            search("Anexo IV do cargo 523",cargo="523",anexo="III",root=ROOT)

    def test_conteudo_nao_e_atribuicao_nem_escolaridade(self):
        for cargo in ("523","324"):
            specific=search_programa(cargo,ROOT,full=True,area="especificos")
            entire="\n".join(loc["text"] for t in specific["topics"]
                             for loc in t["locations"])
            self.assertNotIn("Ensino Médio completo",entire)
            self.assertNotIn("29          Campo Grande",entire)
            self.assertNotIn("Planejar, desenvolver, executar, acompanhar e avaliar atividades, programas, projetos e processos relacionados à gestão pública",entire)

    def test_economia_default_sem_textos_extensos(self):
        for cargo in ("523","324"):
            out=search_programa(cargo,ROOT,full=False)
            self.assertTrue(out["topics"])
            self.assertTrue(all("text" not in loc for t in out["topics"]
                                for loc in t["locations"]))
            self.assertTrue(all("excerpt" in loc for t in out["topics"]
                                for loc in t["locations"]))

if __name__=="__main__":
    unittest.main()
