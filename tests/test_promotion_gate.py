"""C1: portão de promoção (S6-R4) com fakes injetados: ordem das etapas, fechamento por padrão e contraprovas."""
import hashlib
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promotion_gate as pg  # noqa: E402
from core import topic_rows  # noqa: E402

TOPICS = topic_rows(ROOT)
ALVO = "Andraus35/ufms-meu-estudo-dados"
SHA = "a" * 40
AGORA = datetime(2026, 11, 17, 12, 0, tzinfo=timezone(timedelta(hours=-4)))
CPF_VALIDO = "529.982.247-25"


def com_id(evento):
    evento = dict(evento)
    evento.pop("event_id", None)
    evento["event_id"] = pg.derive_event_id(evento)
    return evento


def recomendacao(rec_id="REC-FICT-1"):
    return com_id({"type": "caderno_recomendado", "timestamp": "2026-11-17T09:00:00-04:00", "caderno_id": "interno-1",
                   "recommendation_id": rec_id, "topic_ids": ["GER-LEG"]})


def tentativa(acertos=8, erros=4, **extra):
    base = {"type": "attempt_recorded", "schema_version": "1.0", "attempt_id": "TENT-FICT-1",
            "recommendation_id": "REC-FICT-1", "platform_notebook_id": "EXT-FICT-44", "source_ref": "synthetic-fixture://c1",
            "recorded_at": "2026-11-17T10:05:00-04:00", "attempt_at": "2026-11-17T09:30:00-04:00",
            "total": acertos + erros, "acertos": acertos, "erros": erros, "nao_respondidas": 0,
            "topic_results": [{"topic_id": "GER-LEG", "attempted": acertos + erros, "correct": acertos}]}
    base.update(extra)
    return com_id(base)


def entrada(evento, agente="tutor", **origem):
    o = {"agente": agente, "escritor": "zapia", "comando_hash": "c" * 64}
    o.update(origem)
    return json.dumps({"entrada_versao": 1, "evento": evento, "origem": o}).encode()


class RepoFake:
    def __init__(self):
        self.arquivos, self.chamadas, self.n, self.head = {}, [], 0, None
        self.falha_criar = self.falha_existentes = False
        self.readback = None  # função opcional que altera a resposta do readback
        self.antes_de_criar = None

    def existentes(self):
        self.chamadas.append("existentes")
        if self.falha_existentes:
            raise RuntimeError("indisponível")
        out = []
        for _, v in sorted(self.arquivos.items()):
            try:
                out.append(json.loads(v)["evento"])
            except (ValueError, KeyError, UnicodeDecodeError):
                continue  # arquivo estranho no histórico: o fake o ignora; o conflito aparece na idempotência
        return out

    def ler(self, path):
        self.chamadas.append("ler")
        return self.arquivos.get(path)

    def criar(self, path, dados):
        self.chamadas.append("criar")
        if self.antes_de_criar:
            self.antes_de_criar(self, path)
        if self.falha_criar or path in self.arquivos:
            raise RuntimeError("422")
        self.arquivos[path] = dados
        self.n += 1
        self.head = hashlib.sha1(str(self.n).encode()).hexdigest()
        return {"commit_sha": self.head}

    def ler_de_volta(self, path):
        self.chamadas.append("ler_de_volta")
        resposta = {"conteudo": self.arquivos[path], "blob_sha": pg.git_blob_sha(self.arquivos[path]), "head_sha": self.head}
        return self.readback(resposta) if self.readback else resposta


def contexto(repo, **sobre):
    log = sobre.pop("log", [])

    def visibilidade(alvo):
        log.append("p1")
        return {"private": True, "visibility": "private", "full_name": alvo}

    def consentimento():
        log.append("p3")
        return {"version": "v3", "scope": "resultados_estudo", "granted_at": "2026-11-16T10:00:00-04:00", "revoked_at": None}

    ctx = {"agora": AGORA, "alvo": ALVO, "configurado": ALVO, "leitor_visibilidade": visibilidade,
           "leitor_consentimento": consentimento, "escritas_habilitadas": True, "repositorio": repo, "topicos": TOPICS,
           "validador_sha": SHA, "validador_sha_fixado": SHA, "execucao": "9876543210", "entrada_id": "fila-001.json", "log": log}
    ctx.update(sobre)
    return ctx


def preparar(com_recomendacao=True):
    repo = RepoFake()
    if com_recomendacao:
        rec = recomendacao()
        assert pg.promover(entrada(rec), contexto(repo))["status"] == "COMMITTED"
    return repo


class PortaoTests(unittest.TestCase):
    # caminho feliz e identidade -------------------------------------------------------------------------------
    def test_caminho_feliz_grava_um_arquivo_com_envelope_e_recibo_sem_dado(self):
        repo = preparar()
        ev = tentativa()
        r = pg.promover(entrada(ev, agente="coach"), contexto(repo))
        self.assertEqual(r["status"], "COMMITTED", r)
        self.assertFalse(r["ja_registrado"])
        self.assertRegex(r["path"], r"^eventos/2026-11/20261117-[0-9a-f]{12}\.json$")
        guardado = json.loads(repo.arquivos[r["path"]])
        env = guardado["envelope"]
        self.assertEqual((env["origem"], env["entregue_por"], env["escritor"], env["validador_sha"], env["execucao"]),
                         ("coach", "zapia", "fluxo", SHA, "9876543210"))
        self.assertEqual(env["hash_corpo"], pg.sha256_hex(pg.canonical(ev)))
        self.assertEqual(guardado["evento"], ev)
        recibo = json.dumps(r["recibo"])
        self.assertNotIn("TENT-FICT-1", recibo)
        self.assertNotIn("acertos", recibo)

    # marca de evento sintético (C5) -----------------------------------------------------------------------------
    def entrada_marcada(self, ev, valor):
        corpo = json.loads(entrada(ev))
        corpo["sintetico"] = valor
        return json.dumps(corpo).encode()

    def test_entrada_sintetica_grava_com_a_marca_no_envelope_e_a_normal_nao_tem_marca(self):
        repo = preparar()
        r = pg.promover(self.entrada_marcada(tentativa(), True), contexto(repo))
        self.assertEqual(r["status"], "COMMITTED", r)
        self.assertIs(json.loads(repo.arquivos[r["path"]])["envelope"]["sintetico"], True)
        repo2 = preparar()
        r2 = pg.promover(entrada(tentativa()), contexto(repo2))
        self.assertEqual(r2["status"], "COMMITTED", r2)
        self.assertNotIn("sintetico", json.loads(repo2.arquivos[r2["path"]])["envelope"])  # evento real: envelope inalterado

    def test_marca_so_aceita_o_booleano_true(self):
        for valor in (False, "true", 1, 0, None, [], {}, "sim"):
            repo = preparar()
            antes = dict(repo.arquivos)
            r = pg.promover(self.entrada_marcada(tentativa(), valor), contexto(repo))
            self.assertEqual((r["status"], r["codigo"]), ("DENIED", "ENTRADA_CAMPOS"), valor)
            self.assertEqual(repo.arquivos, antes, valor)  # nada foi gravado

    def test_outro_campo_extra_continua_recusado_mesmo_com_a_marca(self):
        corpo = json.loads(self.entrada_marcada(tentativa(), True))
        corpo["extra"] = 1
        r = pg.promover(json.dumps(corpo).encode(), contexto(preparar()))
        self.assertEqual((r["status"], r["codigo"]), ("DENIED", "ENTRADA_CAMPOS"))

    def test_event_id_e_data_mais_hash_do_corpo_e_muda_com_o_conteudo(self):
        a, b = tentativa(), tentativa(acertos=9)
        self.assertRegex(a["event_id"], r"^20261117-[0-9a-f]{12}$")
        self.assertNotEqual(a["event_id"], b["event_id"])
        self.assertEqual(a["event_id"], pg.derive_event_id(a))

    def test_arquivo_guardado_e_canonico_e_estavel(self):
        repo = preparar()
        r = pg.promover(entrada(tentativa()), contexto(repo))
        dados = repo.arquivos[r["path"]]
        self.assertEqual(dados, pg.canonical(json.loads(dados)))

    # idempotência e conflito ----------------------------------------------------------------------------------
    def test_mesmo_evento_duas_vezes_nao_grava_de_novo(self):
        repo = preparar()
        e = entrada(tentativa())
        primeiro = pg.promover(e, contexto(repo))
        antes = repo.n
        segundo = pg.promover(e, contexto(repo, execucao="1111111111"))
        self.assertEqual((segundo["status"], segundo["ja_registrado"]), ("COMMITTED", True))
        self.assertEqual(repo.n, antes)
        self.assertEqual(primeiro["path"], segundo["path"])

    def test_corpo_diferente_no_mesmo_caminho_e_conflito(self):
        repo = preparar()
        ev = tentativa()
        repo.arquivos[pg.event_path(ev["event_id"])] = pg.canonical({"evento": dict(ev, total=99), "envelope": {}})
        r = pg.promover(entrada(ev), contexto(repo))
        self.assertEqual((r["status"], r["codigo"]), ("DENIED", "CONFLITO_ID"))

    def test_arquivo_ilegivel_no_caminho_e_conflito(self):
        repo = preparar()
        ev = tentativa()
        repo.arquivos[pg.event_path(ev["event_id"])] = b"\xff\xfe nao e json"
        self.assertEqual(pg.promover(entrada(ev), contexto(repo))["codigo"], "CONFLITO_ID")

    def test_corrida_com_outro_escritor_vira_escrita_falhou_e_a_repeticao_e_idempotente(self):
        repo = preparar()
        ev = tentativa()
        e = entrada(ev)

        def outro(r, path):
            r.arquivos[path] = pg.canonical({"evento": ev, "envelope": {}})
        repo.antes_de_criar = outro
        self.assertEqual(pg.promover(e, contexto(repo))["codigo"], "ESCRITA_FALHOU")
        repo.antes_de_criar = None
        self.assertTrue(pg.promover(e, contexto(repo))["ja_registrado"])

    # flag, P1, P2, P3 -----------------------------------------------------------------------------------------
    def test_flag_desligada_nao_promove_nada_e_mantem_na_fila(self):
        repo = preparar(com_recomendacao=False)
        r = pg.promover(entrada(recomendacao()), contexto(repo, escritas_habilitadas=False))
        self.assertEqual((r["status"], r["codigo"], r["mantem_na_fila"]), ("NOT_IMPLEMENTED", "FLAG_DESLIGADA", True))
        self.assertEqual(repo.n, 0)
        for valor in (None, "true", 1, 0):
            self.assertEqual(pg.promover(entrada(recomendacao()), contexto(RepoFake(), escritas_habilitadas=valor))["status"], "NOT_IMPLEMENTED")

    def test_p1_visibilidade_publica_erro_ou_resposta_malformada_bloqueiam(self):
        def levanta(_):
            raise RuntimeError("404")
        casos = [lambda a: {"private": False, "visibility": "public", "full_name": a}, levanta, lambda a: "x", lambda a: None,
                 lambda a: {"private": True, "visibility": "public", "full_name": a},
                 lambda a: {"private": True, "visibility": "private", "full_name": "outro/repo"}, lambda a: {}]
        for leitor in casos:
            repo = preparar(com_recomendacao=False)
            r = pg.promover(entrada(recomendacao()), contexto(repo, leitor_visibilidade=leitor))
            self.assertEqual((r["status"], r["codigo"]), ("DENIED", "P1_VISIBILIDADE"))
            self.assertEqual(repo.n, 0)

    def test_p2_destino_publico_ou_diferente_do_configurado_bloqueia(self):
        for alvo, configurado in (("Andraus35/UFMS-MEU-ESTUDO", "Andraus35/UFMS-MEU-ESTUDO"), (ALVO, "outro/repo-privado"),
                                  ("outro/repo-privado", ALVO), (None, ALVO), ("sem-barra", ALVO)):
            repo = preparar(com_recomendacao=False)
            r = pg.promover(entrada(recomendacao()), contexto(repo, alvo=alvo, configurado=configurado))
            self.assertEqual(r["codigo"], "P2_DESTINO", (alvo, configurado))
            self.assertEqual(repo.n, 0)

    def test_p3_consentimento_ausente_revogado_ou_de_outro_escopo_bloqueia(self):
        base = {"version": "v3", "scope": "resultados_estudo", "granted_at": "2026-11-16T10:00:00-04:00", "revoked_at": None}
        casos = [None, "texto", {}, dict(base, revoked_at="2026-11-17T00:00:00-04:00"), dict(base, scope="plano_estudo"),
                 dict(base, granted_at="2026-12-01T10:00:00-04:00"), dict(base, granted_at="2026-11-16T10:00:00"), dict(base, version="")]
        for consent in casos:
            repo = preparar(com_recomendacao=False)
            r = pg.promover(entrada(recomendacao()), contexto(repo, leitor_consentimento=lambda c=consent: c))
            self.assertEqual(r["codigo"], "P3_CONSENTIMENTO", consent)
            self.assertEqual(repo.n, 0)

        def levanta():
            raise RuntimeError("403")
        self.assertEqual(pg.promover(entrada(recomendacao()), contexto(RepoFake(), leitor_consentimento=levanta))["codigo"], "P3_CONSENTIMENTO")

    # forma ----------------------------------------------------------------------------------------------------
    def test_forma_invalida_e_recusada_antes_de_tocar_no_historico(self):
        ev = recomendacao()
        grande = json.dumps({"entrada_versao": 1, "evento": dict(ev, nota="x" * 20000), "origem": {}}).encode()
        casos = {
            "ENTRADA_GRANDE": grande, "ENTRADA_INVALIDA": b"{nao json", "ENTRADA_CAMPOS": b'{"entrada_versao":1}',
            "ENTRADA_TIPO": "texto, não bytes", "ENTRADA_INVALIDA ": b'{"entrada_versao":1,"entrada_versao":1,"evento":{},"origem":{}}',
            "ENTRADA_VERSAO": json.dumps({"entrada_versao": 2, "evento": ev, "origem": {"agente": "tutor", "escritor": "zapia", "comando_hash": "c" * 64}}).encode(),
            "ORIGEM_INVALIDA": entrada(ev, agente="zapia"), "ORIGEM_INVALIDA  ": entrada(ev, escritor="humano"),
            "ORIGEM_HASH": entrada(ev, comando_hash="xyz"), "ORIGEM_CAMPOS": entrada(ev, extra="x"),
            "EVENTO_TIPO": json.dumps({"entrada_versao": 1, "evento": [], "origem": {"agente": "tutor", "escritor": "zapia", "comando_hash": "c" * 64}}).encode(),
        }
        for esperado, raw in casos.items():
            repo = RepoFake()
            r = pg.promover(raw, contexto(repo))
            self.assertEqual((r["status"], r["codigo"]), ("DENIED", esperado.strip()), esperado)
            self.assertEqual(repo.chamadas, [], esperado)

    # esquema --------------------------------------------------------------------------------------------------
    def test_esquema_tipo_total_recomendacao_versao_e_id(self):
        repo = preparar()
        casos = {
            "TIPO_NAO_SUPORTADO": com_id({"type": "plano_recebido", "timestamp": "2026-11-17T09:00:00-04:00"}),
            "ESQUEMA_INVALIDO": tentativa(total=1),
            "ESQUEMA_INVALIDO ": tentativa(recommendation_id="REC-INEXISTENTE"),
            "ESQUEMA_INVALIDO  ": tentativa(schema_version="9.9"),
            "ID_AUSENTE": {k: v for k, v in tentativa().items() if k != "event_id"},
            "ID_DIVERGENTE": dict(tentativa(), event_id="20261117-" + "0" * 12),
            "ID_DATA_INVALIDA": dict(tentativa(), recorded_at="ontem"),
        }
        for esperado, ev in casos.items():
            r = pg.promover(entrada(ev), contexto(repo))
            self.assertEqual(r["status"], "DENIED", (esperado, r))
            self.assertIn(r["codigo"], (esperado.strip(), "ESQUEMA_INVALIDO"), esperado)
        self.assertEqual(repo.n, 1)  # só a recomendação do preparo

    # filtro ---------------------------------------------------------------------------------------------------
    def test_filtro_recusa_cpf_email_segredo_campo_proibido_e_texto_longo(self):
        repo = preparar()
        casos = {
            "cpf": tentativa(source_ref=CPF_VALIDO), "email": tentativa(source_ref="a.b@exemplo.com"),
            "segredo": tentativa(platform_notebook_id="github_pat_" + "A" * 30), "campo": tentativa(enunciado="qual é a regra?"),
            "longo": tentativa(source_ref="y" * 2500), "html": tentativa(source_ref="<script>x</script>"),
        }
        for nome, ev in casos.items():
            r = pg.promover(entrada(ev), contexto(repo))
            self.assertEqual(r["status"], "DENIED", nome)
            self.assertTrue(r["codigo"].startswith("FILTRO_"), (nome, r["codigo"]))
        self.assertEqual(repo.n, 1)

    # validador e contexto -------------------------------------------------------------------------------------
    def test_validador_fora_do_sha_fixado_ou_execucao_invalida_nem_le_o_historico(self):
        for sobre in ({"validador_sha": "b" * 40}, {"validador_sha": "xyz", "validador_sha_fixado": "xyz"}, {"validador_sha_fixado": None},
                      {"execucao": "../x"}, {"execucao": ""}, {"repositorio": None}):
            repo = RepoFake()
            sobre = dict(sobre)
            r = pg.promover(entrada(recomendacao()), contexto(sobre.pop("repositorio", repo) if False else repo, **sobre))
            self.assertEqual(r["status"], "DENIED", sobre)
            self.assertEqual(repo.chamadas, [], sobre)
            self.assertEqual(repo.n, 0)

    def test_historico_ilegivel_ou_erro_inesperado_fecha(self):
        repo = RepoFake()
        repo.falha_existentes = True
        self.assertEqual(pg.promover(entrada(recomendacao()), contexto(repo))["codigo"], "HISTORICO_ILEGIVEL")
        self.assertEqual(repo.n, 0)
        r = pg.promover(entrada(recomendacao()), contexto(RepoFake(), topicos=object()))
        self.assertEqual(r["status"], "DENIED")

    # escrita e readback ---------------------------------------------------------------------------------------
    def test_falha_ao_criar_nao_deixa_arquivo(self):
        repo = preparar()
        repo.falha_criar = True
        r = pg.promover(entrada(tentativa()), contexto(repo))
        self.assertEqual((r["status"], r["codigo"]), ("DENIED", "ESCRITA_FALHOU"))
        self.assertEqual(repo.n, 1)

    def test_readback_divergente_ausente_ou_com_head_diferente_fica_pendente_nunca_confirmado(self):
        alteracoes = {
            "conteudo": lambda r: dict(r, conteudo=r["conteudo"] + b" "),
            "blob": lambda r: dict(r, blob_sha="0" * 40),
            "head": lambda r: dict(r, head_sha="1" * 40),
            "malformado": lambda r: {"conteudo": r["conteudo"]},
        }
        for nome, alterar in alteracoes.items():
            repo = preparar()
            repo.readback = alterar
            r = pg.promover(entrada(tentativa()), contexto(repo))
            self.assertEqual((r["status"], r["codigo"]), ("PENDENTE", "READBACK_DIVERGENTE"), nome)
            self.assertNotEqual(r["status"], "COMMITTED")

    def test_pendente_pode_ser_repetido_com_seguranca(self):
        repo = preparar()
        repo.readback = lambda r: dict(r, blob_sha="0" * 40)
        e = entrada(tentativa())
        self.assertEqual(pg.promover(e, contexto(repo))["status"], "PENDENTE")
        repo.readback = None
        r = pg.promover(e, contexto(repo))
        self.assertEqual((r["status"], r["ja_registrado"]), ("COMMITTED", True))
        self.assertEqual(repo.n, 2)

    # rejeição e ordem -----------------------------------------------------------------------------------------
    def test_registro_de_rejeicao_tem_so_codigo_e_id_da_entrada_sem_eco_do_conteudo(self):
        repo = preparar()
        ev = tentativa(source_ref="SENTINELA-SECRETA " + CPF_VALIDO)
        r = pg.promover(entrada(ev), contexto(repo, entrada_id="fila-001.json"))
        rej = r["rejeicao"]
        self.assertEqual(set(rej), {"entrada_id", "status", "codigo", "quando"})
        self.assertEqual(rej["entrada_id"], "fila-001.json")
        self.assertNotIn("SENTINELA", json.dumps(r))
        self.assertNotIn(CPF_VALIDO, json.dumps(r))
        self.assertEqual(rej["quando"], "2026-11-17T16:00:00Z")

    def test_nome_de_entrada_malicioso_vira_invalido(self):
        for nome in ("../x", "a/b", "a b", "", "x" * 100, None, 7):
            r = pg.promover(b"{", contexto(RepoFake(), entrada_id=nome))
            self.assertEqual(r["rejeicao"]["entrada_id"], "invalido")

    def test_ordem_das_etapas_p1_antes_de_p3_e_ambos_antes_da_flag(self):
        log = []
        repo = preparar(com_recomendacao=False)
        pg.promover(entrada(recomendacao()), contexto(repo, log=log, escritas_habilitadas=False))
        self.assertEqual(log, ["p1", "p3"])
        log2 = []
        r = pg.promover(entrada(recomendacao()), contexto(RepoFake(), log=log2, leitor_visibilidade=lambda a: {"private": False}))
        self.assertEqual((r["codigo"], log2), ("P1_VISIBILIDADE", []))  # P3 não é lida se P1 falha

    def test_flag_desligada_com_entrada_invalida_continua_negando_pela_forma(self):
        r = pg.promover(b"{", contexto(RepoFake(), escritas_habilitadas=False))
        self.assertEqual((r["status"], r["codigo"]), ("DENIED", "ENTRADA_INVALIDA"))

    def test_nenhuma_recusa_escreve(self):
        repo = preparar()
        antes = repo.n
        for raw in (b"{", entrada(tentativa(source_ref=CPF_VALIDO)), entrada(tentativa(total=1))):
            pg.promover(raw, contexto(repo))
        pg.promover(entrada(tentativa()), contexto(repo, escritas_habilitadas=False))
        pg.promover(entrada(tentativa()), contexto(repo, leitor_visibilidade=lambda a: {"private": False}))
        self.assertEqual(repo.n, antes)

    # fronteiras do módulo -------------------------------------------------------------------------------------
    def test_modulo_nao_usa_rede_nem_processo_nem_arquivo(self):
        fonte = (ROOT / "scripts" / "promotion_gate.py").read_text(encoding="utf-8")
        for proibido in ("urllib", "http.client", "socket", "requests", "subprocess", "os.environ", "open(", "Path("):
            self.assertNotIn(proibido, fonte, proibido)

    def test_flag_real_continua_falsa_e_o_modulo_nao_a_le(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertNotIn("settings", (ROOT / "scripts" / "promotion_gate.py").read_text(encoding="utf-8").split('"""', 2)[2])


if __name__ == "__main__":
    unittest.main()
