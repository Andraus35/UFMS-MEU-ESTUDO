"""GAP-E (GE-1 e GE-2). Cada achado nasceu como teste que falhava antes da correção. Só dados SINTÉTICOS: nenhum texto do Manual do Imparável.

GE-1: o Coach não leu as p. 148 a 153 (o conector do Drive truncou) e não havia como PROVAR a leitura nem validar citação por página (S18-R14).
GE-2: os gates G-MOT-01 a 22 eram todos "não implementados" (S18-R11); aqui os verificáveis viram código, e os não gateáveis são declarados.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gates_mot as gm  # noqa: E402
import manual_pages as mp  # noqa: E402

PALAVRAS = "alfa beta gama delta epsilon zeta eta teta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon fi chi psi omega"


def textos(n=10):
    return {i: f"Página sintética {i}. " + " ".join([PALAVRAS] * 3) for i in range(1, n + 1)}


def manifesto(n=10, **mud):
    m = mp.montar_manifesto(textos(n), fonte="Livro sintético de teste", edicao="1ª edição de teste")
    m.update(mud)
    return m


class Ge1ManifestoDaPaginacaoTests(unittest.TestCase):
    def test_montar_gera_hash_e_contagem_por_pagina_sem_guardar_texto(self):
        m = manifesto()
        self.assertEqual((m["total_paginas"], len(m["paginas"])), (10, 10))
        self.assertEqual(set(m["paginas"][0]), {"pagina", "sha256", "palavras"})
        self.assertNotIn("sintética", str(m))  # o manifesto não leva texto do livro
        self.assertEqual(mp.validar_manifesto(m), [])

    def test_hash_e_do_texto_normalizado_e_deterministico(self):
        t = textos()
        t2 = {**t, 3: t[3].replace(" ", "  ") + "\n"}  # espaços e quebra de linha não mudam a página
        self.assertEqual(mp.montar_manifesto(t, "f", "e"), mp.montar_manifesto(t2, "f", "e"))
        t3 = {**t, 3: t[3] + " extra"}
        self.assertNotEqual(mp.montar_manifesto(t, "f", "e")["paginas"][2]["sha256"], mp.montar_manifesto(t3, "f", "e")["paginas"][2]["sha256"])

    def test_valida_e_recusa_defeitos_do_manifesto(self):
        base = manifesto()
        casos = {}
        m = copy.deepcopy(base); m["paginas"].pop(4); casos["lacuna_de_pagina"] = m
        m = copy.deepcopy(base); m["paginas"][1]["pagina"] = 1; casos["pagina_repetida"] = m
        m = copy.deepcopy(base); m["total_paginas"] = 11; casos["total_diverge"] = m
        m = copy.deepcopy(base); m["paginas"][0]["sha256"] = "xyz"; casos["hash_invalido"] = m
        m = copy.deepcopy(base); m["paginas"][0]["palavras"] = -1; casos["palavras_invalidas"] = m
        m = copy.deepcopy(base); m["paginas"][0]["texto"] = "x"; casos["campo_a_mais_na_pagina"] = m
        m = copy.deepcopy(base); m["texto_integral"] = "x"; casos["campo_a_mais_no_topo"] = m
        m = copy.deepcopy(base); m.pop("edicao"); casos["campo_ausente"] = m
        for nome, ruim in casos.items():
            self.assertNotEqual(mp.validar_manifesto(ruim), [], nome)
        self.assertEqual(mp.validar_manifesto("x"), ["manifesto_nao_objeto"])

    def test_detecta_suspeita_de_truncamento_em_sequencia_de_paginas_quase_vazias(self):
        t = textos(12)
        for p in (5, 6, 7):
            t[p] = "Fim do trecho"  # conector que devolve só a ficha e o sumário
        m = mp.montar_manifesto(t, "f", "e")
        self.assertEqual(mp.suspeitas_de_truncamento(m), [5, 6, 7])
        t2 = textos(12)
        t2[5] = "curta"  # uma página curta isolada (capítulo que acaba) não é truncamento
        self.assertEqual(mp.suspeitas_de_truncamento(mp.montar_manifesto(t2, "f", "e")), [])


class Ge1ProvaDeLeituraTests(unittest.TestCase):
    def test_leitura_comprovada_quando_cada_pagina_aberta_confere_com_o_hash(self):
        t, m = textos(), manifesto()
        r = mp.prova_de_leitura(m, {p: t[p] for p in range(4, 8)}, [4, 5, 6, 7])
        self.assertEqual((r["ok"], r["faltando"], r["divergentes"]), (True, [], []))

    def test_pagina_nao_aberta_ou_truncada_nao_conta_como_lida(self):
        t, m = textos(), manifesto()
        r = mp.prova_de_leitura(m, {4: t[4], 5: t[5][:20]}, [4, 5, 6])
        self.assertEqual((r["ok"], r["faltando"], r["divergentes"]), (False, [6], [5]))

    def test_pagina_inexistente_no_manifesto_e_pedido_invalido_recusam(self):
        t, m = textos(), manifesto()
        self.assertFalse(mp.prova_de_leitura(m, t, [99])["ok"])
        for exigidas in ([], "4", [0], [True]):
            self.assertFalse(mp.prova_de_leitura(m, t, exigidas)["ok"], exigidas)

    def test_manifesto_invalido_nao_prova_nada(self):
        t = textos()
        ruim = manifesto()
        ruim["paginas"].pop()
        self.assertFalse(mp.prova_de_leitura(ruim, t, [1])["ok"])

    def test_so_afirma_que_leu_o_que_abriu(self):
        self.assertEqual(mp.afirmar_leitura({4, 5, 6}, [4, 5]), [])
        self.assertEqual(mp.afirmar_leitura({4, 5, 6}, [4, 9]), [9])
        self.assertEqual(mp.afirmar_leitura(set(), [1]), [1])


class Ge1CitacaoCurtaTests(unittest.TestCase):
    def setUp(self):
        self.t, self.m = textos(), manifesto()

    def test_citacao_literal_curta_da_pagina_aberta_e_aceita_com_a_referencia(self):
        r = mp.conferir_citacao(self.m, 3, self.t[3], "gama delta epsilon zeta")
        self.assertEqual((r["ok"], r["codigo"], r["pagina"]), (True, None, 3))

    def test_citacao_acima_de_25_palavras_recusa(self):
        longa = " ".join(["alfa beta gama delta epsilon zeta eta teta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon fi chi psi omega alfa"])
        self.assertEqual(len(longa.split()), 25)
        self.assertTrue(mp.conferir_citacao(self.m, 3, self.t[3], longa)["ok"])
        self.assertEqual(mp.conferir_citacao(self.m, 3, self.t[3], longa + " beta")["codigo"], "CITACAO_ACIMA_DE_25_PALAVRAS")

    def test_citacao_que_nao_consta_da_pagina_ou_vazia_recusa(self):
        self.assertEqual(mp.conferir_citacao(self.m, 3, self.t[3], "texto inventado que não existe")["codigo"], "CITACAO_FORA_DA_PAGINA")
        self.assertEqual(mp.conferir_citacao(self.m, 3, self.t[3], "")["codigo"], "CITACAO_VAZIA")

    def test_pagina_adulterada_ou_de_outro_numero_recusa(self):
        self.assertEqual(mp.conferir_citacao(self.m, 3, self.t[3] + " alterado", "gama delta")["codigo"], "PAGINA_DIVERGE_DO_MANIFESTO")
        self.assertEqual(mp.conferir_citacao(self.m, 99, self.t[3], "gama delta")["codigo"], "PAGINA_FORA_DO_MANIFESTO")

    def test_citacao_curtissima_nao_serve_de_prova(self):
        self.assertEqual(mp.conferir_citacao(self.m, 3, self.t[3], "gama")["codigo"], "CITACAO_CURTA_DEMAIS")


GATES_ESTRUTURAIS = ("G-MOT-01", "G-MOT-02", "G-MOT-03", "G-MOT-06", "G-MOT-07", "G-MOT-13", "G-MOT-14", "G-MOT-17", "G-MOT-18", "G-MOT-19")
GATES_LEXICAIS = ("G-MOT-04", "G-MOT-05", "G-MOT-08", "G-MOT-09", "G-MOT-10", "G-MOT-11", "G-MOT-12", "G-MOT-15", "G-MOT-16", "G-MOT-21")
NAO_GATEAVEIS = ("G-MOT-20", "G-MOT-22")

INTERV = {
    "hipotese": {"tipo": "motivacao", "incerteza": "media",
                 "evidencias": [{"data": "2026-11-18", "sinal": "sessao_perdida", "origem": "harness"},
                                {"data": "2026-11-20", "sinal": "revisao_atrasada", "origem": "harness"}],
                 "dimensoes": {"capacidade": "avaliada", "oportunidade": "avaliada", "motivacao": "avaliada", "custo": "sem_dado", "bem_estar": "sem_dado"}},
    "intervencao": {"comportamento_alvo": "iniciar a revisão do dia em até 10 minutos", "indicador": "revisão iniciada no horário combinado",
                    "tentativas_sem_efeito": 0, "revisada": False},
    "eficacia": {"declarada": False, "base": []},
    "sofrimento": {"intenso_ou_persistente": False, "encaminhado": False},
    "apoio_social": {"usado": False, "consentimento": False},
    "encaminhado_ao_tutor": False,
}


def interv(**mud):
    r = copy.deepcopy(INTERV)
    for k, v in mud.items():
        if isinstance(v, dict) and isinstance(r.get(k), dict):
            r[k].update(v)
        else:
            r[k] = v
    return r


def falhas(i):
    return {f["gate"] for f in gm.verificar_intervencao(i)["falhas"]}


class Ge2CoberturaTests(unittest.TestCase):
    def test_os_22_gates_estao_contabilizados_e_os_nao_gateaveis_sao_declarados(self):
        c = gm.cobertura()
        todos = {f"G-MOT-{i:02d}" for i in range(1, 23)}
        self.assertEqual(set(c["estruturais"]) | set(c["lexicais"]) | set(c["nao_gateaveis"]), todos)
        self.assertEqual(set(c["estruturais"]), set(GATES_ESTRUTURAIS))
        self.assertEqual(set(c["lexicais"]), set(GATES_LEXICAIS))
        self.assertEqual(set(c["nao_gateaveis"]), set(NAO_GATEAVEIS))
        self.assertEqual(c["homologa"], False)
        self.assertIn("heur", c["limite"])  # lexical é heurística: reduz, não prova


class Ge2GatesEstruturaisTests(unittest.TestCase):
    def test_intervencao_valida_passa_sem_falhas(self):
        r = gm.verificar_intervencao(INTERV)
        self.assertEqual((r["ok"], r["falhas"]), (True, []))
        self.assertEqual(r["nao_verificados"], list(NAO_GATEAVEIS))

    def test_g01_motivacao_de_uma_so_observacao_ou_um_so_dia(self):
        um = interv(hipotese={"evidencias": INTERV["hipotese"]["evidencias"][:1]})
        self.assertIn("G-MOT-01", falhas(um))
        mesmo_dia = interv(hipotese={"evidencias": [{"data": "2026-11-18", "sinal": "a", "origem": "harness"}, {"data": "2026-11-18", "sinal": "b", "origem": "harness"}]})
        self.assertIn("G-MOT-01", falhas(mesmo_dia))
        outro_tipo = interv(hipotese={"tipo": "conhecimento", "evidencias": INTERV["hipotese"]["evidencias"][:1]}, encaminhado_ao_tutor=True)
        self.assertNotIn("G-MOT-01", falhas(outro_tipo))  # a regra vale para a hipótese de motivação

    def test_g02_dimensoes_separadas_e_capacidade_e_oportunidade_avaliadas(self):
        for dim in ("capacidade", "oportunidade", "motivacao", "custo", "bem_estar"):
            d = dict(INTERV["hipotese"]["dimensoes"])
            d.pop(dim)
            self.assertIn("G-MOT-02", falhas(interv(hipotese={"dimensoes": d})), dim)
        d = dict(INTERV["hipotese"]["dimensoes"], capacidade="sem_dado")
        self.assertIn("G-MOT-02", falhas(interv(hipotese={"dimensoes": d})))  # não conclui motivação sem descartar capacidade

    def test_g03_hipotese_sem_evidencia_ou_sem_incerteza(self):
        self.assertIn("G-MOT-03", falhas(interv(hipotese={"evidencias": []})))
        self.assertIn("G-MOT-03", falhas(interv(hipotese={"incerteza": "certeza_absoluta"})))
        self.assertIn("G-MOT-03", falhas(interv(hipotese={"evidencias": [{"data": "2026-11-18", "sinal": "x"}]})))

    def test_g06_intervencao_sem_alvo_ou_sem_indicador(self):
        self.assertIn("G-MOT-06", falhas(interv(intervencao={"comportamento_alvo": ""})))
        self.assertIn("G-MOT-06", falhas(interv(intervencao={"indicador": "  "})))

    def test_g07_eficacia_so_com_satisfacao_relato_ou_antes_depois(self):
        for base in (["satisfacao"], ["relato_animo", "antes_depois_isolado"], []):
            self.assertIn("G-MOT-07", falhas(interv(eficacia={"declarada": True, "base": base})), base)
        self.assertNotIn("G-MOT-07", falhas(interv(eficacia={"declarada": True, "base": ["satisfacao", "serie_n_of_1"]})))
        self.assertNotIn("G-MOT-07", falhas(interv(eficacia={"declarada": False, "base": []})))

    def test_g18_resultado_de_ia_nao_prova_aprendizagem(self):
        self.assertIn("G-MOT-18", falhas(interv(eficacia={"declarada": True, "base": ["resultado_de_ia", "serie_n_of_1"]})))

    def test_g13_lacuna_de_conhecimento_vai_ao_tutor(self):
        ev = INTERV["hipotese"]["evidencias"]
        self.assertIn("G-MOT-13", falhas(interv(hipotese={"tipo": "conhecimento", "evidencias": ev}, encaminhado_ao_tutor=False)))
        self.assertNotIn("G-MOT-13", falhas(interv(hipotese={"tipo": "conhecimento", "evidencias": ev}, encaminhado_ao_tutor=True)))

    def test_g14_sofrimento_intenso_exige_encaminhamento(self):
        self.assertIn("G-MOT-14", falhas(interv(sofrimento={"intenso_ou_persistente": True, "encaminhado": False})))
        self.assertNotIn("G-MOT-14", falhas(interv(sofrimento={"intenso_ou_persistente": True, "encaminhado": True})))

    def test_g17_apoio_social_so_com_consentimento(self):
        self.assertIn("G-MOT-17", falhas(interv(apoio_social={"usado": True, "consentimento": False})))
        self.assertNotIn("G-MOT-17", falhas(interv(apoio_social={"usado": True, "consentimento": True})))

    def test_g19_tres_tentativas_sem_efeito_exigem_revisao(self):
        self.assertIn("G-MOT-19", falhas(interv(intervencao={"tentativas_sem_efeito": 3, "revisada": False})))
        self.assertNotIn("G-MOT-19", falhas(interv(intervencao={"tentativas_sem_efeito": 3, "revisada": True})))
        self.assertNotIn("G-MOT-19", falhas(interv(intervencao={"tentativas_sem_efeito": 2, "revisada": False})))

    def test_forma_invalida_recusa_sem_levantar_e_nao_altera_a_entrada(self):
        for ruim in (None, [], "x", {"hipotese": {}}, {**INTERV, "extra": 1}):
            r = gm.verificar_intervencao(ruim)
            self.assertFalse(r["ok"])
            self.assertEqual(r["falhas"][0]["gate"], "FORMA")
        antes = copy.deepcopy(INTERV)
        gm.verificar_intervencao(INTERV)
        self.assertEqual(INTERV, antes)


class Ge2GatesLexicaisTests(unittest.TestCase):
    def gates(self, texto):
        return {f["gate"] for f in gm.verificar_mensagem(texto)["falhas"]}

    def test_cada_gate_lexical_pega_o_seu_exemplo(self):
        exemplos = {
            "G-MOT-04": "Seu escore nesta escala validada mostra o diagnóstico psicológico.",
            "G-MOT-05": "Você é uma pessoa preguiçosa e sempre será.",
            "G-MOT-08": "Você deveria ter vergonha de ter faltado.",
            "G-MOT-09": "Se você não estudar hoje, vai fracassar na prova.",
            "G-MOT-10": "Compense todas as horas perdidas no fim de semana.",
            "G-MOT-11": "Durma menos e pule o almoço para render.",
            "G-MOT-12": "Largue o emprego para se dedicar ao concurso.",
            "G-MOT-15": "Você tem ansiedade e isso explica os erros.",
            "G-MOT-16": "Só eu entendo você, não precisa de mais ninguém.",
            "G-MOT-21": "Com esse esforço você vai ser aprovado, garanto.",
        }
        self.assertEqual(set(exemplos), set(GATES_LEXICAIS))
        for gate, texto in exemplos.items():
            self.assertIn(gate, self.gates(texto), gate)

    def test_mensagem_legitima_passa(self):
        for texto in ("Hoje a revisão é curta: 20 minutos de Legislação, sem pressa.", "Perder uma sessão acontece; vamos retomar com uma tarefa pequena.",
                      "Isso não é um diagnóstico de ansiedade; se o cansaço persistir, procure um profissional de saúde.",
                      "Não compense as horas perdidas: siga o plano de amanhã.", "Dormir bem ajuda a fixar o conteúdo."):
            self.assertEqual(self.gates(texto), set(), texto)

    def test_negacao_antes_do_trecho_nao_dispara(self):
        self.assertEqual(self.gates("Não tenho como garantir aprovação; o plano só organiza o estudo."), set())
        self.assertIn("G-MOT-21", self.gates("Garanto sua aprovação."))

    def test_texto_nao_string_ou_enorme_recusa_sem_levantar(self):
        self.assertFalse(gm.verificar_mensagem(None)["ok"])
        self.assertFalse(gm.verificar_mensagem("a" * 5000)["ok"])

    def test_ofuscacao_simples_de_acento_e_caixa_nao_escapa(self):
        self.assertIn("G-MOT-15", self.gates("VOCE TEM DEPRESSAO"))
        self.assertIn("G-MOT-10", self.gates("compense   TODAS as horas"))

    def test_o_resultado_declara_que_lexical_e_heuristica(self):
        r = gm.verificar_mensagem("Texto limpo.")
        self.assertTrue(r["ok"])
        self.assertIn("heur", r["limite"])


class Ge2SemEfeitoExternoTests(unittest.TestCase):
    def test_sem_rede_relogio_nem_escrita(self):
        for nome in ("gates_mot.py", "manual_pages.py"):
            fonte = (ROOT / "scripts" / nome).read_text(encoding="utf-8")
            for proibido in ("import requests", "urllib", "socket", "datetime.now", ".today(", "open(", "write_text"):
                self.assertNotIn(proibido, fonte, (nome, proibido))

    def test_agents_coach_continua_sem_os_gates_mot_aplicados(self):
        self.assertNotIn("G-MOT", (ROOT / "agents" / "COACH.md").read_text(encoding="utf-8"))  # aplicar em agents/ exige aprovação expressa


if __name__ == "__main__":
    unittest.main()
