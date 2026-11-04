"""Regras de recuperação por trecho exato e consultas de regressão."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from index_edital import build,validate
from search_edital import load,search

class TopicIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'tests/fixtures/retrieval_cases.json').read_text(encoding='utf-8'))
        cls.index=json.loads((ROOT/'edital/topic_index.json').read_text(encoding='utf-8'))
        cls.by_chunk={x['id']:x for x in load(ROOT)}

    def test_indice_deterministico(self):
        self.assertEqual(validate(ROOT),23)
        self.assertEqual(build(ROOT),self.index)
        self.assertEqual(self.index['classification'],'derived_non_normative')

    def test_intervalos_consistentes(self):
        for topic in self.index['topics']:
            self.assertIn(topic['area'],('gerais','especificos'))
            self.assertTrue(topic['locations'])
            for loc in topic['locations']:
                c=self.by_chunk[loc['chunk_id']]
                a,b=loc['chunk_char_start'],loc['chunk_char_end']
                self.assertTrue(0<=a<b<=len(c['body']))
                self.assertEqual(c['page'],loc['page'])
                self.assertEqual(loc['path'],c['path'])
                self.assertEqual(loc['page_char_start'],c['char_start']+a)
                self.assertEqual(loc['page_char_end'],c['char_start']+b)
                self.assertTrue(c['body'][a:b].strip())

    def test_consultas_de_regressao(self):
        for case in self.data['cases']:
            with self.subTest(query=case['query']):
                matches=search(case['query'],cargo=case['cargo'],area=case['area'],
                               limit=3,root=ROOT)
                if case['type']=='negative':
                    self.assertEqual(matches,[])
                else:
                    self.assertTrue(matches, 'Nenhum resultado: '+case['query'])
                    if case['type']=='rule':
                        self.assertIn(case['page'],[x['page'] for x in matches])
                    else:
                        self.assertEqual(matches[0].get('topic_id'),case['topic_id'])
                        self.assertEqual(matches[0]['page'],case['page'])
                    self.assertEqual(matches[0]['source_sha'],
                                     self.index['source_git_blob_sha'])

    def test_cargo_523_nao_importa_conteudo_524(self):
        r=search(topic='523-10',cargo='523',area='especificos',full=True,root=ROOT)
        self.assertTrue(r)
        self.assertTrue(all('CAMPUS) (CÓDIGOS 524' not in x['text'] for x in r))
        self.assertEqual(search('endodontia apicectomia',cargo='523',
                                area='especificos',root=ROOT),[])

    def test_cargo_324_nao_importa_cargo_anterior(self):
        r=search(topic='324-06',cargo='324',area='especificos',full=True,root=ROOT)
        self.assertEqual(len(r),1)
        self.assertIn('Conduta Estudantil',r[0]['text'])
        self.assertNotIn('TÉCNICO EM EDUCAÇÃO / PROCESSOS EDUCACIONAIS',
                         r[0]['text'])

    def test_expansao_contextual(self):
        r=search(topic='324-03',cargo='324',root=ROOT,neighbors=True)
        self.assertEqual(r[0]['adjacent_chunks'][0]['chunk_id'],'p45-c01')

    def test_economia_em_caracteres(self):
        source=(ROOT/'EDITAL_UFMS_152_2026.md').read_text(encoding='utf-8')
        r=search(topic='523-06',cargo='523',area='especificos',full=True,root=ROOT)
        self.assertLess(sum(len(x['text']) for x in r),len(source)//50)

    def test_erros_de_escopo(self):
        with self.assertRaises(ValueError):
            search('questao',area='especificos',root=ROOT)
        with self.assertRaises(ValueError):
            search(topic='523-06',cargo='324',root=ROOT)
        with self.assertRaises(ValueError):
            search('questao',limit=0,root=ROOT)

if __name__=='__main__':
    unittest.main()
