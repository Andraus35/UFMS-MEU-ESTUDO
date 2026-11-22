"""S20 F0/F1: ponta a ponta OFFLINE do caminho de ida e do recibo de volta, com a Zapia SIMULADA (leitor e `enviar` injetados).

Prova o código do nosso lado. NÃO prova que a Zapia tenha conector, rotina ou notificação (autorrelato, confiança C)."""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import command_box as cb  # noqa: E402
import command_box_runner as cbr  # noqa: E402
import promotion_runner as pr  # noqa: E402
import test_command_box as tcb  # noqa: E402
import test_promotion_runner as tpr  # noqa: E402
import zapia_entrega as ze  # noqa: E402

ENTRADA, SHA = tpr.ENTRADA, tpr.SHA


class Base(unittest.TestCase):
    def setUp(self):
        self.gh = tpr.GitHubFalso()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.caixa = cbr.Caixa(pr.GitHubApi(tpr.TOKEN_ENTRADA, self.gh.transporte), ENTRADA)
        self.enviadas, self.falhar = [], False

    def promover(self, *comandos, **sobre):
        entradas = []
        for i, c in enumerate(comandos):
            nome = f"c{i}.json"
            self.gh.repos[ENTRADA]["files"][f"comandos/{nome}"] = tcb.raw(c)
            entradas.append((nome, tcb.raw(c)))
        ctx = {"escritas_habilitadas": True, "agora": tcb.AGORA, "execucao": "77", "validador_sha": SHA, "validador_sha_fixado": SHA,
               "dia_de_descanso": False, "atividades_pendentes": [], "chaves_do_dia": []}
        ctx.update(sobre)
        return cbr.executar(entradas, ctx, self.caixa)

    def arquivos(self):
        return self.gh.repos[ENTRADA]["files"]

    def ler_zapia(self):
        """O que o conector de GitHub SIMULADO da Zapia enxerga: só validados e recibos."""
        listagem = {p: b for p, b in self.arquivos().items() if p.startswith("comandos/validados/")}
        recibos = {p.rsplit("/", 1)[-1]: json.loads(b)["hash_corpo"] for p, b in self.arquivos().items() if p.startswith("comandos/recibos/")}
        return listagem, recibos

    def enviar(self, texto):
        if self.falhar:
            raise RuntimeError("zapia fora do ar")
        self.enviadas.append(texto)
        return True

    def rodada(self, entregues=(), hoje=0, agora=None):
        listagem, recibos = self.ler_zapia()
        return ze.executar_rotina(listagem, recibos, entregues, self.enviar, agora or tcb.AGORA, hoje)

    def comando(self, origem="coach", chave="rotina-2026-11-17-briefing-dia", nonce="nonce-fake-0000000001", texto="Revisão pendente de teste fictício.", **mais):
        return tcb.comando(origin=origem, idempotency_key=chave, nonce=nonce, params={"texto": texto}, **mais)


class CaminhoDeIdaEVoltaTeste(Base):
    def test_coach_ida_e_volta_com_recibo_de_mesmo_hash(self):
        self.assertEqual(self.promover(self.comando())["itens"][0]["codigo"], "OK")
        r = self.rodada()
        self.assertEqual([i["status"] for i in r["itens"]], [ze.ENTREGUE])
        self.assertEqual(self.enviadas, ["Coach (origem declarada): Revisão pendente de teste fictício."])
        _, recibos = self.ler_zapia()
        for nome, corpo in r["entregas"].items():  # a Zapia grava o recibo de volta SÓ na entrada
            self.assertIsNone(ze.conferir_entrega(corpo, recibos, nome))
            self.assertNotIn(b"Revis", corpo)  # o recibo de volta não leva o texto
            self.caixa.escrever(ze.ENTREGAS + nome, corpo)
        self.assertIn("comandos/entregas/c0.json", self.arquivos())

    def test_tutor_tambem_notifica_em_nome_dele(self):
        self.promover(self.comando(origem="tutor", chave="k-00000001"))
        self.rodada()
        self.assertTrue(self.enviadas[0].startswith("Tutor (origem declarada): "))

    def test_segunda_rodada_nao_entrega_de_novo(self):
        self.promover(self.comando())
        r1 = self.rodada()
        entregues = {json.loads(b)["hash_corpo"] for b in r1["entregas"].values()}
        r2 = self.rodada(entregues=entregues)
        self.assertEqual([i["status"] for i in r2["itens"]], ["JA_ENTREGUE"])
        self.assertEqual(len(self.enviadas), 1)


class FalhaSeguraTeste(Base):
    def test_sem_recibo_ou_hash_alterado_nada_e_enviado(self):
        self.promover(self.comando())
        listagem, recibos = self.ler_zapia()
        sem_recibo = ze.executar_rotina(listagem, {}, (), self.enviar, tcb.AGORA)
        alterado = {p: b.replace(b"pendente", b"urgente!") for p, b in listagem.items()}
        com_hash_errado = ze.executar_rotina(alterado, recibos, (), self.enviar, tcb.AGORA)
        self.assertEqual((sem_recibo["itens"], com_hash_errado["itens"], self.enviadas), ([], [], []))

    def test_falha_no_envio_nao_gera_recibo_nem_reenvio_em_laco(self):
        self.promover(self.comando())
        self.falhar = True
        r = self.rodada()
        self.assertEqual((r["itens"][0]["codigo"], r["entregas"], self.enviadas), ("FALHA_NO_ENVIO", {}, []))

    def test_comando_expirado_nao_vira_notificacao(self):
        self.promover(self.comando())
        r = self.rodada(agora=tcb.AGORA + timedelta(hours=25))
        self.assertEqual((r["itens"][0]["codigo"], self.enviadas), ("COMANDO_EXPIRADO", []))
        r2 = self.rodada(agora=tcb.AGORA - timedelta(hours=1))  # relógio fora: comando "do futuro"
        self.assertEqual(r2["itens"][0]["codigo"], "COMANDO_EXPIRADO")

    def test_teto_diario_na_zapia(self):
        self.promover(self.comando())
        r = self.rodada(hoje=ze.TETO_POR_DIA)
        self.assertEqual((r["itens"][0]["codigo"], self.enviadas), ("TETO_DIARIO", []))

    def test_operacao_nao_suportada_e_ignorada_sem_efeito(self):
        agenda = tcb.comando(origin="coach", operation="consultar_agenda_minima", destination="agenda_proprietario", params={"data": "2026-11-17"},
                             idempotency_key="k-00000009")
        self.promover(agenda)
        r = self.rodada()
        self.assertEqual((r["itens"][0]["codigo"], self.enviadas), ("OPERACAO_NAO_SUPORTADA", []))

    def test_texto_ruim_e_recusado_tambem_no_lado_da_zapia_mesmo_com_hash_correto(self):
        ruim = self.comando(texto="Veja exemplo.com agora")  # a caixa já recusaria; simula caixa contornada com recibo de mesmo hash
        h = cb.command_hash(ruim)
        listagem, recibos = {"comandos/validados/x.json": tcb.raw(ruim)}, {"x.json": h}
        r = ze.executar_rotina(listagem, recibos, (), self.enviar, tcb.AGORA)
        self.assertEqual((r["itens"][0]["codigo"], self.enviadas), ("TEXTO_OU_ORIGEM_RECUSADOS", []))

    def test_origem_fora_de_tutor_e_coach_e_recusada(self):
        self.assertIsNone(ze.montar_notificacao(self.comando(origem="zapia")))
        self.assertIsNone(ze.montar_notificacao({"operation": "enviar_mensagem", "origin": "tutor", "params": {"texto": "ok", "extra": 1}}))

    def test_contexto_invalido_nao_envia(self):
        listagem, recibos = self.ler_zapia()
        self.assertEqual(ze.executar_rotina(listagem, recibos, (), self.enviar, None)["estado"], "CONTEXTO_INVALIDO")
        self.assertEqual(ze.executar_rotina(listagem, recibos, (), None, tcb.AGORA)["estado"], "CONTEXTO_INVALIDO")


class ReciboDeVoltaTeste(Base):
    def entrega(self, **mudar):
        self.promover(self.comando())
        r = self.rodada()
        e = json.loads(r["entregas"]["c0.json"])
        e.update(mudar)
        return json.dumps(e).encode(), self.ler_zapia()[1]

    def test_recibo_de_volta_adulterado_e_recusado(self):
        for mudar, codigo in (({"hash_corpo": "0" * 64}, "ENTREGA_COM_HASH_DIFERENTE_DO_RECIBO"), ({"status": "FALHA"}, "ENTREGA_INCONSISTENTE"),
                              ({"entrada_id": "outro.json"}, "ENTREGA_INCONSISTENTE"), ({"texto": "vazou"}, "ENTREGA_FORA_DO_FORMATO"),
                              ({"origem_declarada": "zapia"}, "ENTREGA_INCONSISTENTE")):
            corpo, recibos = self.entrega(**mudar)
            self.assertEqual(ze.conferir_entrega(corpo, recibos, "c0.json"), codigo, mudar)
        self.assertEqual(ze.conferir_entrega(b"nao json", {}, "c0.json"), "ENTREGA_ILEGIVEL")

    def test_contraprova_recibo_fiel_confere(self):
        corpo, recibos = self.entrega()
        self.assertIsNone(ze.conferir_entrega(corpo, recibos, "c0.json"))


if __name__ == "__main__":
    unittest.main()


class ConferirPastaTeste(Base):
    def test_cli_confere_recibos_de_volta_de_um_checkout(self):
        self.promover(self.comando())
        r = self.rodada()
        raiz = self.tmp / "entrada"
        for p, b in self.arquivos().items():
            if p.startswith("comandos/recibos/"):
                (raiz / p).parent.mkdir(parents=True, exist_ok=True)
                (raiz / p).write_bytes(b)
        (raiz / "comandos" / "entregas").mkdir(parents=True, exist_ok=True)
        for nome, corpo in r["entregas"].items():
            (raiz / "comandos" / "entregas" / nome).write_bytes(corpo)
        self.assertEqual(ze.conferir_pasta(raiz), {"conferidas": 1, "falhas": {}})
        self.assertEqual(ze.main(["--raiz", str(raiz)]), 0)
        (raiz / "comandos" / "entregas" / "c0.json").write_bytes(b'{"x":1}')  # adulterado
        self.assertEqual(ze.main(["--raiz", str(raiz)]), 1)

    def test_sem_nenhum_recibo_de_volta_a_prova_nao_passa(self):
        raiz = self.tmp / "vazia"
        (raiz / "comandos" / "recibos").mkdir(parents=True)
        self.assertEqual(ze.main(["--raiz", str(raiz)]), 1)
