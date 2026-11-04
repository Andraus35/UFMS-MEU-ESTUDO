"""Testes de reconstrução e recuperação do edital."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from chunk_edital import validate,read_pages,blob_sha
from search_edital import search,page_text

class EditalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(ROOT/'EDITAL_UFMS_152_2026.md').read_text(encoding='utf-8')
        cls.manifest=json.loads((ROOT/'edital/manifest.json').read_text(encoding='utf-8'))
    def test_integralidade(self):
        self.assertEqual(len(read_pages(self.source)),47)
        self.assertEqual(validate(ROOT),81)
    def test_hash_da_fonte(self):
        self.assertEqual(blob_sha(self.source),self.manifest['source_git_blob_sha'])
    def test_identificadores_unicos(self):
        chunks=self.manifest['chunks']
        self.assertEqual(len({x['id'] for x in chunks}),len(chunks))
    def test_programas_523(self):
        self.assertIn('GESTÃO PÚBLICA (CÓDIGO 523)',page_text(35,ROOT))
        self.assertIn('Orçamento e Administração Financeira Pública',page_text(36,ROOT))
    def test_programas_324(self):
        self.assertIn('ASSUNTOS ESTUDANTIS (CÓDIGOS 324 A 330)',page_text(45,ROOT))
        self.assertTrue(any(x['page']==45 for x in search('conduta estudantil',cargo='324',root=ROOT)))
    def test_conhecimentos_gerais(self):
        self.assertTrue(any(x['page']==29 for x in search('Língua Portuguesa classes de palavras',root=ROOT)))
    def test_regras_gerais_nao_excluidas(self):
        self.assertTrue(any(x['page']<=13 for x in search('fechamento dos portões',cargo='523',root=ROOT)))
    def test_termo_inexistente(self):
        self.assertEqual(search('xxyyzzinexistente',root=ROOT),[])
    def test_corrupcao_detectada(self):
        p=ROOT/self.manifest['chunks'][0]['path']
        old=p.read_text(encoding='utf-8')
        try:
            p.write_text(old+'alteracao',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Chunk divergente'): validate(ROOT)
        finally: p.write_text(old,encoding='utf-8')

if __name__=='__main__': unittest.main()
