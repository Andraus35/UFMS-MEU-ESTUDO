"""COR-B (AC-3, AC-4, AC-8 e decisor do teto diário; S8-R1, S15-R17): contraprovas offline, dados fictícios.

Cada achado tem teste que falhava antes da correção e contraprova do caso permitido (sem falso positivo)."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import command_box as cb  # noqa: E402
import command_idempotency as ci  # noqa: E402
import test_command_box as tcb  # noqa: E402

HOJE = "2026-11-17"
BRIEFING = f"rotina-{HOJE}-briefing-dia"
LEMBRETE2 = f"rotina-{HOJE}-lembrete2-UFMS-002"


def valida(c, **ctx):
    return cb.validar("c.json", tcb.raw(c), tcb.ctx(**ctx))


def msg_lembrete2(**mudar):
    return tcb.comando(origin="coach", idempotency_key=LEMBRETE2, **mudar)


def agenda(data):
    return tcb.comando(origin="coach", operation="consultar_agenda_minima", destination="agenda_proprietario", params={"data": data},
                       idempotency_key="k-00000009")


class Ac3ChaveBriefingTeste(unittest.TestCase):
    def test_briefing_com_id_livre_e_recusado(self):
        for ruim in ("x", "y", "outra", "DIA", "dia2"):
            r = valida(tcb.comando(idempotency_key=f"rotina-{HOJE}-briefing-{ruim}"))
            self.assertEqual((r["status"], r["codigo"]), (cb.DENIED, "CHAVE_BRIEFING_ID_INVALIDO"), ruim)

    def test_briefing_dia_continua_valido_e_repeticao_e_duplicada(self):
        contexto = tcb.ctx()
        self.assertEqual(cb.validar("a.json", tcb.raw(tcb.comando()), contexto)["status"], cb.PROMOVER)
        again = cb.validar("b.json", tcb.raw(tcb.comando(nonce="nonce-fake-0000000002")), contexto)
        self.assertEqual((again["status"], again["codigo"]), (cb.DUPLICADO, "IDEMPOTENTE"))

    def test_teto_um_por_tipo_e_um_lembrete2_por_dia(self):
        r = valida(msg_lembrete2(), chaves_do_dia=[BRIEFING, f"rotina-{HOJE}-lembrete2-UFMS-003"], atividades_pendentes=["UFMS-002", "UFMS-003"])
        self.assertEqual(r["codigo"], "TETO_DIARIO_TIPO")
        r2 = valida(msg_lembrete2(), chaves_do_dia=[BRIEFING], atividades_pendentes=["UFMS-002"])  # contraprova: 2º do dia, tipo novo
        self.assertEqual(r2["status"], cb.PROMOVER)

    def test_chave_de_outro_dia_nao_ocupa_o_teto_de_hoje(self):
        r = valida(tcb.comando(), chaves_do_dia=["rotina-2026-11-16-briefing-dia"])
        self.assertEqual(r["status"], cb.PROMOVER)

    def test_teto_desconhecido_recusa_a_chave_de_rotina_mas_nao_a_mensagem_comum(self):
        r = valida(tcb.comando(), chaves_do_dia=None)
        self.assertEqual(r["codigo"], "TETO_DESCONHECIDO")
        self.assertEqual(valida(tcb.comando(idempotency_key="k-00000001"), chaves_do_dia=None)["status"], cb.PROMOVER)

    def test_decisor_e_funcao_pura_do_dia_local(self):
        agora = datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc)  # 17/11 22:00 em Campo Grande
        self.assertIsNone(ci.decidir_rotina("enviar_mensagem", BRIEFING, {}, agora, descanso=False, pendentes=[], chaves_do_dia=[]))
        self.assertEqual(ci.decidir_rotina("enviar_mensagem", BRIEFING, {}, None, descanso=False, pendentes=[], chaves_do_dia=[]), "RELOGIO_AUSENTE")


class Ac4DescansoEPendenciaTeste(unittest.TestCase):
    def test_enviar_mensagem_lembrete2_em_descanso_e_recusado(self):
        self.assertEqual(valida(msg_lembrete2(), dia_de_descanso=True)["codigo"], "DIA_DE_DESCANSO")
        self.assertEqual(valida(msg_lembrete2(), dia_de_descanso=None)["codigo"], "DESCANSO_DESCONHECIDO")

    def test_lembrete2_exige_atividade_pendente(self):
        self.assertEqual(valida(msg_lembrete2(), atividades_pendentes=[])["codigo"], "SEM_ATIVIDADE_PENDENTE")
        self.assertEqual(valida(msg_lembrete2(), atividades_pendentes=["OUTRA-1"])["codigo"], "SEM_ATIVIDADE_PENDENTE")
        self.assertEqual(valida(msg_lembrete2(), atividades_pendentes=None)["codigo"], "PENDENCIA_DESCONHECIDA")
        self.assertEqual(valida(msg_lembrete2())["status"], cb.PROMOVER)  # contraprova: pendente e dia útil

    def test_criar_lembrete_com_atividade_nao_pendente_na_lista_e_recusado(self):
        params = {"atividade_ids": ["UFMS-002", "FORA-9"], "lembrete_sha256": "a" * 64}
        c = tcb.comando(origin="coach", operation="criar_lembrete", destination="agenda_proprietario", params=params, idempotency_key=LEMBRETE2)
        self.assertEqual(valida(c)["codigo"], "SEM_ATIVIDADE_PENDENTE")
        self.assertEqual(valida(c, atividades_pendentes=["UFMS-002", "FORA-9"])["status"], cb.PROMOVER)

    def test_briefing_e_acompanhamento_em_descanso_seguem_permitidos(self):
        self.assertEqual(valida(tcb.comando(), dia_de_descanso=True)["status"], cb.PROMOVER)  # S8-R1: mensagem curta no descanso


class Ac8LimitesTeste(unittest.TestCase):
    def test_janela_injetada_tem_teto(self):
        for ruim in (10 ** 9, cb.MAX_JANELA_SEGUNDOS + 1, 0, -5, True):
            self.assertEqual(valida(tcb.comando(), janela_segundos=ruim)["codigo"], "JANELA_INVALIDA", ruim)
        self.assertEqual(valida(tcb.comando(), janela_segundos=cb.MAX_JANELA_SEGUNDOS)["status"], cb.PROMOVER)

    def test_chave_rotina_em_maiusculas_nao_escapa_da_regra(self):
        for ruim in (f"ROTINA-{HOJE}-briefing-dia", f"Rotina-2020-01-01-briefing-dia", "rOtInA-x"):
            r = valida(tcb.comando(idempotency_key=ruim))
            self.assertEqual(r["codigo"], "CHAVE_ROTINA_INVALIDA", ruim)
        self.assertTrue(ci.eh_chave_de_rotina("ROTINA-1"))

    def test_agenda_so_hoje_ou_amanha(self):
        for ruim in ("2030-01-01", "2026-11-16", "2026-11-19"):
            self.assertEqual(valida(agenda(ruim))["codigo"], "AGENDA_DATA_FORA_DA_JANELA", ruim)
        for bom in (HOJE, "2026-11-18"):
            self.assertEqual(valida(agenda(bom))["status"], cb.PROMOVER, bom)

    def test_agenda_em_descanso_ou_desconhecido_e_recusada(self):
        self.assertEqual(valida(agenda(HOJE), dia_de_descanso=True)["codigo"], "DIA_DE_DESCANSO")
        self.assertEqual(valida(agenda(HOJE), dia_de_descanso=None)["codigo"], "DESCANSO_DESCONHECIDO")


if __name__ == "__main__":
    unittest.main()
