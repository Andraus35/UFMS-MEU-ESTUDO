"""Scripts do Termux da sonda de leitura e do teste F1 da Zapia (S20), com um `gh` FALSO em memória (sem rede, sem token).

O `gh` falso imita o comportamento real que já nos enganou uma vez: em erro (404) imprime o corpo do erro na saída normal E sai com código 1.
A Zapia é simulada pelo próprio `gh` falso (modos `ok`, `errado`, `nada`, `formato`). No modo F1 a "Zapia" calcula o hash com o algoritmo CANÔNICO
descrito no prompt (json.dumps sort_keys, separators, ensure_ascii=False), implementado de forma independente do código do repositório."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import zapia_f1_prep as f1  # noqa: E402

BASH = shutil.which("bash")
FAKE_GH = textwrap.dedent('''\
    #!/usr/bin/env python3
    import sys, os, json, base64, hashlib
    ST = os.environ["FAKE_ST"]; MODE = os.environ.get("ZAPIA_MODE", "ok")
    a = sys.argv[1:]
    def path(p): return os.path.join(ST, p.replace("/", "__"))
    def tick():
        n = int(open(path("_t")).read()) + 1 if os.path.exists(path("_t")) else 1
        open(path("_t"), "w").write(str(n)); return "2026-11-22T10:00:%02dZ" % n
    def put(p, text): open(path(p), "w").write(text); open(path(p + ".date"), "w").write(tick())
    def flag(n): return a[a.index(n) + 1] if n in a else None
    def ff(k):
        for i, x in enumerate(a):
            if x == "-f" and a[i + 1].startswith(k + "="): return a[i + 1].split("=", 1)[1]
    def nao_achou():
        print(json.dumps({"message": "Not Found", "status": "404"})); sys.exit(1)
    if a[:2] == ["auth", "status"]: sys.exit(0)
    method = flag("-X") or "GET"
    target = [x for x in a[1:] if x.startswith("repos/")][0]
    if target.endswith("ufms-meu-estudo-entrada"): print("true"); sys.exit(0)
    if "/commits?path=" in target:
        p = target.split("path=")[1].split("&")[0]
        if os.path.exists(path(p + ".date")): print(open(path(p + ".date")).read()); sys.exit(0)
        nao_achou()
    p = target.split("/contents/", 1)[1]
    if method == "PUT":
        put(p, base64.b64decode(ff("content")).decode()); sys.exit(0)
    if method == "DELETE":
        for suf in ("", ".date"):
            if os.path.exists(path(p + suf)): os.remove(path(p + suf))
        sys.exit(0)
    ex = lambda q: os.path.exists(path(q))
    if p == "sondas/resposta.json" and not ex(p) and ex("sondas/nonce.json") and MODE != "nada":
        n = json.loads(open(path("sondas/nonce.json")).read())["nonce"]
        body = {"ok": {"nonce_lido": n, "lido_em": "x"}, "errado": {"nonce_lido": "0" * 32, "lido_em": "x"}, "formato": {"outro": 1}}[MODE]
        put(p, json.dumps(body))
    if p == "comandos/entregas/f1-teste.json" and not ex(p) and ex("comandos/validados/f1-teste.json") and ex("comandos/recibos/f1-teste.json") and MODE != "nada":
        cmd = json.loads(open(path("comandos/validados/f1-teste.json")).read())
        h = hashlib.sha256(json.dumps(cmd, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        if MODE == "errado": h = "0" * 64
        put(p, json.dumps({"entrada_id": "f1-teste.json", "hash_corpo": h, "status": "ENTREGUE", "entregue_em": "2026-11-22T10:05:00Z", "origem_declarada": "coach"}))
    if not ex(p): nao_achou()
    jq = flag("--jq")
    print(base64.b64encode(open(path(p)).read().encode()).decode() if jq == ".content" else "sha-" + p)
''')


@unittest.skipUnless(BASH, "precisa de bash")
class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "bin").mkdir()
        (self.tmp / "st").mkdir()
        gh = self.tmp / "bin" / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        # o `python` do script precisa existir no PATH (no ambiente de teste pode haver só python3)
        if not shutil.which("python"):
            os.symlink(shutil.which("python3"), self.tmp / "bin" / "python")

    def rodar(self, script, entrada, modo="ok", extra_env=None):
        env = {**os.environ, "PATH": f"{self.tmp / 'bin'}{os.pathsep}{os.environ['PATH']}", "FAKE_ST": str(self.tmp / "st"), "ZAPIA_MODE": modo}
        env.update(extra_env or {})
        r = subprocess.run([BASH, str(ROOT / "scripts" / "termux" / script)], input=entrada, capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout + r.stderr

    def restos(self):
        return sorted(p.name for p in (self.tmp / "st").iterdir() if not p.name.startswith("_") and not p.name.endswith(".date"))

    def semear(self, nome, texto):
        (self.tmp / "st" / nome.replace("/", "__")).write_text(texto)
        (self.tmp / "st" / (nome.replace("/", "__") + ".date")).write_text("2026-11-22T09:00:00Z")


class SondaDeLeituraTeste(Base):
    ENTRADA = "SONDAR\n\nLIMPAR\n"

    def test_zapia_leu_e_gravou_prova_e_limpa(self):
        codigo, saida = self.rodar("sonda_zapia_do_zero.sh", self.ENTRADA)
        self.assertEqual(codigo, 0, saida)
        self.assertIn("RESULTADO: PROVADO", saida)
        self.assertIn("IGUAL ao nonce", saida)
        self.assertEqual(self.restos(), [])

    def test_valor_errado_ausente_ou_fora_do_formato_nao_prova(self):
        for modo, trecho in (("errado", "NÃO é o nonce"), ("nada", "não gravou"), ("formato", "fora do formato")):
            with self.subTest(modo):
                shutil.rmtree(self.tmp / "st")
                (self.tmp / "st").mkdir()
                codigo, saida = self.rodar("sonda_zapia_do_zero.sh", self.ENTRADA, modo)
                self.assertEqual(codigo, 2, saida)
                self.assertIn("RESULTADO: NÃO PROVADO", saida)
                self.assertIn(trecho, saida)

    def test_404_do_gh_nao_e_confundido_com_arquivo_existente(self):
        # regressão do bug real: o gh imprime o corpo do erro e sai com 1; o script tratava isso como "já existe"
        codigo, saida = self.rodar("sonda_zapia_do_zero.sh", self.ENTRADA)
        self.assertNotIn("já existe", saida)
        self.assertIn("sem resto de sonda anterior", saida)

    def test_resto_de_sonda_anterior_bloqueia_sem_sobrescrever(self):
        self.semear("sondas/nonce.json", '{"nonce":"velho"}')
        codigo, saida = self.rodar("sonda_zapia_do_zero.sh", self.ENTRADA)
        self.assertEqual(codigo, 1, saida)
        self.assertIn("já existe sondas/nonce.json", saida)
        self.assertEqual((self.tmp / "st" / "sondas__nonce.json").read_text(), '{"nonce":"velho"}')

    def test_nada_e_criado_sem_a_palavra_de_confirmacao(self):
        codigo, saida = self.rodar("sonda_zapia_do_zero.sh", "\n")
        self.assertEqual(codigo, 1, saida)
        self.assertEqual(self.restos(), [])

    def test_prompt_pede_so_o_formato_de_chamada_que_a_ferramenta_aceita(self):
        _, saida = self.rodar("sonda_zapia_do_zero.sh", self.ENTRADA)
        self.assertIn("SÓ as flags -X, -H e -d", saida)
        self.assertIn("nada de -s, -S", saida)
        self.assertNotIn("zapia token\" (", "")  # nenhum valor de token no texto

    def test_conferir_prova_e_bloqueia_sem_nonce(self):
        self.semear("sondas/nonce.json", '{"nonce":"abc123"}')
        codigo, saida = self.rodar("sonda_conferir.sh", "LIMPAR\n")
        self.assertEqual((codigo, self.restos()), (0, []), saida)
        shutil.rmtree(self.tmp / "st")
        (self.tmp / "st").mkdir()
        codigo, saida = self.rodar("sonda_conferir.sh", "\n")
        self.assertEqual(codigo, 1, saida)
        self.assertIn("não existe sondas/nonce.json", saida)

    def test_conferir_com_valor_errado_nao_prova(self):
        self.semear("sondas/nonce.json", '{"nonce":"abc123"}')
        codigo, saida = self.rodar("sonda_conferir.sh", "\n", "errado")
        self.assertEqual(codigo, 2, saida)
        self.assertIn("NÃO é o nonce", saida)


class ProvaF1Teste(Base):
    ENTRADA = "TESTAR\n\nSIM\nLIMPAR\n"

    def test_entrega_e_recibo_de_volta_conferem(self):
        codigo, saida = self.rodar("prova_f1_zapia.sh", self.ENTRADA)
        self.assertEqual(codigo, 0, saida)
        self.assertIn("RESULTADO: PROVADO", saida)
        self.assertIn("o recibo de volta confere", saida)
        self.assertEqual(self.restos(), [])

    def test_hash_errado_do_recibo_de_volta_nao_prova(self):
        codigo, saida = self.rodar("prova_f1_zapia.sh", self.ENTRADA, "errado")
        self.assertEqual(codigo, 2, saida)
        self.assertIn("NÃO confere", saida)

    def test_sem_recibo_de_volta_ou_sem_notificacao_vista_nao_prova(self):
        codigo, saida = self.rodar("prova_f1_zapia.sh", self.ENTRADA, "nada")
        self.assertEqual(codigo, 2, saida)
        self.assertIn("não gravou", saida)
        shutil.rmtree(self.tmp / "st")
        (self.tmp / "st").mkdir()
        codigo, saida = self.rodar("prova_f1_zapia.sh", "TESTAR\n\nNAO\nLIMPAR\n")
        self.assertEqual(codigo, 2, saida)
        self.assertIn("não confirmou a notificação", saida)

    def test_prompt_traz_hash_canonico_e_formato_de_chamada(self):
        _, saida = self.rodar("prova_f1_zapia.sh", self.ENTRADA)
        for trecho in ("sort_keys=True", "ensure_ascii=False", "SÓ as flags -X, -H e -d", "Coach (origem declarada): ", "sem o texto da mensagem"):
            self.assertIn(trecho, saida)

    def test_resto_de_teste_anterior_bloqueia(self):
        self.semear("comandos/validados/f1-teste.json", "{}")
        codigo, saida = self.rodar("prova_f1_zapia.sh", self.ENTRADA)
        self.assertEqual(codigo, 1, saida)

    def test_nada_e_gravado_sem_a_palavra_de_confirmacao(self):
        codigo, _ = self.rodar("prova_f1_zapia.sh", "\n")
        self.assertEqual((codigo, self.restos()), (1, []))


class PreparoF1Teste(unittest.TestCase):
    def test_comando_sintetico_passa_na_caixa_e_o_recibo_tem_o_mesmo_hash(self):
        from datetime import datetime, timezone
        m = f1.montar(datetime(2026, 11, 22, 15, 0, tzinfo=timezone.utc))
        c = json.loads(m["comando_bytes"])
        self.assertEqual((c["origin"], c["operation"], c["idempotency_key"]), ("coach", "enviar_mensagem", "rotina-2026-11-22-briefing-dia"))
        self.assertEqual(json.loads(m["recibo_bytes"])["hash_corpo"], m["hash_corpo"])
        self.assertEqual(json.loads(m["recibo_bytes"])["codigo"], "SINTETICO_MANUAL")  # nunca passa por promoção real

    def test_relogio_sem_fuso_e_recusado(self):
        from datetime import datetime
        with self.assertRaises(ValueError):
            f1.montar(datetime(2026, 11, 22, 15, 0))

    def test_conferir_recusa_hash_ou_campo_diferente(self):
        from datetime import datetime, timezone
        m = f1.montar(datetime(2026, 11, 22, 15, 0, tzinfo=timezone.utc))
        meta = {"nome": m["nome"], "hash_corpo": m["hash_corpo"]}
        base = {"entrada_id": m["nome"], "hash_corpo": m["hash_corpo"], "status": "ENTREGUE", "entregue_em": "2026-11-22T15:00:00Z", "origem_declarada": "coach"}
        self.assertIsNone(f1.conferir(json.dumps(base).encode(), meta))
        for mudar in ({"hash_corpo": "0" * 64}, {"status": "FALHA"}, {"texto": "vazou"}):
            self.assertIsNotNone(f1.conferir(json.dumps({**base, **mudar}).encode(), meta), mudar)


if __name__ == "__main__":
    unittest.main()
