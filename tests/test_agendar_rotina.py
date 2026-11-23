"""ZAPIA-APL (E24, E26): operação `agendar_rotina` aplicada ao contrato. Contraprovas em ALTA e MEDIA: modelo preso à origem, janela de 15 min a 24 h,
teto por origem, alvo promovido, chave de parada, forma fechada, modelos de instrução com hash e URLs literais. Offline, dados fictícios.
NÃO prova que a Zapia crie a rotina (autorrelato até o recibo e o verificador)."""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import agendar_rotina as ar  # noqa: E402
import agent_commands  # noqa: E402
import agents_gate  # noqa: E402
import command_box as cb  # noqa: E402
import command_box_runner as cbr  # noqa: E402
import command_params_schema as cps  # noqa: E402
import promotion_runner as pr  # noqa: E402
import test_command_box as tcb  # noqa: E402
import test_promotion_runner as tpr  # noqa: E402

AGORA = datetime(2026, 11, 23, 12, 0, 0, tzinfo=timezone.utc)
H1, H2 = "a" * 64, "b" * 64
HOJE = "2026-11-23"


def params(modelo="F1_ENTREGA_UNICA", quando="2026-11-23T13:00:00Z", hashes=None):
    if hashes is None:
        hashes = [H1] if ar.MODELOS[modelo]["hashes"] else []
    return {"modelo": modelo, "agendado_utc": quando, "comandos_sha256": hashes}


def contexto(**mudar):
    c = {"agendar_rotina_habilitada": True, "hashes_promovidos": [H1], "agendamentos_do_dia": []}
    c.update(mudar)
    return c


def comando(origem="coach", p=None, **mudar):
    base = {"schema_version": agent_commands.load_schema()["schema_version"], "origin": origem, "operation": "agendar_rotina", "destination": "zapia_rotina",
            "params": p if p is not None else params(), "idempotency_key": f"agenda-{origem}-0001", "nonce": f"nonce-agenda-{origem}-000001",
            "issued_at": "2026-11-23T12:00:00Z"}
    base.update(mudar)
    return base


def caixa_ctx(**mudar):
    c = {"agora": AGORA, "ledger": agent_commands.CommandLedger(), "dia_de_descanso": False, "atividades_pendentes": [], "chaves_do_dia": []}
    c.update(contexto())
    c.update(mudar)
    return c


class FormaTeste(unittest.TestCase):
    def test_forma_valida_por_modelo(self):
        for m in ar.MODELOS:
            self.assertIsNone(ar.validar_forma(params(m)), m)

    def test_campo_extra_ou_ausente_e_recusado(self):
        p = params(); p["texto"] = "livre"
        self.assertEqual(ar.validar_forma(p), "PARAMS_CAMPO_DESCONHECIDO")
        p = params(); del p["modelo"]
        self.assertEqual(ar.validar_forma(p), "PARAMS_CAMPO_DESCONHECIDO")
        self.assertEqual(ar.validar_forma("x"), "PARAMS_CAMPO_DESCONHECIDO")

    def test_modelo_desconhecido_ou_nao_texto(self):
        for m in ("OUTRO", "", None, 5, ["F1_ENTREGA_UNICA"]):
            p = params(); p["modelo"] = m
            self.assertEqual(ar.validar_forma(p), "PARAMS_MODELO_DESCONHECIDO", repr(m))

    def test_agendamento_mal_formado(self):
        for q in ("2026-11-23 13:00:00", "2026-11-23T13:00:00+00:00", "amanha", "2026-13-40T99:99:99Z", "2026-11-3T13:00:00Z", None, 5):
            self.assertEqual(ar.validar_forma(params(quando=q)), "PARAMS_AGENDAMENTO_INVALIDO", repr(q))

    def test_hashes_no_numero_do_modelo_sem_repeticao_e_hex(self):
        self.assertEqual(ar.validar_forma(params("F1_ENTREGA_UNICA", hashes=[])), "PARAMS_LISTA_INVALIDA")
        self.assertEqual(ar.validar_forma(params("F1_ENTREGA_UNICA", hashes=[H1, H2])), "PARAMS_LISTA_INVALIDA")
        self.assertEqual(ar.validar_forma(params("BRIEFING_DIARIO", hashes=[H1])), "PARAMS_LISTA_INVALIDA")
        self.assertEqual(ar.validar_forma(params("F1_ENTREGA_UNICA", hashes="x")), "PARAMS_LISTA_INVALIDA")
        for ruim in ("A" * 64, "a" * 63, "z" * 64, 5, None):
            self.assertEqual(ar.validar_forma(params("F1_ENTREGA_UNICA", hashes=[ruim])), "PARAMS_HASH_INVALIDO", repr(ruim))


class DecidirTeste(unittest.TestCase):
    def decidir(self, origem="coach", p=None, emitido=AGORA, **ctx):
        return ar.decidir(origem, p if p is not None else params(), emitido, contexto(**ctx))

    def test_pedido_valido_passa(self):
        self.assertIsNone(self.decidir())
        self.assertIsNone(self.decidir("tutor"))
        self.assertIsNone(self.decidir("tutor", params("ROTINA_ESTUDO_DIARIA")))
        self.assertIsNone(self.decidir("coach", params("BRIEFING_DIARIO")))

    def test_chave_de_parada_falsa_ausente_ou_nao_booleana_recusa(self):
        for v in (False, None, "true", 1, [True]):
            self.assertEqual(self.decidir(agendar_rotina_habilitada=v), "ROTINA_PARADA", repr(v))
        self.assertEqual(ar.decidir("coach", params(), AGORA, {"hashes_promovidos": [H1], "agendamentos_do_dia": []}), "ROTINA_PARADA")

    def test_modelo_preso_a_origem(self):
        self.assertEqual(self.decidir("coach", params("ROTINA_ESTUDO_DIARIA")), "ORIGEM_FORA_DO_MODELO")
        self.assertEqual(self.decidir("coach", params("ROTINA_ESTUDO_SEMANAL")), "ORIGEM_FORA_DO_MODELO")
        self.assertEqual(self.decidir("tutor", params("BRIEFING_DIARIO")), "ORIGEM_FORA_DO_MODELO")
        self.assertEqual(self.decidir("zapia"), "ORIGEM_FORA_DO_MODELO")

    def test_janela_de_15_minutos_a_24_horas(self):
        base = AGORA
        casos = [(timedelta(minutes=14, seconds=59), "AGENDAMENTO_FORA_DA_JANELA"), (timedelta(minutes=15), None), (timedelta(hours=24), None),
                 (timedelta(hours=24, seconds=1), "AGENDAMENTO_FORA_DA_JANELA"), (timedelta(seconds=-1), "AGENDAMENTO_FORA_DA_JANELA"), (timedelta(0), "AGENDAMENTO_FORA_DA_JANELA")]
        for delta, esperado in casos:
            q = (base + delta).strftime("%Y-%m-%dT%H:%M:%SZ")
            self.assertEqual(self.decidir(p=params(quando=q)), esperado, str(delta))

    def test_relogio_sem_fuso_recusa(self):
        self.assertEqual(self.decidir(emitido=datetime(2026, 11, 23, 12, 0, 0)), "RELOGIO_AUSENTE")
        self.assertEqual(self.decidir(emitido="2026-11-23T12:00:00Z"), "RELOGIO_AUSENTE")

    def test_alvo_precisa_ser_comando_ja_promovido(self):
        self.assertEqual(self.decidir(hashes_promovidos=[H2]), "ALVO_NAO_PROMOVIDO")
        self.assertEqual(self.decidir(hashes_promovidos=[]), "ALVO_NAO_PROMOVIDO")
        self.assertEqual(self.decidir(hashes_promovidos=None), "ALVOS_DESCONHECIDOS")
        self.assertEqual(self.decidir(hashes_promovidos="x"), "ALVOS_DESCONHECIDOS")

    def test_modelo_de_escuta_nao_exige_alvo_mas_exige_o_teto_conhecido(self):
        self.assertIsNone(self.decidir("coach", params("BRIEFING_DIARIO"), hashes_promovidos=None))
        self.assertEqual(self.decidir("coach", params("BRIEFING_DIARIO"), agendamentos_do_dia=None), "TETO_DESCONHECIDO")

    def test_teto_de_um_pedido_por_dia_por_origem(self):
        self.assertEqual(self.decidir("coach", agendamentos_do_dia=["coach"]), "TETO_DIARIO_AGENDAMENTO")
        self.assertIsNone(self.decidir("coach", agendamentos_do_dia=["tutor"]))  # a outra origem tem o seu teto
        self.assertEqual(self.decidir("tutor", agendamentos_do_dia=["tutor"]), "TETO_DIARIO_AGENDAMENTO")
        self.assertEqual(self.decidir(agendamentos_do_dia="coach"), "TETO_DESCONHECIDO")

    def test_forma_ruim_recusa_antes_de_qualquer_regra(self):
        self.assertEqual(self.decidir(p={"modelo": "F1_ENTREGA_UNICA"}), "PARAMS_CAMPO_DESCONHECIDO")


class ListaRepetidaTeste(unittest.TestCase):
    def test_hash_repetido_e_recusado_em_modelo_com_varios_alvos(self):
        original = dict(ar.MODELOS)
        self.addCleanup(lambda: (ar.MODELOS.clear(), ar.MODELOS.update(original)))
        ar.MODELOS["F1_ENTREGA_UNICA"] = dict(original["F1_ENTREGA_UNICA"], hashes=2)
        self.assertEqual(ar.validar_forma(params(hashes=[H1, H1])), "PARAMS_LISTA_INVALIDA")
        self.assertIsNone(ar.validar_forma(params(hashes=[H1, H2])))


class ChaveDeParadaTeste(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def escrever(self, obj):
        (self.tmp / "settings.json").write_text(json.dumps(obj), encoding="utf-8")

    def test_a_chave_entregue_esta_ligada_uma_vez_e_o_settings_do_repositorio_a_le(self):
        self.assertIs(ar.flag_habilitada(ROOT), True)
        self.assertEqual((ROOT / "settings.json").read_text(encoding="utf-8").count('"agendar_rotina_enabled"'), 1)

    def test_valores_e_leituras_que_viram_parada(self):
        self.escrever({"automation": {"agendar_rotina_enabled": False}})
        self.assertIs(ar.flag_habilitada(self.tmp), False)
        for obj in ({}, {"automation": {"agendar_rotina_enabled": "true"}}, {"a": {"agendar_rotina_enabled": True}, "b": {"agendar_rotina_enabled": True}}):
            self.escrever(obj)
            self.assertIsNone(ar.flag_habilitada(self.tmp), obj)
        (self.tmp / "settings.json").write_text("{nao json", encoding="utf-8")
        self.assertIsNone(ar.flag_habilitada(self.tmp))
        self.assertIsNone(ar.flag_habilitada(self.tmp / "nada"))


class CaixaTeste(unittest.TestCase):
    """A operação passa pela caixa de comandos (command_box.validar), com o contexto injetado."""

    def validar(self, c=None, **ctx):
        return cb.validar("a.json", json.dumps(c if c is not None else comando(), ensure_ascii=False).encode("utf-8"), caixa_ctx(**ctx))

    def test_pedido_valido_de_cada_origem_e_promovido(self):
        for origem in ("coach", "tutor"):
            r = self.validar(comando(origem))
            self.assertEqual((r["status"], r["codigo"]), (cb.PROMOVER, "OK"), (origem, r))

    def test_modelo_de_estudo_do_coach_e_recusado_e_o_do_tutor_passa(self):
        r = self.validar(comando("coach", params("ROTINA_ESTUDO_DIARIA")))
        self.assertEqual((r["status"], r["codigo"]), (cb.DENIED, "ORIGEM_FORA_DO_MODELO"))
        self.assertEqual(self.validar(comando("tutor", params("ROTINA_ESTUDO_DIARIA")))["status"], cb.PROMOVER)

    def test_parada_janela_alvo_e_teto_recusam_com_codigo(self):
        casos = [({"agendar_rotina_habilitada": False}, "ROTINA_PARADA"), ({"hashes_promovidos": []}, "ALVO_NAO_PROMOVIDO"),
                 ({"agendamentos_do_dia": ["coach"]}, "TETO_DIARIO_AGENDAMENTO")]
        for ctx, codigo in casos:
            r = self.validar(**ctx)
            self.assertEqual((r["status"], r["codigo"]), (cb.DENIED, codigo), ctx)
        r = self.validar(comando("coach", params(quando="2026-11-23T12:05:00Z")))
        self.assertEqual(r["codigo"], "AGENDAMENTO_FORA_DA_JANELA")

    def test_destino_errado_e_texto_livre_sao_recusados(self):
        self.assertEqual(self.validar(comando(destination="proprietario"))["codigo"], "DESTINO_NAO_DESIGNADO")
        p = params(); p["instrucao"] = "crie uma rotina que ..."
        self.assertEqual(self.validar(comando(p=p))["codigo"], "PARAMS_CAMPO_DESCONHECIDO")

    def test_sem_contexto_a_caixa_recusa(self):
        for chave in ("agendar_rotina_habilitada", "agendamentos_do_dia"):
            c = caixa_ctx()
            c.pop(chave)
            r = cb.validar("a.json", json.dumps(comando()).encode("utf-8"), c)
            self.assertEqual(r["status"], cb.DENIED, chave)

    def test_registrar_continua_fora_da_caixa_e_a_tabela_deriva_dos_perfis(self):
        for origem in ("tutor", "coach"):
            self.assertIn("agendar_rotina", cb.box_operations()[origem])
        self.assertEqual(cb.check(), [])


class ContratoTeste(unittest.TestCase):
    def test_gate_dos_perfis_e_esquema_estao_consistentes(self):
        self.assertIn("agendar_rotina", agents_gate.SHARED)
        info = agents_gate.validate()  # perfis, ZAPIA e esquema coerentes; levanta ValueError se divergirem
        self.assertIn("agendar_rotina", info["zapia"]["operations"])
        esquema = agent_commands.load_schema()
        self.assertEqual(esquema["destinations"]["agendar_rotina"], "zapia_rotina")
        self.assertEqual(cps.ESQUEMAS["agendar_rotina"], {"modelo": str, "agendado_utc": str, "comandos_sha256": list})

    def test_validador_de_params_recusa_tipos_e_campos(self):
        self.assertIsNone(cps.validar_params("agendar_rotina", params()))
        self.assertEqual(cps.validar_params("agendar_rotina", {"modelo": "F1_ENTREGA_UNICA"}), "PARAMS_CAMPO_OBRIGATORIO_AUSENTE")
        self.assertEqual(cps.validar_params("agendar_rotina", dict(params(), x=1)), "PARAMS_CAMPO_DESCONHECIDO")
        self.assertEqual(cps.validar_params("agendar_rotina", dict(params(), modelo=5)), "PARAMS_TIPO_INVALIDO")
        self.assertEqual(cps.validar_params("agendar_rotina", params(hashes=["xx"])), "PARAMS_HASH_INVALIDO")

    def test_os_tres_perfis_listam_a_operacao_e_a_zapia_cita_os_modelos_versionados(self):
        for rel in ("agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md"):
            self.assertIn("`agendar_rotina`", (ROOT / rel).read_text(encoding="utf-8"), rel)
        z = (ROOT / "agents" / "ZAPIA.md").read_text(encoding="utf-8")
        self.assertIn("config/rotina_instrucoes.json", z)
        self.assertIn("sem traduzir", z)


class InstrucaoTeste(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "config").mkdir()
        shutil.copy(ROOT / "config" / "rotina_instrucoes.json", self.tmp / "config" / "rotina_instrucoes.json")

    def mutar(self, chave, a, b):
        p = self.tmp / "config" / "rotina_instrucoes.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d[chave]["template"] = d[chave]["template"].replace(a, b)
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    def test_os_modelos_entregues_conferem(self):
        self.assertEqual(ar.check(ROOT), [])
        self.assertEqual(ar.main(["--check"]), 0)

    def test_hash_que_nao_confere_e_recusado(self):
        self.mutar("UNICA", "never reveal it", "never reveal it!")
        self.assertTrue(any("hash não confere" in e for e in ar.check(self.tmp)))

    def test_caminho_traduzido_e_recusado_mesmo_com_hash_refeito(self):
        p = self.tmp / "config" / "rotina_instrucoes.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["ESCUTA"]["template"] = d["ESCUTA"]["template"].replace("contents/comandos/recibos", "contents/commands/recibos") + " commands/x"
        d["ESCUTA"]["sha256"] = ar.hash_texto(d["ESCUTA"]["template"])
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        erros = ar.check(self.tmp)
        self.assertTrue(any("URL literal ausente" in e for e in erros) or any("traduzido" in e for e in erros), erros)

    def test_caminho_traduzido_extra_e_recusado_mesmo_com_as_tres_urls_literais(self):
        p = self.tmp / "config" / "rotina_instrucoes.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["UNICA"]["template"] += " Then GET https://api.github.com/repos/{REPO}/contents/commands/entregas ."
        d["UNICA"]["sha256"] = ar.hash_texto(d["UNICA"]["template"])
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        self.assertEqual([e for e in ar.check(self.tmp) if "literal ausente" in e], [])
        self.assertTrue(any("caminho traduzido" in e for e in ar.check(self.tmp)))

    def test_segredo_ou_falta_das_ordens_e_recusado(self):
        p = self.tmp / "config" / "rotina_instrucoes.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["UNICA"]["template"] += " Authorization: Bearer abcdefghijklmnop"
        d["UNICA"]["sha256"] = ar.hash_texto(d["UNICA"]["template"])
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(any("segredo" in e for e in ar.check(self.tmp)))
        self.mutar("ESCUTA", "Do not translate", "Please translate")
        self.assertTrue(any("sigilo" in e or "hash" in e for e in ar.check(self.tmp)))

    def test_arquivo_ausente_ou_ilegivel(self):
        (self.tmp / "config" / "rotina_instrucoes.json").write_text("{", encoding="utf-8")
        self.assertEqual(ar.check(self.tmp), ["config/rotina_instrucoes.json ausente ou ilegível"])

    def test_renderiza_com_urls_completos_hash_e_sem_marcador_sobrando(self):
        t = ar.renderizar("F1_ENTREGA_UNICA", repo="Andraus35/ufms-meu-estudo-entrada", credencial="github_ufms_repo_token",
                          agendado_utc="2026-11-24T14:00:00Z", hashes=[H1], origem="coach")
        self.assertIn("https://api.github.com/repos/Andraus35/ufms-meu-estudo-entrada/contents/comandos/recibos", t)
        self.assertIn(H1, t)
        self.assertIn("2026-11-24T14:00:00Z", t)
        self.assertNotIn("commands/", t)
        for marcador in ("{REPO}", "{HASH}", "{CREDENCIAL}", "{AGENDADO_UTC}", "{DIAS}", "{ORIGEM}"):
            self.assertNotIn(marcador, t)

    def test_escuta_fixa_a_origem_e_os_dias(self):
        t = ar.renderizar("ROTINA_ESTUDO_SEMANAL", repo="Andraus35/ufms-meu-estudo-entrada", credencial="github_ufms_repo_token",
                          agendado_utc="2026-11-24T14:00:00Z", origem="tutor")
        self.assertIn("for 7 days", t)
        self.assertIn("origin is exactly tutor", t)

    def test_renderizacao_recusa_parametro_ruim(self):
        base = dict(repo="Andraus35/ufms-meu-estudo-entrada", credencial="github_ufms_repo_token", agendado_utc="2026-11-24T14:00:00Z")
        with self.assertRaises(ValueError):
            ar.renderizar("F1_ENTREGA_UNICA", **base, hashes=[])  # falta o hash
        with self.assertRaises(ValueError):
            ar.renderizar("F1_ENTREGA_UNICA", **dict(base, repo="x y/z"), hashes=[H1])
        with self.assertRaises(ValueError):
            ar.renderizar("F1_ENTREGA_UNICA", **dict(base, credencial="ghp_abc def"), hashes=[H1])
        with self.assertRaises(ValueError):
            ar.renderizar("BRIEFING_DIARIO", **base, origem="tutor")  # origem fora do modelo
        with self.assertRaises(ValueError):
            ar.renderizar("OUTRO", **base)
        with self.assertRaises(ValueError):
            ar.renderizar("F1_ENTREGA_UNICA", **dict(base, agendado_utc="amanha"), hashes=[H1])
        self.assertEqual(ar.main(["--instrucao", "F1_ENTREGA_UNICA", "--agendado", "amanha"]), 2)


class RunnerTeste(unittest.TestCase):
    """Em série: o pedido promovido ocupa o teto da origem e o comando promovido vira alvo válido para o pedido seguinte."""

    def setUp(self):
        self.gh = tpr.GitHubFalso()
        self.caixa = cbr.Caixa(pr.GitHubApi(tpr.TOKEN_ENTRADA, self.gh.transporte), tpr.ENTRADA)

    def rodar(self, entradas, **sobre):
        c = {"escritas_habilitadas": True, "agora": AGORA, "execucao": "77", "validador_sha": tpr.SHA, "validador_sha_fixado": tpr.SHA,
             "dia_de_descanso": False, "atividades_pendentes": [], "chaves_do_dia": [], "agendar_rotina_habilitada": True,
             "hashes_promovidos": [H1], "agendamentos_do_dia": []}
        c.update(sobre)
        return cbr.executar(entradas, c, self.caixa)

    def entrada(self, nome, c):
        return (nome, json.dumps(c, ensure_ascii=False).encode("utf-8"))

    def test_segundo_pedido_da_mesma_origem_na_mesma_execucao_e_recusado(self):
        a = comando("coach"); b = comando("coach", nonce="nonce-agenda-coach-000002", idempotency_key="agenda-coach-0002")
        res = self.rodar([self.entrada("a.json", a), self.entrada("b.json", b)])
        status = {i["entrada_id"]: (i["status"], i["codigo"]) for i in res["itens"]}
        self.assertEqual(status["a.json"], ("PROMOVER", "OK"))
        self.assertEqual(status["b.json"], ("DENIED", "TETO_DIARIO_AGENDAMENTO"))

    def test_origens_diferentes_tem_cada_uma_o_seu_pedido(self):
        res = self.rodar([self.entrada("a.json", comando("coach")), self.entrada("b.json", comando("tutor"))])
        self.assertEqual([i["status"] for i in res["itens"]], ["PROMOVER", "PROMOVER"])

    def test_parada_no_contexto_recusa_e_contexto_ausente_recusa(self):
        res = self.rodar([self.entrada("a.json", comando())], agendar_rotina_habilitada=False)
        self.assertEqual(res["itens"][0]["codigo"], "ROTINA_PARADA")
        res = self.rodar([self.entrada("c.json", comando(nonce="nonce-agenda-coach-000009", idempotency_key="agenda-coach-0009"))], agendamentos_do_dia=None, hashes_promovidos=None)
        self.assertEqual(res["itens"][0]["status"], "DENIED")

    def test_comando_promovido_na_mesma_execucao_vira_alvo_valido_apenas_depois_dele(self):
        msg = {"schema_version": agent_commands.load_schema()["schema_version"], "origin": "coach", "operation": "enviar_mensagem", "destination": "proprietario",
               "params": {"texto": "Teste de rotina, sem dado pessoal."}, "idempotency_key": "rotina-2026-11-23-briefing-dia", "nonce": "nonce-msg-coach-0000001",
               "issued_at": "2026-11-23T12:00:00Z"}
        alvo = cb.command_hash(msg)
        pedido = comando("coach", params(hashes=[alvo]))
        depois = self.rodar([self.entrada("a_msg.json", msg), self.entrada("b_agenda.json", pedido)], hashes_promovidos=[])
        self.assertEqual([(i["entrada_id"], i["status"]) for i in depois["itens"]], [("a_msg.json", "PROMOVER"), ("b_agenda.json", "PROMOVER")])
        gh2 = tpr.GitHubFalso()
        self.caixa = cbr.Caixa(pr.GitHubApi(tpr.TOKEN_ENTRADA, gh2.transporte), tpr.ENTRADA)
        antes = self.rodar([self.entrada("a_agenda.json", pedido), self.entrada("b_msg.json", msg)], hashes_promovidos=[])
        self.assertEqual((antes["itens"][0]["status"], antes["itens"][0]["codigo"]), ("DENIED", "ALVO_NAO_PROMOVIDO"))


if __name__ == "__main__":
    unittest.main()
