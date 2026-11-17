"""RUNNER: adaptador HTTP do portão de promoção (S6-R4/R5/R6) com GitHub FALSO em memória. Sem rede, sem token real."""
import base64
import io
import re
import json
import shutil
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import promotion_gate as pg  # noqa: E402
import promotion_runner as pr  # noqa: E402
import test_promotion_gate as tg  # noqa: E402

ENTRADA = "Andraus35/ufms-meu-estudo-entrada"
DADOS = pr.DADOS_REPO
TOKEN_ENTRADA = "tok-entrada-ficticio-0001"
TOKEN_DADOS = "tok-dados-ficticio-0002"
SHA = "a" * 40
SEGREDOS = (TOKEN_ENTRADA, TOKEN_DADOS)


def b64(dados):
    return base64.b64encode(dados).decode("ascii")


class GitHubFalso:
    """Imita o mínimo da API de conteúdo do GitHub para dois repositórios, cada um com o SEU token."""

    def __init__(self):
        self.repos = {
            ENTRADA: {"private": True, "files": {}, "head": "e" * 40, "n": 0, "token": TOKEN_ENTRADA},
            DADOS: {"private": True, "files": {}, "head": "d" * 40, "n": 0, "token": TOKEN_DADOS},
        }
        self.chamadas = []
        self.corpos = []  # (metodo, repo, caminho, corpo_json) de toda escrita
        self.omitir_visibility = False
        self.falhar = lambda metodo, repo, caminho: None  # devolve um status para forçar erro
        self.depois_de_criar = None  # gancho: simula outro commit chegando

    def total_de_chamadas(self):
        return len(self.chamadas)

    def transporte(self, metodo, url, cab, corpo, tempo):
        assert url.startswith(pr.API + "/repos/"), url
        resto = url[len(pr.API + "/repos/"):].split("/")
        repo = "/".join(resto[:2])
        caminho = "/".join(resto[2:])
        self.chamadas.append((metodo, repo, caminho))
        dados = self.repos.get(repo)
        if dados is None:
            return 404, b'{"message":"Not Found"}'
        if cab.get("Authorization") != "Bearer " + dados["token"]:
            return 403, b'{"message":"token errado para este repositorio"}'
        forcado = self.falhar(metodo, repo, caminho)
        if forcado:
            return forcado, b'{"message":"falha forcada"}'
        corpo_json = json.loads(corpo) if corpo else None
        if metodo in ("PUT", "DELETE"):
            self.corpos.append((metodo, repo, caminho, corpo_json))
        if caminho == "":
            info = {"private": dados["private"], "visibility": "private" if dados["private"] else "public",
                    "full_name": repo, "default_branch": "main"}
            if self.omitir_visibility:
                info.pop("visibility")
            return 200, json.dumps(info).encode()
        if caminho == "git/ref/heads/main":
            return 200, json.dumps({"object": {"sha": dados["head"]}}).encode()
        assert caminho.startswith("contents/"), caminho
        arq = caminho[len("contents/"):]
        arquivos = dados["files"]
        if metodo == "GET":
            if arq in arquivos:
                return 200, json.dumps({"type": "file", "content": b64(arquivos[arq]), "sha": pg.git_blob_sha(arquivos[arq])}).encode()
            filhos = {}
            for caminho_f in arquivos:
                if caminho_f.startswith(arq + "/"):
                    nome = caminho_f[len(arq) + 1:].split("/")[0]
                    filhos[nome] = "dir" if "/" in caminho_f[len(arq) + 1:] else "file"
            if filhos:
                return 200, json.dumps([{"type": t, "name": n} for n, t in sorted(filhos.items())]).encode()
            return 404, b'{"message":"Not Found"}'
        if metodo == "PUT":
            if arq in arquivos:
                return 422, b'{"message":"sha wasn\'t supplied"}'
            arquivos[arq] = base64.b64decode(corpo_json["content"])
            dados["n"] += 1
            dados["head"] = ("%040x" % (dados["n"] + (1 if repo == DADOS else 100)))
            commit = dados["head"]
            if self.depois_de_criar:
                self.depois_de_criar(repo, dados)  # pode mover o HEAD depois do commit devolvido
            return 201, json.dumps({"commit": {"sha": commit}}).encode()
        if metodo == "DELETE":
            if arq not in arquivos:
                return 404, b'{"message":"Not Found"}'
            if corpo_json.get("sha") != pg.git_blob_sha(arquivos[arq]):
                return 409, b'{"message":"sha divergente"}'
            del arquivos[arq]
            return 200, json.dumps({"commit": {"sha": "f" * 40}}).encode()
        return 405, b"{}"


class Base(unittest.TestCase):
    def setUp(self):
        self.gh = GitHubFalso()
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.validador = self.tmp / "validador"
        self.validador.mkdir()
        (self.validador / "config").mkdir()
        shutil.copy(ROOT / "config" / "topics.csv", self.validador / "config" / "topics.csv")
        self.escrever_settings(True)
        (self.validador / ".git").mkdir()
        (self.validador / ".git" / "HEAD").write_text(SHA + "\n")
        # histórico de dados: consentimento e a recomendação que a tentativa referencia
        rec = tg.recomendacao()
        self.gh.repos[DADOS]["files"]["consent.json"] = json.dumps(
            {"version": "v3", "scope": "resultados_estudo", "granted_at": "2026-11-16T10:00:00-04:00", "revoked_at": None}).encode()
        self.gh.repos[DADOS]["files"][pg.event_path(rec["event_id"])] = pg.canonical({"evento": rec, "envelope": {}})
        self.dados = pr.RepositorioDados(pr.GitHubApi(TOKEN_DADOS, self.gh.transporte), DADOS)
        self.fila = pr.FilaEntrada(pr.GitHubApi(TOKEN_ENTRADA, self.gh.transporte), ENTRADA)

    def escrever_settings(self, flag):
        (self.validador / "settings.json").write_text(json.dumps({"storage": {"personal_results_writes_enabled": flag}}))

    def contexto(self, **sobre):
        ctx = pr.montar_contexto(dados=self.dados, agora=tg.AGORA, alvo=DADOS, validador_dir=self.validador,
                                 validador_sha_fixado=SHA, execucao="9876543210")
        ctx.update(sobre)
        return ctx

    def entrar(self, nome, bruto):
        self.gh.repos[ENTRADA]["files"][f"{pr.FILA_DIR}/{nome}"] = bruto
        return (nome, bruto)

    def arquivos(self, repo):
        return self.gh.repos[repo]["files"]

    def novos_eventos(self):
        return sorted(p for p in self.arquivos(DADOS) if p.startswith("eventos/") and p != pg.event_path(tg.recomendacao()["event_id"]))


class FlagDesligadaTest(Base):
    def test_ler_flag_so_aceita_o_booleano_true(self):
        casos = {'{"storage":{"personal_results_writes_enabled":true}}': True,
                 '{"storage":{"personal_results_writes_enabled":false}}': False,
                 '{"storage":{"personal_results_writes_enabled":"true"}}': False,
                 '{"storage":{"personal_results_writes_enabled":1}}': False,
                 '{"storage":{}}': False, '{}': False, 'lixo': False, '': False, '[]': False, 'null': False}
        for texto, esperado in casos.items():
            self.assertIs(pr.ler_flag(texto), esperado, texto)

    def test_settings_real_do_repositorio_esta_com_flag_falsa(self):
        self.assertFalse(pr.ler_flag((ROOT / "settings.json").read_text(encoding="utf-8")))

    def test_flag_falsa_nao_faz_nenhuma_chamada_nem_le_nem_grava(self):
        self.escrever_settings(False)
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        antes = json.dumps({k: sorted(v["files"]) for k, v in self.gh.repos.items()})
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual((res["estado"], res["mantidas"]), ("FLAG_DESLIGADA", 1))
        self.assertEqual(self.gh.total_de_chamadas(), 0)
        self.assertEqual(antes, json.dumps({k: sorted(v["files"]) for k, v in self.gh.repos.items()}))

    def test_cli_com_flag_falsa_nao_le_token_nem_usa_rede(self):
        self.escrever_settings(False)
        fila = self.tmp / "fila"
        fila.mkdir()
        (fila / "a.json").write_bytes(tg.entrada(tg.tentativa()))
        class AmbienteIntocavel(dict):
            def get(self, *a, **k):
                raise AssertionError("o ambiente (tokens) não pode ser lido com a flag desligada")

            __getitem__ = get

        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = pr.main(["--fila", str(fila), "--execucao", "1", "--validador-sha", SHA, "--entrada-repo", ENTRADA,
                              "--validador-dir", str(self.validador)], transporte=self._proibido, ambiente=AmbienteIntocavel())
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(saida.getvalue()), {"estado": "FLAG_DESLIGADA", "mantidas": 1, "flag": False})
        self.assertEqual(self.gh.total_de_chamadas(), 0)

    @staticmethod
    def _proibido(*a, **k):
        raise AssertionError("o transporte não pode ser usado com a flag desligada")

    def test_entrada_nao_consegue_ligar_a_flag(self):
        self.escrever_settings(False)
        evento = json.loads(tg.entrada(tg.tentativa()))
        evento["escritas_habilitadas"] = True
        evento["origem"]["escritas_habilitadas"] = True
        res = pr.executar([self.entrar("x.json", json.dumps(evento).encode())], self.contexto(), self.fila)
        self.assertEqual(res["estado"], "FLAG_DESLIGADA")
        self.assertEqual(self.gh.total_de_chamadas(), 0)


class PromocaoTest(Base):
    def test_caminho_feliz_grava_no_historico_recibo_na_fila_e_remove_a_entrada(self):
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["estado"], "PROCESSADO")
        self.assertEqual([(i["status"], i["codigo"]) for i in res["itens"]], [("COMMITTED", "OK")])
        self.assertEqual(len(self.novos_eventos()), 1)
        self.assertIn("recibos/fila-001.json", self.arquivos(ENTRADA))
        self.assertNotIn(f"{pr.FILA_DIR}/fila-001.json", self.arquivos(ENTRADA))
        recibo = json.loads(self.arquivos(ENTRADA)["recibos/fila-001.json"])
        self.assertEqual(recibo["validador_sha"], SHA)
        self.assertNotIn("topic_results", json.dumps(recibo))  # recibo sem dado do evento
        armazenado = json.loads(self.arquivos(DADOS)[self.novos_eventos()[0]])
        self.assertEqual(armazenado["envelope"]["escritor"], "fluxo")

    def test_escrita_no_historico_so_cria_arquivo_novo_e_nunca_apaga(self):
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        pr.executar([entrada], self.contexto(), self.fila)
        escritas = [c for c in self.gh.corpos if c[1] == DADOS]
        self.assertEqual([c[0] for c in escritas], ["PUT"])
        self.assertTrue(all("sha" not in c[3] for c in escritas))  # sem sha, o GitHub recusa sobrescrever (422)
        self.assertTrue(escritas[0][2].startswith("contents/eventos/"))
        self.assertFalse(any(c[0] == "DELETE" and c[1] == DADOS for c in self.gh.corpos))

    def test_repetir_a_mesma_entrada_e_idempotente(self):
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        pr.executar([entrada], self.contexto(), self.fila)
        antes = self.arquivos(DADOS).copy()
        self.gh.repos[ENTRADA]["files"].pop("recibos/fila-001.json")  # a execução anterior foi interrompida antes do recibo
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["itens"][0]["status"], "COMMITTED")
        self.assertEqual(self.arquivos(DADOS), antes)  # nenhum arquivo novo, nenhum sobrescrito

    def test_entrada_rejeitada_vira_so_codigo_e_id_e_sai_da_fila(self):
        evento = tg.tentativa(source_ref="CPF " + tg.CPF_VALIDO)
        entrada = self.entrar("fila-002.json", tg.entrada(evento))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["itens"][0]["status"], "DENIED")
        self.assertEqual(self.novos_eventos(), [])
        rej = json.loads(self.arquivos(ENTRADA)["rejeitadas/fila-002.json"])
        self.assertEqual(set(rej), {"entrada_id", "status", "codigo", "quando"})
        self.assertNotIn(tg.CPF_VALIDO, json.dumps(rej))
        self.assertNotIn(f"{pr.FILA_DIR}/fila-002.json", self.arquivos(ENTRADA))

    def test_processa_em_serie_e_em_ordem_de_nome(self):
        nomes = ["c.json", "a.json", "b.json"]
        entradas = [self.entrar(n, b"lixo") for n in nomes]
        res = pr.executar(entradas, self.contexto(), self.fila)
        self.assertEqual([i["entrada_id"] for i in res["itens"]], ["a.json", "b.json", "c.json"])

    def test_nome_invalido_e_ignorado_sem_tocar_em_nada(self):
        res = pr.executar([("a b.json", b"x"), ("../x.json", b"x"), ("sem-ext", b"x"), (7, b"x")], self.contexto(), self.fila)
        self.assertTrue(all(i["status"] == "IGNORADA" and i["codigo"] == "NOME_INVALIDO" for i in res["itens"]))
        self.assertEqual(self.gh.total_de_chamadas(), 0)


class ControlesTest(Base):
    def rodar(self, **sobre):
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        return pr.executar([entrada], self.contexto(**sobre), self.fila)["itens"][0]

    def test_p1_repositorio_publico_nao_grava(self):
        self.gh.repos[DADOS]["private"] = False
        item = self.rodar()
        self.assertEqual(item["codigo"], "P1_VISIBILIDADE")
        self.assertEqual(self.novos_eventos(), [])

    def test_p1_vale_so_pelo_campo_private_mesmo_sem_visibility(self):
        self.gh.repos[DADOS]["private"] = False
        self.gh.omitir_visibility = True
        item = self.rodar()
        self.assertEqual(item["codigo"], "P1_VISIBILIDADE")
        self.assertEqual(self.novos_eventos(), [])

    def test_p2_destino_publico_ou_diferente_do_configurado_nao_grava(self):
        for alvo in ("Andraus35/UFMS-MEU-ESTUDO", "andraus35/outro-repo"):
            ctx = pr.montar_contexto(dados=self.dados, agora=tg.AGORA, alvo=alvo, validador_dir=self.validador,
                                     validador_sha_fixado=SHA, execucao="1")  # o alvo vem do CLI; o configurado é fixo no código
            entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
            item = pr.executar([entrada], ctx, self.fila)["itens"][0]
            self.assertEqual(item["codigo"], "P2_DESTINO", alvo)
            self.gh.repos[ENTRADA]["files"].clear()
        self.assertEqual(self.novos_eventos(), [])
        self.assertNotIn(("GET", "andraus35/outro-repo", ""), self.gh.chamadas)  # nem chegou a consultar o destino errado

    def test_p3_consentimento_ausente_revogado_ou_de_outro_escopo(self):
        consent = self.arquivos(DADOS)["consent.json"]
        base = json.loads(consent)
        for nome, mudanca in {"revogado": {"revoked_at": "2026-11-17T08:00:00-04:00"}, "escopo": {"scope": "plano"}}.items():
            self.arquivos(DADOS)["consent.json"] = json.dumps({**base, **mudanca}).encode()
            self.assertEqual(self.rodar()["codigo"], "P3_CONSENTIMENTO", nome)
            self.gh.repos[ENTRADA]["files"].clear()
        del self.arquivos(DADOS)["consent.json"]
        self.assertEqual(self.rodar()["codigo"], "P3_CONSENTIMENTO")
        self.assertEqual(self.novos_eventos(), [])

    def test_validador_diferente_do_fixado_recusa_tudo(self):
        (self.validador / ".git" / "HEAD").write_text("b" * 40 + "\n")
        item = self.rodar()
        self.assertEqual(item["codigo"], "VALIDADOR_DIVERGENTE")
        self.assertEqual(self.novos_eventos(), [])
        (self.validador / ".git" / "HEAD").write_text("ref: refs/../../x\n")
        self.assertIsNone(pr.ler_head_sha(self.validador))
        self.assertEqual(self.rodar()["codigo"], "VALIDADOR_DIVERGENTE")

    def test_tokens_trocados_nao_funcionam_e_nao_vazam(self):
        dados_com_token_errado = pr.RepositorioDados(pr.GitHubApi(TOKEN_ENTRADA, self.gh.transporte), DADOS)
        ctx = pr.montar_contexto(dados=dados_com_token_errado, agora=tg.AGORA, alvo=DADOS, validador_dir=self.validador,
                                 validador_sha_fixado=SHA, execucao="1")
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], ctx, self.fila)
        self.assertEqual(res["itens"][0]["status"], "DENIED")
        self.assertEqual(self.novos_eventos(), [])
        for segredo in SEGREDOS:
            self.assertNotIn(segredo, json.dumps(res))

    def test_token_invalido_nao_e_ecoado_e_repr_oculta(self):
        for ruim in ("", "curto", "com espaco no meio 123456", None, 12345678, "x" * 300):
            with self.assertRaises(ValueError) as e:
                pr.GitHubApi(ruim, self.gh.transporte)
            self.assertNotIn(str(ruim) if ruim else "@@", str(e.exception) if ruim and len(str(ruim)) > 8 else "")
        self.assertNotIn(TOKEN_DADOS, repr(self.dados.api))

    def test_falha_de_api_na_leitura_do_historico_fecha(self):
        self.gh.falhar = lambda m, repo, c: 500 if (repo == DADOS and c == "contents/eventos") else None
        item = self.rodar()
        self.assertEqual(item["codigo"], "HISTORICO_ILEGIVEL")
        self.assertEqual(self.novos_eventos(), [])

    def test_historico_acima_do_teto_fecha_em_vez_de_ler_parcial(self):
        base = pg.event_path(tg.recomendacao()["event_id"])
        for i in range(4):
            self.arquivos(DADOS)[base.rsplit("/", 1)[0] + f"/extra-{i}.json"] = b'{"evento": {}}'
        with mock.patch.object(pr, "MAX_HISTORICO", 3):
            item = self.rodar()
        self.assertEqual(item["codigo"], "HISTORICO_ILEGIVEL")
        self.assertEqual(len(self.novos_eventos()), 4)  # só os 4 extras plantados; nada foi promovido

    def test_readback_divergente_deixa_pendente_e_a_entrada_na_fila(self):
        def outro_commit(repo, dados):
            if repo == DADOS:
                dados["head"] = "9" * 40  # outro commit chegou entre a escrita e a leitura de volta
        self.gh.depois_de_criar = outro_commit
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["itens"][0]["status"], "PENDENTE")
        self.assertIn(f"{pr.FILA_DIR}/fila-001.json", self.arquivos(ENTRADA))
        self.assertNotIn("recibos/fila-001.json", self.arquivos(ENTRADA))

    def test_falha_ao_gravar_recibo_mantem_a_entrada_e_a_reexecucao_conclui(self):
        self.gh.falhar = lambda m, repo, c: 500 if (repo == ENTRADA and c.startswith("contents/recibos/") and m == "PUT") else None
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["falhas_de_registro"], 1)
        self.assertIn(f"{pr.FILA_DIR}/fila-001.json", self.arquivos(ENTRADA))
        self.assertEqual(len(self.novos_eventos()), 1)
        self.gh.falhar = lambda *a: None
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["falhas_de_registro"], 0)
        self.assertEqual(len(self.novos_eventos()), 1)  # sem duplicar
        self.assertIn("recibos/fila-001.json", self.arquivos(ENTRADA))
        self.assertNotIn(f"{pr.FILA_DIR}/fila-001.json", self.arquivos(ENTRADA))

    def test_recibo_existente_com_conteudo_diferente_nao_e_sobrescrito(self):
        self.arquivos(ENTRADA)["recibos/fila-001.json"] = b'{"outro":"conteudo"}'
        entrada = self.entrar("fila-001.json", tg.entrada(tg.tentativa()))
        res = pr.executar([entrada], self.contexto(), self.fila)
        self.assertEqual(res["falhas_de_registro"], 1)
        self.assertEqual(self.arquivos(ENTRADA)["recibos/fila-001.json"], b'{"outro":"conteudo"}')


class ApiETransporteTest(Base):
    def test_caminho_malicioso_ou_fora_da_api_e_recusado_sem_chamar(self):
        api = pr.GitHubApi(TOKEN_DADOS, self.gh.transporte)
        for caminho in ("/repos/a/b/../c", "/users/x", "repos/a/b", "/repos/a/b?x=1", "/repos/a/b#f", "/repos/a/b c", "", None):
            with self.assertRaises(pr.ApiError):
                api.chamar("GET", caminho)
        self.assertEqual(self.gh.total_de_chamadas(), 0)

    def test_resposta_ilegivel_ou_transporte_quebrado_vira_apierror_sem_vazar(self):
        for transporte in (lambda *a: (200, b"nao e json"), lambda *a: (_ for _ in ()).throw(OSError(TOKEN_DADOS)),
                           lambda *a: ("200", b"{}"), lambda *a: (500, b'{"message":"x"}')):
            with self.assertRaises(pr.ApiError) as e:
                pr.GitHubApi(TOKEN_DADOS, transporte).chamar("GET", "/repos/a/b")
            self.assertNotIn(TOKEN_DADOS, str(e.exception))

    def test_cabecalho_leva_so_o_token_do_proprio_cliente(self):
        vistos = []

        def espiao(metodo, url, cab, corpo, tempo):
            vistos.append(cab["Authorization"])
            return 200, b"{}"
        pr.GitHubApi(TOKEN_DADOS, espiao).chamar("GET", "/repos/a/b")
        self.assertEqual(vistos, ["Bearer " + TOKEN_DADOS])

    def test_ler_fila_ignora_link_diretorio_e_limita_quantidade(self):
        d = self.tmp / "fila"
        d.mkdir()
        (d / "ok.json").write_text("{}")
        (d / "subdir").mkdir()
        (d / "link.json").symlink_to(d / "ok.json")
        self.assertEqual([n for n, _ in pr.ler_fila(d)], ["ok.json"])
        for i in range(501):
            (d / f"f{i:04d}.json").write_text("{}")
        with self.assertRaises(ValueError):
            pr.ler_fila(d)


class CLITest(Base):
    def rodar_cli(self, ambiente, fila_arquivos=None):
        fila = self.tmp / "fila_cli"
        shutil.rmtree(fila, True)
        fila.mkdir()
        for nome, dados in (fila_arquivos or {}).items():
            (fila / nome).write_bytes(dados)
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = pr.main(["--fila", str(fila), "--execucao", "77", "--validador-sha", SHA, "--entrada-repo", ENTRADA,
                              "--validador-dir", str(self.validador)], transporte=self.gh.transporte, ambiente=ambiente, agora=tg.AGORA)
        return codigo, saida.getvalue()

    def test_cli_com_flag_ligada_promove_e_nao_imprime_token(self):
        bruto = tg.entrada(tg.tentativa())
        self.entrar("fila-001.json", bruto)
        codigo, texto = self.rodar_cli({"DADOS_TOKEN": TOKEN_DADOS, "GH_TOKEN": TOKEN_ENTRADA}, {"fila-001.json": bruto})
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(json.loads(texto)["itens"][0]["status"], "COMMITTED")
        for segredo in SEGREDOS:
            self.assertNotIn(segredo, texto)

    def test_cli_sem_token_ou_com_repo_de_fila_invalido_falha_sem_vazar(self):
        codigo, texto = self.rodar_cli({})
        self.assertEqual(codigo, 1)
        self.assertEqual(json.loads(texto)["codigo"], "ValueError")
        self.assertEqual(self.gh.total_de_chamadas(), 0)
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = pr.main(["--fila", str(self.tmp), "--execucao", "1", "--validador-sha", SHA, "--entrada-repo", "../x",
                              "--validador-dir", str(self.validador)], transporte=self.gh.transporte, ambiente={})
        self.assertEqual((codigo, json.loads(saida.getvalue())["codigo"]), (1, "ENTRADA_REPO_INVALIDO"))

    def test_cli_sai_com_1_se_falhar_ao_registrar(self):
        self.gh.falhar = lambda m, repo, c: 500 if (repo == ENTRADA and c.startswith("contents/recibos/")) else None
        bruto = tg.entrada(tg.tentativa())
        self.entrar("fila-001.json", bruto)
        codigo, _ = self.rodar_cli({"DADOS_TOKEN": TOKEN_DADOS, "GH_TOKEN": TOKEN_ENTRADA}, {"fila-001.json": bruto})
        self.assertEqual(codigo, 1)

    def test_argumentos_exigidos_pelo_runner_estao_no_modelo_do_fluxo(self):
        modelo = (ROOT / "config/modelos_fluxo/promover.yml").read_text(encoding="utf-8")
        passo = modelo[modelo.index("promotion_runner.py"):]
        for flag in ("--fila", "--execucao", "--validador-sha", "--entrada-repo", "--validador-dir"):
            self.assertIn(flag, passo)
        self.assertIn("GH_TOKEN: ${{ github.token }}", modelo)


class FronteirasTest(unittest.TestCase):
    def test_nenhum_teste_toca_a_rede_real(self):
        with mock.patch.object(socket.socket, "connect", side_effect=AssertionError("rede real")):
            gh = GitHubFalso()
            api = pr.GitHubApi(TOKEN_DADOS, gh.transporte)
            self.assertEqual(api.chamar("GET", "/repos/" + DADOS)[0], 200)

    def test_transporte_real_so_aceita_a_api_oficial(self):
        with self.assertRaises(ValueError):
            pr.transporte_urllib("GET", "https://exemplo.invalido/repos/a/b", {}, None, 1)

    def test_codigo_nao_imprime_nem_grava_token_e_flag_so_vem_do_settings(self):
        fonte = (ROOT / "scripts/promotion_runner.py").read_text(encoding="utf-8")
        for proibido in ("personal_results_writes_enabled = True", "print(token", "print(self._token", "write_text(",
                         "write_bytes(", "import subprocess", "os.system", "eval(", "exec("):
            self.assertNotIn(proibido, fonte)
        self.assertIsNone(re.search(r"(?<![.\w])open\(", fonte))  # nenhum open() embutido (abridor.open do urllib não conta)
        self.assertEqual(fonte.count("print("), 4)  # só o resumo e os códigos do CLI
        self.assertIn('personal_results_writes_enabled"] is True', fonte)

    def test_destino_do_historico_e_fixo_no_codigo_e_privado_por_nome(self):
        self.assertEqual(pr.DADOS_REPO, "Andraus35/ufms-meu-estudo-dados")
        self.assertNotEqual(pr.DADOS_REPO.casefold(), "andraus35/ufms-meu-estudo")


if __name__ == "__main__":
    unittest.main()
