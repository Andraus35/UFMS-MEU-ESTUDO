"""GAP-B (GB-1 e GB-2). Cada achado nasceu como teste que falhava antes da correção.

GB-1: a classificação do dia (S15-R16) não existia em código; o Coach classificava à mão.
GB-2: `check_projection` só aceitava `gerado_em` como DATA, mas a S15-R5 exige idade máxima em horas (instante UTC): projeção com instante era recusada.
"""
import ast
import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import day_classifier as dc  # noqa: E402
import projection_generator as pg  # noqa: E402
import session_read_guard as g  # noqa: E402
from private_persistence_guard import PersistenceBlocked  # noqa: E402

REV_VENCIDA = {"topico": "Língua Portuguesa", "vence_em": "2026-11-18"}
REV_HOJE = {"topico": "Língua Inglesa", "vence_em": "2026-11-20"}
REV_FUTURA = {"topico": "Informática", "vence_em": "2026-11-27"}


def classe(**mud):
    base = dict(data_local="2026-11-20", descanso=False, tem_plano=True, atividades_do_dia=[], revisoes=[])
    base.update(mud)
    return dc.classificar_dia(**base)


class Gb1TabelaDeVerdadeTests(unittest.TestCase):
    def test_cada_classe(self):
        self.assertEqual(classe(descanso=True)["classe"], "DESCANSO")
        self.assertEqual(classe(tem_plano=False)["classe"], "SEM_PLANO")
        self.assertEqual(classe(revisoes=[REV_VENCIDA])["classe"], "REVISAO_VENCIDA")
        self.assertEqual(classe(revisoes=[REV_HOJE])["classe"], "DEVIDO_HOJE")
        self.assertEqual(classe(atividades_do_dia=["UFMS-002"])["classe"], "DEVIDO_HOJE")
        self.assertEqual(classe()["classe"], "SEM_ATIVIDADE")
        self.assertEqual(classe(revisoes=[REV_FUTURA])["classe"], "SEM_ATIVIDADE")  # revisão futura não é cobrança de hoje

    def test_precedencia_par_a_par(self):
        tudo = dict(revisoes=[REV_VENCIDA, REV_HOJE], atividades_do_dia=["UFMS-002"])
        self.assertEqual(classe(descanso=True, tem_plano=False, **tudo)["classe"], "DESCANSO")  # descanso vence SEM_PLANO e a vencida
        self.assertEqual(classe(tem_plano=False, **tudo)["classe"], "SEM_PLANO")  # sem plano vence a vencida
        self.assertEqual(classe(**tudo)["classe"], "REVISAO_VENCIDA")  # vencida vence a devida hoje
        self.assertEqual(classe(revisoes=[REV_HOJE], atividades_do_dia=["UFMS-002"])["classe"], "DEVIDO_HOJE")

    def test_vencida_aparece_como_vencida_e_nao_e_reagendada(self):
        r = classe(revisoes=[REV_HOJE, REV_VENCIDA, REV_FUTURA])
        self.assertEqual(r["revisoes_vencidas"], [REV_VENCIDA])
        self.assertEqual(r["revisoes_devidas"], [REV_HOJE])
        self.assertNotIn("reagendar", str(r).lower())

    def test_descanso_nao_esconde_a_vencida_mas_nao_cobra(self):
        r = classe(descanso=True, revisoes=[REV_VENCIDA])
        self.assertEqual((r["classe"], r["revisoes_vencidas"]), ("DESCANSO", [REV_VENCIDA]))  # informa, a mensagem não cobra (S3-R2)

    def test_mesma_entrada_mesma_classe_e_nao_altera_a_entrada(self):
        revs = [REV_VENCIDA, REV_HOJE]
        antes = copy.deepcopy(revs)
        self.assertEqual(classe(revisoes=revs), classe(revisoes=list(reversed(revs))))
        self.assertEqual(revs, antes)

    def test_virada_do_dia_local_vira_a_classe(self):
        self.assertEqual(classe(data_local="2026-11-19", revisoes=[REV_HOJE])["classe"], "SEM_ATIVIDADE")
        self.assertEqual(classe(data_local="2026-11-20", revisoes=[REV_HOJE])["classe"], "DEVIDO_HOJE")
        self.assertEqual(classe(data_local="2026-11-21", revisoes=[REV_HOJE])["classe"], "REVISAO_VENCIDA")

    def test_virada_de_mes_ano_e_29_de_fevereiro(self):
        rev = {"topico": "T", "vence_em": "2027-12-31"}
        self.assertEqual(classe(data_local="2028-01-01", revisoes=[rev])["classe"], "REVISAO_VENCIDA")
        bis = {"topico": "T", "vence_em": "2028-02-29"}
        self.assertEqual(classe(data_local="2028-02-29", revisoes=[bis])["classe"], "DEVIDO_HOJE")
        self.assertEqual(classe(data_local="2028-03-01", revisoes=[bis])["classe"], "REVISAO_VENCIDA")

    def test_entrada_desconhecida_ou_malformada_nao_classifica(self):
        for mud, codigo in (({"descanso": None}, "DESCANSO_DESCONHECIDO"), ({"tem_plano": None}, "PLANO_DESCONHECIDO"),
                            ({"descanso": "sim"}, "DESCANSO_DESCONHECIDO"), ({"data_local": "20/11/2026"}, "DATA_LOCAL_INVALIDA"),
                            ({"data_local": "2026-02-30"}, "DATA_LOCAL_INVALIDA"), ({"data_local": None}, "DATA_LOCAL_INVALIDA"),
                            ({"revisoes": "x"}, "REVISOES_INVALIDAS"), ({"revisoes": [{"topico": "T"}]}, "REVISOES_INVALIDAS"),
                            ({"revisoes": [{"topico": "T", "vence_em": "amanha"}]}, "REVISOES_INVALIDAS"),
                            ({"atividades_do_dia": "UFMS-002"}, "ATIVIDADES_INVALIDAS"), ({"atividades_do_dia": [1]}, "ATIVIDADES_INVALIDAS")):
            r = classe(**mud)
            self.assertEqual((r["classe"], r["erro"]), (None, codigo), mud)

    def test_classificar_pelo_instante_usa_o_dia_local_de_campo_grande(self):
        madrugada = datetime(2026, 11, 21, 2, 0, tzinfo=timezone.utc)  # 22:00 de 20/11 em Campo Grande
        r = dc.classificar_instante(madrugada, descanso=False, tem_plano=True, atividades_do_dia=[], revisoes=[REV_HOJE])
        self.assertEqual((r["classe"], r["data_local"]), ("DEVIDO_HOJE", "2026-11-20"))
        virou = datetime(2026, 11, 21, 4, 0, tzinfo=timezone.utc)
        r = dc.classificar_instante(virou, descanso=False, tem_plano=True, atividades_do_dia=[], revisoes=[REV_HOJE])
        self.assertEqual((r["classe"], r["data_local"]), ("REVISAO_VENCIDA", "2026-11-21"))

    def test_relogio_ausente_ou_sem_fuso_nao_classifica(self):
        for relogio in (None, datetime(2026, 11, 20, 12, 0), "2026-11-20"):
            r = dc.classificar_instante(relogio, descanso=False, tem_plano=True, atividades_do_dia=[], revisoes=[])
            self.assertEqual((r["classe"], r["erro"]), (None, "RELOGIO_AUSENTE"))

    def test_nenhuma_funcao_le_o_relogio_do_sistema(self):  # S15-R1: relógio só injetado
        arvore = ast.parse((ROOT / "scripts" / "day_classifier.py").read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            if isinstance(no, ast.Attribute) and no.attr in ("now", "today", "utcnow"):
                self.fail("day_classifier lê o relógio do sistema")
            if isinstance(no, ast.Import):
                self.assertFalse({a.name for a in no.names} & {"time", "requests", "urllib", "socket"})


AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


def proj(gerado_em):
    return {"schema": 1, "gerado_em": gerado_em, "niveis": [], "pendencias": [], "revisoes": []}


def instante(delta_horas):
    return (AGORA - timedelta(hours=delta_horas)).strftime("%Y-%m-%dT%H:%M:%SZ")


class Gb2InstanteUtcTests(unittest.TestCase):
    def test_check_projection_aceita_instante_utc_e_continua_aceitando_data(self):
        g.check_projection(proj("2026-11-20T11:00:00Z"))
        g.check_projection(proj("2026-11-20"))

    def test_instante_malformado_ou_impossivel_e_recusado(self):
        for ruim in ("2026-11-20T11:00:00", "2026-11-20T11:00:00+00:00", "2026-11-20T25:00:00Z", "2026-02-30T10:00:00Z", "2026-11-20 11:00:00Z",
                     "hoje", "", None, 20261120):
            with self.assertRaises(PersistenceBlocked, msg=repr(ruim)):
                g.check_projection(proj(ruim))

    def test_idades_de_1h_25h_e_80h_para_prazo(self):
        self.assertEqual(g.conferir_idade(proj(instante(1)), AGORA, "prazo"), {"decisao": "OK", "codigo": None, "horas": 1.0})
        self.assertEqual(g.conferir_idade(proj(instante(24)), AGORA, "prazo")["decisao"], "OK")  # no limite
        r = g.conferir_idade(proj(instante(25)), AGORA, "prazo")
        self.assertEqual((r["decisao"], r["codigo"]), ("RECUSA", "PROJECAO_VELHA_PARA_PRAZO"))
        self.assertEqual(g.conferir_idade(proj(instante(80)), AGORA, "prazo")["decisao"], "RECUSA")

    def test_orientacao_avisa_a_partir_de_73h_e_nao_recusa(self):
        self.assertEqual(g.conferir_idade(proj(instante(25)), AGORA, "orientacao")["decisao"], "OK")
        self.assertEqual(g.conferir_idade(proj(instante(72)), AGORA, "orientacao")["decisao"], "OK")
        r = g.conferir_idade(proj(instante(73)), AGORA, "orientacao")
        self.assertEqual((r["decisao"], r["codigo"]), ("AVISO", "PROJECAO_DEFASADA"))
        self.assertEqual(g.conferir_idade(proj(instante(80)), AGORA, "orientacao")["decisao"], "AVISO")

    def test_instante_no_futuro_ou_sem_gerado_em_recusa(self):
        futuro = (AGORA + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for uso in ("prazo", "orientacao"):
            self.assertEqual(g.conferir_idade(proj(futuro), AGORA, uso)["codigo"], "PROJECAO_NO_FUTURO", uso)
            sem = proj(None)
            sem.pop("gerado_em")
            self.assertEqual(g.conferir_idade(sem, AGORA, uso)["codigo"], "PROJECAO_SEM_GERADO_EM", uso)

    def test_data_sem_hora_nao_decide_prazo_mas_serve_a_orientacao(self):
        self.assertEqual(g.conferir_idade(proj("2026-11-20"), AGORA, "prazo")["codigo"], "PROJECAO_SEM_INSTANTE")
        self.assertEqual(g.conferir_idade(proj("2026-11-20"), AGORA, "orientacao")["decisao"], "OK")  # data de hoje; aviso só se passar de 72h por dia
        self.assertEqual(g.conferir_idade(proj("2026-11-10"), AGORA, "orientacao")["decisao"], "AVISO")

    def test_relogio_ausente_uso_desconhecido_e_limites_ajustaveis(self):
        for relogio in (None, datetime(2026, 11, 20, 12, 0)):
            self.assertEqual(g.conferir_idade(proj(instante(1)), relogio, "prazo")["codigo"], "RELOGIO_AUSENTE")
        self.assertEqual(g.conferir_idade(proj(instante(1)), AGORA, "outro")["codigo"], "USO_DESCONHECIDO")
        self.assertEqual(g.conferir_idade(proj(instante(5)), AGORA, "prazo", limite_prazo_h=4)["decisao"], "RECUSA")  # ajustável (S15-R5)

    def test_gerador_de_projecao_emite_instante_utc_e_a_guarda_aceita(self):
        self.assertRegex(pg.formatar_gerado_em(AGORA), r"^2026-11-20T12:00:00Z$")
        g.check_projection(proj(pg.formatar_gerado_em(AGORA)))
        com_fuso = datetime(2026, 11, 20, 23, 30, tzinfo=timezone(timedelta(hours=-4)))
        self.assertEqual(pg.formatar_gerado_em(com_fuso), "2026-11-21T03:30:00Z")  # sempre UTC


if __name__ == "__main__":
    unittest.main()
