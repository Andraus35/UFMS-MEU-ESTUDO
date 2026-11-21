"""AE: avaliação offline do verificador de entrega (S14-R12a). A suíte também precisa FALHAR quando o verificador é frouxo."""
import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import delivery_eval as e  # noqa: E402
import delivery_gate as g  # noqa: E402


class SuiteConforme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rel = e.executar()

    def test_todos_os_casos_conformes_e_nenhum_codigo_sem_exercicio(self):
        self.assertTrue(self.rel["conforme"], self.rel["divergentes"])
        self.assertEqual(self.rel["conformes"], self.rel["casos"])
        self.assertGreaterEqual(self.rel["casos"], 70)
        self.assertEqual(self.rel["codigos_nao_exercidos"], [])

    def test_ids_unicos_e_ha_validos_e_adversariais(self):
        casos = e.corpus()
        ids = [c["id"] for c in casos]
        self.assertEqual(len(ids), len(set(ids)))
        decisoes = {c["decisao"] for c in casos}
        self.assertEqual(decisoes, {"ACEITA", "AVISO", "RECUSADA"})
        self.assertGreaterEqual(sum(c["decisao"] == "ACEITA" for c in casos), 8)

    def test_cada_regra_do_escopo_tem_casos(self):
        for regra, minimo in (("R2", 2), ("R3", 3), ("R5", 10), ("R6", 12), ("R7", 5), ("R8", 8), ("R9", 4), ("R11", 4), ("R17", 3)):
            self.assertGreaterEqual(self.rel["por_regra"].get(regra, {}).get("casos", 0), minimo, regra)

    def test_cada_codigo_de_recusa_do_portao_aparece_como_esperado_de_algum_caso(self):
        esperados = {m for c in e.corpus() for m in (*c["motivos"], *c["avisos"])}
        self.assertEqual(e.codigos_do_portao() - esperados, set())

    def test_sombra_bloqueio_e_efeito_externo_estao_no_corpus(self):
        por_id = {c["id"]: c for c in e.corpus()}
        self.assertEqual((por_id["M01"]["modo"], por_id["M01"]["decisao"]), ("sombra", "AVISO"))
        self.assertEqual((por_id["M02"]["modo"], por_id["M02"]["decisao"]), ("bloqueio", "RECUSADA"))
        for cid in ("M03", "M04", "M05", "M06", "M07", "M09"):
            self.assertEqual((por_id[cid]["modo"], por_id[cid]["decisao"]), ("sombra", "RECUSADA"), cid)

    def test_registro_s14_r13(self):
        nomes = {v["verificacao"] for v in self.rel["registro"]}
        self.assertGreaterEqual(len(nomes), 5)
        self.assertTrue(all(v["conforme"] for v in self.rel["registro"]))

    def test_relatorio_declara_o_que_nao_cobre_e_que_nao_homologa(self):
        self.assertIs(self.rel["chama_modelo"], False)
        self.assertIs(self.rel["homologa"], False)
        texto = " ".join(self.rel["nao_cobre"])
        for trecho in ("NÃO GATEÁVEL", "RM-06 e RM-07", "taxa de falso positivo", "origem do comando"):
            self.assertIn(trecho, texto)

    def test_sem_lacunas_conhecidas_e_a_contagem_antes_da_palavra_e_recusada(self):
        self.assertEqual(self.rel["lacunas_conhecidas"], [])
        por_id = {c["id"]: c for c in e.corpus()}
        self.assertEqual((por_id["A06"]["decisao"], por_id["A06c"]["decisao"]), ("RECUSADA", "ACEITA"))


class SuiteDetectaVerificadorFrouxo(unittest.TestCase):
    """Contraprovas da avaliação: se o verificador afrouxar, a suíte reprova."""

    def reprova(self, **patches):
        with mock.patch.multiple(g, **patches):
            rel = e.executar()
        self.assertFalse(rel["conforme"])
        return rel

    def test_verificador_que_aceita_tudo_reprova(self):
        saida = {"decisao": "ACEITA", "modo_efetivo": "bloqueio", "tipo": "ORIENTACAO", "classe_de_risco": "ORIENTACAO", "motivos": [], "avisos": [],
                 "gerado_em": "2026-11-20T12:00:00Z"}
        rel = self.reprova(verificar_entrega=lambda *a, **k: dict(saida))
        self.assertGreater(len(rel["divergentes"]), 40)

    def test_sem_conferencia_de_alegacoes_reprova(self):
        rel = self.reprova(_alegacoes=lambda *a, **k: {"paginas": set(), "citou": True, "niveis": set(), "ids": set()})
        self.assertTrue({"A01", "A03", "A08"} <= {d["id"] for d in rel["divergentes"]})

    def test_sem_filtro_de_privacidade_reprova(self):
        with mock.patch.object(g.agent_commands, "scan_text", lambda *a, **k: []):
            rel = e.executar()
        self.assertFalse(rel["conforme"])
        self.assertTrue({"P01", "P02", "P03"} <= {d["id"] for d in rel["divergentes"]})

    def test_sem_conferencia_do_sha_reprova(self):
        orig = g._verificar

        def sem_sha(env, contexto):
            return orig(env, {**contexto, "sha_contrato": env.get("sha_contrato") if isinstance(env, dict) else None})
        rel = self.reprova(_verificar=sem_sha)
        self.assertIn("S01", {d["id"] for d in rel["divergentes"]})

    def test_sem_bloqueio_do_efeito_externo_reprova(self):
        with mock.patch.object(g, "TIPOS_COM_EFEITO", ()):
            rel = e.executar()
        self.assertFalse(rel["conforme"])
        self.assertTrue({"M03", "M04", "M05"} <= {d["id"] for d in rel["divergentes"]})

    def test_caso_com_esperado_errado_e_apontado(self):
        caso = copy.deepcopy(next(c for c in e.corpus() if c["id"] == "P01"))
        caso["decisao"] = "ACEITA"
        res = e.avaliar_caso(caso)
        self.assertFalse(res["conforme"])
        self.assertIn("decisao", res["divergencias"])

    def test_codigo_novo_sem_caso_aparece_como_nao_exercido(self):
        fonte = (ROOT / "scripts" / "delivery_gate.py").read_text(encoding="utf-8") + '\nx.append("codigo_novo_sem_caso")\n'
        with tempfile.TemporaryDirectory() as pasta:
            tmp = Path(pasta) / "gate.py"
            tmp.write_text(fonte, encoding="utf-8")
            achados = e.codigos_do_portao(tmp)
        self.assertIn("codigo_novo_sem_caso", achados - {m for c in e.corpus() for m in (*c["motivos"], *c["avisos"])})


class LinhaDeComandoESemModelo(unittest.TestCase):
    def test_cli_sai_0_e_o_relatorio_nao_repete_conteudo(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "delivery_eval.py")], capture_output=True, text=True, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rel = json.loads(proc.stdout)
        self.assertTrue(rel["conforme"])
        for proibido in (e.TOKEN_FALSO, e.CPF_FALSO, "pessoa@exemplo.org", "https://", "conteudo-que-nao-pode"):
            self.assertNotIn(proibido, proc.stdout)

    def test_nenhum_portao_nem_o_avaliador_chama_modelo_ou_rede(self):
        proibidos = {"anthropic", "openai", "requests", "socket", "urllib", "http", "ssl", "httpx", "aiohttp"}
        for nome in ("delivery_eval.py", "delivery_gate.py", "start_receipt.py"):
            arvore = ast.parse((ROOT / "scripts" / nome).read_text(encoding="utf-8"))
            importados = {n.names[0].name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import)}
            importados |= {n.module.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
            self.assertFalse(importados & proibidos, (nome, importados & proibidos))

    def test_avaliador_nao_escreve_arquivo(self):
        arvore = ast.parse((ROOT / "scripts" / "delivery_eval.py").read_text(encoding="utf-8"))
        chamadas = {n.func.attr for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse(chamadas & {"write_text", "write_bytes", "mkdir", "unlink", "rename"}, chamadas)


if __name__ == "__main__":
    unittest.main()
