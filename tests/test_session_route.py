import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import session_route as sr  # noqa: E402
import doc_cohesion  # noqa: E402


class SessionRouteTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "repo"
        self.addCleanup(shutil.rmtree, self.root.parent, True)
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

    def routes(self, mutate):
        p = self.root / "config/session_routes.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        mutate(d["rotas"])
        p.write_text(json.dumps(d), encoding="utf-8")

    def test_todas_as_rotas_do_repositorio_real_constroem(self):
        for intent in sr.INTENTS:
            r = sr.build(ROOT, intent)
            self.assertEqual(len(r["route_sha256"]), 64)
            for st in r["etapas"]:
                if st["tipo"] in ("ler", "consultar_se"):
                    self.assertEqual(len(st["sha256"]), 64)

    def test_situacoes_esperadas(self):
        self.assertEqual(sr.build(self.root, "engineering")["situacao"], "pronta")
        self.assertEqual(sr.build(self.root, "write")["situacao"], "pronta")
        self.assertEqual(sr.build(self.root, "persistence")["situacao"], "bloqueada")
        self.assertEqual(sr.build(self.root, "governance")["situacao"], "requer_aprovacao_humana")

    def test_estudo_nao_e_bloqueado_pelo_aviso_de_gravacao(self):
        r = sr.build(self.root, "study")
        self.assertEqual(r["situacao"], "pronta")
        aviso = [s for s in r["etapas"] if s["tipo"] == "aviso_se"][0]
        self.assertTrue(aviso["acionada"])

    def test_persistencia_libera_so_com_flag_ligada(self):
        p = self.root / "settings.json"
        s = json.loads(p.read_text(encoding="utf-8"))
        s["storage"]["personal_results_writes_enabled"] = True
        p.write_text(json.dumps(s), encoding="utf-8")
        self.assertEqual(sr.build(self.root, "persistence")["situacao"], "pronta")

    def test_flag_ausente_continua_bloqueando(self):
        p = self.root / "settings.json"
        s = json.loads(p.read_text(encoding="utf-8"))
        s["storage"].pop("personal_results_writes_enabled")
        p.write_text(json.dumps(s), encoding="utf-8")
        self.assertEqual(sr.build(self.root, "persistence")["situacao"], "bloqueada")

    def test_hash_da_rota_muda_quando_um_documento_muda(self):
        antes = sr.build(self.root, "engineering")["route_sha256"]
        p = self.root / "PRODUCT.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nx\n", encoding="utf-8")
        self.assertNotEqual(antes, sr.build(self.root, "engineering")["route_sha256"])

    def test_expect_detecta_documento_alterado(self):
        antes = sr.build(self.root, "engineering")["route_sha256"]
        self.assertEqual(sr.main(["--root", str(self.root), "--intent", "engineering", "--expect", antes]), 0)
        p = self.root / "PRODUCT.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nx\n", encoding="utf-8")
        self.assertEqual(sr.main(["--root", str(self.root), "--intent", "engineering", "--expect", antes]), 1)

    def test_comando_fora_da_lista_e_recusado(self):
        for cmd in ("rm -rf /", "python -c print(1)", "python scripts/doc_cohesion.py; ls", "bash scripts/x.sh"):
            self.routes(lambda r, c=cmd: r["engineering"]["etapas"].append({"id": "XX", "tipo": "executar", "comando": c}))
            with self.assertRaises(ValueError):
                sr.build(self.root, "engineering")

    def test_arquivo_inexistente_na_rota_falha(self):
        self.routes(lambda r: r["engineering"]["etapas"].append({"id": "XX", "tipo": "ler", "arquivo": "nao_existe.md", "porque": "x"}))
        with self.assertRaises(OSError):
            sr.build(self.root, "engineering")

    def test_run_executa_na_ordem_e_para_na_falha(self):
        self.routes(lambda r: r["engineering"]["etapas"].insert(6, {"id": "XF", "tipo": "executar", "comando": "python scripts/nao_existe.py"}))
        route = sr.build(self.root, "engineering")
        res = sr.run_checks(self.root, route)
        self.assertEqual([v["id"] for v in res], ["XF"])
        self.assertFalse(res[0]["ok"])

    def test_run_nao_executa_depois_de_parada_acionada(self):
        res = sr.run_checks(self.root, sr.build(self.root, "persistence"))
        self.assertEqual(res, [])

    def test_run_do_repositorio_real_passa(self):
        res = sr.run_checks(ROOT, sr.build(ROOT, "engineering"))
        self.assertTrue(res and all(v["ok"] for v in res), res)

    def test_c9_valida_o_repositorio_e_pega_divergencias(self):
        self.assertEqual(doc_cohesion.check_routes(ROOT), [])
        # rota de estudo diverge de settings.json
        self.routes(lambda r: r["study"]["etapas"].pop(0))
        self.assertTrue(any("study" in e for e in doc_cohesion.check_routes(self.root)))

    def test_c9_write_precisa_dos_comandos_do_agents_md(self):
        self.routes(lambda r: r["write"].update(etapas=[s for s in r["write"]["etapas"] if s.get("comando") != "python hooks/before_write.py"]))
        self.assertTrue(any("before_write" in e for e in doc_cohesion.check_routes(self.root)))

    def test_c9_write_exige_ordem_antes_e_depois(self):
        def troca(r):
            st = r["write"]["etapas"]
            i = next(k for k, s in enumerate(st) if s["tipo"] == "manual")
            st.insert(0, st.pop(i))
        self.routes(troca)
        self.assertTrue(any("antes/depois" in e for e in doc_cohesion.check_routes(self.root)))

    def test_c9_governanca_e_persistencia_precisam_de_parada(self):
        self.routes(lambda r: r["governance"].update(etapas=[s for s in r["governance"]["etapas"] if s["tipo"] != "parar_se"]))
        self.assertTrue(any("governance" in e for e in doc_cohesion.check_routes(self.root)))
        self.routes(lambda r: r["persistence"].update(etapas=[s for s in r["persistence"]["etapas"] if s["tipo"] != "parar_se"]))
        self.assertTrue(any("persistence" in e for e in doc_cohesion.check_routes(self.root)))

    def test_c9_rota_ausente(self):
        self.routes(lambda r: r.pop("persistence"))
        self.assertTrue(any("ausente" in e for e in doc_cohesion.check_routes(self.root)))


if __name__ == "__main__":
    unittest.main()
