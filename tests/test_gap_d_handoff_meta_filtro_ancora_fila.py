"""GAP-D (GD-1 a GD-5). Cada achado nasceu como teste que falhava antes da correção.

GD-1: não existia formato estruturado Tutor→Coach (S13-R3, T3). GD-2: a meta pretendida não era um campo separado da disponibilidade.
GD-3: o filtro de dado pessoal não pegava texto de questão em prosa curta nos `params`. GD-4: sem âncora local da Lei 8.112.
GD-5: a fila exigia 10 fatores e SHA para uma consulta simples.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import agent_commands as ac  # noqa: E402
import decision_queue as dq  # noqa: E402
import notebook_prescriber as npr  # noqa: E402
import tutor_coach_handoff as th  # noqa: E402
import test_delivery_gate as tdg  # noqa: E402
import test_notebook_prescriber as tnp  # noqa: E402

OK = {"topico": "GER-LEG", "origem_item": "banco", "referencia_item": "TEC:Q-000123", "resposta": "certo", "fundamento_ref": "Lei 8.112 art. 116",
      "confianca": "alta", "assistencia": "H0", "tempo_segundos": 95,
      "codigos_erro": [{"codigo": "P-NEG", "evidencia": "marcou certo sem ver a negação", "hipotese": False}],
      "objetivo": "Reter o regime disciplinar", "reteste": {"item_novo": True}}


def reg(**mud):
    r = copy.deepcopy(OK)
    r.update(mud)
    return r


class Gd1RegistroDePassagemTests(unittest.TestCase):
    def test_registro_valido_e_aceito_e_encaminhado(self):
        r = th.validar_registro(OK)
        self.assertEqual((r["ok"], r["codigo"], r["destino"]), (True, None, "coach"))

    def test_campos_obrigatorios_ausentes_recusam_um_a_um(self):
        for campo in OK:
            r = copy.deepcopy(OK)
            del r[campo]
            res = th.validar_registro(r)
            self.assertEqual((res["ok"], res["codigo"], res["campo"]), (False, "CAMPO_OBRIGATORIO_AUSENTE", campo), campo)

    def test_campo_fora_da_lista_fechada_recusa(self):
        for extra in ("enunciado", "texto_questao", "alternativas", "nome_do_aluno", "qualquer"):
            res = th.validar_registro({**OK, extra: "x"})
            self.assertEqual((res["ok"], res["codigo"]), (False, "CAMPO_FORA_DA_LISTA"), extra)

    def test_sem_origem_sem_assistencia_ou_valores_fora_do_enum_recusam(self):
        for campo, valor in (("origem_item", "internet"), ("origem_item", None), ("assistencia", "H6"), ("assistencia", None), ("confianca", "total"),
                             ("resposta", "talvez"), ("topico", "TOPICO-INEXISTENTE")):
            res = th.validar_registro(reg(**{campo: valor}))
            self.assertFalse(res["ok"], (campo, valor))
            self.assertEqual(res["campo"], campo)

    def test_assistencia_desconhecida_nao_vira_h0(self):
        res = th.validar_registro(reg(assistencia="desconhecido"))
        self.assertTrue(res["ok"])
        self.assertEqual(res["independencia"], "desconhecida")
        self.assertEqual(th.validar_registro(reg(assistencia="H0"))["independencia"], "independente")
        self.assertEqual(th.validar_registro(reg(assistencia="H2"))["independencia"], "guiada")
        self.assertEqual(th.validar_registro(reg(assistencia="H4"))["independencia"], "assistida")

    def test_texto_de_questao_no_lugar_da_referencia_ou_em_texto_livre_recusa(self):
        enunciado = "Julgue o item a seguir: o servidor pode ser demitido sem processo."
        for campo in ("referencia_item", "fundamento_ref", "objetivo"):
            self.assertFalse(th.validar_registro(reg(**{campo: enunciado}))["ok"], campo)
        r = reg(codigos_erro=[{"codigo": "P-NEG", "evidencia": enunciado, "hipotese": False}])
        self.assertEqual(th.validar_registro(r)["codigo"], "TEXTO_DE_QUESTAO_OU_DADO_PESSOAL")

    def test_dado_pessoal_e_segredo_em_texto_livre_recusam(self):
        for texto in ("contato fulano@exemplo.com", "CPF 529.982.247-25", "token ghp_ABCDEFGH12345678"):
            self.assertFalse(th.validar_registro(reg(objetivo=texto))["ok"], texto)

    def test_codigos_de_erro_validos_evidencia_e_hipotese(self):
        for codigos in ([], [{"codigo": "X-ABC", "evidencia": "e", "hipotese": False}], [{"codigo": "P-NEG", "evidencia": "", "hipotese": False}],
                        [{"codigo": "P-NEG", "evidencia": "e", "hipotese": "sim"}], [{"codigo": "P-NEG", "evidencia": "e"}],
                        [{"codigo": "P-NEG", "evidencia": "e", "hipotese": False, "extra": 1}], "P-NEG",
                        [{"codigo": "P-NEG", "evidencia": "e", "hipotese": False}] * 7):
            if codigos == []:
                self.assertTrue(th.validar_registro(reg(codigos_erro=codigos))["ok"])  # acerto sem erro: lista vazia é válida
            else:
                self.assertFalse(th.validar_registro(reg(codigos_erro=codigos))["ok"], codigos)

    def test_reteste_exige_item_novo_verdadeiro(self):
        for reteste in ({"item_novo": False}, {}, {"item_novo": 1}, None, {"item_novo": True, "x": 1}):
            self.assertFalse(th.validar_registro(reg(reteste=reteste))["ok"], reteste)

    def test_tempo_so_inteiro_nao_negativo_e_limitado(self):
        for t in (-1, 3.5, True, "95", 36001, None):
            self.assertFalse(th.validar_registro(reg(tempo_segundos=t))["ok"], t)
        self.assertTrue(th.validar_registro(reg(tempo_segundos=0))["ok"])

    def test_registro_nao_objeto_recusa_sem_levantar(self):
        for ruim in (None, [], "x", 1):
            self.assertEqual(th.validar_registro(ruim)["codigo"], "REGISTRO_NAO_OBJETO")

    def test_encaminhamento_da_s13_r3(self):
        casos = (("L-KNO", "tutor"), ("L-REC", "tutor"), ("L-RET", "tutor"), ("L-HNT", "tutor"), ("P-CMD", "coach"), ("P-NEG", "coach"),
                 ("P-QNT", "coach"), ("P-EXT", "coach"), ("P-TEM", "coach"), ("P-DEC", "coach"), ("L-DIS", "ambos"), ("L-APP", "ambos"),
                 ("L-TRF", "ambos"), ("M-SRC", "diagnostico_complementar"), ("P-SEM", "diagnostico_complementar"))
        for codigo, destino in casos:
            self.assertEqual(th.encaminhar([{"codigo": codigo, "hipotese": False}]), destino, codigo)

    def test_causa_mista_ou_hipotese_vai_a_diagnostico_complementar(self):
        self.assertEqual(th.encaminhar([{"codigo": "L-KNO", "hipotese": False}, {"codigo": "P-NEG", "hipotese": False}]), "diagnostico_complementar")
        self.assertEqual(th.encaminhar([{"codigo": "P-NEG", "hipotese": True}]), "diagnostico_complementar")
        self.assertEqual(th.encaminhar([]), "diagnostico_complementar")
        self.assertEqual(th.encaminhar([{"codigo": "L-DIS", "hipotese": False}, {"codigo": "L-KNO", "hipotese": False}]), "ambos")

    def test_alta_confianca_com_erro_e_prioridade(self):
        self.assertTrue(th.validar_registro(OK)["prioridade"])
        self.assertFalse(th.validar_registro(reg(confianca="baixa"))["prioridade"])
        self.assertFalse(th.validar_registro(reg(codigos_erro=[]))["prioridade"])

    def test_nao_altera_a_entrada_e_e_deterministico(self):
        antes = copy.deepcopy(OK)
        self.assertEqual(th.validar_registro(OK), th.validar_registro(OK))
        self.assertEqual(OK, antes)


class Gd2MetaPretendidaTests(unittest.TestCase):
    def test_meta_sem_disponibilidade_fica_separada_e_sem_sugestao(self):
        r = tnp.prescribe(question_target=20)
        self.assertEqual(r["meta"], {"pretendida": 20, "disponivel": None, "status": "pretendida_sem_disponibilidade_confirmada"})
        self.assertIsNone(r["questions_suggested"])  # nunca inventa disponibilidade

    def test_meta_dentro_e_acima_da_disponibilidade(self):
        dentro = tnp.prescribe(question_target=5, availability={"status": "confirmed", "available_count": 9, "evidence_ref": "e1"})
        self.assertEqual(dentro["meta"], {"pretendida": 5, "disponivel": 9, "status": "dentro_da_disponibilidade"})
        acima = tnp.prescribe(question_target=20, availability={"status": "confirmed", "available_count": 7, "evidence_ref": "e1"})
        self.assertEqual(acima["meta"], {"pretendida": 20, "disponivel": 7, "status": "acima_da_disponibilidade"})
        self.assertEqual(acima["questions_suggested"], 7)

    def test_sem_meta(self):
        self.assertEqual(tnp.prescribe()["meta"], {"pretendida": None, "disponivel": None, "status": "sem_meta"})


class Gd3QuestaoEmProsaCurtaTests(unittest.TestCase):
    def test_prosa_curta_de_questao_nos_params_e_recusada(self):
        for texto in ("Julgue o item a seguir: o servidor tem direito a férias.", "Assinale a alternativa correta sobre o prazo.",
                      "(A) cinco dias (B) dez dias (C) quinze dias", "Gabarito: C", "marque a assertiva incorreta"):
            self.assertTrue(ac.texto_de_questao(texto), texto)
            self.assertEqual(ac._scan_params({"texto": texto}, ac.load_schema()), "PARAMS_TEXTO_DE_QUESTAO", texto)

    def test_orientacao_legitima_continua_aceita(self):
        for texto in ("Releia o enunciado e elimine duas alternativas.", "Revise as alternativas que misturam prazo e termo.",
                      "Na prova, marque primeiro o que você tem certeza.", "Faça um caderno de 10 questões de Legislação.",
                      "O item 3 da lista de revisão fica para amanhã."):
            self.assertFalse(ac.texto_de_questao(texto), texto)
            self.assertIsNone(ac._scan_params({"texto": texto}, ac.load_schema()), texto)

    def test_validador_de_comandos_e_o_verificador_de_entrega_recusam(self):
        r = tdg.vai(tdg.comando(params={"texto": "Julgue o item a seguir: o servidor tem direito a férias."}))
        self.assertEqual(r["decisao"], "RECUSADA")
        self.assertIn("comando_com_parametro_proibido", r["motivos"])

    def test_nao_trata_nao_texto_e_nao_levanta(self):
        for v in (None, 3, [], {}):
            self.assertFalse(ac.texto_de_questao(v))


ANCORA = {"norma": "Norma sintética de teste", "artigo": "art. 1", "pagina": "p. 1", "fonte": "teste://sintetico",
          "texto": "O prazo é de trinta dias contados da publicação do ato."}


def com_hash(a):
    return {**a, "sha256": th.hash_texto(a["texto"])}


class Gd4AncoraDaNormaTests(unittest.TestCase):
    def test_arquivo_de_ancoras_declara_que_o_texto_oficial_esta_pendente(self):
        c = json.loads((ROOT / "config" / "norma_ancoras.json").read_text(encoding="utf-8"))
        self.assertEqual(c["norma"], "Lei 8.112/1990")
        self.assertEqual(c["status"], "texto_oficial_pendente")
        self.assertEqual(c["ancoras"], [])  # nenhum texto inventado ou de memória
        self.assertIn("planalto.gov.br", c["fonte_oficial"])

    def test_sem_ancora_a_conferencia_recusa_em_vez_de_aprovar(self):
        r = th.conferir_citacao_norma("art. 116", "trinta dias", [])
        self.assertEqual((r["ok"], r["codigo"]), (False, "ANCORA_AUSENTE"))

    def test_citacao_que_consta_da_ancora_confere(self):
        r = th.conferir_citacao_norma("art. 1", "prazo é de trinta dias", [com_hash(ANCORA)])
        self.assertEqual((r["ok"], r["codigo"], r["fonte"]), (True, None, "teste://sintetico"))

    def test_citacao_que_extrapola_ou_de_outro_artigo_recusa(self):
        self.assertEqual(th.conferir_citacao_norma("art. 1", "prazo é de sessenta dias", [com_hash(ANCORA)])["codigo"], "TRECHO_FORA_DA_ANCORA")
        self.assertEqual(th.conferir_citacao_norma("art. 2", "prazo é de trinta dias", [com_hash(ANCORA)])["codigo"], "ANCORA_AUSENTE")

    def test_ancora_adulterada_hash_diverge_recusa(self):
        ruim = {**com_hash(ANCORA), "texto": ANCORA["texto"] + " e mais um prazo."}
        self.assertEqual(th.conferir_citacao_norma("art. 1", "prazo é de trinta dias", [ruim])["codigo"], "ANCORA_ADULTERADA")

    def test_trecho_curto_demais_nao_confere(self):
        self.assertEqual(th.conferir_citacao_norma("art. 1", "prazo", [com_hash(ANCORA)])["codigo"], "TRECHO_CURTO_DEMAIS")

    def test_ancora_malformada_recusa(self):
        for ruim in ({"artigo": "art. 1"}, {**com_hash(ANCORA), "extra": 1}, "x"):
            self.assertEqual(th.conferir_citacao_norma("art. 1", "prazo é de trinta dias", [ruim])["codigo"], "ANCORA_MALFORMADA")


def cand(cid, **fatores):
    return {"candidate_id": cid, "eligibility": "eligible", "topic_ids": ["GER-LEG"], "cargo_ids": ["523"], "priority_factors": fatores,
            "justification": "Tópico com tentativa registrada."}


class Gd5ConsultaSimplesTests(unittest.TestCase):
    def test_consulta_simples_aceita_poucos_fatores_e_sem_sha(self):
        s = dq.rank_simple([cand("a", feasibility=3, learning_need=2), cand("b", feasibility=1)], as_of="2026-11-21T12:00:00-04:00")
        self.assertEqual(s["selected_candidate_id"], "a")
        self.assertIsNone(s["source_commit"])
        self.assertIs(s["auditavel"], False)
        self.assertIs(s["simples"], True)
        self.assertEqual(s["probability_claims"], False)
        self.assertEqual(s["ranked"][0]["score_breakdown"]["learning_need"]["value"], 2)

    def test_fatores_ausentes_ficam_desconhecidos_e_nunca_zero(self):
        s = dq.rank_simple([cand("a", feasibility=3)], as_of="2026-11-21T12:00:00-04:00")
        faltantes = s["ranked"][0]["unknown_factors"]
        self.assertEqual(set(faltantes), set(dq.FACTOR_NAMES) - {"feasibility"})

    def test_modo_completo_continua_exigindo_sha_e_todos_os_fatores(self):
        with self.assertRaises(ValueError):
            dq.rank_candidates([cand("a", feasibility=3)], as_of="2026-11-21T12:00:00-04:00", source_commit=None, edital_version="e1")
        with self.assertRaises(ValueError):
            dq.rank_candidates([cand("a", feasibility=3)], as_of="2026-11-21T12:00:00-04:00", source_commit="a" * 40, edital_version="e1")

    def test_simples_recusa_fator_desconhecido_valor_invalido_e_as_of_sem_fuso(self):
        for c, as_of in ((cand("a", inventado=1), "2026-11-21T12:00:00-04:00"), (cand("a", feasibility=9), "2026-11-21T12:00:00-04:00"),
                         (cand("a", feasibility=1), "2026-11-21T12:00:00")):
            with self.assertRaises(ValueError):
                dq.rank_simple([c], as_of=as_of)

    def test_snapshot_simples_nao_se_passa_por_auditavel(self):
        s = dq.rank_simple([cand("a", feasibility=3)], as_of="2026-11-21T12:00:00-04:00")
        completo = dq.rank_candidates([{**cand("a"), "priority_factors": {n: (3 if n == "feasibility" else None) for n in dq.FACTOR_NAMES}}],
                                      as_of="2026-11-21T12:00:00-04:00", source_commit="a" * 40, edital_version="e1")
        self.assertNotIn("auditavel", completo)
        self.assertNotEqual(s["snapshot_id"], completo["snapshot_id"])

    def test_o_prescritor_aceita_o_snapshot_simples(self):
        s = dq.rank_simple([cand("a", feasibility=3)], as_of="2026-11-21T12:00:00-04:00")
        r = npr.prescribe_notebook(s, candidate_id="a", intervention="active_retrieval", objective="Reter o tópico", platform="TEC")
        self.assertEqual(r["source_snapshot"]["snapshot_id"], s["snapshot_id"])
        self.assertIsNone(r["source_snapshot"]["source_commit"])


if __name__ == "__main__":
    unittest.main()
