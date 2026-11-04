"""Contraprovas independentes de aliases, com isolamento de cargos e falha segura."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from search_edital import search

class AdversarialRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=json.loads((ROOT/'tests/fixtures/adversarial_cases.json').read_text(encoding='utf-8'))['cases']
        cls.source_sha=json.loads((ROOT/'edital/manifest.json').read_text(encoding='utf-8'))['source_git_blob_sha']

    def test_consultas_fora_do_benchmark_inicial(self):
        for c in self.cases:
            with self.subTest(query=c['query'],kind=c['kind']):
                kwargs={'cargo':c['cargo'],'area':c['area'],'root':ROOT,'limit':3,'full':True}
                if c['kind']=='conflict':
                    with self.assertRaisesRegex(ValueError,'contradiz'):
                        search(c['query'],**kwargs)
                    continue
                hits=search(c['query'],**kwargs)
                if c['kind']=='positive':
                    self.assertTrue(hits,'Sem recuperação para '+c['query'])
                    matching=[h for h in hits if h['page']==c['page']
                              and c['expected_text'].casefold() in ' '.join(
                                  h.get('text','').casefold().split())
                              and h['route']==c['expected_route']]
                    self.assertTrue(matching,'Evidência literal não recuperada: '+c['query'])
                elif c['kind']=='negative':
                    self.assertEqual(hits,[],'Resultado indevido para '+c['query'])
                elif c['kind']=='isolation':
                    self.assertFalse(any(h['chunk_id']==c['forbidden_chunk'] for h in hits),
                                     'Programa de outro cargo recuperado: '+c['query'])
                elif c['kind']=='not_item':
                    self.assertFalse(any(h['route']=='literal_item_marker' for h in hits),
                                     'Lei externa confundida com número de item')
                else:
                    self.fail('Classe não reconhecida '+c['kind'])
                for h in hits:
                    self.assertEqual(h['source_sha'],self.source_sha)
                    self.assertTrue(h['path'].startswith('edital/chunks/'))
                    self.assertIn(h['page'],range(1,48))
                    if 'text' in h:self.assertTrue(h['text'])

    def test_negativo_ao_erro_de_tipo_de_filtro(self):
        with self.assertRaises(ValueError):
            search('autonomia',cargo='524',root=ROOT)
        with self.assertRaises(ValueError):
            search('autonomia',area='especificos',root=ROOT)

if __name__=='__main__':unittest.main()
