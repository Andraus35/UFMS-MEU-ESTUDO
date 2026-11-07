"""Resposta completa da rodada 2 da Zapia: íntegra, sem dados pessoais e coerente com o PRODUCT.md."""
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/governanca/RESPOSTA_RODADA2_ZAPIA_20261107.md").read_text(encoding="utf-8")
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
ADR = (ROOT / "docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md").read_text(encoding="utf-8")
STATUS = {"OBSERVADO", "DOCUMENTADO", "DESCONHECIDO"}


def entries():
    return json.loads(re.search(r"```json\n(.*?)\n```", DOC, re.S).group(1))


class Rodada2RespostaTests(unittest.TestCase):
    def test_r1_a_r34_validas_e_sequenciais(self):
        data = entries()
        self.assertEqual([e["id"] for e in data], [f"R{n}" for n in range(1, 35)])
        for e in data:
            self.assertIn(e["status"], STATUS, e["id"])
            for campo in ("resposta", "evidencia", "risco"):
                self.assertTrue(e[campo].strip(), f"{e['id']}.{campo}")

    def test_contagem_de_status_confere_com_o_arquivo_recebido(self):
        self.assertEqual(Counter(e["status"] for e in entries()),
                         {"OBSERVADO": 22, "DOCUMENTADO": 8, "DESCONHECIDO": 4})

    def test_declara_completa_e_nao_cita_versao_truncada_como_vigente(self):
        self.assertIn("COMPLETA (R1 a R34)", DOC)
        self.assertNotIn("INCOMPLETA", DOC)

    def test_sem_dados_pessoais_nem_segredos(self):
        for padrao, rotulo in ((r"[\w.+-]+@[\w-]+\.[\w.]+", "e-mail"), (r"\b55\d{10,11}\b", "telefone"),
                               (r"ghp_[A-Za-z0-9]{20,}", "token"), (r"github_pat_[A-Za-z0-9_]{20,}", "token"),
                               (r"github_ufms_repo_token", "referência de credencial")):
            self.assertIsNone(re.search(padrao, DOC), rotulo)
        for termo in ("Ondas de Elliot", "Catalogo Oficial do SOT", "Constituição do Sistema de Trading", "Radar"):
            self.assertNotIn(termo, DOC)

    def test_fatos_chave_registrados(self):
        text = json.dumps(entries(), ensure_ascii=False)
        for trecho in ("Inteligencia-SOT", "nenhum privado foi listado", "status=cancelled",
                       "Git não estava disponível", "notebook público da Bloomsbury",
                       "servidores nos Estados Unidos", "36 meses", "plano Free"):
            self.assertIn(trecho, text)

    def test_r34_cita_head_e_blob_que_o_repositorio_confirmou(self):
        text = json.dumps(entries(), ensure_ascii=False)
        self.assertIn("82d7b309c89bd07508e3cc7b2597f166106edd69", text)
        self.assertIn("db799954bf7ddc551794e6e05883a87748770ea1", text)
        self.assertIn("coincidem exatamente", DOC)

    def test_product_incorpora_os_fatos_da_rodada_2(self):
        for trecho in ("E-08", "E-09", "OPEN-07", "D-08", "D-09", "PR-012", "não está disponível", "sem informação de expiração",
                       "3 repositórios públicos", "exclusão lógica foi **comprovada na rodada 2**",
                       "Não declarar que apagar o repositório privado elimina todas as cópias"):
            self.assertIn(trecho, PRODUCT)

    def test_consentimento_v2_aprovado_substitui_o_v1_sem_gravar_nada(self):
        self.assertIn("Consentimento v2 (APROVADO pelo proprietário em 07/11/2026, sem ajustes; substitui o v1)", ADR)
        self.assertIn("SUBSTITUÍDO pelo v2", ADR)
        self.assertIn("A aprovação do texto (v2, abaixo) não grava consentimento", ADR)
        self.assertIn("consentimento **v2** aprovado, sem ajustes", PRODUCT)
        self.assertIn("consentimento v2 (D-04) fica registrado no repositório privado antes do primeiro evento", PRODUCT)

    def test_testes_sinteticos_seguem_nao_executados(self):
        self.assertIn("não foram executados", DOC)


if __name__ == "__main__":
    unittest.main()
