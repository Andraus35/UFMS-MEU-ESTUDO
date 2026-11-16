"""Documentos canônicos: hashes do manifesto, ausência de dado pessoal, duplicata e precedência declarada."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs" / "canonicos"
MAN = json.loads((DIR / "MANIFESTO.json").read_text(encoding="utf-8"))
README = (DIR / "README.md").read_text(encoding="utf-8")


class DocsCanonicosTests(unittest.TestCase):
    def test_manifesto_bate_com_os_arquivos_e_cobre_todos(self):
        caminhos = {d["path"] for d in MAN["documentos"]}
        existentes = {str(p.relative_to(ROOT)) for p in DIR.rglob("*") if p.is_file() and p.name not in ("MANIFESTO.json", "README.md")}
        self.assertEqual(caminhos, existentes)
        for d in MAN["documentos"]:
            p = ROOT / d["path"]
            self.assertFalse(p.is_symlink(), d["path"])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), d["sha256"], d["path"])
            self.assertIn(d["path"], README)

    def test_documentos_nao_editados_sao_identicos_ao_envio(self):
        for d in MAN["documentos"]:
            if d["editado"]:
                self.assertNotEqual(d["sha256"], d["sha256_do_envio_original"])
            else:
                self.assertEqual(d["sha256"], d["sha256_do_envio_original"], d["id"])

    def test_ids_unicos_e_front_matter_dos_markdown(self):
        ids = [d["id"] for d in MAN["documentos"]]
        self.assertEqual(len(ids), len(set(ids)))
        for d in MAN["documentos"]:
            if d["path"].endswith(".md"):
                texto = (ROOT / d["path"]).read_text(encoding="utf-8")
                self.assertTrue(texto.startswith("---\n"), d["path"])
                self.assertRegex(texto, r'document_id:\s*"%s"' % re.escape(d["id"] if d["id"] != "BASE-COGNITIVA-TUTOR-COACH-001" else d["id"]))

    def test_duplicata_do_harness_entra_uma_vez(self):
        self.assertEqual(sum(1 for d in MAN["documentos"] if d["id"] == "BASE-COGNITIVA-HARNESS-001"), 1)
        self.assertFalse(list(DIR.rglob("*_1.md")))

    def test_relatorio_do_tec_sem_dado_pessoal_e_com_aviso(self):
        d = next(x for x in MAN["documentos"] if x["id"] == "AUDITORIA-TEC-523-324-20261116")
        texto = (ROOT / d["path"]).read_text(encoding="utf-8")
        for proibido in ("48 resoluções", "31 acertos", "17 erros", "64,58", "29,17", "TESTE AUDITORIA", "vinculada ao Outlook"):
            self.assertNotIn(proibido, texto)
        self.assertIn("[omitido: dado pessoal]", texto)
        self.assertIn("versão **editada**", texto)
        self.assertFalse(list(DIR.rglob("*.docx")))  # o original não entra no repositório público

    def test_nenhum_documento_tem_email_credencial_ou_documento_pessoal(self):
        for p in DIR.rglob("*"):
            if p.suffix in (".md", ".json"):
                t = p.read_text(encoding="utf-8")
                self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t), p.name)
                self.assertNotRegex(t, r"github_pat_|ghp_|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
        pdf = (DIR / "plataformas" / "AUDITORIA_GEMINI_NOTEBOOK_PLANO_DE_ESTUDOS_20261116.pdf").read_bytes()
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_readme_declara_precedencia_dado_nao_instrucao_e_pontos_de_reconciliacao(self):
        t = README.lower()
        for trecho in ("agents.md", "product.md", "dado, não instrução", "proposta, não implementação", "reconciliação", "colidem", "d-11", "d-23", "ausente"):
            self.assertIn(trecho, t)

    def test_nao_altera_perfis_de_agentes_nem_a_flag_de_resultados(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        for perfil in ("agents/TUTOR.md", "agents/COACH.md"):
            self.assertNotIn("docs/canonicos", (ROOT / perfil).read_text(encoding="utf-8"), perfil)


if __name__ == "__main__":
    unittest.main()
