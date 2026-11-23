"""ZAPIA-F3 (E29): par sintético, instrução do poller pinada e verificador do recibo CRIADA; sonda real somente leitura do contexto. Offline."""
import copy
import hashlib
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
import command_box as cb  # noqa: E402
import command_box_runner as cbr  # noqa: E402
import ctx_leitura_real as clr  # noqa: E402
import promotion_runner as pr  # noqa: E402
import test_command_box_runner as tcbr  # noqa: E402
import test_promotion_runner as tpr  # noqa: E402
import zapia_entrega as ze  # noqa: E402
import zapia_f1_prep as f1  # noqa: E402
import zapia_poller as zp  # noqa: E402

AGORA = datetime(2026, 11, 23, 15, 0, 0, tzinfo=timezone.utc)
FILHA = "2026-11-23T17:00:00Z"
POLLER = datetime(2026, 11, 23, 15, 20, 0, tzinfo=timezone.utc)
REPO = "Andraus35/ufms-meu-estudo-entrada"
REF = "a" * 40


def canon(o):
    return ze._canonico(o)


class Cenario(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.alvo = f1.montar(AGORA, nome=zp.NOME_ALVO)
        self.ped = zp.montar_pedido(AGORA, FILHA, self.alvo["hash_corpo"])
        self.comando = json.loads(self.ped["comando_bytes"])
        self.recibos = {zp.NOME_PEDIDO: self.ped["hash_corpo"], zp.NOME_ALVO: self.alvo["hash_corpo"]}

    def criada(self, **mud):
        texto = zp.instrucao_esperada(self.comando, REPO)
        c = {"entrada_id": zp.NOME_PEDIDO, "hash_corpo": self.ped["hash_corpo"], "status": "CRIADA", "criada_em": "2026-11-23T15:20:30Z",
             "agendado_utc": FILHA, "rotina_id_relatado": "rotina-abc.123", "instrucao_sha256": hashlib.sha256(texto.encode()).hexdigest()}
        c.update(mud)
        return {k: v for k, v in c.items() if v is not ...}

    def conferir(self, c, poller=POLLER, **kw):
        return zp.conferir_criada(canon(c), self.ped["comando_bytes"], self.recibos, zp.NOME_PEDIDO, poller, REPO, **kw)

    def gravar(self, raiz, criada=True, entrega=True, **mud):
        for sub in ("validados", "recibos", "criadas", "entregas"):
            (raiz / "comandos" / sub).mkdir(parents=True, exist_ok=True)
        for m in (self.alvo, self.ped):
            (raiz / "comandos" / "validados" / m["nome"]).write_bytes(m["comando_bytes"])
            (raiz / "comandos" / "recibos" / m["nome"]).write_bytes(m["recibo_bytes"])
        if criada:
            (raiz / "comandos" / "criadas" / zp.NOME_PEDIDO).write_bytes(canon(self.criada(**mud)))
        if entrega:
            e = {"entrada_id": zp.NOME_ALVO, "hash_corpo": self.alvo["hash_corpo"], "status": "ENTREGUE", "origem_declarada": "coach",
                 "entregue_em": "2026-11-23T17:00:21Z"}
            (raiz / "comandos" / "entregas" / zp.NOME_ALVO).write_bytes(canon(e))


class PreparoTest(Cenario):
    def test_pedido_passa_na_caixa_e_aponta_para_o_alvo(self):
        self.assertEqual(self.comando["operation"], "agendar_rotina")
        self.assertEqual(self.comando["params"]["comandos_sha256"], [self.alvo["hash_corpo"]])
        self.assertEqual(json.loads(self.ped["recibo_bytes"])["codigo"], "SINTETICO_MANUAL")

    def test_antecedencia_menor_que_90_min_e_recusada_pela_caixa(self):
        with self.assertRaises(ValueError):
            zp.montar_pedido(AGORA, "2026-11-23T16:20:00Z", self.alvo["hash_corpo"])
        zp.montar_pedido(AGORA, "2026-11-23T16:30:00Z", self.alvo["hash_corpo"])

    def test_filha_fora_de_24h_ou_relogio_sem_fuso_e_recusado(self):
        with self.assertRaises(ValueError):
            zp.montar_pedido(AGORA, "2026-11-24T15:00:01Z", self.alvo["hash_corpo"])
        with self.assertRaises(ValueError):
            zp.montar_pedido(datetime(2026, 11, 23, 15, 0), FILHA, self.alvo["hash_corpo"])


class InstrucaoDoPollerTest(unittest.TestCase):
    def test_poller_usa_urls_literais_pin_do_commit_e_do_hash_do_modelo_filho(self):
        t = ar.renderizar_poller(repo=REPO, credencial="github_ufms_repo_token", agendado_utc="2026-11-23T15:20:00Z", ref=REF)
        unica = ar.carregar_instrucoes()["UNICA"]["sha256"]
        for trecho in (f"https://api.github.com/repos/{REPO}/contents/comandos/recibos", f"https://api.github.com/repos/{REPO}/contents/comandos/validados",
                       f"https://api.github.com/repos/{REPO}/contents/comandos/criadas", f"contents/config/rotina_instrucoes.json?ref={REF}", unica,
                       "never reveal", "Do not translate", "do not create a recurring routine", "One execution only"):
            self.assertIn(trecho, t, trecho)
        self.assertNotIn("commands/", t)
        self.assertNotRegex(t, r"\{[A-Z_0-9]+\}")  # nenhum marcador sem preencher (as chaves do modelo filho são citadas por NOME, sem chaves)

    def test_poller_recusa_parametro_ruim(self):
        base = dict(repo=REPO, credencial="github_ufms_repo_token", agendado_utc="2026-11-23T15:20:00Z", ref=REF)
        for campo, valor in (("ref", "main"), ("ref", "a" * 39), ("ref", ""), ("agendado_utc", "amanha"), ("repo", "x y"), ("credencial", "ghp_x y")):
            with self.assertRaises(ValueError, msg=campo):
                ar.renderizar_poller(**dict(base, **{campo: valor}))

    def test_mudar_o_modelo_do_poller_ou_o_filho_quebra_o_check(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "config").mkdir()
        dados = ar.carregar_instrucoes()
        for chave, mut in (("POLLER", lambda t: t.replace("comandos/criadas", "commands/criadas")), ("POLLER", lambda t: t + " x"), ("UNICA", lambda t: t + " x")):
            d = copy.deepcopy(dados)
            d[chave]["template"] = mut(d[chave]["template"])
            (tmp / "config" / "rotina_instrucoes.json").write_text(json.dumps(d), encoding="utf-8")
            self.assertTrue(ar.check(tmp), chave)
            with self.assertRaises(ValueError):
                ar.renderizar_poller(repo=REPO, credencial="github_ufms_repo_token", agendado_utc="2026-11-23T15:20:00Z", ref=REF, root=tmp)


class ConferirCriadaTest(Cenario):
    def test_recibo_consistente_passa(self):
        self.assertIsNone(self.conferir(self.criada()))

    def test_campo_extra_ou_faltando_ou_texto_no_recibo(self):
        self.assertEqual(self.conferir(self.criada(texto="oi")), "CAMPOS_FORA_DO_CONTRATO")
        self.assertEqual(self.conferir(self.criada(rotina_id_relatado=...)), "CAMPOS_FORA_DO_CONTRATO")

    def test_status_nome_e_hash(self):
        self.assertEqual(self.conferir(self.criada(status="ENTREGUE")), "STATUS_OU_NOME_INVALIDO")
        self.assertEqual(self.conferir(self.criada(entrada_id="outro.json")), "STATUS_OU_NOME_INVALIDO")
        self.assertEqual(self.conferir(self.criada(hash_corpo="d" * 64)), "HASH_DIVERGE")
        self.recibos[zp.NOME_PEDIDO] = "d" * 64
        self.assertEqual(self.conferir(self.criada()), "HASH_DIVERGE")

    def test_agendado_diferente_do_pedido(self):
        self.assertEqual(self.conferir(self.criada(agendado_utc="2026-11-23T18:00:00Z")), "AGENDADO_DIVERGE_DO_PEDIDO")

    def test_carimbo_antes_do_poller_fora_da_tolerancia_e_depois_da_filha(self):
        self.assertEqual(self.conferir(self.criada(criada_em="2026-11-23T15:19:59Z")), "CRIADA_ANTES_DO_POLLER")
        self.assertEqual(self.conferir(self.criada(criada_em="2026-11-23T15:35:01Z")), "CRIADA_FORA_DA_TOLERANCIA")
        self.assertIsNone(self.conferir(self.criada(criada_em="2026-11-23T15:35:00Z")))
        self.assertEqual(self.conferir(self.criada(criada_em="2026-11-23T15:20:30")), "CARIMBO_INVALIDO")
        self.assertEqual(self.conferir(self.criada(criada_em="2026-11-23T17:00:00Z"), tolerancia=timedelta(hours=3)), "CRIADA_DEPOIS_DO_DISPARO_DA_FILHA")

    def test_rotina_id_invalido(self):
        for ruim in ("", "a b", "x" * 65, "ação", 5, None):
            self.assertEqual(self.conferir(self.criada(rotina_id_relatado=ruim)), "ROTINA_ID_INVALIDO", repr(ruim))

    def test_instrucao_da_filha_diferente_do_modelo_versionado(self):
        self.assertEqual(self.conferir(self.criada(instrucao_sha256="e" * 64)), "INSTRUCAO_DA_FILHA_DIVERGE_DO_MODELO")
        traduzida = zp.instrucao_esperada(self.comando, REPO).replace("comandos", "commands")
        self.assertEqual(self.conferir(self.criada(instrucao_sha256=hashlib.sha256(traduzida.encode()).hexdigest())), "INSTRUCAO_DA_FILHA_DIVERGE_DO_MODELO")

    def test_arquivo_ilegivel_pedido_que_nao_e_agendamento_e_relogio_ruim(self):
        self.assertEqual(zp.conferir_criada(b"nao json", self.ped["comando_bytes"], self.recibos, zp.NOME_PEDIDO, POLLER, REPO), "ARQUIVO_ILEGIVEL")
        self.assertEqual(zp.conferir_criada(canon(self.criada()), self.alvo["comando_bytes"], self.recibos, zp.NOME_PEDIDO, POLLER, REPO), "PEDIDO_INVALIDO")
        self.assertEqual(self.conferir(self.criada(), poller=datetime(2026, 11, 23, 15, 20)), "AGENDAMENTO_INVALIDO")
        self.assertEqual(self.conferir(self.criada(), tolerancia=timedelta(0)), "AGENDAMENTO_INVALIDO")


class ConferirPastaTest(Cenario):
    def pasta(self, **kw):
        raiz = self.tmp / "entrada"
        self.gravar(raiz, **kw)
        return zp.conferir_pasta(raiz, zp.NOME_PEDIDO, zp.NOME_ALVO, POLLER, REPO)

    def test_completo_passa_com_limite_declarado(self):
        r = self.pasta()
        self.assertTrue(r["ok"], r)
        self.assertIn("autorrelato", r["limite"])

    def test_sem_recibo_criada_para_na_fase_do_poller(self):
        r = self.pasta(criada=False)
        self.assertEqual((r["ok"], r["fase"], r["codigo"]), (False, "poller", "SEM_RECIBO_CRIADA"))

    def test_poller_ok_mas_filha_nao_entregou(self):
        r = self.pasta(entrega=False)
        self.assertEqual((r["ok"], r["fase"], r["codigo"]), (False, "filha", "SEM_ENTREGA"))

    def test_recibo_criada_invalido_barra_antes_da_filha(self):
        r = self.pasta(status="PENDENTE")
        self.assertEqual((r["fase"], r["codigo"]), ("poller", "STATUS_OU_NOME_INVALIDO"))

    def test_entrega_da_filha_antes_do_horario_nao_passa(self):
        raiz = self.tmp / "entrada"
        self.gravar(raiz, entrega=False)
        (raiz / "comandos" / "entregas" / zp.NOME_ALVO).write_bytes(canon({"entrada_id": zp.NOME_ALVO, "hash_corpo": self.alvo["hash_corpo"], "status": "ENTREGUE",
                                                                         "origem_declarada": "coach", "entregue_em": "2026-11-23T16:00:00Z"}))
        r = zp.conferir_pasta(raiz, zp.NOME_PEDIDO, zp.NOME_ALVO, POLLER, REPO)
        self.assertEqual((r["fase"], r["codigo"]), ("filha", "ENTREGA_ANTES_DO_AGENDADO"))

    def test_cli_preparar_e_conferir(self):
        saida = self.tmp / "par"
        self.assertEqual(zp.main(["preparar", "--saida", str(saida), "--agendado-filha", (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")]), 0)
        for sub in ("validados", "recibos"):
            self.assertEqual(sorted(p.name for p in (saida / sub).iterdir()), [zp.NOME_ALVO, zp.NOME_PEDIDO])
        self.assertEqual(zp.main(["preparar", "--saida", str(saida), "--agendado-filha", "amanha"]), 2)
        self.assertEqual(zp.main(["preparar", "--saida", str(saida), "--agendado-filha", (datetime.now(timezone.utc) + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")]), 1)
        self.assertEqual(zp.main(["conferir", "--raiz", str(self.tmp / "vazia"), "--poller-agendado", "2026-11-23T15:20:00Z"]), 1)
        self.assertEqual(zp.main(["conferir", "--raiz", str(self.tmp), "--poller-agendado", "x"]), 2)


class SondaRealSoLeituraTest(tcbr.Base):
    def test_so_deixa_passar_get(self):
        chamadas = []

        class Espiao:
            def chamar(self, metodo, caminho, corpo=None):
                chamadas.append(metodo)
                return 200, {}

        api = clr.ApiSoLeitura(Espiao())
        for metodo in ("PUT", "DELETE", "POST", "PATCH", "get"):
            with self.assertRaises(pr.ApiError):
                api.chamar(metodo, "/repos/x/y/contents/a", {"a": 1})
        with self.assertRaises(pr.ApiError):
            api.chamar("GET", "/repos/x/y/contents/a", {"a": 1})
        self.assertEqual(chamadas, [])  # nada chegou ao cliente real
        api.chamar("GET", "/repos/x/y/contents/a")
        self.assertEqual(chamadas, ["GET"])

    def test_sonda_em_caixa_vazia_e_com_promovido_sem_escrever_nada(self):
        self.entrar("alvo.json", __import__("test_command_box").comando())
        res = cbr.executar([("alvo.json", self.gh.repos[tpr.ENTRADA]["files"]["comandos/alvo.json"])], self.contexto(), self.caixa)
        self.assertEqual(res["itens"][0]["status"], "PROMOVER")
        antes = dict(self.arquivos())
        escritas = len(self.gh.corpos)
        s = clr.sondar(clr.cbr.Caixa(clr.ApiSoLeitura(self.caixa.api), tpr.ENTRADA), datetime(2026, 11, 17, 15, 0, tzinfo=timezone.utc))
        self.assertEqual((s["ok"], s["validados"], s["recibos"], s["hashes_promovidos"]), (True, 1, 1, 1))
        self.assertEqual(len(s["prefixos"][0]), 12)
        self.assertEqual(self.arquivos(), antes)
        self.assertTrue(all(c[0] == "GET" for c in self.gh.corpos[escritas:]) or len(self.gh.corpos) == escritas)

    def test_cli_nao_imprime_token_nem_mensagem_de_erro(self):
        import io
        from contextlib import redirect_stdout
        for amb, rc in (({"GH_TOKEN": ""}, 1), ({"GH_TOKEN": "tem espaco"}, 1)):
            saida = io.StringIO()
            with redirect_stdout(saida):
                self.assertEqual(clr.main([tpr.ENTRADA], transporte=self.gh.transporte, ambiente=amb), rc)
            self.assertNotIn("tem espaco", saida.getvalue())
            self.assertEqual(json.loads(saida.getvalue())["codigo"], "ValueError")
        saida = io.StringIO()
        with redirect_stdout(saida):
            self.assertEqual(clr.main(["nao é repo"], transporte=self.gh.transporte, ambiente={"GH_TOKEN": tpr.TOKEN_ENTRADA}), 2)
        saida = io.StringIO()
        with redirect_stdout(saida):
            rc = clr.main([tpr.ENTRADA], transporte=self.gh.transporte, ambiente={"GH_TOKEN": tpr.TOKEN_ENTRADA}, agora=datetime(2026, 11, 17, 15, 0, tzinfo=timezone.utc))
        self.assertEqual(rc, 0, saida.getvalue())
        self.assertTrue(json.loads(saida.getvalue())["ok"])

    def test_relogio_sem_fuso_e_falha_e_falha_de_api_nao_vaza(self):
        self.assertEqual(clr.sondar(self.caixa, datetime(2026, 11, 17, 15, 0)), {"ok": False, "codigo": "RELOGIO_SEM_FUSO"})
        import io
        from contextlib import redirect_stdout
        saida = io.StringIO()
        with redirect_stdout(saida):
            rc = clr.main([tpr.ENTRADA], transporte=lambda *a: (500, b"{}"), ambiente={"GH_TOKEN": tpr.TOKEN_ENTRADA})
        self.assertEqual((rc, json.loads(saida.getvalue())["codigo"]), (1, "ApiError"))


if __name__ == "__main__":
    unittest.main()
