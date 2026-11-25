"""Contraprovas do emissor da campainha (ZAPIA-EMISSOR, E34). Offline: transporte falso, sem rede."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sinal_emissor as se  # noqa: E402

TOKEN = "ghs_" + "a" * 30
REPO = "Andraus35/ufms-meu-estudo-entrada"


def resumo(itens, estado="PROCESSADO", flag=True, falhas=0):
    return json.dumps({"flag": flag, "itens": itens, "falhas_de_registro": falhas, "estado": estado})


class Falso:
    def __init__(self, status=201):
        self.chamadas, self.status = [], status

    def __call__(self, metodo, url, cab, corpo, tempo):
        self.chamadas.append((metodo, url, json.loads(corpo) if corpo else None))
        return self.status, b"{}"


class ContarTest(unittest.TestCase):
    def test_conta_so_promovidos(self):
        itens = [{"entrada_id": "a.json", "status": "PROMOVER"}, {"entrada_id": "b.json", "status": "REJEITAR"},
                 {"entrada_id": "c.json", "status": "PROMOVER"}, {"entrada_id": "d.json", "status": "IGNORADA"},
                 {"entrada_id": "e.json", "status": "PROMOVER"}, {"entrada_id": "f.json", "status": "MANTIDA"},
                 {"entrada_id": "g.json", "status": "IGNORADA"}]
        self.assertEqual(se.contar(resumo(itens)), 3)

    def test_duvida_vale_zero(self):
        ok = [{"status": "PROMOVER"}]
        for texto in ("", "nao e json", "[]", "{}", resumo(ok, estado="FLAG_DESLIGADA"), resumo(ok, flag=False),
                      resumo(ok, falhas=1), resumo(ok, estado="VALIDADOR_DIVERGENTE"), json.dumps({"itens": ok})):
            self.assertEqual(se.contar(texto), 0, texto)

    def test_item_malformado_nao_conta(self):
        self.assertEqual(se.contar(resumo(["PROMOVER", None, 3, {"status": "promover"}])), 0)

    def test_cli_contar_escreve_so_a_contagem(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "r.json"
            arq.write_text(resumo([{"status": "PROMOVER"}]), encoding="utf-8")
            import contextlib
            import io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(se.main(["--contar", str(arq)]), 0)
            self.assertEqual(buf.getvalue(), "promovidos=1\n")
            with contextlib.redirect_stdout(buf):
                se.main(["--contar", str(Path(d) / "ausente.json")])
            self.assertTrue(buf.getvalue().endswith("promovidos=0\n"))


class EmitirTest(unittest.TestCase):
    def test_flag_desligada_nao_faz_rede(self):
        t = Falso()
        for flag in (False, None, "true", 1):
            self.assertEqual(se.emitir(REPO, TOKEN, t, flag), {"estado": "FLAG_DESLIGADA"})
        self.assertEqual(t.chamadas, [])

    def test_titulo_fixo_e_corpo_vazio(self):
        t = Falso()
        r = se.emitir(REPO, TOKEN, t, True)
        self.assertEqual(r, {"estado": "EMITIDO", "http": 201})
        self.assertEqual(t.chamadas, [("POST", "https://api.github.com/repos/%s/issues" % REPO,
                                       {"title": "SINAL comando-promovido", "body": ""})])

    def test_repositorio_invalido_recusado_sem_rede(self):
        t = Falso()
        for repo in ("", None, "sem-barra", "a/b/../c", "a/b c"):
            self.assertEqual(se.emitir(repo, TOKEN, t, True)["estado"], "ERRO")
        self.assertEqual(t.chamadas, [])

    def test_erro_de_api_nao_vaza_token(self):
        r = se.emitir(REPO, TOKEN, Falso(status=403), True)
        self.assertEqual(r["estado"], "ERRO")
        self.assertNotIn(TOKEN, json.dumps(r))
        r2 = se.emitir(REPO, "curto", Falso(), True)
        self.assertEqual(r2["estado"], "ERRO")
        self.assertNotIn("curto", json.dumps(r2))

    def test_titulo_e_constante_sem_entrada_variavel(self):
        import inspect
        self.assertEqual(inspect.signature(se.emitir).parameters.keys(), {"entrada_repo", "token", "transporte", "flag"})
        self.assertEqual(se.TITULO, "SINAL comando-promovido")
        self.assertEqual(se.CORPO, "")

    def test_cli_emitir_respeita_a_flag_do_validador(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            for flag in (False, True):
                Path(d, "settings.json").write_text(json.dumps({"storage": {"private_flow_promotion_enabled": flag}}), encoding="utf-8")
                t = Falso()
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = se.main(["--emitir", "--entrada-repo", REPO, "--validador-dir", d], transporte=t, ambiente={"GH_TOKEN": TOKEN})
                self.assertEqual(len(t.chamadas), 0 if not flag else 1)
                self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
