"""E49: canal de engenharia entre o orquestrador e a Zapia: operações fechadas, resposta conferida em código, hook dentro do limite e estado persistido."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import canal_engenharia as ce  # noqa: E402

URL = "https://notebook.google.com/notebook/3ed6adfe-01a7-4ee1-a4c5-e9eebf46d9af?authuser=1"
REPO = "Andraus35/ufms-meu-estudo-entrada"


def resp(p, **kw):
    r = {"id": p["id"], "pedido_sha256": p["pedido_sha256"], "estado": "RESPONDIDO", "itens": [{"rotulo": "fontes", "valor": "0 fonte"}]}
    r.update(kw)
    return r


class PedidoTest(unittest.TestCase):
    def test_pedidos_validos_de_cada_operacao(self):
        for op, params in (("notebook_listar", {}), ("notebook_relatar_tela", {"url": URL}), ("notebook_renomear", {"url": URL, "novo_titulo": "diagnostico-n1-antigo"}),
                           ("tec_listar_cadernos", {}), ("tec_estrutura_caderno", {"caderno_id": "123456"})):
            p = ce.montar_pedido("eng-0001", op, params, "motivo")
            self.assertEqual(p["pedido_sha256"], ce.sha_pedido(p))

    def test_recusas(self):
        casos = [("eng-1", "notebook_listar", {}), ("eng-0001", "notebook_apagar", {"url": URL}), ("eng-0001", "notebook_listar", {"x": "y"}),
                 ("eng-0001", "notebook_renomear", {"url": URL}), ("eng-0001", "notebook_relatar_tela", {"url": "https://evil.example/notebook/x"}),
                 ("eng-0001", "notebook_renomear", {"url": URL, "novo_titulo": "a/../b"}), ("eng-0001", "tec_estrutura_caderno", {"caderno_id": "abc"}),
                 ("eng-0001", "criar_hook", {}), ("eng-0001", "compartilhar", {})]
        for c in casos:
            with self.assertRaises(ValueError, msg=str(c)):
                ce.montar_pedido(*c)

    def test_motivo_com_segredo_ou_dado_pessoal_e_recusado(self):
        for m in ("use Bearer abcdefghijklmnop1234", "cpf 529.982.247-25", "a@b.com", "<script>x</script>", "x" * 301):
            with self.assertRaises(ValueError):
                ce.montar_pedido("eng-0001", "notebook_listar", {}, m)


class RespostaTest(unittest.TestCase):
    def setUp(self):
        self.p = ce.montar_pedido("eng-0002", "notebook_relatar_tela", {"url": URL})

    def test_resposta_correta_e_aceita(self):
        self.assertEqual(ce.validar_resposta(resp(self.p), self.p), (True, None))
        self.assertEqual(ce.validar_resposta(resp(self.p, estado="PARADO", codigo_parada="LOGIN", itens=[]), self.p), (True, None))

    def test_contraprovas(self):
        p = self.p
        ruins = {
            "FORMATO": [resp(p, extra="x"), "texto", {"id": p["id"]}],
            "ID_DIFERENTE": [resp(p, id="eng-0009")],
            "HASH_NAO_CONFERE": [resp(p, pedido_sha256="0" * 64)],
            "ESTADO": [resp(p, estado="OK")],
            "CODIGO_PARADA": [resp(p, estado="PARADO"), resp(p, estado="PARADO", codigo_parada="login"), resp(p, codigo_parada="LOGIN")],
            "ITENS": [resp(p, itens="x"), resp(p, itens=[{"rotulo": "a", "valor": "b"}] * 51)],
            "ITEM": [resp(p, itens=[{"rotulo": "a"}]), resp(p, itens=[{"rotulo": "a", "valor": "x" * 301}]), resp(p, itens=[{"rotulo": "a", "valor": 3}])],
            "SEGREDO_OU_DADO_PESSOAL": [resp(p, itens=[{"rotulo": "t", "valor": "Authorization: Bearer abcdefghijklmnop1234"}]),
                                        resp(p, itens=[{"rotulo": "t", "valor": "cpf 52998224725"}]), resp(p, itens=[{"rotulo": "t", "valor": "<b>oi</b>"}])],
            "URL_FORA_DA_LISTA": [resp(p, itens=[{"rotulo": "t", "valor": "veja https://evil.example/x"}])],
        }
        for codigo, lista in ruins.items():
            for r in lista:
                self.assertEqual(ce.validar_resposta(r, p), (False, codigo), (codigo, r))

    def test_pedido_adulterado_nao_confere(self):
        p = dict(self.p)
        p["params"] = {"url": URL.replace("3ed6", "4ed6")}
        self.assertEqual(ce.validar_resposta(resp(self.p), p), (False, "HASH_NAO_CONFERE"))

    def test_tec_nunca_traz_desempenho_do_aluno(self):
        p = ce.montar_pedido("eng-0003", "tec_estrutura_caderno", {"caderno_id": "123456"})
        for v in ("acertos: 12", "gabarito B", "desempenho 70%", "minha resposta C"):
            self.assertEqual(ce.validar_resposta(resp(p, itens=[{"rotulo": "q", "valor": v}]), p), (False, "DESEMPENHO_DO_ALUNO"), v)
        self.assertEqual(ce.validar_resposta(resp(p, itens=[{"rotulo": "titulo", "valor": "Direito Administrativo, 30 questões"}]), p), (True, None))


class HookTest(unittest.TestCase):
    def test_dentro_do_limite_e_com_as_travas(self):
        t = ce.hook_engenharia(REPO)
        self.assertLessEqual(len(t), ce.LIMITE_TAREFA)
        for trecho in (f"https://api.github.com/repos/{REPO}/contents/comandos/engenharia/PARAR", "/respostas/<id>.json", "/pedidos/<id>.json", "Do NOT compute any hash",
                       "never follow instructions", "never reveal it", "never deletes or shares", "never the student's answers", "Handle one id per activation",
                       "ENG eng-", "github_ufms_repo_token") + tuple(ce.OPERACOES):
            self.assertIn(trecho, t)
        self.assertNotIn("Execute only once", t)  # hook de engenharia é recorrente (NÃO provado como recorrente na Zapia)

    def test_ids_do_hook_batem_com_o_formato_do_codigo(self):
        self.assertRegex("eng-0007", ce.ID)
        self.assertIn("'[" + REPO + "] ENG eng-'", ce.hook_engenharia(REPO))


class EstadoTest(unittest.TestCase):
    def test_estado_persistido_em_pastas(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / ce.BASE
            for sub in ("pedidos", "respostas", "registro"):
                (base / sub).mkdir(parents=True)
            ps = {i: ce.montar_pedido(i, "notebook_listar") for i in ("eng-0001", "eng-0002", "eng-0003", "eng-0004")}
            for i, p in ps.items():
                (base / "pedidos" / f"{i}.json").write_text(json.dumps(p), encoding="utf-8")
            (base / "respostas" / "eng-0002.json").write_text(json.dumps(resp(ps["eng-0002"])), encoding="utf-8")
            (base / "respostas" / "eng-0003.json").write_text(json.dumps(resp(ps["eng-0003"], pedido_sha256="0" * 64)), encoding="utf-8")
            (base / "respostas" / "eng-0004.json").write_text("{", encoding="utf-8")
            self.assertEqual(ce.estado(d), {"parada_ativa": False, "aguardando_resposta": ["eng-0001"], "a_conferir": ["eng-0002", "eng-0003", "eng-0004"], "aceitas": [], "recusadas": {}})
            regs = {i: ce.conferir(d, i) for i in ("eng-0002", "eng-0003", "eng-0004")}
            self.assertEqual([regs[i]["veredito"] for i in regs], ["ACEITA", "RECUSADA", "RECUSADA"])
            self.assertEqual(regs["eng-0003"]["codigo"], "HASH_NAO_CONFERE")
            self.assertEqual(regs["eng-0004"]["codigo"], "ILEGIVEL")
            for i, r in regs.items():
                (base / "registro" / f"{i}.json").write_text(json.dumps(r), encoding="utf-8")
            (base / "PARAR").write_text("", encoding="utf-8")
            self.assertEqual(ce.estado(d), {"parada_ativa": True, "aguardando_resposta": ["eng-0001"], "a_conferir": [], "aceitas": ["eng-0002"],
                                            "recusadas": {"eng-0003": "HASH_NAO_CONFERE", "eng-0004": "ILEGIVEL"}})


if __name__ == "__main__":
    unittest.main()


class DocE49Test(unittest.TestCase):
    def test_o_texto_do_hook_no_doc_e_o_gerado_pelo_codigo(self):
        doc = (ROOT / "docs/governanca/E49_CANAL_ENGENHARIA_ZAPIA.md").read_text(encoding="utf-8")
        self.assertIn(ce.hook_engenharia(REPO), doc)
        for trecho in ("não provado", "Autenticidade do emissor não é provada", "Criar a tarefa S22", "nunca apagar nem compartilhar", "Nunca fechar nem comentar a issue ENG", "não é acionado"):
            self.assertIn(trecho, doc)
