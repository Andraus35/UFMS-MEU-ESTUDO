"""AM: auditoria por amostra e critério de pausa (S14-R14). Dados sintéticos; uma contraprova por regra."""
import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_sample as a  # noqa: E402


def entrega(eid="E1", tipo="ORIENTACAO", grave=None, leve=None):
    crit = {k: "ok" for k in a.CRITERIOS}
    if leve:
        crit[leve] = "falha"
    e = {"entrega_id": eid, "tipo": tipo, "criterios": crit, "citacao_inventada": False, "efeito_sem_gate": False}
    if grave == "dado_pessoal":
        crit["sem_dado_pessoal"] = "falha"
    elif grave == "citacao_inventada":
        e["citacao_inventada"] = True
    elif grave == "efeito_sem_gate":
        e["efeito_sem_gate"] = True
    return e


def amostra(aid, data, *entregas):
    return {"amostra_id": aid, "data": data, "entregas": list(entregas) or [entrega()]}


LIMPA = lambda aid, d: amostra(aid, d)  # noqa: E731
GRAVE = lambda aid, d, g="dado_pessoal": amostra(aid, d, entrega("E1"), entrega("E2", grave=g))  # noqa: E731


class CriterioDePausa(unittest.TestCase):
    def pausa(self, *amostras):
        return a.relatorio(list(amostras))["pausa"]

    def test_duas_amostras_seguidas_com_falha_grave_pausam(self):
        for g in ("dado_pessoal", "citacao_inventada", "efeito_sem_gate"):
            self.assertTrue(self.pausa(GRAVE("A1", "2026-12-01", g), GRAVE("A2", "2026-12-15", g)), g)

    def test_graves_de_tipos_diferentes_tambem_pausam(self):
        self.assertTrue(self.pausa(GRAVE("A1", "2026-12-01", "dado_pessoal"), GRAVE("A2", "2026-12-15", "efeito_sem_gate")))

    def test_uma_amostra_grave_nao_pausa(self):
        self.assertFalse(self.pausa(GRAVE("A1", "2026-12-01")))
        self.assertFalse(self.pausa(LIMPA("A0", "2026-11-20"), GRAVE("A1", "2026-12-01")))

    def test_graves_nao_consecutivas_nao_pausam(self):
        self.assertFalse(self.pausa(GRAVE("A1", "2026-12-01"), LIMPA("A2", "2026-12-08"), GRAVE("A3", "2026-12-15")))

    def test_amostra_limpa_depois_zera_a_sequencia(self):
        self.assertFalse(self.pausa(GRAVE("A1", "2026-12-01"), GRAVE("A2", "2026-12-08"), LIMPA("A3", "2026-12-15")))

    def test_falha_leve_nao_conta_como_grave(self):
        leve = lambda aid, d: amostra(aid, d, entrega(leve="coerente_com_projecao"), entrega("E2", leve="fato_com_fonte"))  # noqa: E731
        self.assertFalse(self.pausa(leve("A1", "2026-12-01"), leve("A2", "2026-12-15")))

    def test_veredito_na_nao_e_falha(self):
        e = entrega()
        e["criterios"]["fato_com_fonte"] = "na"
        rel = a.relatorio([amostra("A1", "2026-12-01", e)])
        self.assertEqual(rel["amostras"][0]["entregas_com_falha"], 0)

    def test_ordem_e_cronologica_nao_a_da_lista(self):
        # A3 (limpa) é a mais recente: mesmo listada antes, quebra a sequência
        self.assertFalse(self.pausa(LIMPA("A3", "2026-12-20"), GRAVE("A1", "2026-12-01"), GRAVE("A2", "2026-12-08")))
        self.assertTrue(self.pausa(GRAVE("A2", "2026-12-08"), GRAVE("A1", "2026-12-01"), LIMPA("A0", "2026-11-01")))

    def test_funcao_pura_das_entradas(self):
        r1 = a.criterio_de_pausa([{"tem_falha_grave": True}, {"tem_falha_grave": True}])
        r2 = a.criterio_de_pausa([{"tem_falha_grave": True}, {"tem_falha_grave": False}])
        self.assertEqual((r1, r2, a.criterio_de_pausa([]), a.criterio_de_pausa([{"tem_falha_grave": True}])), (True, False, False, False))

    def test_pausa_so_indica_e_explica_que_o_ato_e_do_proprietario(self):
        rel = a.relatorio([GRAVE("A1", "2026-12-01"), GRAVE("A2", "2026-12-15")])
        self.assertIn("desfixar o SHA de produção", rel["efeito_da_pausa"])
        self.assertIn("ato dele, não deste módulo", rel["efeito_da_pausa"])
        self.assertIsNone(a.relatorio([LIMPA("A1", "2026-12-01")])["efeito_da_pausa"])


class Periodicidade(unittest.TestCase):
    def test_padrao_proposto_dez_entregas_ou_quinze_dias(self):
        self.assertEqual((a.ENTREGAS_PADRAO, a.DIAS_PADRAO), (10, 15))
        self.assertFalse(a.amostra_devida(9, 14)["devida"])
        self.assertTrue(a.amostra_devida(10, 0)["por_entregas"])
        self.assertTrue(a.amostra_devida(0, 15)["por_dias"])
        self.assertTrue(a.amostra_devida(3, 15)["devida"])

    def test_limites_ajustaveis_pelo_proprietario(self):
        cfg = a.configuracao(5, 7)
        self.assertTrue(a.amostra_devida(5, 0, cfg)["devida"])
        self.assertTrue(a.amostra_devida(0, 7, cfg)["devida"])
        self.assertFalse(a.amostra_devida(4, 6, cfg)["devida"])
        self.assertTrue(a.relatorio([LIMPA("A1", "2026-12-01")], cfg)["periodicidade"]["ajustavel_pelo_proprietario"])

    def test_configuracao_invalida_recusa(self):
        for bruto in ((0, 15), (10, 0), (-1, 15), (10, True), (10.5, 15), ("10", 15)):
            with self.assertRaises(a.AmostraInvalida, msg=repr(bruto)):
                a.configuracao(*bruto)

    def test_contagem_invalida_recusa(self):
        for bruto in ((-1, 0), (0, -1), (True, 0), (1.5, 0), ("1", 0)):
            with self.assertRaises(a.AmostraInvalida, msg=repr(bruto)):
                a.amostra_devida(*bruto)

    def test_relatorio_traz_a_proxima_amostra_quando_ha_contagem(self):
        rel = a.relatorio([LIMPA("A1", "2026-12-01")], None, 12, 3)
        self.assertTrue(rel["proxima_amostra"]["devida"])
        self.assertIsNone(a.relatorio([LIMPA("A1", "2026-12-01")])["proxima_amostra"])


class ValidacaoFechada(unittest.TestCase):
    def recusa(self, amostras, codigo):
        with self.assertRaises(a.AmostraInvalida) as c:
            a.relatorio(amostras)
        self.assertEqual(str(c.exception), codigo)

    def test_sem_amostras(self):
        for v in ([], None, "x", {}):
            self.recusa(v, "sem_amostras")

    def test_amostra_com_campo_extra_ou_faltando(self):
        ok = LIMPA("A1", "2026-12-01")
        self.recusa([{**ok, "obs": "texto livre"}], "amostra_fora_da_lista_fechada")
        self.recusa([{k: v for k, v in ok.items() if k != "data"}], "amostra_fora_da_lista_fechada")
        self.recusa(["x"], "amostra_fora_da_lista_fechada")

    def test_entrega_com_campo_extra_ou_texto_livre(self):
        e = entrega()
        e["conteudo"] = "texto da entrega"
        self.recusa([amostra("A1", "2026-12-01", e)], "entrega_fora_da_lista_fechada")

    def test_ids_com_conteudo_ou_padrao_de_segredo(self):
        for ruim in ("com espaço", "x" * 41, "", "a@b.com", "ghp_" + "A" * 20, "https://x", "529.982.247-25"):
            self.recusa([amostra(ruim, "2026-12-01")], "amostra_id_invalido")
            e = entrega(eid=ruim)
            self.recusa([amostra("A1", "2026-12-01", e)], "entrega_id_invalido")

    def test_data_invalida(self):
        for d in ("2026-13-01", "2026-02-30", "01/12/2026", "2026-12-1", 20261201, None):
            self.recusa([amostra("A1", d)], "data_invalida")

    def test_tipo_e_criterios_fora_da_rubrica(self):
        self.recusa([amostra("A1", "2026-12-01", entrega(tipo="TWEET"))], "tipo_invalido")
        e = entrega()
        e["criterios"]["novo_criterio"] = "ok"
        self.recusa([amostra("A1", "2026-12-01", e)], "criterios_fora_da_rubrica")
        e = entrega()
        e["criterios"].pop("sem_dado_pessoal")
        self.recusa([amostra("A1", "2026-12-01", e)], "criterios_fora_da_rubrica")
        e = entrega()
        e["criterios"]["fato_com_fonte"] = "talvez"
        self.recusa([amostra("A1", "2026-12-01", e)], "criterios_fora_da_rubrica")

    def test_marcas_graves_precisam_ser_booleanas(self):
        for campo in ("citacao_inventada", "efeito_sem_gate"):
            e = entrega()
            e[campo] = "sim"
            self.recusa([amostra("A1", "2026-12-01", e)], "marca_grave_invalida")
            e[campo] = 0
            self.recusa([amostra("A1", "2026-12-01", e)], "marca_grave_invalida")

    def test_amostra_vazia_ou_ids_repetidos(self):
        self.recusa([{"amostra_id": "A1", "data": "2026-12-01", "entregas": []}], "amostra_sem_entregas_ou_grande_demais")
        self.recusa([amostra("A1", "2026-12-01", entrega("E1"), entrega("E1"))], "entrega_id_repetido")
        self.recusa([LIMPA("A1", "2026-12-01"), LIMPA("A1", "2026-12-02")], "amostra_id_repetido")

    def test_entrada_malformada_nunca_vaza_o_conteudo_na_mensagem(self):
        segredo = "ghp_" + "S" * 24
        with self.assertRaises(a.AmostraInvalida) as c:
            a.relatorio([amostra(segredo, "2026-12-01")])
        self.assertNotIn(segredo, str(c.exception))


class RelatorioSemConteudo(unittest.TestCase):
    def test_relatorio_so_tem_ids_datas_e_contagens(self):
        rel = a.relatorio([GRAVE("A1", "2026-12-01"), LIMPA("A2", "2026-12-15")])
        r1 = rel["amostras"][0]
        self.assertEqual((r1["entregas"], r1["entregas_com_falha"], r1["graves"]["dado_pessoal"], r1["tem_falha_grave"]), (2, 1, 1, True))
        self.assertEqual(r1["falhas_por_criterio"]["sem_dado_pessoal"], 1)
        self.assertEqual(set(rel), {"amostras", "pausa", "efeito_da_pausa", "periodicidade", "proxima_amostra", "limites", "chama_modelo"})
        self.assertNotIn("E2", json.dumps(rel), "ids de entrega não vão ao relatório")

    def test_declara_limites_e_que_nao_e_cronograma_de_estudo(self):
        rel = a.relatorio([LIMPA("A1", "2026-12-01")])
        for trecho in ("não garante que seja representativa", "atos do proprietário", "NÃO GATEÁVEL", "não é cronograma de estudo"):
            self.assertIn(trecho, rel["limites"])
        self.assertIs(rel["chama_modelo"], False)

    def test_regra_do_proprietario_no_texto_do_modulo(self):
        doc = a.__doc__
        for trecho in ("10 entregas", "15 dias", "AJUSTÁVEL", "SEGUIDAS", "DESFIXA o SHA", "juiz-LLM não participa"):
            self.assertIn(trecho, doc)


class LinhaDeComando(unittest.TestCase):
    def roda(self, dados, *args):
        with tempfile.TemporaryDirectory() as pasta:
            f = Path(pasta) / "amostras.json"
            f.write_text(dados if isinstance(dados, str) else json.dumps(dados), encoding="utf-8")
            return subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_sample.py"), "--amostras", str(f), *args], capture_output=True, text=True, timeout=60)

    def test_sai_0_sem_pausa_e_1_com_pausa(self):
        self.assertEqual(self.roda([LIMPA("A1", "2026-12-01")]).returncode, 0)
        r = self.roda([GRAVE("A1", "2026-12-01"), GRAVE("A2", "2026-12-15")])
        self.assertEqual(r.returncode, 1)
        self.assertTrue(json.loads(r.stdout)["pausa"])

    def test_entrada_invalida_sai_3_sem_repetir_o_conteudo(self):
        segredo = "ghp_" + "S" * 24
        r = self.roda([amostra(segredo, "2026-12-01")])
        self.assertEqual(r.returncode, 3)
        self.assertNotIn(segredo, r.stdout + r.stderr)
        self.assertEqual(self.roda("não é json").returncode, 3)

    def test_limites_ajustaveis_pela_linha_de_comando(self):
        r = self.roda([LIMPA("A1", "2026-12-01")], "--limite-entregas", "3", "--limite-dias", "5", "--entregas-desde-a-ultima", "3")
        rel = json.loads(r.stdout)
        self.assertEqual((rel["periodicidade"]["limite_entregas"], rel["proxima_amostra"]["devida"]), (3, True))
        self.assertEqual(self.roda([LIMPA("A1", "2026-12-01")], "--limite-entregas", "0").returncode, 3)


class SemModeloRedeNemEscrita(unittest.TestCase):
    def test_modulo(self):
        arvore = ast.parse((ROOT / "scripts" / "audit_sample.py").read_text(encoding="utf-8"))
        importados = {n.names[0].name.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.Import)}
        importados |= {n.module.split(".")[0] for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(importados & {"anthropic", "openai", "requests", "socket", "urllib", "http", "ssl", "httpx"}, importados)
        chamadas = {n.func.attr for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertFalse(chamadas & {"write_text", "write_bytes", "unlink", "mkdir", "rename", "replace"}, chamadas)


if __name__ == "__main__":
    unittest.main()
