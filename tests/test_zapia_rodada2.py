"""Resposta parcial da rodada 2 da Zapia: íntegra, sem dados pessoais e sem inferir o que não veio."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/RESPOSTA_RODADA2_ZAPIA_20261107.md").read_text(encoding="utf-8")
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
STATUS = {"OBSERVADO", "DOCUMENTADO", "DESCONHECIDO"}


def entries():
    return json.loads(re.search(r"```json\n(.*?)\n```", DOC, re.S).group(1))


class Rodada2RespostaTests(unittest.TestCase):
    def test_r1_a_r29_validas_e_sequenciais(self):
        data = entries()
        self.assertEqual([e["id"] for e in data], [f"R{n}" for n in range(1, 30)])
        for e in data:
            self.assertIn(e["status"], STATUS, e["id"])
            for campo in ("resposta", "evidencia", "risco"):
                self.assertTrue(e[campo].strip(), f"{e['id']}.{campo}")

    def test_declara_que_esta_incompleta_e_nao_inventa_r30_a_r34(self):
        self.assertIn("INCOMPLETA", DOC)
        self.assertIn("R31, R32, R33 e R34 não foram recebidos", DOC)
        ids = {e["id"] for e in entries()}
        for faltante in ("R30", "R31", "R32", "R33", "R34"):
            self.assertNotIn(faltante, ids)

    def test_sem_dados_pessoais_nem_segredos(self):
        for padrao, rotulo in ((r"[\w.+-]+@[\w-]+\.[\w.]+", "e-mail"), (r"\b55\d{10,11}\b", "telefone"),
                               (r"ghp_[A-Za-z0-9]{20,}", "token"), (r"github_pat_[A-Za-z0-9_]{20,}", "token"),
                               (r"github_ufms_repo_token", "referência de credencial")):
            self.assertIsNone(re.search(padrao, DOC), rotulo)
        for titulo in ("Ondas de Elliot", "Catalogo Oficial do SOT", "Constituição do Sistema de Trading"):
            self.assertNotIn(titulo, DOC)

    def test_fatos_chave_registrados(self):
        text = json.dumps(entries(), ensure_ascii=False)
        self.assertIn("Inteligencia-SOT", text)           # token alcança 3 repositórios públicos
        self.assertIn("nenhum privado foi listado", text)
        self.assertIn("status=cancelled", text)           # exclusão lógica comprovada
        self.assertIn("Git não estava disponível", text)
        self.assertIn("notebook público da Bloomsbury", text)

    def test_product_incorpora_os_fatos_da_rodada_2(self):
        for trecho in ("E-08", "OPEN-07", "não está disponível", "sem informação de expiração",
                       "3 repositórios públicos", "exclusão lógica foi **comprovada na rodada 2**"):
            self.assertIn(trecho, PRODUCT)

    def test_testes_sinteticos_seguem_nao_executados(self):
        self.assertIn("não foram executados", DOC)


if __name__ == "__main__":
    unittest.main()
