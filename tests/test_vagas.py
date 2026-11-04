"""Validação adversarial das linhas de vagas e requisitos, sem alterar o PDF."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from index_vagas import build, validate, locate_row
from search_edital import search, search_vaga, load

class VagasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=json.loads((ROOT/'edital/vagas_index.json').read_text(encoding='utf-8'))
        cls.chunks={c['id']:c for c in load(ROOT)}

    def test_integridade_e_identidade(self):
        self.assertEqual(validate(ROOT),2)
        self.assertEqual(build(ROOT),self.index)
        self.assertEqual(self.index['classification'],'derived_non_normative')
        source=json.loads((ROOT/'edital/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(self.index['source_git_blob_sha'],source['source_git_blob_sha'])
        self.assertEqual(self.index['source_pdf_sha256'],source['source_pdf_sha256'])

    def test_anchors_dos_campos_e_offsets(self):
        for item in self.index['entries']:
            with self.subTest(code=item['cargo']):
                row=locate_row(item,ROOT)
                body=self.chunks[item['chunk_id']]['body']
                self.assertEqual(body[row['chunk_char_start']:row['chunk_char_end']],row['text'])
                self.assertEqual(row['page_char_start'],
                                 self.chunks[item['chunk_id']]['char_start']+row['chunk_char_start'])
                for field in row['fields']:
                    a,b=field['chunk_char_start'],field['chunk_char_end']
                    self.assertEqual(body[a:b],field['literal'])
                    self.assertEqual(field['page_char_start'],
                                     a+self.chunks[item['chunk_id']]['char_start'])

    def test_523_alternativas_sem_cargo_vizinho(self):
        result=search_vaga('523',ROOT,full=True)
        self.assertEqual((result['page'],result['vacancies'],result['location']),(15,29,'Campo Grande'))
        self.assertIn('Curso Superior em qualquer área do conhecimento',result['text'])
        self.assertIn('Especialização em Gestão Pública',result['text'])
        self.assertIn('360 horas',result['text'])
        self.assertNotIn('524',result['text'])
        self.assertNotIn('Produção Cultural**',result['text'])

    def test_324_sem_confundir_cargos_323_e_325(self):
        result=search_vaga('324',ROOT,full=True)
        self.assertEqual((result['page'],result['vacancies'],result['location']),(18,18,'Campo Grande'))
        self.assertIn('Ensino Médio completo',result['text'])
        self.assertNotIn('323',result['text'])
        self.assertNotIn('325',result['text'])
        self.assertNotIn('Registro no Conselho competente',result['text'])

    def test_buscas_diretas_e_sem_contaminacao(self):
        for code,expected in (('523',29),('324',18)):
            with self.subTest(code=code):
                query='Quais são as vagas e requisitos do cargo '+code+'?'
                hits=search(query,root=ROOT,full=True)
                self.assertEqual(len(hits),1)
                self.assertEqual(hits[0]['route'],'quadro_vagas_derived_verified_anchors')
                self.assertEqual(hits[0]['vacancies'],expected)
                self.assertEqual(hits[0]['cargo'],code)
        with self.assertRaisesRegex(ValueError,'contradiz'):
            search('Requisitos do cargo 523',cargo='324',root=ROOT)
        with self.assertRaisesRegex(ValueError,'não indexado'):
            search_vaga('524',root=ROOT)
        with self.assertRaisesRegex(ValueError,'múltiplos cargos'):
            search('Comparar vagas do cargo 523 com cargo 324',root=ROOT)

    def test_mutacao_do_indice_derivado_e_detectada(self):
        import tempfile
        import copy
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'edital').mkdir()
            for name in ('EDITAL_UFMS_152_2026.md','edital/manifest.json'):
                (root/name).symlink_to(ROOT/name)
            (root/'edital/chunks').symlink_to(ROOT/'edital/chunks',target_is_directory=True)
            altered=copy.deepcopy(self.index)
            altered['entries'][0]['vacancies']=30
            (root/'edital/vagas_index.json').write_text(
                json.dumps(altered,ensure_ascii=False),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Índice de vagas divergente'):
                validate(root)

    def test_custo_de_contexto(self):
        src=(ROOT/'EDITAL_UFMS_152_2026.md').read_text(encoding='utf-8')
        for code in ('523','324'):
            row=search_vaga(code,ROOT,full=True)
            self.assertLess(len(row['text']),len(src)//100)

if __name__=='__main__':unittest.main()
