"""Contraprovas do T2 (S16): top 10 por matéria. Árvore e números FICTÍCIOS, em memória; nenhum ranking real."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import top10_materia as t  # noqa: E402


def no(nome, pct, materia="Materia X", modalidade=1, cargos=("324", "523"), estado="definitiva", caderno_pct=None):
    return {"cargos": list(cargos), "guia": "Guia sintetico", "bloco": "desconhecido", "caderno": "Caderno sintetico",
            "materia": materia, "caminho": [materia, nome], "modalidade": modalidade,
            "origem": {"fonte": "amostra sintetica", "data": "2026-11-21", "filtros": "banca sintetica"},
            "estado_amostra": estado, "folha": True,
            "percentual_materia": None if pct is None else {"valor": pct, "denominador": 1000},
            "percentual_caderno": caderno_pct}


def nos(valores, **kw):
    return [no(f"A{i:02d}", v, **kw) for i, v in enumerate(valores)]


def sel(brutos, **kw):
    kw.setdefault("materia", "Materia X")
    kw.setdefault("cargo", "523")
    return t.selecionar_top10(brutos, **kw)


def nomes(r):
    return [i["caminho"][-1] for i in r["itens"]]


class Top10Tests(unittest.TestCase):
    def test_top10_do_maior_para_o_menor_com_posicao(self):
        r = sel(nos([1, 9, 3, 8, 5, 7, 2, 6, 4, 10, 0.5, 0.4]))
        self.assertEqual(r["status"], "LISTA")
        self.assertEqual([i["percentual_materia"]["valor"] for i in r["itens"]], [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertEqual([i["posicao"] for i in r["itens"]], list(range(1, 11)))
        self.assertFalse(r["parcial"])

    def test_registro_completo_por_item_r5(self):
        r = sel(nos([5.0] * 1, ), cargo="324")
        i = r["itens"][0]
        for campo in ("cargos", "guia", "bloco", "caderno", "materia", "caminho", "posicao", "modalidade", "percentual_materia",
                      "percentual_caderno", "fonte", "data", "filtros", "guia_tec"):
            self.assertIn(campo, i, campo)
        self.assertEqual(i["cargo_pedido"], "324")
        self.assertEqual(i["percentual_materia"]["denominador"], 1000)

    def test_empate_no_decimo_inclui_todos_ate_o_teto(self):
        r = sel(nos([9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5, 4, 4, 4, 1]))
        self.assertEqual(r["status"], "LISTA")
        self.assertEqual(len(r["itens"]), 12)  # 9 + 3 empatados no 10º
        self.assertEqual([i["posicao"] for i in r["itens"]][-3:], [10, 10, 10])  # mesma posição, sem desempate inventado
        self.assertNotIn(1, [i["percentual_materia"]["valor"] for i in r["itens"]])

    def test_empate_entre_9o_e_10o_nao_estoura_a_lista(self):
        r = sel(nos([12, 11, 10, 9, 8, 7, 6, 5, 4, 4, 3]))
        self.assertEqual(len(r["itens"]), 10)
        self.assertEqual([i["posicao"] for i in r["itens"]][-2:], [9, 9])

    def test_exatamente_no_teto_de_15_e_aceito(self):
        r = sel(nos([9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5] + [4] * 6 + [1]))
        self.assertEqual(r["status"], "LISTA")
        self.assertEqual(len(r["itens"]), 15)

    def test_acima_do_teto_vai_ao_proprietario_sem_lista(self):
        r = sel(nos([9, 8.5, 8, 7.5, 7, 6.5, 6, 5.5, 5] + [4] * 7 + [1]))
        self.assertEqual(r["status"], "DECISAO_DO_PROPRIETARIO")
        self.assertEqual(r["codigo"], "EMPATE_ACIMA_DO_TETO")
        self.assertEqual(r["itens"], [])
        self.assertEqual(len(r["empatados"]), 7)
        self.assertEqual(r["valor_do_empate"], 4)

    def test_menos_de_10_folhas_lista_as_encontradas_e_declara_parcial(self):
        r = sel(nos([3, 2, 1]))
        self.assertEqual((r["status"], len(r["itens"]), r["parcial"]), ("LISTA", 3, True))

    def test_percentual_ausente_deixa_o_item_de_fora_sem_estimar(self):
        r = sel(nos([3, None, 1]))
        self.assertEqual(len(r["itens"]), 2)
        self.assertEqual(r["sem_percentual"], ["Materia X > A01"])
        self.assertTrue(r["parcial"])
        self.assertNotIn("A01", nomes(r))

    def test_nenhum_percentual_e_recusado(self):
        r = sel(nos([None, None]))
        self.assertEqual((r["status"], r["codigo"], r["itens"]), ("RECUSADA", "PERCENTUAL_AUSENTE", []))
        # só o percentual do caderno não basta: o ranking é pela matéria, sem estimativa
        so_caderno = [no("A", None, caderno_pct={"valor": 5, "denominador": 100})]
        self.assertEqual(sel(so_caderno)["codigo"], "PERCENTUAL_AUSENTE")

    def test_amostra_nao_definitiva_ou_instavel_gera_pendencia_aberta(self):
        for estado in ("nao_definitiva", "instavel"):
            r = sel(nos([5, 4, 3], estado=estado))
            self.assertEqual((r["status"], r["codigo"], r["itens"]), ("PENDENCIA_ABERTA", "AMOSTRA_NAO_DEFINITIVA", []), estado)
        mista = nos([5, 4]) + [no("Z", 3, estado="nao_definitiva")]
        self.assertEqual(sel(mista)["status"], "PENDENCIA_ABERTA")  # um nó não definitivo basta para fechar a matéria

    def test_amostra_ausente_gera_pendencia_aberta(self):
        self.assertEqual(sel(nos([5]), materia="Outra")["codigo"], "AMOSTRA_AUSENTE")
        self.assertEqual(sel(nos([5], cargos=("324",)), cargo="523")["codigo"], "AMOSTRA_AUSENTE")

    def test_so_a_modalidade_1_ranqueia(self):
        so_m2 = nos([5, 4, 3], modalidade=2)
        self.assertEqual(sel(so_m2)["codigo"], "AMOSTRA_AUSENTE")  # guias do TEC não geram top 10
        misto = nos([5, 4]) + [no("Gigante", 99, modalidade=2)]
        r = sel(misto)
        self.assertNotIn("Gigante", nomes(r))
        self.assertTrue(all(i["modalidade"] == 1 for i in r["itens"]))

    def test_pai_nao_compete_com_filho(self):
        pai = no("Pai", 50)
        pai["folha"] = False
        filho = no("Pai", 30)
        filho["caminho"] = ["Materia X", "Pai", "Filho"]
        r = sel([pai, filho])
        self.assertEqual([i["caminho"][-1] for i in r["itens"]], ["Filho"])
        pai_folha = no("Pai", 50)
        r2 = sel([pai_folha, filho])
        self.assertEqual((r2["status"], r2["codigo"]), ("RECUSADA", "PAI_MARCADO_FOLHA"))

    def test_materias_nao_se_misturam(self):
        r = sel(nos([5, 4]) + nos([90], materia="Materia Y"))
        self.assertEqual(len(r["itens"]), 2)

    # P8: correspondência só por mapa explícito, nunca por nome
    def test_correspondencia_nao_e_forcada_por_nome(self):
        base = nos([5, 4])
        guia = no("A00", 7, modalidade=2)  # mesmo nome, outro nó: não casa sozinho
        r = sel(base + [guia])
        self.assertTrue(all(i["guia_tec"] == "nao_avaliada" for i in r["itens"]))
        r = sel(base + [guia], correspondencias={})
        self.assertTrue(all(i["guia_tec"] == "sem correspondência" for i in r["itens"]))
        r = sel(base + [guia], correspondencias={("Materia X", "A00"): ("Materia X", "A00")})
        por = {i["caminho"][-1]: i["guia_tec"] for i in r["itens"]}
        self.assertEqual(por["A00"], "Materia X > A00")
        self.assertEqual(por["A01"], "sem correspondência")

    def test_mapa_para_no_inexistente_da_modalidade_2_vira_sem_correspondencia(self):
        r = sel(nos([5]), correspondencias={("Materia X", "A00"): ("Materia X", "Inventado")})
        self.assertEqual(r["itens"][0]["guia_tec"], "sem correspondência")

    def test_mapa_malformado_e_recusado(self):
        for m in ([], {"a": ("b",)}, {("a",): "b"}, {("a",): (1,)}):
            self.assertEqual(sel(nos([5]), correspondencias=m)["codigo"], "CORRESPONDENCIAS_INVALIDAS", m)

    # entrada ruim fecha por padrão
    def test_entrada_invalida_e_recusada_sem_excecao(self):
        self.assertEqual(sel(nos([5]), cargo="999")["codigo"], "CARGO_INVALIDO")
        self.assertEqual(sel(nos([5]), materia="")["codigo"], "MATERIA_INVALIDA")
        self.assertEqual(sel([])["codigo"], "CONJUNTO_INVALIDO")
        ruim = nos([5])
        ruim[0]["probabilidade"] = 90
        self.assertEqual(sel(ruim)["codigo"], "CHAVE_FORA_DO_CONTRATO")
        soma = nos([60, 60])
        self.assertEqual(sel(soma)["codigo"], "SOMA_DE_FOLHAS_EXCEDE_100")
        for r in (sel(ruim), sel(soma)):
            self.assertEqual((r["status"], r["itens"]), ("RECUSADA", []))

    def test_aviso_nao_chama_percentual_de_probabilidade(self):
        r = sel(nos([5]))
        self.assertNotIn("probabilidade", r["aviso"].lower())
        self.assertIn("composição da amostra", r["aviso"])

    def test_entrada_nao_e_alterada_e_resultado_e_deterministico(self):
        bruto = nos([3, 9, 5, 5, 1])
        copia = copy.deepcopy(bruto)
        a, b = sel(bruto), sel(list(reversed(bruto)))
        self.assertEqual(bruto, copia)
        self.assertEqual(a, b)

    def test_modulo_nao_traz_lista_nem_faz_rede_ou_arquivo(self):
        fonte = (ROOT / "scripts" / "top10_materia.py").read_text(encoding="utf-8")
        for proibido in ("import requests", "urllib", "socket", "open(", "subprocess", "os.environ", "random"):
            self.assertNotIn(proibido, fonte, proibido)


if __name__ == "__main__":
    unittest.main()
