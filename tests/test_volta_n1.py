"""Volta do N1 (E41, lote VOLTA-N1): conferência, relatório do Tutor sem texto do Notebook, entrada do Coach e proposta do Coach pela caixa. Offline."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import subagent_harness as sh  # noqa: E402
import volta_n1 as vn  # noqa: E402
import zapia_n1_prep as prep  # noqa: E402

M = prep.montar(datetime(2026, 11, 25, 15, 0, 0, tzinfo=timezone.utc))
FONTE = M["fonte_bytes"].decode("utf-8")
META = {"fonte_nome": M["fonte_nome"], "itens": {i["nome"]: {"hash_corpo": i["hash_corpo"], "contraprova": i["contraprova"], "ancora_gabarito": i["ancora_gabarito"]}
                                                  for i in M["itens"]}}
CIT = "obedecerá aos princípios de legalidade, impessoalidade, moralidade, publicidade e eficiência"
SEGREDO_DO_NOTEBOOK = "TRECHO-LITERAL-DO-NOTEBOOK-UNICO-0001"


def resp(nome, **mud):
    r = {"entrada_id": nome, "hash_corpo": META["itens"][nome]["hash_corpo"], "estado": "RESPONDIDO", "texto_literal": "1. Pergunta curta? Dica: releia o caput.",
         "citacao_trecho": CIT, "fonte_nome": META["fonte_nome"], "interface": "gemini_notebook"}
    r.update(mud)
    return json.dumps({k: v for k, v in r.items() if v is not None}, ensure_ascii=False).encode("utf-8")


def boas():
    return {"n1-fonte.json": resp("n1-fonte.json"), "n1-questao.json": resp("n1-questao.json"),
            "n1-contraprova.json": resp("n1-contraprova.json", texto_literal="Isso não consta nas fontes.", citacao_trecho="")}


class RelatorioTest(unittest.TestCase):
    def test_tudo_conferido_e_pronto_e_o_relatorio_nao_leva_texto_do_notebook(self):
        b = boas()
        b["n1-fonte.json"] = resp("n1-fonte.json", texto_literal=SEGREDO_DO_NOTEBOOK)
        r = vn.processar(META, FONTE, b)
        self.assertEqual((r["veredito"], r["confianca"], r["pendentes"], r["parados"]), (vn.PRONTO, "B", 0, 0))
        self.assertTrue(all(i["estado"] == "CONFERIDA" for i in r["relatorio_tutor"]))
        self.assertNotIn(SEGREDO_DO_NOTEBOOK, json.dumps(r, ensure_ascii=False))
        self.assertNotIn(SEGREDO_DO_NOTEBOOK, json.dumps(vn.entrada_coach(r), ensure_ascii=False))

    def test_pendente_parado_e_recusada_nao_provam(self):
        b = boas()
        b.pop("n1-contraprova.json")
        r = vn.processar(META, FONTE, b)
        self.assertEqual((r["veredito"], r["pendentes"]), (vn.NAO_PROVADO, 1))
        b = boas()
        b["n1-fonte.json"] = resp("n1-fonte.json", estado="PARADO", texto_literal="", citacao_trecho="", codigo_parada="LOGIN")
        r = vn.processar(META, FONTE, b)
        self.assertEqual((r["veredito"], r["parados"]), (vn.NAO_PROVADO, 1))
        b = boas()
        b["n1-fonte.json"] = resp("n1-fonte.json", citacao_trecho="trecho que a fonte não tem")
        r = vn.processar(META, FONTE, b)
        self.assertEqual(r["veredito"], vn.NAO_PROVADO)
        self.assertEqual([i["conferencia"] for i in r["relatorio_tutor"] if i["estado"] == "RECUSADA"], ["CITACAO_NAO_ESTA_NA_FONTE"])

    def test_questao_sem_ancora_do_gabarito_e_recusada(self):
        b = boas()
        b["n1-questao.json"] = resp("n1-questao.json", citacao_trecho="e, também, ao seguinte:")
        r = vn.processar(META, FONTE, b)
        self.assertEqual(r["veredito"], vn.NAO_PROVADO)
        self.assertIn("CITACAO_NAO_SUSTENTA_GABARITO", [i["conferencia"] for i in r["relatorio_tutor"]])

    def test_resposta_de_outro_comando_e_lixo_nao_passam(self):
        b = boas()
        b["n1-fonte.json"] = resp("n1-fonte.json", hash_corpo="0" * 64)
        self.assertEqual(vn.processar(META, FONTE, b)["veredito"], vn.NAO_PROVADO)
        b = boas()
        b["n1-fonte.json"] = b"nao e json"
        r = vn.processar(META, FONTE, b)
        self.assertEqual(r["veredito"], vn.NAO_PROVADO)

    def test_captura_sobe_a_confianca_so_se_valida(self):
        ok = {"relogio_visivel": True, "descricao": "captura do chat do Notebook com a hora do aparelho visível"}
        r = vn.processar(META, FONTE, boas(), ok)
        self.assertEqual((r["veredito"], r["confianca"], r["captura"]), (vn.PRONTO, "B+captura", "registrada"))
        for ruim, cod in (({"relogio_visivel": False, "descricao": "x"}, "CAPTURA_SEM_RELOGIO"), ({"relogio_visivel": True}, "CAPTURA_FORA_DO_FORMATO"),
                          ({"relogio_visivel": True, "descricao": "a" * 201}, "CAPTURA_DESCRICAO_INVALIDA"),
                          ({"relogio_visivel": True, "descricao": "veja https://x.com"}, "CAPTURA_DESCRICAO_INVALIDA"), ("texto", "CAPTURA_FORA_DO_FORMATO")):
            r = vn.processar(META, FONTE, boas(), ruim)
            self.assertEqual((r["veredito"], r["confianca"], r["captura"]), (vn.NAO_PROVADO, "B", cod), str(ruim))

    def test_entrada_do_coach_so_tem_contagens(self):
        e = vn.entrada_coach(vn.processar(META, FONTE, boas()))
        self.assertEqual(e, {"origem": "relatorio_tutor_n1", "veredito": vn.PRONTO, "confianca": "B", "conferidas": 3, "total": 3, "pendentes": 0, "parados": 0,
                             "dado_do_aluno": False})

    def test_entrada_nao_e_alterada(self):
        b, m = boas(), copy.deepcopy(META)
        vn.processar(META, FONTE, b)
        self.assertEqual(m, META)


class PropostaDoCoachTest(unittest.TestCase):
    def prop(self, texto, **mud):
        return sh.comando(origin="coach", nonce="nonce-fake-0000000003", idempotency_key="k-00000010", params={"texto": texto}, **mud)

    def test_proposta_comum_passa_pela_caixa(self):
        r = vn.avaliar_proposta_coach(self.prop("Quando fizer o caderno, me conta em uma linha como foi."), boas())
        self.assertEqual(r["status"], "PROMOVER", r)

    def test_eco_do_texto_do_notebook_e_recusado(self):
        b = boas()
        b["n1-fonte.json"] = resp("n1-fonte.json", texto_literal="Resposta longa do notebook sobre os principios do caput do artigo.")
        r = vn.avaliar_proposta_coach(self.prop("Lembrete: Resposta longa do notebook sobre os principios do caput do artigo, ok?"), b)
        self.assertEqual((r["status"], r["codigo"]), ("RECUSADA", "ECO_DO_NOTEBOOK"))

    def test_proposta_de_outra_origem_ou_operacao_e_recusada_pela_caixa(self):
        for mud in ({"origin": "tutor"}, {"operation": "enviar_prompt_notebook"}, {"destination": "notebook_estudo"}):
            r = vn.avaliar_proposta_coach(sh.comando(**{**dict(origin="coach", nonce="nonce-fake-0000000003", idempotency_key="k-00000010"), **mud}), boas())
            self.assertNotEqual(r["status"], "PROMOVER", str(mud))

    def test_a_volta_so_aceita_mensagem_do_coach_mesmo_que_a_caixa_aceite_outra_operacao(self):
        lembrete = sh.comando(origin="coach", operation="criar_lembrete", destination="agenda_proprietario", nonce="nonce-fake-0000000004",
                              params={"atividade_ids": ["UFMS-002"], "lembrete_sha256": "a" * 64}, idempotency_key="k-00000011")
        r = vn.avaliar_proposta_coach(lembrete, boas())
        self.assertEqual((r["status"], r["codigo"]), ("RECUSADA", "PROPOSTA_NAO_E_DO_COACH"))
        tutor = sh.comando(nonce="nonce-fake-0000000005", idempotency_key="k-00000012")
        self.assertEqual(vn.avaliar_proposta_coach(tutor, boas())["codigo"], "PROPOSTA_NAO_E_DO_COACH")

    def test_proposta_com_dado_pessoal_ou_lixo_e_recusada(self):
        self.assertNotEqual(vn.avaliar_proposta_coach(self.prop("Meu CPF é 123.456.789-09"), boas())["status"], "PROMOVER")
        self.assertNotEqual(vn.avaliar_proposta_coach(None, boas())["status"], "PROMOVER")
        self.assertNotEqual(vn.avaliar_proposta_coach("texto", boas())["status"], "PROMOVER")


class CLITest(unittest.TestCase):
    def test_cli_le_o_checkout_e_devolve_codigo_de_saida(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "meta.json").write_text(json.dumps(META, ensure_ascii=False), encoding="utf-8")
            (d / "fonte.txt").write_text(FONTE, encoding="utf-8")
            (d / "ent/comandos/respostas").mkdir(parents=True)
            args = ["--entrada", str(d / "ent"), "--meta", str(d / "meta.json"), "--fonte", str(d / "fonte.txt")]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(vn.main(args), 2)  # nenhuma resposta ainda
            self.assertEqual(json.loads(out.getvalue())["relatorio"]["pendentes"], 3)
            for nome, bruto in boas().items():
                (d / "ent/comandos/respostas" / nome).write_bytes(bruto)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(vn.main(args), 0)
            self.assertEqual(json.loads(out.getvalue())["relatorio"]["veredito"], vn.PRONTO)


if __name__ == "__main__":
    unittest.main()
