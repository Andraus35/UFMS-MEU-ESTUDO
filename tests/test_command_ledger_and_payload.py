"""Contraprovas do registro durável de nonce/idempotência (S4-R3) e do montador de requisição (S5-R12)."""
import json
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_commands as ac  # noqa: E402
import github_issue_payload as gp  # noqa: E402
from command_ledger import SqliteLedger  # noqa: E402

SCHEMA = ac.load_schema()
NOW = datetime(2026, 11, 9, 15, 0, 0, tzinfo=timezone.utc)
KEY = b"chave-sintetica-tutor-0001"


def command(nonce="n-0000000000000001", key="k-00000001", texto="Revisar GER-LEG."):
    cmd = {"schema_version": "1.0", "origin": "tutor", "operation": "enviar_mensagem", "destination": "proprietario",
           "params": {"texto": texto}, "idempotency_key": key, "nonce": nonce,
           "issued_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "signature": ""}
    cmd["signature"] = ac.sign(cmd, KEY)
    return cmd


def run(cmd, ledger):
    return ac.validate_command(cmd, keys={"tutor": KEY}, now=NOW, ledger=ledger, schema=SCHEMA)


class SqliteLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.sqlite"

    def tearDown(self):
        self.tmp.cleanup()

    def test_regras_basicas_e_persistencia_entre_instancias(self):
        a = SqliteLedger(self.path)
        self.assertEqual(run(command(), a)["decision"], ac.ACCEPTED)
        b = SqliteLedger(self.path)  # outra instância, mesmo arquivo: simula novo processo
        self.assertEqual(run(command(), b)["code"], "NONCE_REPETIDO")
        r = run(command(nonce="n-0000000000000002"), b)
        self.assertEqual((r["decision"], r["code"]), (ac.DUPLICATE, "IDEMPOTENTE"))
        r = run(command(nonce="n-0000000000000003", texto="outro corpo"), b)
        self.assertEqual(r["code"], "CHAVE_REUTILIZADA_COM_OUTRO_CORPO")
        self.assertEqual(run(command(nonce="n-0000000000000002"), SqliteLedger(self.path))["code"], "NONCE_REPETIDO")

    def test_recusa_antes_do_registro_nao_grava_nada(self):
        ledger = SqliteLedger(self.path)
        ruim = command()
        ruim["params"]["texto"] = "adulterado"
        self.assertEqual(run(ruim, ledger)["code"], "ASSINATURA_INVALIDA")
        self.assertEqual(run(command(), ledger)["decision"], ac.ACCEPTED)

    def test_concorrencia_so_um_aceita_o_mesmo_nonce(self):
        resultados = []

        def tentar():
            resultados.append(run(command(), SqliteLedger(self.path))["decision"])

        threads = [threading.Thread(target=tentar) for _ in range(12)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(resultados.count(ac.ACCEPTED), 1, resultados)
        self.assertEqual(resultados.count(ac.DENIED), 11, resultados)

    def test_abrir_o_mesmo_arquivo_em_paralelo_nao_levanta_erro_de_bloqueio(self):
        """Regressão: PRAGMA journal_mode concorrente dava 'database is locked' em cerca de 18% das rodadas."""
        for rodada in range(8):
            caminho = Path(self.tmp.name) / f"paralelo-{rodada}.sqlite"
            erros, aceitos = [], []

            def tentar():
                try:
                    aceitos.append(run(command(), SqliteLedger(caminho))["decision"])
                except Exception as exc:  # noqa: BLE001 - o teste existe para pegar qualquer erro
                    erros.append(repr(exc))

            threads = [threading.Thread(target=tentar) for _ in range(12)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(erros, [], rodada)
            self.assertEqual(aceitos.count(ac.ACCEPTED), 1, (rodada, aceitos))
            self.assertEqual(len(aceitos), 12)

    def test_registro_inesperado_falha_fechado(self):
        class Quebrado:
            def admit(self, *a):
                return "talvez"
        self.assertEqual(run(command(), Quebrado())["code"], "REGISTRO_INDISPONIVEL")

    def test_prune_remove_so_o_antigo(self):
        ledger = SqliteLedger(self.path)
        run(command(), ledger)
        ledger.prune(nonces_before="2000-01-01T00:00:00Z", keys_before="2000-01-01T00:00:00Z")
        self.assertEqual(run(command(), ledger)["code"], "NONCE_REPETIDO")
        ledger.prune(nonces_before="2999-01-01T00:00:00Z", keys_before="2999-01-01T00:00:00Z")
        self.assertEqual(run(command(), ledger)["decision"], ac.ACCEPTED)

    def test_nenhum_segredo_armazenado(self):
        ledger = SqliteLedger(self.path)
        run(command(), ledger)
        bruto = self.path.read_bytes()
        self.assertNotIn(KEY, bruto)


class PayloadTests(unittest.TestCase):
    def test_issue_e_comentario_validos_sao_objetos(self):
        req = gp.build_issue("[Zapia -> Claude] Teste", '```json\n{"a": 1}\n```')
        self.assertEqual(req["method"], "POST")
        self.assertIsInstance(req["json"], dict)
        self.assertEqual(set(req["json"]), {"title", "body"})
        gp.validate_request(req)
        com = gp.build_comment(75, "texto")
        self.assertEqual(com["url"], "https://api.github.com/repos/Andraus35/UFMS-MEU-ESTUDO/issues/75/comments")
        self.assertEqual(set(com["json"]), {"body"})
        gp.validate_request(com)

    def test_corpo_como_texto_serializado_ou_lista_e_recusado_causa_do_422(self):
        req = gp.build_issue("t", "corpo")
        for ruim in (json.dumps(req["json"]), [req["json"]], None, "", 5):
            with self.subTest(tipo=type(ruim).__name__):
                with self.assertRaises(ValueError):
                    gp.validate_request({**req, "json": ruim})

    def test_campos_extras_url_e_metodo_fora_da_lista(self):
        req = gp.build_issue("t", "corpo")
        for payload in ({"title": "t", "body": "b", "labels": []}, {"title": "t"}, {"body": "b"}):
            with self.assertRaises(ValueError):
                gp.validate_request({**req, "json": payload})
        for url in ("https://api.github.com/repos/outro/repo/issues", "https://api.github.com/repos/Andraus35/UFMS-MEU-ESTUDO/contents/x.md",
                    "https://api.github.com/repos/Andraus35/UFMS-MEU-ESTUDO/issues/x/comments", "http://api.github.com/repos/Andraus35/UFMS-MEU-ESTUDO/issues"):
            with self.assertRaises(ValueError, msg=url):
                gp.validate_request({**req, "url": url})
        with self.assertRaises(ValueError):
            gp.validate_request({**req, "method": "PUT"})
        with self.assertRaises(ValueError):
            gp.build_issue("t", "b", repo="outro/repo")
        with self.assertRaises(ValueError):
            gp.build_comment(0, "b")
        with self.assertRaises(ValueError):
            gp.build_comment(True, "b")

    def test_titulo_e_limites(self):
        for titulo in ("", "   ", "a\nb", "x" * (gp.MAX_TITLE + 1)):
            with self.assertRaises(ValueError, msg=repr(titulo)):
                gp.build_issue(titulo, "corpo")
        with self.assertRaises(ValueError):
            gp.build_issue("t", "x" * (gp.MAX_BODY + 1))
        gp.build_issue("t", "x" * gp.MAX_BODY)

    def test_filtro_de_segredo_e_dado_pessoal(self):
        for texto in ("ghp_" + "a" * 20, "fulano@example.com", "cpf 529.982.247-25", "id 52998224725"):
            with self.assertRaises(ValueError, msg=texto):
                gp.build_issue("t", texto)
        gp.build_issue("t", "protocolo 12345678901")  # onze dígitos que não são CPF

    def test_filtro_e_linear_em_texto_longo(self):
        import time
        for texto in ("x" * gp.MAX_BODY, "a." * (gp.MAX_BODY // 2), "9" * gp.MAX_BODY, ("a" * 60 + " ") * 900):
            inicio = time.monotonic()
            ac.scan_text(texto, html=True)
            self.assertLess(time.monotonic() - inicio, 2.0)

    def test_divisao_em_partes_numeradas_dentro_do_limite(self):
        corpo = "linha de teste\n" * 20000  # 300 mil caracteres
        partes = gp.split_body(corpo)
        self.assertGreater(len(partes), 1)
        self.assertTrue(all(len(p) <= gp.CHUNK for p in partes))
        self.assertTrue(partes[0].startswith(f"parte 1/{len(partes)}"))
        reconstruido = "".join(p.split("\n\n", 1)[1] for p in partes)
        self.assertEqual(reconstruido, corpo)
        for req in gp.build_comments(75, corpo):
            gp.validate_request(req)
        self.assertEqual(len(gp.split_body("curto")), 1)

    def test_nao_usa_rede_nem_credencial(self):
        source = (ROOT / "scripts/github_issue_payload.py").read_text(encoding="utf-8")
        for proibido in ("import requests", "urllib.request", "import socket", "subprocess", "os.environ", "Authorization"):
            self.assertNotIn(proibido, source, proibido)

    def test_cli_imprime_a_requisicao_sem_enviar(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "corpo.txt"
            arq.write_text("conteúdo", encoding="utf-8")
            self.assertEqual(gp.main(["issue", "--title", "t", "--body-file", str(arq)]), 0)
            self.assertEqual(gp.main(["comment", "--number", "75", "--body-file", str(arq)]), 0)
            arq.write_text("ghp_" + "a" * 20, encoding="utf-8")
            self.assertEqual(gp.main(["issue", "--title", "t", "--body-file", str(arq)]), 1)


if __name__ == "__main__":
    unittest.main()
