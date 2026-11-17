"""COMANDOS: caixa de comandos ligada ao runner (S6-R8, R12) com GitHub FALSO em memória. Sem rede, sem token real."""
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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

ENTRADA, DADOS, SHA = tpr.ENTRADA, tpr.DADOS, tpr.SHA


class Base(unittest.TestCase):
    def setUp(self):
        self.gh = tpr.GitHubFalso()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.validador = self.tmp / "validador"
        (self.validador / ".git").mkdir(parents=True)
        (self.validador / ".git" / "HEAD").write_text(SHA + "\n")
        self.flag(True)
        self.caixa = cbr.Caixa(pr.GitHubApi(tpr.TOKEN_ENTRADA, self.gh.transporte), ENTRADA)

    def flag(self, valor):
        (self.validador / "settings.json").write_text(json.dumps({"storage": {"personal_results_writes_enabled": valor}}))

    def contexto(self, **sobre):
        c = {"escritas_habilitadas": True, "agora": tcb.AGORA, "execucao": "77", "validador_sha": SHA,
             "validador_sha_fixado": SHA, "dia_de_descanso": False}
        c.update(sobre)
        return c

    def entrar(self, nome, comando):
        bruto = tcb.raw(comando) if isinstance(comando, dict) else comando
        self.gh.repos[ENTRADA]["files"][f"comandos/{nome}"] = bruto
        return (nome, bruto)

    def arquivos(self):
        return self.gh.repos[ENTRADA]["files"]

    def com_prefixo(self, prefixo):
        return sorted(p for p in self.arquivos() if p.startswith(prefixo))

    def rodar(self, *entradas, **sobre):
        return cbr.executar(list(entradas), self.contexto(**sobre), self.caixa)

    def unico(self, resumo):
        self.assertEqual(len(resumo["itens"]), 1)
        return resumo["itens"][0]


class FlagTest(Base):
    def test_flag_falsa_nao_faz_nenhuma_chamada(self):
        e = self.entrar("a.json", tcb.comando())
        res = self.rodar(e, escritas_habilitadas=False)
        self.assertEqual((res["estado"], res["mantidas"]), ("FLAG_DESLIGADA", 1))
        self.assertEqual(self.gh.total_de_chamadas(), 0)

    def test_flag_so_liga_com_o_booleano_true(self):
        for ruim in (None, "true", 1, "sim", [], {}):
            res = self.rodar(self.entrar("a.json", tcb.comando()), escritas_habilitadas=ruim)
            self.assertEqual(res["estado"], "FLAG_DESLIGADA", repr(ruim))
        self.assertEqual(self.gh.total_de_chamadas(), 0)

    def test_cli_com_flag_falsa_nao_le_token_nem_usa_rede(self):
        self.flag(False)
        pasta = self.tmp / "comandos"
        pasta.mkdir()
        (pasta / "a.json").write_bytes(tcb.raw(tcb.comando()))

        class Intocavel(dict):
            def get(self, *a, **k):
                raise AssertionError("ambiente lido com a flag desligada")
            __getitem__ = get

        def proibido(*a, **k):
            raise AssertionError("rede usada com a flag desligada")
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = cbr.main(["--comandos", str(pasta), "--execucao", "1", "--validador-sha", SHA, "--entrada-repo", ENTRADA,
                               "--validador-dir", str(self.validador)], transporte=proibido, ambiente=Intocavel())
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(saida.getvalue()), {"estado": "FLAG_DESLIGADA", "mantidas": 1, "flag": False})

    def test_validador_diferente_do_fixado_recusa_tudo_sem_tocar_na_caixa(self):
        e = self.entrar("a.json", tcb.comando())
        for sha in ("b" * 40, None, "curto", 7):
            res = self.rodar(e, validador_sha=sha)
            self.assertEqual(res["estado"], "VALIDADOR_DIVERGENTE", repr(sha))
        self.assertEqual(self.gh.total_de_chamadas(), 0)


class PromocaoTest(Base):
    def test_comando_valido_e_copiado_igual_e_recebe_recibo_e_ledger_e_sai_da_caixa(self):
        e = self.entrar("cmd-001.json", tcb.comando())
        item = self.unico(self.rodar(e))
        self.assertEqual((item["status"], item["codigo"]), (cb.PROMOVER, "OK"))
        self.assertEqual(self.arquivos()["comandos/validados/cmd-001.json"], e[1])  # os mesmos bytes
        self.assertNotIn("comandos/cmd-001.json", self.arquivos())
        recibo = json.loads(self.arquivos()["comandos/recibos/cmd-001.json"])
        self.assertEqual(recibo["hash_corpo"], cb.command_hash(json.loads(e[1])))
        self.assertEqual(set(recibo), {"entrada_id", "status", "codigo", "hash_corpo", "execucao", "validador_sha"})
        self.assertNotIn("Revisão pendente", json.dumps(recibo, ensure_ascii=False))
        self.assertEqual(len(self.com_prefixo("comandos/ledger/")), 2)  # chave e nonce

    def test_escreve_so_dentro_de_comandos_e_nunca_toca_no_historico(self):
        self.rodar(self.entrar("a.json", tcb.comando()), self.entrar("b.json", tcb.comando(operation="registrar_plano")))
        for metodo, repo, caminho, _ in self.gh.corpos:
            self.assertEqual(repo, ENTRADA)
            self.assertTrue(caminho.startswith("contents/comandos/"), caminho)
        self.assertFalse(any(repo == DADOS for _, repo, _ in self.gh.chamadas))

    def test_so_o_token_da_fila_e_usado(self):
        self.rodar(self.entrar("a.json", tcb.comando()))  # o fake devolve 403 se o token for o do histórico
        self.assertTrue(self.com_prefixo("comandos/validados/"))

    def test_rejeitado_vira_so_codigo_e_id_e_sai_da_caixa_sem_ledger(self):
        e = self.entrar("r.json", tcb.comando(operation="registrar_resultado", destination="repo_privado_dados", params={"a": 1}))
        item = self.unico(self.rodar(e))
        self.assertEqual((item["status"], item["codigo"]), (cb.DENIED, "REGISTRAR_FORA_DA_CAIXA"))
        rej = json.loads(self.arquivos()["comandos/rejeitadas/r.json"])
        self.assertEqual(set(rej), {"entrada_id", "status", "codigo", "quando"})
        self.assertNotIn("comandos/r.json", self.arquivos())
        self.assertEqual(self.com_prefixo("comandos/validados/"), [])
        self.assertEqual(self.com_prefixo("comandos/ledger/"), [])  # rejeitado não consome nonce nem chave
        self.assertEqual(self.com_prefixo("comandos/recibos/"), [])

    def test_dado_pessoal_nao_e_promovido_nem_ecoado(self):
        e = self.entrar("p.json", tcb.comando(params={"texto": "CPF 123.456.789-09"}))
        item = self.unico(self.rodar(e))
        self.assertEqual(item["codigo"], "PARAMS_DADO_PESSOAL")
        self.assertNotIn("123.456", json.dumps(self.arquivos()["comandos/rejeitadas/p.json"].decode()))

    def test_em_ordem_de_nome_e_nome_invalido_e_ignorado(self):
        a, b = self.entrar("b.json", tcb.comando(nonce="nonce-fake-0000000002", idempotency_key="rotina-2026-11-17-b")), \
            self.entrar("a.json", tcb.comando())
        res = self.rodar(a, b, ("../x.json", b"x"), ("a b.json", b"x"))
        # ordem de nome: "../x.json" e "a b.json" (nomes inválidos) ordenam antes de "a.json"; só os válidos tocam a API
        self.assertEqual([i["entrada_id"] for i in res["itens"]], ["invalido", "invalido", "a.json", "b.json"])
        self.assertEqual([i["status"] for i in res["itens"][:2]], ["IGNORADA", "IGNORADA"])
        self.assertEqual([i["codigo"] for i in res["itens"][2:]], ["OK", "OK"])

    def test_janela_de_300s_injetada_aceita_atraso_do_actions_e_rejeita_o_velho(self):
        def emitido(segundos):
            return (tcb.AGORA - timedelta(seconds=segundos)).strftime("%Y-%m-%dT%H:%M:%SZ")
        ok = self.entrar("ok.json", tcb.comando(issued_at=emitido(250)))  # 120 s do esquema recusaria
        velho = self.entrar("velho.json", tcb.comando(issued_at=emitido(400), nonce="nonce-fake-0000000002",
                                                      idempotency_key="rotina-2026-11-17-velho"))
        res = self.rodar(ok, velho)
        self.assertEqual([(i["entrada_id"], i["codigo"]) for i in res["itens"]],
                         [("ok.json", "OK"), ("velho.json", "FORA_DA_JANELA")])
        self.assertEqual(cbr.WINDOW_SECONDS, 300)

    def test_lembrete_sem_leitor_do_plano_e_recusado_mas_mensagem_passa(self):
        lembrete = tcb.comando(origin="coach", operation="criar_lembrete", destination="agenda_proprietario", params={"titulo": "x"})
        e = self.entrar("l.json", lembrete)
        item = self.unico(self.rodar(e, dia_de_descanso=None))
        self.assertEqual(item["codigo"], "DESCANSO_DESCONHECIDO")
        e2 = self.entrar("m.json", tcb.comando(origin="coach"))
        self.assertEqual(self.unico(self.rodar(e2, dia_de_descanso=None))["status"], cb.PROMOVER)
        e3 = self.entrar("l2.json", tcb.comando(**{**lembrete, "nonce": "nonce-fake-0000000009",
                                                   "idempotency_key": "rotina-2026-11-17-lembrete2"}))
        self.assertEqual(self.unico(self.rodar(e3, dia_de_descanso=False))["status"], cb.PROMOVER)
        e4 = self.entrar("l3.json", tcb.comando(**{**lembrete, "nonce": "nonce-fake-0000000010",
                                                   "idempotency_key": "rotina-2026-11-17-lembrete3"}))
        self.assertEqual(self.unico(self.rodar(e4, dia_de_descanso=True))["codigo"], "DIA_DE_DESCANSO")


class IdempotenciaDuravelTest(Base):
    def test_nonce_repetido_em_outra_execucao_e_recusado(self):
        self.rodar(self.entrar("a.json", tcb.comando()))
        e = self.entrar("b.json", tcb.comando(idempotency_key="rotina-2026-11-17-outra"))  # mesmo nonce
        self.assertEqual(self.unico(cbr.executar([e], self.contexto(), cbr.Caixa(pr.GitHubApi(tpr.TOKEN_ENTRADA, self.gh.transporte), ENTRADA)))["codigo"],
                         "NONCE_REPETIDO")

    def test_mesma_chave_e_corpo_com_nonce_novo_e_duplicado_e_nao_promove_de_novo(self):
        self.rodar(self.entrar("a.json", tcb.comando()))
        e = self.entrar("b.json", tcb.comando(nonce="nonce-fake-0000000002"))
        item = self.unico(self.rodar(e))
        self.assertEqual((item["status"], item["codigo"]), (cb.DUPLICADO, "IDEMPOTENTE"))
        self.assertNotIn("comandos/validados/b.json", self.arquivos())
        self.assertEqual(json.loads(self.arquivos()["comandos/recibos/b.json"])["status"], cb.DUPLICADO)
        self.assertNotIn("comandos/b.json", self.arquivos())

    def test_mesma_chave_com_outro_corpo_e_conflito(self):
        self.rodar(self.entrar("a.json", tcb.comando()))
        e = self.entrar("b.json", tcb.comando(nonce="nonce-fake-0000000002", params={"texto": "outro corpo"}))
        self.assertEqual(self.unico(self.rodar(e))["codigo"], "CHAVE_REUTILIZADA_COM_OUTRO_CORPO")

    def test_duas_entradas_com_o_mesmo_nonce_na_mesma_execucao(self):
        a = self.entrar("a.json", tcb.comando())
        b = self.entrar("b.json", tcb.comando(idempotency_key="rotina-2026-11-17-outra"))
        res = self.rodar(a, b)
        self.assertEqual([i["codigo"] for i in res["itens"]], ["OK", "NONCE_REPETIDO"])

    def test_leitura_do_ledger_falha_mantem_a_entrada_e_nao_rejeita(self):
        self.gh.falhar = lambda m, repo, c: 500 if c.startswith("contents/comandos/ledger/") else None
        e = self.entrar("a.json", tcb.comando())
        res = self.rodar(e)
        self.assertEqual(res["falhas_de_registro"], 1)
        self.assertIn("comandos/a.json", self.arquivos())  # continua na caixa
        self.assertEqual(self.com_prefixo("comandos/rejeitadas/"), [])  # falha transitória não vira rejeição
        self.assertEqual(self.com_prefixo("comandos/validados/"), [])
        self.gh.falhar = lambda *a: None
        self.assertEqual(self.unico(self.rodar(e))["status"], cb.PROMOVER)  # a reexecução conclui

    def test_queda_depois_de_promover_antes_do_recibo_e_retomada_sem_duplicar(self):
        e = self.entrar("a.json", tcb.comando())
        self.gh.falhar = lambda m, repo, c: 500 if (m == "PUT" and c.startswith("contents/comandos/recibos/")) else None
        res = self.rodar(e)
        self.assertEqual(res["falhas_de_registro"], 1)
        copia = self.arquivos()["comandos/validados/a.json"]
        self.assertIn("comandos/a.json", self.arquivos())
        self.gh.falhar = lambda *a: None
        item = self.unico(self.rodar(e))
        self.assertEqual((item["status"], item["codigo"]), (cb.PROMOVER, "RETOMADA"))
        self.assertEqual(self.arquivos()["comandos/validados/a.json"], copia)
        self.assertIn("comandos/recibos/a.json", self.arquivos())
        self.assertNotIn("comandos/a.json", self.arquivos())
        self.assertEqual(self.com_prefixo("comandos/rejeitadas/"), [])

    def test_falha_ao_copiar_para_validados_nao_consome_nonce_nem_chave(self):
        e = self.entrar("a.json", tcb.comando())
        self.gh.falhar = lambda m, repo, c: 500 if (m == "PUT" and c.startswith("contents/comandos/validados/")) else None
        res = self.rodar(e)
        self.assertEqual(res["falhas_de_registro"], 1)
        self.assertEqual(self.com_prefixo("comandos/ledger/"), [])
        self.assertIn("comandos/a.json", self.arquivos())
        self.gh.falhar = lambda *a: None
        self.assertEqual(self.unico(self.rodar(e))["status"], cb.PROMOVER)

    def test_queda_antes_de_gravar_o_ledger_nao_consome_o_nonce(self):
        e = self.entrar("a.json", tcb.comando())
        self.gh.falhar = lambda m, repo, c: 500 if (m == "PUT" and c.startswith("contents/comandos/ledger/")) else None
        self.rodar(e)
        self.assertEqual(self.com_prefixo("comandos/ledger/"), [])
        self.gh.falhar = lambda *a: None
        self.assertEqual(self.unico(self.rodar(e))["status"], cb.PROMOVER)  # nonce ainda livre: retomada concluiu
        self.assertEqual(len(self.com_prefixo("comandos/ledger/")), 2)

    def test_mesmo_nome_com_outro_conteudo_nunca_sobrescreve_o_validado(self):
        self.rodar(self.entrar("a.json", tcb.comando()))
        original = self.arquivos()["comandos/validados/a.json"]
        e = self.entrar("a.json", tcb.comando(nonce="nonce-fake-0000000002", idempotency_key="rotina-2026-11-17-novo"))
        self.assertEqual(self.unico(self.rodar(e))["codigo"], "NOME_JA_VALIDADO")
        self.assertEqual(self.arquivos()["comandos/validados/a.json"], original)

    def test_retomada_nao_confia_na_existencia_do_arquivo_e_revalida(self):
        ruim = tcb.raw(tcb.comando(operation="registrar_resultado", destination="repo_privado_dados", params={"a": 1}))
        self.arquivos()["comandos/validados/p.json"] = ruim  # plantado, sem passar pela validação
        e = self.entrar("p.json", ruim)
        item = self.unico(self.rodar(e))
        self.assertEqual((item["status"], item["codigo"]), (cb.DENIED, "REGISTRAR_FORA_DA_CAIXA"))
        self.assertEqual(self.com_prefixo("comandos/recibos/"), [])  # nenhum recibo para comando que não passa na validação
        self.assertEqual(self.com_prefixo("comandos/ledger/"), [])

    def test_retomada_aceita_comando_antigo_porque_a_janela_nao_vale_para_finalizar(self):
        e = self.entrar("a.json", tcb.comando())
        self.gh.falhar = lambda m, repo, c: 500 if (m == "PUT" and c.startswith("contents/comandos/recibos/")) else None
        self.rodar(e)
        self.gh.falhar = lambda *a: None
        item = self.unico(self.rodar(e, agora=tcb.AGORA + timedelta(hours=3)))  # muito além dos 300 s
        self.assertEqual(item["codigo"], "RETOMADA")


class ZapiaEExecutaveisTest(Base):
    def test_zapia_so_executa_o_validado_com_recibo_de_mesmo_hash(self):
        e = self.entrar("a.json", tcb.comando())
        self.rodar(e)
        recibo = json.loads(self.arquivos()["comandos/recibos/a.json"])
        listagem = {"comandos/validados/a.json": self.arquivos()["comandos/validados/a.json"]}
        self.assertEqual(set(cb.selecionar_executaveis(listagem, {"a.json": recibo["hash_corpo"]})), {"comandos/validados/a.json"})
        adulterado = {"comandos/validados/a.json": e[1].replace(b"Revis", b"Revoc")}
        self.assertEqual(cb.selecionar_executaveis(adulterado, {"a.json": recibo["hash_corpo"]}), {})
        self.assertEqual(cb.selecionar_executaveis({"comandos/a.json": e[1]}, {"a.json": recibo["hash_corpo"]}), {})


class CLITest(Base):
    def rodar_cli(self, ambiente, arquivos):
        pasta = self.tmp / "caixa_cli"
        shutil.rmtree(pasta, True)
        pasta.mkdir()
        (pasta / "ignorado.txt").write_text("x")
        (pasta / "subpasta").mkdir()
        for nome, dados in arquivos.items():
            (pasta / nome).write_bytes(dados)
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = cbr.main(["--comandos", str(pasta), "--execucao", "77", "--validador-sha", SHA, "--entrada-repo", ENTRADA,
                               "--validador-dir", str(self.validador)], transporte=self.gh.transporte, ambiente=ambiente, agora=tcb.AGORA)
        return codigo, saida.getvalue()

    def test_cli_promove_so_com_o_token_da_fila_e_nao_imprime_token(self):
        bruto = tcb.raw(tcb.comando())
        self.entrar("a.json", bruto)
        codigo, texto = self.rodar_cli({"GH_TOKEN": tpr.TOKEN_ENTRADA}, {"a.json": bruto})  # sem DADOS_TOKEN
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(json.loads(texto)["itens"][0]["status"], cb.PROMOVER)
        for segredo in tpr.SEGREDOS:
            self.assertNotIn(segredo, texto)

    def test_cli_sem_token_ou_repo_invalido_falha_sem_vazar(self):
        codigo, texto = self.rodar_cli({}, {})
        self.assertEqual((codigo, json.loads(texto)["codigo"]), (1, "ValueError"))
        self.assertEqual(self.gh.total_de_chamadas(), 0)
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = cbr.main(["--comandos", str(self.tmp), "--execucao", "1", "--validador-sha", SHA, "--entrada-repo", "../x",
                               "--validador-dir", str(self.validador)], transporte=self.gh.transporte, ambiente={})
        self.assertEqual((codigo, json.loads(saida.getvalue())["codigo"]), (1, "ENTRADA_REPO_INVALIDO"))

    def test_cli_nao_conhece_o_plano_entao_lembrete_e_recusado_por_descanso_desconhecido(self):
        lembrete = tcb.raw(tcb.comando(origin="coach", operation="criar_lembrete", destination="agenda_proprietario",
                                       params={"titulo": "x"}))
        self.entrar("l.json", lembrete)
        codigo, texto = self.rodar_cli({"GH_TOKEN": tpr.TOKEN_ENTRADA}, {"l.json": lembrete})
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(texto)["itens"][0]["codigo"], "DESCANSO_DESCONHECIDO")
        self.assertEqual(self.com_prefixo("comandos/validados/"), [])

    def test_cli_sai_com_1_se_falhar_ao_registrar_e_com_1_se_o_validador_divergir(self):
        self.gh.falhar = lambda m, repo, c: 500 if (m == "PUT" and c.startswith("contents/comandos/recibos/")) else None
        bruto = tcb.raw(tcb.comando())
        self.entrar("a.json", bruto)
        self.assertEqual(self.rodar_cli({"GH_TOKEN": tpr.TOKEN_ENTRADA}, {"a.json": bruto})[0], 1)
        (self.validador / ".git" / "HEAD").write_text("c" * 40 + "\n")
        codigo, texto = self.rodar_cli({"GH_TOKEN": tpr.TOKEN_ENTRADA}, {"a.json": bruto})
        self.assertEqual((codigo, json.loads(texto)["estado"]), (1, "VALIDADOR_DIVERGENTE"))

    def test_ler_caixa_ignora_link_subpasta_e_nao_json_e_limita(self):
        d = self.tmp / "c"
        d.mkdir()
        (d / "ok.json").write_text("{}")
        (d / "nota.txt").write_text("x")
        (d / "sub").mkdir()
        (d / "link.json").symlink_to(d / "ok.json")
        self.assertEqual([n for n, _ in cbr.ler_caixa(d)], ["ok.json"])
        for i in range(501):
            (d / f"f{i:04d}.json").write_text("{}")
        with self.assertRaises(ValueError):
            cbr.ler_caixa(d)


class FronteirasTest(unittest.TestCase):
    def test_modelo_do_fluxo_chama_o_runner_da_caixa_sem_o_segredo_do_historico(self):
        modelo = (ROOT / "config/modelos_fluxo/promover.yml").read_text(encoding="utf-8")
        passo = modelo[modelo.index("name: Promover comandos"):]
        self.assertIn("command_box_runner.py", passo)
        for flag in ("--comandos", "--execucao", "--validador-sha", "--entrada-repo", "--validador-dir"):
            self.assertIn(flag, passo)
        self.assertNotIn("DADOS_TOKEN", passo)  # este passo não recebe o segredo do histórico
        self.assertIn("GH_TOKEN: ${{ github.token }}", passo)

    def test_codigo_nao_grava_localmente_nem_imprime_token_nem_usa_rede_direta(self):
        fonte = (ROOT / "scripts/command_box_runner.py").read_text(encoding="utf-8")
        for proibido in ("write_text(", "write_bytes(", "import subprocess", "os.system", "eval(", "exec(", "import urllib", "import socket",
                         "DADOS_TOKEN", "print(token", "personal_results_writes_enabled ="):
            self.assertNotIn(proibido, fonte)
        self.assertIsNone(re.search(r"(?<![.\w])open\(", fonte))
        self.assertEqual(fonte.count("print("), 4)

    def test_janela_e_ledger_ficam_no_codigo_do_runner_e_o_esquema_fica_intacto(self):
        esquema = json.loads((ROOT / "config/agent_command_schema.json").read_text(encoding="utf-8"))
        self.assertEqual(esquema["limits"]["time_window_seconds"], 120)
        self.assertEqual((cbr.WINDOW_SECONDS, cbr.LEDGER), (300, "comandos/ledger/"))


if __name__ == "__main__":
    unittest.main()
