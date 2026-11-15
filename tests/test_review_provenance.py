"""Contraprovas do registro de proveniência do material de revisão (D-23, PR-005, S2-R10)."""
import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import review_provenance as rp  # noqa: E402

BASE = {"schema_version": "1.0", "topic": "Lei 8.112, regime disciplinar", "date": "2026-11-15", "status": "rascunho",
        "prompt_author": "tutor", "generator": "gemini_notebook", "transport": "zapia", "command_id": "cmd-00000001",
        "verified_by": None, "sources": []}
VERIFICADO = dict(BASE, status="verificado", verified_by="tutor",
                  sources=[{"ref": "EDITAL_UFMS_152_2026.md", "locator": "conteúdos específicos do cargo 523"}])


def com(base, **changes):
    r = copy.deepcopy(base)
    r.update(changes)
    return r


def cli(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = rp.main(args)
    return code, out.getvalue(), err.getvalue()


class ProvenanceTests(unittest.TestCase):
    def test_rascunho_do_gemini_via_zapia_e_valido(self):
        self.assertEqual(rp.check(BASE), [])

    def test_verificado_e_entregue_exigem_o_tutor_e_fonte_com_localizador(self):
        self.assertEqual(rp.check(VERIFICADO), [])
        self.assertEqual(rp.check(com(VERIFICADO, status="entregue")), [])
        for estado in ("verificado", "entregue"):
            self.assertIn("SEM_VERIFICACAO_DO_TUTOR", rp.check(com(VERIFICADO, status=estado, verified_by=None)))
            for quem in ("zapia", "gemini_notebook", "claude_engenharia"):
                self.assertIn("SEM_VERIFICACAO_DO_TUTOR", rp.check(com(VERIFICADO, status=estado, verified_by=quem)))
            self.assertIn("FONTE_SEM_LOCALIZADOR", rp.check(com(VERIFICADO, status=estado, sources=[])))
            self.assertIn("FONTE_SEM_LOCALIZADOR", rp.check(com(VERIFICADO, status=estado,
                                                                sources=[{"ref": "EDITAL", "locator": ""}])))
            self.assertIn("FONTE_SEM_LOCALIZADOR", rp.check(com(VERIFICADO, status=estado, sources=[{"ref": "EDITAL"}])))

    def test_so_o_tutor_escreve_o_prompt(self):
        for autor in ("zapia", "gemini_notebook", "claude_engenharia", "coach", None):
            self.assertIn("AUTOR_DO_PROMPT_NAO_E_O_TUTOR", rp.check(com(BASE, prompt_author=autor)), autor)

    def test_transporte_pela_zapia_exige_comando(self):
        self.assertIn("TRANSPORTE_SEM_COMANDO", rp.check(com(BASE, command_id=None)))
        self.assertIn("TRANSPORTE_SEM_COMANDO", rp.check(com(BASE, command_id="x")))
        self.assertEqual(rp.check(com(BASE, transport="direto", command_id=None)), [])
        self.assertIn("TRANSPORTE_INVALIDO", rp.check(com(BASE, transport="whatsapp")))

    def test_recusa_texto_integral_e_campo_desconhecido(self):
        for chave in ("texto", "conteudo", "body", "resposta", "nota", "material"):
            self.assertIn("TEXTO_INTEGRAL_PROIBIDO", rp.check(com(BASE, **{chave: "um parágrafo inteiro"})), chave)
        self.assertIn("CAMPO_DESCONHECIDO", rp.check(com(BASE, extra="x")))

    def test_recusa_dado_pessoal_nos_metadados(self):
        self.assertTrue(any(e.startswith("DADO_SENSIVEL") for e in rp.check(com(BASE, topic="falar com fulano@example.com"))))
        ruim = com(VERIFICADO, sources=[{"ref": "EDITAL", "locator": "contato fulano@example.com"}])
        self.assertTrue(any(e.startswith("DADO_SENSIVEL") for e in rp.check(ruim)))

    def test_formas_invalidas(self):
        for ruim in (None, [], "texto", 7):
            self.assertEqual(rp.check(ruim), ["REGISTRO_FORA_DO_FORMATO"])
        self.assertIn("DATA_INVALIDA", rp.check(com(BASE, date="15/11/2026")))
        self.assertIn("ESTADO_INVALIDO", rp.check(com(BASE, status="aprovado")))
        self.assertIn("GERADOR_INVALIDO", rp.check(com(BASE, generator="zapia")))
        self.assertIn("VERSAO_INVALIDA", rp.check(com(BASE, schema_version="2.0")))
        self.assertIn("ASSUNTO_INVALIDO", rp.check(com(BASE, topic="a\nb")))
        self.assertIn("VERIFICADOR_INVALIDO", rp.check(com(BASE, verified_by="zapia")))

    def test_validate_levanta_com_os_codigos(self):
        with self.assertRaisesRegex(ValueError, "AUTOR_DO_PROMPT_NAO_E_O_TUTOR"):
            rp.validate(com(BASE, prompt_author="zapia"))
        rp.validate(BASE)

    def test_cli_codigos_de_saida_e_sem_ecoar_texto(self):
        with tempfile.TemporaryDirectory() as tmp:
            bom, mau = Path(tmp) / "bom.json", Path(tmp) / "mau.json"
            bom.write_text(json.dumps(VERIFICADO), encoding="utf-8")
            mau.write_text(json.dumps(com(BASE, texto="SEGREDO-NAO-ECOAR")), encoding="utf-8")
            code, out, _ = cli(["--file", str(bom)])
            self.assertEqual((code, json.loads(out)["valid"]), (0, True))
            code, out, err = cli(["--file", str(mau)])
            self.assertEqual((code, json.loads(out)["valid"]), (1, False))
            self.assertNotIn("SEGREDO-NAO-ECOAR", out + err)
            code, _, err = cli(["--file", str(Path(tmp) / "nao_existe.json")])
            self.assertEqual(code, 1)
            self.assertIn("FALHA", err)


if __name__ == "__main__":
    unittest.main()
