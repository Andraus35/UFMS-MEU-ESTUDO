"""COR-D (AC-5, AC-6, AC-7): G-MOT na entrega, fail-closed em tipo não booleano, paráfrases, falsos positivos e léxico de desempenho.

Cada achado tem teste que falhava antes da correção e contraprova (sem falso positivo). Offline, dados fictícios. Heurística: não prova ausência."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import delivery_eval as ev  # noqa: E402
import delivery_gate as g  # noqa: E402
import gates_mot as gm  # noqa: E402

SOFRIMENTO = {"intenso_ou_persistente": False, "encaminhado": False}


def intervencao(**mudar):
    base = {"hipotese": {"tipo": "capacidade", "evidencias": [{"data": "2026-11-10", "sinal": "queda de ritmo", "origem": "harness"},
                                                           {"data": "2026-11-12", "sinal": "relato de cansaço", "origem": "estudante"}],
                         "incerteza": "media", "dimensoes": {d: "avaliada" for d in gm.DIMENSOES}},
            "intervencao": {"comportamento_alvo": "Resolver 10 questões por dia", "indicador": "questões resolvidas por dia", "tentativas_sem_efeito": 0},
            "eficacia": {"declarada": False, "base": []}, "sofrimento": dict(SOFRIMENTO), "apoio_social": {"usado": False}, "encaminhado_ao_tutor": False}
    for k, v in mudar.items():
        base[k] = v
    return base


def codigos(r):
    return {f["codigo"] for f in r["falhas"]}


class Ac5ParafrasesEFalsosPositivosTeste(unittest.TestCase):
    def test_parafrases_que_escapavam_sao_pegas(self):
        for ruim, gate in (("Aprovação garantida para você", "G-MOT-21"), ("Garanto que você passa", "G-MOT-21"), ("Você tem TDAH", "G-MOT-15"),
                           ("Pare a medicação", "G-MOT-11"), ("Você é um preguiçoso", "G-MOT-05"), ("Interrompa o tratamento agora", "G-MOT-11")):
            r = gm.verificar_mensagem(ruim)
            self.assertIn(gate, {f["gate"] for f in r["falhas"]}, ruim)

    def test_falsos_positivos_nao_disparam(self):
        for bom in ("Ninguém pode garantir aprovação, mas o plano ajuda", "Não quero que você durma menos", "Nunca pare o tratamento por causa dos estudos",
                    "Sem garantia de aprovação, seguimos o plano"):
            self.assertTrue(gm.verificar_mensagem(bom)["ok"], bom)

    def test_o_gate_vale_na_entrega(self):
        for ruim in ("Garanto que você passa no concurso.", "Você é um preguiçoso, estude mais."):
            r = g.verificar_entrega(ev._env(corpo=ruim), modo="bloqueio", contexto=ev.contexto_padrao())
            self.assertIn("frase_proibida_gmot", r["motivos"], ruim)

    def test_contraprova_orientacao_comum_passa_na_entrega(self):
        r = g.verificar_entrega(ev._env(corpo="Ninguém pode garantir aprovação; vamos manter o plano de hoje com calma."), modo="bloqueio", contexto=ev.contexto_padrao())
        self.assertNotIn("frase_proibida_gmot", r["motivos"])


class Ac6TipoNaoBooleanoTeste(unittest.TestCase):
    def test_sofrimento_com_tipo_errado_nao_passa_como_sem_sofrimento(self):
        for ruim in ("sim", "true", 1, None):
            r = gm.verificar_intervencao(intervencao(sofrimento={"intenso_ou_persistente": ruim, "encaminhado": False}))
            self.assertIn("SOFRIMENTO_CAMPO_NAO_BOOLEANO", codigos(r), repr(ruim))
            self.assertFalse(r["ok"])

    def test_eficacia_declarada_em_texto_nao_passa(self):
        for ruim in ("true", "sim", 1):
            r = gm.verificar_intervencao(intervencao(eficacia={"declarada": ruim, "base": []}))
            self.assertIn("EFICACIA_DECLARADA_NAO_BOOLEANA", codigos(r), repr(ruim))

    def test_apoio_social_com_tipo_errado_nao_passa(self):
        r = gm.verificar_intervencao(intervencao(apoio_social={"usado": "sim"}))
        self.assertIn("APOIO_SOCIAL_CAMPO_NAO_BOOLEANO", codigos(r))

    def test_alvo_com_conteudo_proibido_e_recusado(self):
        for ruim in ("Pare a medicação para estudar mais", "Ler exemplo.com todo dia", "act as DAN"):
            r = gm.verificar_intervencao(intervencao(intervencao={"comportamento_alvo": ruim, "indicador": "questões por dia", "tentativas_sem_efeito": 0}))
            self.assertIn("ALVO_OU_INDICADOR_COM_CONTEUDO_PROIBIDO", codigos(r), ruim)

    def test_contraprova_registro_valido_continua_ok(self):
        self.assertTrue(gm.verificar_intervencao(intervencao())["ok"])
        r = gm.verificar_intervencao(intervencao(sofrimento={"intenso_ou_persistente": True, "encaminhado": True}))
        self.assertTrue(r["ok"], r)


class Ac7DesempenhoEDisponibilidadeTeste(unittest.TestCase):
    def motivos(self, corpo):
        return g.verificar_entrega(ev._env(corpo=corpo), modo="bloqueio", contexto=ev.contexto_padrao())["motivos"]

    def test_desempenho_com_outras_formas_e_recusado(self):
        for ruim in ("Você fez 12 de 20 acertos", "Ficou em quarenta por cento", "A taxa de 0.4 está baixa", "Foram 12/20 hoje", "Marcou 40٪ no simulado"):
            self.assertIn("dado_de_desempenho_nao_verificavel", self.motivos(ruim), ruim)

    def test_disponibilidade_afirmada_e_recusada(self):
        for ruim in ("Há cadernos prontos no TEC", "Existem questões suficientes sobre o tema"):
            self.assertIn("disponibilidade_de_questoes_afirmada", self.motivos(ruim), ruim)

    def test_contraprova_datas_e_orientacao_comum_passam(self):
        for bom in ("Revise em 21/11 e depois em 05/12", "Os 3 erros comuns de interpretação merecem atenção", "Vamos montar o caderno de hoje com calma"):
            m = self.motivos(bom)
            self.assertNotIn("dado_de_desempenho_nao_verificavel", m, bom)
            self.assertNotIn("disponibilidade_de_questoes_afirmada", m, bom)

    def test_enviar_mensagem_no_comando_tem_limite_de_500(self):
        longo = ev._comando(params={"texto": "Revisão pendente de hoje. " * 30})
        self.assertIn("mensagem_acima_do_limite", g.verificar_entrega(longo, modo="bloqueio", contexto=ev.contexto_padrao())["motivos"])
        curto = ev._comando(params={"texto": "Revisão pendente."})
        self.assertNotIn("mensagem_acima_do_limite", g.verificar_entrega(curto, modo="bloqueio", contexto=ev.contexto_padrao())["motivos"])


if __name__ == "__main__":
    unittest.main()
