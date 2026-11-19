"""PROJ: gerador offline de projeções para sessões (consentimento v4, lista fechada, sem sintéticos). Só dados sintéticos de teste."""
import copy
import hashlib
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import core  # noqa: E402
import projection_generator as pg  # noqa: E402
import session_read_guard as g  # noqa: E402
from private_persistence_guard import PersistenceBlocked  # noqa: E402

DOC = (ROOT / "docs/governanca/E5_CONSENTIMENTO_V4_PROPOSTA_20261118.md").read_text(encoding="utf-8")
TEXTO = next(l[2:].strip() for l in DOC.splitlines() if l.startswith("> "))
AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
TOPICOS = core.topic_rows(ROOT)
T = "2026-11-19T12:00:00+00:00"


def consent(**mud):
    c = {"version": "v4", "scope": "resultados_estudo", "inclui": ["resultados_estudo", "plano_estudo", "leitura_projecoes_sessoes_app_claude"],
         "granted_at": "2026-11-19T12:00:00+00:00", "revoked_at": None, "text": TEXTO,
         "text_sha256": hashlib.sha256(TEXTO.encode("utf-8")).hexdigest()}
    c.update(mud)
    return c


def real(evento):
    return {"evento": evento, "envelope": {"origem": "tutor", "escritor": "fluxo"}}


def rec(cid="UFMS-001"):
    return {"event_id": "rec-" + cid, "type": "caderno_recomendado", "timestamp": T, "caderno_id": cid, "topic_ids": ["GER-LEG"]}


def res(cid="UFMS-001", eid="res-1"):
    return {"event_id": eid, "type": "resultado_recebido", "timestamp": T, "caderno_id": cid, "total": 12, "acertos": 8, "erros": 4,
            "topic_results": [{"topic_id": "GER-LEG", "attempted": 12, "correct": 8}]}


def revisao(topico="GER-PORT", due="2026-11-26T12:00:00+00:00"):
    return {"event_id": "rev-" + topico, "type": "revisao_agendada", "timestamp": T, "topic_id": topico, "due_at": due}


def bloqueia(teste, fn, trecho=""):
    with teste.assertRaises(PersistenceBlocked) as cm:
        fn()
    teste.assertIn(trecho, str(cm.exception))


def gerar(registros, c=None, agora=AGORA):
    return pg.gerar_projecao(registros, TOPICOS, consent() if c is None else c, agora)


def tentativa(topico="GER-LEG", n="1", data="2026-11-10", conjunto="CJ-1"):
    return {"event_id": "att-" + n, "type": "attempt_recorded", "schema_version": "1.0", "attempt_id": "A" + n, "recorded_at": data + "T11:00:00-04:00",
            "attempt_at": data + "T10:00:00-04:00", "recommendation_id": "REC-A" + n, "platform_notebook_id": "EXT-A" + n,
            "source_ref": "synthetic://proj/A" + n, "independence": "without_consultation", "familiarity": "new", "diversity": "varied",
            "source_kind": "platform_export", "confidence": "secure", "item_set_id": conjunto, "total": 10, "acertos": 7, "erros": 3,
            "topic_results": [{"topic_id": topico, "attempted": 10, "correct": 7}]}


class CaminhoFelizTests(unittest.TestCase):
    def test_historico_vazio_e_e0_sem_itens(self):
        p = gerar([])
        self.assertEqual(p, {"schema": 1, "gerado_em": "2026-11-20", "niveis": [], "pendencias": [], "revisoes": []})
        g.check_projection(p)

    def test_projecao_na_lista_fechada_com_pendencia_e_revisao(self):
        p = gerar([real(rec("UFMS-002")), real(res()), real(rec("UFMS-003")), real(revisao())])
        self.assertEqual(set(p), g.TOPO)
        self.assertEqual(p["niveis"], [{"topico": "Legislação geral e normas da UFMS", "nivel": "E2"}])
        self.assertEqual(p["pendencias"], [{"atividade_id": "UFMS-002", "tipo": "caderno"}, {"atividade_id": "UFMS-003", "tipo": "caderno"}])
        self.assertEqual(p["revisoes"], [{"topico": "Língua Portuguesa", "vence_em": "2026-11-26"}])
        g.check_projection(p)

    def test_nao_vaza_numeros_nem_ids_de_evento(self):
        texto = json.dumps(gerar([real(rec()), real(res())]), ensure_ascii=False)
        for proibido in ("acertos", "erros", "total", "attempted", "event_id", "res-1", "envelope", "escritor", "tutor"):
            self.assertNotIn(proibido, texto)

    def test_nao_muda_a_entrada_e_e_deterministico(self):
        regs = [real(rec()), real(res()), real(revisao())]
        antes = copy.deepcopy(regs)
        self.assertEqual(gerar(regs), gerar(regs))
        self.assertEqual(regs, antes)

    def test_nivel_por_topico_nao_repete_o_global(self):
        """Tópico com contexto completo chega a E3; tópico só com resultado por tópico fica em E2 (não herda o nível do outro)."""
        recomendacao = rec("UFMS-REC") | {"recommendation_id": "REC-A1"}
        regs = [real(recomendacao), real(tentativa("GER-LEG")), real(res("PORT-1", "res-p") | {"topic_results": [{"topic_id": "GER-PORT", "attempted": 12, "correct": 8}]})]
        p = gerar(regs)
        niveis = {i["topico"]: i["nivel"] for i in p["niveis"]}
        self.assertEqual(niveis, {"Legislação geral e normas da UFMS": "E3", "Língua Portuguesa": "E2"})

    def test_revisoes_em_ordem_de_vencimento_e_data_utc(self):
        regs = [real(revisao("GER-ING", "2026-12-30T12:00:00+00:00")), real(revisao("GER-PORT", "2026-11-21T12:00:00+00:00")),
                real(revisao("GER-LEG", "2026-11-26T23:30:00-04:00"))]
        p = gerar(regs)
        self.assertEqual([(r["topico"], r["vence_em"]) for r in p["revisoes"]],
                         [("Língua Portuguesa", "2026-11-21"), ("Legislação geral e normas da UFMS", "2026-11-27"), ("Língua Inglesa", "2026-12-30")])

    def test_vencimento_vem_do_evento_sem_recalculo(self):
        p = gerar([real(revisao("GER-ING", "2027-01-15T10:00:00+00:00"))])
        self.assertEqual(p["revisoes"], [{"topico": "Língua Inglesa", "vence_em": "2027-01-15"}])


class ContraprovasTests(unittest.TestCase):
    def test_sem_consentimento_v4_bloqueia_antes_de_olhar_os_registros(self):
        for c in (None, consent(version="v3"), consent(revoked_at="2026-11-19T13:00:00+00:00"),
                  consent(inclui=["resultados_estudo", "plano_estudo"]), consent(text_sha256="0" * 64)):
            bloqueia(self, lambda c=c: pg.gerar_projecao([real(rec())], TOPICOS, c, AGORA), "V4")
        # mesmo com registros malformados, a recusa é a do consentimento (V4), não a dos dados
        bloqueia(self, lambda: pg.gerar_projecao("lixo", TOPICOS, None, AGORA), "V4")

    def test_eventos_sinteticos_e_marcas_ambiguas_saem(self):
        sintetico = real(res("SINT-1", "res-s"))
        sintetico["envelope"]["sintetico"] = True
        marca_falsa = real(res("SINT-2", "res-f"))
        marca_falsa["envelope"]["sintetico"] = False
        sem_envelope = {"evento": res("SINT-3", "res-e")}
        envelope_ruim = {"evento": res("SINT-4", "res-r"), "envelope": "texto"}
        p = gerar([sintetico, marca_falsa, sem_envelope, envelope_ruim, "lixo", None, 7])
        self.assertEqual(p["niveis"], [])
        self.assertEqual(p["pendencias"], [])

    def test_sintetico_nao_contamina_o_real(self):
        sintetico = real(rec("SINT-9"))
        sintetico["envelope"]["sintetico"] = True
        p = gerar([sintetico, real(rec("UFMS-010"))])
        self.assertEqual(p["pendencias"], [{"atividade_id": "UFMS-010", "tipo": "caderno"}])

    def test_registro_real_sem_evento_ou_evento_invalido_bloqueia(self):
        bloqueia(self, lambda: gerar([{"envelope": {"origem": "tutor"}}]), "sem evento")
        bloqueia(self, lambda: gerar([{"evento": "texto", "envelope": {"origem": "tutor"}}]), "sem evento")
        ruim = res()
        ruim["acertos"] = 99
        bloqueia(self, lambda: gerar([real(ruim)]), "inválidos")
        bloqueia(self, lambda: gerar([real(rec()), real(rec())]), "inválidos")
        bloqueia(self, lambda: gerar([real({"event_id": "x", "type": "tipo_inventado", "timestamp": T})]), "inválidos")

    def test_topico_desconhecido_bloqueia(self):
        bloqueia(self, lambda: gerar([real(revisao("TOPICO-FALSO"))]), "inválidos")

    def test_identificador_de_atividade_com_conteudo_proibido_bloqueia(self):
        for cid in ("a@b.com", "https://x.y", "enunciado 1", "x" * 80, "com espaco"):
            bloqueia(self, lambda cid=cid: gerar([real(rec(cid))]))

    def test_entrada_que_nao_e_lista_bloqueia(self):
        for entrada in ("texto", {"evento": {}}, None, 3):
            bloqueia(self, lambda e=entrada: gerar(e), "registros inválidos")

    def test_horario_sem_fuso_bloqueia(self):
        bloqueia(self, lambda: gerar([], agora=datetime(2026, 11, 20, 12, 0)), "fuso")

    def test_so_projecao_nunca_historico_bruto(self):
        p = gerar([real(rec()), real(res())])
        self.assertEqual(g.authorize_session_read(consent(), "projecao", p, AGORA)["kind"], "projecao")
        for tipo in ("historico", "fila", "exportacao"):
            bloqueia(self, lambda t=tipo: g.authorize_session_read(consent(), t, p, AGORA), "projeções")

    def test_limite_de_itens_do_guarda_continua_valendo(self):
        p = gerar([])
        p["niveis"] = [{"topico": "Língua Portuguesa", "nivel": "E1"}] * (g.MAX_ITENS + 1)
        bloqueia(self, lambda: g.check_projection(p), "niveis")

    def test_importa_so_modulos_offline_da_lista_permitida(self):
        import ast
        arvore = ast.parse((ROOT / "scripts/projection_generator.py").read_text(encoding="utf-8"))
        usados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                usados |= {a.name.split(".")[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom):
                usados.add((no.module or "").split(".")[0])
        self.assertEqual(usados, {"copy", "datetime", "core", "evidence_projection", "private_persistence_guard", "session_read_guard"})
        chamadas = {n.func.id for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(chamadas & {"open", "exec", "eval", "__import__"})


if __name__ == "__main__":
    unittest.main()
