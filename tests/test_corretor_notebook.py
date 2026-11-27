"""E45: o corretor simulado só executa comando validado e íntegro, devolve campos fixos e nunca deixa o segredo sair."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corretor_notebook as cn  # noqa: E402
import zapia_n1_prep as prep  # noqa: E402

AGORA = datetime(2026, 11, 27, 20, 0, tzinfo=timezone.utc)
LOTE = prep.montar(AGORA)
ITEM = LOTE["itens"][0]
NOME = ITEM["nome"] + ".json"
RECIBO = json.loads(ITEM["recibo_bytes"].decode("utf-8"))
FONTE = LOTE["fonte_bytes"]


def rodar(backend=None, comando=None, recibo=None, fonte=FONTE, nome=NOME, agora=AGORA, corretor=None):
    c = corretor or cn.Corretor(backend or cn.BackendSimulado())
    return c.executar(nome, comando if comando is not None else ITEM["comando_bytes"], recibo if recibo is not None else RECIBO,
                      LOTE["fonte_nome"], fonte, agora)


class CorretorTest(unittest.TestCase):
    def test_caminho_feliz_devolve_campos_fixos_e_marca_nao_confiavel(self):
        r = rodar()
        self.assertEqual(r["estado"], "RESPONDIDO")
        self.assertEqual(set(r), {"entrada_id", "hash_corpo", "estado", "resposta", "fonte_sha256", "respondido_em", "nao_confiavel"})
        self.assertTrue(r["nao_confiavel"])
        self.assertEqual(r["hash_corpo"], ITEM["hash_corpo"])

    def test_recibo_sem_promover_ou_sem_hash_para_antes_do_backend(self):
        for rec in ({**RECIBO, "status": "DENIED"}, {k: v for k, v in RECIBO.items() if k != "hash_corpo"}, {**RECIBO, "hash_corpo": 7}, "x"):
            b = cn.BackendSimulado()
            r = rodar(b, recibo=rec)
            self.assertEqual(r["codigo_parada"], "RECIBO_INVALIDO")
            self.assertEqual(b.chamadas, [])

    def test_hash_do_recibo_diferente_para_e_nada_executa(self):
        b = cn.BackendSimulado()
        r = rodar(b, recibo={**RECIBO, "hash_corpo": "0" * 64})
        self.assertEqual(r["codigo_parada"], "HASH_NAO_CONFERE")
        self.assertEqual(b.chamadas, [])

    def test_comando_adulterado_ou_ilegivel_e_recusado_pela_caixa(self):
        adulterado = ITEM["comando_bytes"].replace(b'"tutor"', b'"coach"', 1)
        for bruto in (adulterado, b"{", b"\xff\xfe", b""):
            b = cn.BackendSimulado()
            r = rodar(b, comando=bruto)
            self.assertEqual(r["estado"], "PARADO")
            self.assertIn(r["codigo_parada"], ("COMANDO_RECUSADO", "HASH_NAO_CONFERE"))
            self.assertEqual(b.chamadas, [])

    def test_comando_vencido_e_recusado(self):
        b = cn.BackendSimulado()
        r = rodar(b, agora=AGORA + timedelta(days=3))
        self.assertEqual(r["codigo_parada"], "COMANDO_RECUSADO")
        self.assertEqual(b.chamadas, [])

    def test_outra_operacao_ou_origem_para_mesmo_se_a_caixa_aprovar(self):
        from unittest import mock
        import command_box
        base = json.loads(ITEM["comando_bytes"].decode("utf-8"))
        for campo, valor in (("operation", "criar_lembrete"), ("origin", "coach")):
            cmd = {**base, campo: valor}
            bruto = json.dumps(cmd, ensure_ascii=False).encode("utf-8")
            b = cn.BackendSimulado()
            with mock.patch.object(command_box, "validar", return_value={"status": command_box.PROMOVER}):
                r = rodar(b, comando=bruto, recibo={**RECIBO, "hash_corpo": command_box.command_hash(cmd)})
            self.assertEqual(r["codigo_parada"], "OPERACAO_NAO_PERMITIDA", campo)
            self.assertEqual(b.chamadas, [])

    def test_reexecucao_do_mesmo_hash_nao_chama_o_backend(self):
        c = cn.Corretor(cn.BackendSimulado())
        self.assertEqual(rodar(corretor=c)["estado"], "RESPONDIDO")
        b2 = cn.BackendSimulado()
        c._backend = b2
        self.assertEqual(rodar(corretor=c)["estado"], "JA_RESPONDIDO")
        self.assertEqual(b2.chamadas, [])

    def test_fonte_ausente_vazia_grande_ou_nao_utf8(self):
        for fonte in (None, b"", b"x" * (cn.LIMITE_FONTE_BYTES + 1), b"\xff\xfe\x00", "texto"):
            r = rodar(fonte=fonte)
            self.assertEqual(r["codigo_parada"], "FONTE_AUSENTE")

    def test_falha_ao_adicionar_fonte_para_sem_resposta(self):
        r = rodar(cn.BackendSimulado(falhar="fonte"))
        self.assertEqual(r["codigo_parada"], "FONTE_NAO_ADICIONADA")
        self.assertNotIn("resposta", r)

    def test_falha_ao_perguntar_nao_marca_como_respondido(self):
        c = cn.Corretor(cn.BackendSimulado(falhar="perguntar"))
        self.assertEqual(rodar(corretor=c)["codigo_parada"], "BACKEND_FALHOU")
        self.assertEqual(c.ja_respondidos, set())

    def test_resposta_vazia_ou_gigante_e_invalida(self):
        for resp in ("", "   ", None, "a" * (cn.LIMITE_RESPOSTA + 1)):
            self.assertEqual(rodar(cn.BackendSimulado(resposta=resp))["codigo_parada"], "RESPOSTA_INVALIDA")

    def test_segredo_na_resposta_e_descartado_e_nunca_sai(self):
        c = cn.Corretor(cn.BackendSimulado())
        for vazamento in ("ok " + c._token, "Authorization: Bearer abcdefghijklmnop1234", "chave AIza" + "x" * 30, '{"refresh_token": "x"}'):
            c._backend = cn.BackendSimulado(resposta=vazamento)
            r = rodar(corretor=c)
            self.assertEqual(r["codigo_parada"], "SEGREDO_NA_SAIDA")
            self.assertNotIn("resposta", r)
            self.assertNotIn(c._token, json.dumps(r))
        self.assertEqual(c.ja_respondidos, set())

    def test_segredo_na_fonte_nao_chega_ao_backend(self):
        b = cn.BackendSimulado()
        r = rodar(b, fonte=b"trecho com Bearer abcdefghijklmnop1234")
        self.assertEqual(r["codigo_parada"], "SEGREDO_NA_SAIDA")
        self.assertEqual(b.chamadas, [])

    def test_backend_oficial_nao_tem_pergunta_documentada_nem_credencial(self):
        o = cn.BackendOficialV1Alpha()
        with self.assertRaises(cn.CapacidadeNaoDocumentada):
            o.perguntar("x", "p")
        with self.assertRaises(cn.SemCredencial):
            o.criar_caderno("t")
        self.assertEqual(rodar(o)["codigo_parada"], "BACKEND_FALHOU")

    def test_requisicoes_oficiais_so_texto_e_sem_token(self):
        o = cn.BackendOficialV1Alpha("123", "global")
        c = o.requisicao_criar("t")
        f = o.requisicao_fonte("nb1", "nome", "conteúdo")
        self.assertTrue(c["url"].endswith("/notebooks") and c["corpo"] == {"title": "t"})
        self.assertTrue(f["url"].endswith("/notebooks/nb1/sources:batchCreate"))
        conteudo = f["corpo"]["userContents"][0]
        self.assertEqual(list(conteudo), ["textContent"])  # sem webContent, videoContent nem googleDriveContent
        bruto = json.dumps([c, f])
        self.assertNotIn("Authorization", bruto)
        self.assertNotIn("Bearer", bruto)

    def test_codigos_de_parada_estao_na_lista_fechada(self):
        resultados = [rodar(recibo={**RECIBO, "status": "X"}), rodar(fonte=b""), rodar(cn.BackendSimulado(falhar="fonte")), rodar(cn.BackendOficialV1Alpha())]
        for r in resultados:
            self.assertIn(r["codigo_parada"], cn.CODIGOS)


if __name__ == "__main__":
    unittest.main()


class DocE45Test(unittest.TestCase):
    def test_o_registro_diz_o_que_a_pesquisa_nao_achou(self):
        doc = (ROOT / "docs/governanca/E45_CORRETOR_API_OFICIAL_NOTEBOOK.md").read_text(encoding="utf-8")
        for trecho in ("Preview", "descreve método para fazer pergunta", "Lacunas", "SemCredencial", "D-26", "emendar a D-26 agora", "nada é feito pela sessão"):
            self.assertIn(trecho, doc)


class FilaN1Test(unittest.TestCase):
    def test_itens_abertos_do_n1_nao_contam_como_feitos_por_entrega_ja_existente(self):
        wf = json.loads((ROOT / "state/WORKFLOW.json").read_text(encoding="utf-8"))
        itens = {i["id"]: i for i in wf["work_queue"]}
        for id_ in ("N1-DIAG-FONTE", "N1-RODADA-4", "S22-PROVA-MIN"):
            self.assertFalse((ROOT / itens[id_]["deliverable"]).exists(), id_)  # só passam a existir quando o trabalho for feito
        self.assertEqual(itens["N1-RODADA-4"]["depends_on"], ["N1-DIAG-FONTE"])
