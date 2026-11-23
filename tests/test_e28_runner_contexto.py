"""ZAPIA-CTX (E28): o runner real alimenta `hashes_promovidos` e `agendamentos_do_dia` lendo a caixa. GitHub FALSO em memória.
Contraprovas: recibo ausente, hash divergente, dia virado, teto por origem, retomada, falha de API, formato ruim."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import command_box_runner as cbr  # noqa: E402
import promotion_runner as pr  # noqa: E402
import test_command_box as tcb  # noqa: E402
import test_command_box_runner as tcbr  # noqa: E402

AGORA = tcb.AGORA  # 2026-11-17T15:00Z = 11:00 em Campo Grande


def pedido(origem="coach", n=1, hashes=(), emitido="2026-11-17T15:00:00Z", quando="2026-11-17T17:00:00Z", modelo=None):
    modelo = modelo or ("F1_ENTREGA_UNICA" if hashes else ("BRIEFING_DIARIO" if origem == "coach" else "ROTINA_ESTUDO_DIARIA"))
    return tcb.comando(origin=origem, operation="agendar_rotina", destination="zapia_rotina",
                       params={"modelo": modelo, "agendado_utc": quando, "comandos_sha256": list(hashes)},
                       idempotency_key=f"agenda-{origem}-{n:04d}", nonce=f"nonce-agenda-{origem}-{n:06d}", issued_at=emitido)


class Base(tcbr.Base):
    def contexto(self, **sobre):
        c = super().contexto()
        c.update(agendar_rotina_habilitada=True)
        c.update(sobre)
        return c

    def promover(self, nome="alvo.json", **mud):
        res = self.rodar(self.entrar(nome, tcb.comando(**mud)))
        self.assertEqual(self.unico(res)["status"], "PROMOVER")
        h = json.loads(self.arquivos()["comandos/recibos/" + nome])["hash_corpo"]
        self.assertEqual(h, tcbr.cb.command_hash(json.loads(self.arquivos()["comandos/validados/" + nome])))
        return h

    def ctx_real(self, agora=AGORA):
        return cbr.ler_contexto_agendar(self.caixa, agora)

    def agendar(self, comando, nome="ag.json", agora=AGORA):
        sobre = self.ctx_real(agora)
        res = cbr.executar([self.entrar(nome, comando)], self.contexto(**sobre), self.caixa)
        return self.unico(res)


class LeituraTest(Base):
    def test_caixa_vazia_da_listas_vazias(self):
        self.assertEqual(self.ctx_real(), {"hashes_promovidos": [], "agendamentos_do_dia": []})

    def test_comando_promovido_com_recibo_vira_alvo_valido(self):
        h = self.promover()
        self.assertEqual(self.ctx_real()["hashes_promovidos"], [h])
        item = self.agendar(pedido(hashes=[h]))
        self.assertEqual((item["status"], item["codigo"]), ("PROMOVER", "OK"))

    def test_antes_do_ctx_o_pedido_era_recusado_e_agora_o_alvo_desconhecido_continua_recusado(self):
        item = self.agendar(pedido(hashes=["c" * 64]))
        self.assertEqual(item["codigo"], "ALVO_NAO_PROMOVIDO")

    def test_recibo_ausente_nao_promove(self):
        h = self.promover()
        del self.arquivos()["comandos/recibos/alvo.json"]
        self.assertEqual(self.ctx_real()["hashes_promovidos"], [])
        self.assertEqual(self.agendar(pedido(hashes=[h]))["codigo"], "ALVO_NAO_PROMOVIDO")

    def test_recibo_com_hash_divergente_nao_promove(self):
        h = self.promover()
        rec = json.loads(self.arquivos()["comandos/recibos/alvo.json"])
        rec["hash_corpo"] = "d" * 64
        self.arquivos()["comandos/recibos/alvo.json"] = json.dumps(rec).encode()
        self.assertEqual(self.ctx_real()["hashes_promovidos"], [])
        self.assertEqual(self.agendar(pedido(hashes=["d" * 64]))["codigo"], "ALVO_NAO_PROMOVIDO")
        self.assertEqual(self.agendar(pedido(hashes=[h], n=2), nome="ag2.json")["codigo"], "ALVO_NAO_PROMOVIDO")

    def test_validado_alterado_depois_do_recibo_nao_promove(self):
        self.promover()
        self.arquivos()["comandos/validados/alvo.json"] = tcb.raw(tcb.comando(params={"texto": "Outro texto fictício."}))
        self.assertEqual(self.ctx_real()["hashes_promovidos"], [])

    def test_recibo_rejeitado_ou_ilegivel_nao_promove(self):
        self.promover()
        for ruim in (b'{"status":"DENIED","hash_corpo":"x"}', b"nao e json", b"[]", b'{"status":"PROMOVER"}'):
            self.arquivos()["comandos/recibos/alvo.json"] = ruim
            self.assertEqual(self.ctx_real()["hashes_promovidos"], [], ruim)

    def test_recibo_com_hash_certo_mas_status_que_nao_e_promocao_nao_promove(self):
        h = self.promover()
        for status in ("DENIED", "DUPLICADO", "", None, True):
            self.arquivos()["comandos/recibos/alvo.json"] = json.dumps({"status": status, "hash_corpo": h}).encode()
            self.assertEqual(self.ctx_real()["hashes_promovidos"], [], repr(status))

    def test_validado_ilegivel_e_ignorado_sem_quebrar(self):
        self.promover()
        self.arquivos()["comandos/validados/lixo.json"] = b"\xff\xfe nao json"
        self.arquivos()["comandos/recibos/lixo.json"] = b"{}"
        self.assertEqual(len(self.ctx_real()["hashes_promovidos"]), 1)

    def test_pedido_do_dia_ocupa_o_teto_da_origem_e_so_dela(self):
        self.assertEqual(self.agendar(pedido("coach", 1))["codigo"], "OK")
        self.assertEqual(self.ctx_real()["agendamentos_do_dia"], ["coach"])
        self.assertEqual(self.agendar(pedido("coach", 2), nome="ag2.json")["codigo"], "TETO_DIARIO_AGENDAMENTO")
        self.assertEqual(self.agendar(pedido("tutor", 3, modelo="ROTINA_ESTUDO_SEMANAL"), nome="ag3.json")["codigo"], "OK")

    def test_dia_virado_libera_o_teto_e_o_dia_anterior_nao_conta(self):
        self.assertEqual(self.agendar(pedido("coach", 1))["codigo"], "OK")
        amanha = AGORA + timedelta(days=1)  # 11:00 do dia seguinte em Campo Grande
        self.assertEqual(self.ctx_real(amanha)["agendamentos_do_dia"], [])
        self.assertEqual(self.ctx_real(AGORA)["agendamentos_do_dia"], ["coach"])

    def test_virada_do_dia_local_e_em_campo_grande_nao_em_utc(self):
        self.assertEqual(self.agendar(pedido("coach", 1))["codigo"], "OK")  # 11:00 local de 17/11
        # 02:00 UTC de 18/11 ainda é 22:00 local de 17/11: continua o mesmo dia; 04:00 UTC já é 00:00 local de 18/11
        self.assertEqual(self.ctx_real(datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc))["agendamentos_do_dia"], ["coach"])
        self.assertEqual(self.ctx_real(datetime(2026, 11, 18, 4, 0, tzinfo=timezone.utc))["agendamentos_do_dia"], [])

    def test_relogio_sem_fuso_nao_informa_nada_e_o_pedido_e_recusado(self):
        self.assertEqual(self.ctx_real(datetime(2026, 11, 17, 15, 0)), {})
        self.assertEqual(self.ctx_real("agora"), {})
        res = cbr.executar([self.entrar("ag.json", pedido(hashes=["c" * 64]))], self.contexto(), self.caixa)
        self.assertEqual(self.unico(res)["codigo"], "ALVOS_DESCONHECIDOS")

    def test_pedido_validado_sem_recibo_ainda_ocupa_o_teto(self):
        self.agendar(pedido("coach", 1))
        del self.arquivos()["comandos/recibos/ag.json"]
        self.assertEqual(self.ctx_real()["agendamentos_do_dia"], ["coach"])

    def test_contexto_nao_carrega_dado_do_comando(self):
        self.promover()
        self.agendar(pedido("coach", 1))
        texto = json.dumps(self.ctx_real())
        self.assertNotIn("Revisão", texto)
        self.assertNotIn("nonce", texto)


class RetomadaEFalhasTest(Base):
    def test_retomada_do_pedido_ja_promovido_nao_e_recusada_pelo_proprio_teto(self):
        bruto = tcb.raw(pedido("coach", 1))
        self.arquivos()["comandos/validados/ag.json"] = bruto  # execução interrompida depois de promover
        self.arquivos()["comandos/ag.json"] = bruto
        sobre = self.ctx_real()
        self.assertEqual(sobre["agendamentos_do_dia"], ["coach"])
        res = cbr.executar([("ag.json", bruto)], self.contexto(**sobre), self.caixa)
        item = self.unico(res)
        self.assertEqual((item["status"], item["codigo"]), ("PROMOVER", "RETOMADA"))

    def test_retomada_nao_apaga_o_teto_de_outro_pedido_da_mesma_origem(self):
        a, b = tcb.raw(pedido("coach", 1)), tcb.raw(pedido("coach", 2))
        self.arquivos()["comandos/validados/a.json"] = a
        self.arquivos()["comandos/validados/b.json"] = b
        sobre = self.ctx_real()
        self.assertEqual(sobre["agendamentos_do_dia"], ["coach", "coach"])
        res = cbr.executar([("a.json", a)], self.contexto(**sobre), self.caixa)
        self.assertEqual(self.unico(res)["codigo"], "TETO_DIARIO_AGENDAMENTO")

    def test_falha_de_api_propaga_e_nada_e_inventado(self):
        def quebrado(metodo, url, cab, corpo, tempo):
            return 500, b"{}"
        caixa = cbr.Caixa(pr.GitHubApi(tpr_token(), quebrado), tcbr.ENTRADA)
        with self.assertRaises(pr.ApiError):
            cbr.ler_contexto_agendar(caixa, AGORA)

    def test_listagem_fora_do_formato_propaga(self):
        for resposta in (b'{"type":"file"}', b'[{"type":"file"}]', b'[1]'):
            caixa = cbr.Caixa(pr.GitHubApi(tpr_token(), lambda *a, r=resposta: (200, r)), tcbr.ENTRADA)
            with self.assertRaises(pr.ApiError):
                cbr.ler_contexto_agendar(caixa, AGORA)

    def test_pasta_ausente_e_caixa_vazia(self):
        self.assertEqual(self.caixa.listar("comandos/validados/"), [])

    def test_listar_ignora_subpasta_e_nome_invalido(self):
        self.arquivos()["comandos/validados/ok.json"] = b"{}"
        self.arquivos()["comandos/validados/sub/x.json"] = b"{}"
        self.assertEqual(self.caixa.listar("comandos/validados/"), ["ok.json"])


def tpr_token():
    import test_promotion_runner as tpr
    return tpr.TOKEN_ENTRADA


class CliTest(Base):
    def test_o_cli_alimenta_o_contexto_e_aceita_o_pedido_com_alvo_promovido(self):
        h = self.promover()
        pasta = self.tmp / "comandos"
        pasta.mkdir()
        (pasta / "ag.json").write_bytes(tcb.raw(pedido(hashes=[h])))
        # settings do validador: fluxo e chave de parada ligados
        (self.validador / "settings.json").write_text(json.dumps({"storage": {"private_flow_promotion_enabled": True},
                                                                  "automation": {"agendar_rotina_enabled": True}}))
        import io
        from contextlib import redirect_stdout
        saida = io.StringIO()
        with redirect_stdout(saida):
            rc = cbr.main(["--comandos", str(pasta), "--execucao", "9", "--validador-sha", tcbr.SHA, "--entrada-repo", tcbr.ENTRADA,
                           "--validador-dir", str(self.validador)], transporte=self.gh.transporte,
                          ambiente={"GH_TOKEN": tpr_token()}, agora=AGORA)
        resumo = json.loads(saida.getvalue())
        self.assertEqual(rc, 0, saida.getvalue())
        self.assertEqual(resumo["itens"][0]["codigo"], "OK")


if __name__ == "__main__":
    unittest.main()
