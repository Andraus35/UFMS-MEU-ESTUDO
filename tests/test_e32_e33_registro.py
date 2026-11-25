"""E32 (provas e garantias da sessão de 23 a 25/11/2026) e E33 (plano da próxima sessão): o que foi provado, refutado e NÃO provado fica persistido,
e o plano diz a ordem, os gates, os atos do proprietário e as armadilhas."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E32 = ROOT / "docs" / "governanca" / "E32_REGISTRO_DE_PROVAS_E_GARANTIAS_SESSAO_20261123_25.md"
E33 = ROOT / "docs" / "governanca" / "E33_PLANO_PROXIMA_SESSAO_LIGAR_TUDO_E_SUBAGENTS.md"


class RegistroE32Teste(unittest.TestCase):
    def test_provas_refutacoes_identificadores_e_limites(self):
        t = E32.read_text(encoding="utf-8")
        for trecho in ("PROVADO", "REFUTADO", "NÃO PROVADO", "I cannot create a routine from inside a routine", "4ba5054e", "4ca435fa", "5b91c690", "8b43759f", "2bef6d04",
                       "27 s", "29 s", "48 s", "ed7b09e", "8ea64e5", "zapia_disparo.py", "ok: true", "1a21244610ce2fde", "#187", "#188", "#189", "#190", "c6ec3b1", "2533",
                       "SINTETICO_MANUAL", "S4-R2", "não estão ligados ao fluxo", "revogação do anexo é ato dele", "leitura e escrita", "Nenhum dado pessoal",
                       "fechar ou comentar uma issue com `SINAL` só depois do relato", "Não há prefixo de assunto"):
            self.assertIn(trecho, t, trecho)

    def test_nao_afirma_o_que_nao_foi_provado(self):
        t = E32.read_text(encoding="utf-8").split("## 5. NÃO PROVADO")[1].split("## 6.")[0]
        for trecho in ("Tutor e Coach emitindo comandos reais", "fluxo como emissor", "Hook recorrente", "demais operações", "gates no caminho real", "captura dele"):
            self.assertIn(trecho, t, trecho)


class PlanoE33Teste(unittest.TestCase):
    def test_ordem_lotes_gates_atos_e_armadilhas(self):
        t = E33.read_text(encoding="utf-8")
        for trecho in ("ZAPIA-EMISSOR", "ZAPIA-SUBAGENTS", "ZAPIA-LIGAR", "emenda do D-28", "somente leitura", "offline e sintético", "matriz operação × gate", "agents_gate", "command_box",
                       "delivery_gate", "start_receipt", "promotion_gate", "P9", "janela do piloto (PJ)", "o \"Mesclar\" não vale", "merge -s ours", "61 440", "rm", "repetir `add_repo`",
                       "um lote por vez", "não gateável", "Contraprovas mínimas", "origem forjada", "Limite do START: 64 KB", "título curto"):
            self.assertIn(trecho, t, trecho)

    def test_a_fila_tem_os_tres_lotes_com_entrega_dependencia_e_bloqueio_do_piloto(self):
        fila = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}
        self.assertEqual(fila["ZAPIA-EMISSOR"]["depends_on"], ["ZAPIA-F3"])
        self.assertEqual(fila["ZAPIA-SUBAGENTS"]["depends_on"], ["ZAPIA-EMISSOR"])
        self.assertEqual(fila["ZAPIA-LIGAR"]["depends_on"], ["ZAPIA-SUBAGENTS"])
        self.assertIn("P9", fila["ZAPIA-LIGAR"]["blocking_inputs"][0])
        for k, nome in (("ZAPIA-EMISSOR", "E34"), ("ZAPIA-SUBAGENTS", "E35"), ("ZAPIA-LIGAR", "E36")):
            self.assertTrue(fila[k]["deliverable"].startswith(f"docs/governanca/{nome}_"), k)


if __name__ == "__main__":
    unittest.main()
