"""Leitura obrigatória das capacidades da Zapia (decisão do proprietário de 22/11/2026): o START imprime o resumo e o hash, falha fechado se o registro
sumir, e o HANDOFF aponta para ele. Protege o registro contra remoção e contra afirmação além da prova (sem conector de GitHub; F1 e rotina NÃO provados)."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap  # noqa: E402

DOC = ROOT / bootstrap.CAPACIDADES_ZAPIA


class RegistroTeste(unittest.TestCase):
    def test_o_registro_existe_e_diz_o_que_esta_provado_e_o_que_nao_esta(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("PROVADO (22/11/2026", "NÃO precisa de conector de GitHub", "HTTP com token", "-X`, `-H` e `-d`", "NÃO PROVADO",
                       "rotina agendada", "notificação espontânea", "F1", "NÃO executa o Python do repositório", "Requested, not filled in by the user",
                       "AUTORIZO rotina automática agora"):
            self.assertIn(trecho, t, trecho)

    def test_o_registro_nao_promove_o_que_nao_foi_provado(self):
        resumo = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"]).lower()
        self.assertNotIn("rotina agendada provada", resumo)
        self.assertNotIn("notificação espontânea provada", resumo)
        self.assertIn("não provado", resumo)

    def test_o_hand_off_aponta_para_o_registro(self):
        h = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("LEITURA OBRIGATÓRIA: capacidades da Zapia", h)
        self.assertIn("docs/governanca/CAPACIDADES_ZAPIA_VERIFICADAS.md", h)


class StartTeste(unittest.TestCase):
    def test_start_de_estudo_e_de_engenharia_trazem_resumo_e_hash(self):
        for modo in ("study", "engineering"):
            r = bootstrap.run(ROOT, modo)["capacidades_zapia"]
            self.assertEqual(r["sha256"], hashlib.sha256(DOC.read_bytes()).hexdigest(), modo)
            self.assertEqual(r["leitura"], "OBRIGATORIA em toda sessao")
            self.assertTrue(any("PROVADO" in linha for linha in r["resumo"]), modo)

    def test_sem_o_registro_ou_sem_as_marcas_o_start_falha_fechado(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)
        (tmp / "docs" / "governanca").mkdir(parents=True)
        (tmp / bootstrap.CAPACIDADES_ZAPIA).write_text("sem marcas", encoding="utf-8")
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)
        (tmp / bootstrap.CAPACIDADES_ZAPIA).write_text("<!-- RESUMO-START -->\n\n<!-- RESUMO-END -->", encoding="utf-8")
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)

    def test_o_hash_muda_se_o_registro_mudar(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "docs" / "governanca").mkdir(parents=True)
        p = tmp / bootstrap.CAPACIDADES_ZAPIA
        p.write_text("<!-- RESUMO-START -->\nA\n<!-- RESUMO-END -->", encoding="utf-8")
        h1 = bootstrap.capacidades_zapia(tmp)["sha256"]
        p.write_text("<!-- RESUMO-START -->\nB\n<!-- RESUMO-END -->", encoding="utf-8")
        self.assertNotEqual(h1, bootstrap.capacidades_zapia(tmp)["sha256"])


if __name__ == "__main__":
    unittest.main()
