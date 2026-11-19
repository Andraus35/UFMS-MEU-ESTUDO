"""Contrato da S14: runtime operacional. Cognição livre, leitura e entrega condicionadas por mecanismos determinísticos."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S14_RUNTIME_OPERACIONAL.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Plano", 1)[0]
PLANO = DOC.split("## Plano", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}


def req(n):
    return REQUISITOS.split(f"S14-R{n} ", 1)[1].split("| S14-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS14Tests(unittest.TestCase):
    def test_secoes_na_ordem_do_modelo(self):
        posicoes = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Plano", "## Requisitos", "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_requisitos_r1_a_r19_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S14-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S14-R\d+) ", l).group(1) for l in linhas], [f"S14-R{i}" for i in range(1, 20)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 5)
        self.assertIn("- **Lacunas:**", PESQUISA)
        sem = PESQUISA.replace("**", "").lower()
        for trecho in ("só resumos", "não li o texto original", "numeração da owasp", "benchmarks", "nunca é portão", "voluntário"):
            self.assertIn(trecho, sem, trecho)
        for nivel in ("**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)

    def test_regra_do_proprietario_cognicao_livre_e_bordas_deterministicas(self):
        for trecho in ("19/11/2026", "livre na cognição probabilística", "condicionado nas leituras e nas entregas",
                       "não restringe o raciocínio", "autonomia cognitiva"):
            self.assertIn(trecho, TEXTO, trecho)
        r1 = req(1)
        for trecho in ("nenhum gate avalia o raciocínio", "z0 a z3", "enforçada", "verificável", "não gateável"):
            self.assertIn(trecho, r1, trecho)

    def test_zonas_e_tres_classes_de_garantia_no_plano(self):
        sem = PLANO.replace("**", "").replace("`", "").lower()
        for trecho in ("z0 leitura", "z1 cognição", "z2 entrega", "z3 efeito", "enforçada", "verificável", "não gateável",
                       "no chat direto", "nada é imposto", "fases e portas sem volta", "modo sombra"):
            self.assertIn(trecho, sem, trecho)

    def test_rastreabilidade_de_todas_as_lacunas_da_auditoria(self):
        sem = PLANO.replace("**", "").replace("`", "").lower()
        for trecho in ("comportamento factual e pedagógico sem controle", "start autodeclarado", "zapia caixa-preta",
                       "forma, não a verdade", "rotina diária", "observabilidade", "parada não testada", "rm-06 e rm-07",
                       "versão fixa", "hooks que falham abertos", "regra de merge"):
            self.assertIn(trecho, sem, trecho)
        # a tabela de lacunas cita cada requisito com fronteira de palavra (R1 não pode casar com R10)
        tabela = sem.split("### rastreabilidade", 1)[1]
        for r in (1, 2, 3, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18):
            self.assertRegex(tabela, rf"\br{r}\b", f"R{r}")

    def test_contrato_em_producao_e_sha_fixado(self):
        r2 = req(2)
        for trecho in ("sha da main fixado", "ato dele", "informa o sha", "recusado", "não bloqueia"):
            self.assertIn(trecho, r2, trecho)

    def test_start_verificavel_sem_prometer_compreensao(self):
        r3 = req(3)
        for trecho in ("recibo", "recalcula", "não prova compreensão", "não prova quem o emitiu", "hash adulterado", "ausente"):
            self.assertIn(trecho, r3, trecho)

    def test_leitura_por_lista_fechada(self):
        r4 = req(4)
        for trecho in ("lista fechada", "nunca o histórico bruto", "fila", "exportações", "dado, não instrução", "consentimento v4", "session_read_guard"):
            self.assertIn(trecho, r4, trecho)

    def test_envelope_tipado_com_classes_do_agents_md(self):
        r5 = req(5)
        for trecho in ("campos fechados", "orientacao", "recomendacao_caderno", "lembrete", "comando", "prompt_notebook",
                       "rotina_autorizada", "sensivel", "sem aprovação por mensagem", "campo extra"):
            self.assertIn(trecho, r5, trecho)

    def test_declarar_e_verificar_alegacoes_com_limite_honesto(self):
        r6 = req(6)
        for trecho in ("declara", "citacao_edital", "dado_aluno", "nivel_evidencia", "inferencia", "trecho literal",
                       "fato não declarado bloqueia", "número de prescrição", "só avisa", "em sombra só avisa",
                       "não numérica e não declarada não é detectável"):
            self.assertIn(trecho, r6, trecho)

    def test_caderno_sem_disponibilidade_inventada_e_privacidade_na_saida(self):
        self.assertIn("nunca afirma disponibilidade de questões", req(7))
        r8 = req(8)
        for trecho in ("segredo", "dado pessoal", "enunciado", "url fora da lista", "nunca vai ao repositório público", "não vira instrução"):
            self.assertIn(trecho, r8, trecho)

    def test_efeitos_so_pelo_portao_e_origem_nao_provada(self):
        r9 = req(9)
        for trecho in ("só por comando validado", "rotina versionada", "registrar_* ainda não existe", "origem do comando não é provada",
                       "reduz o dano, não o elimina", "contents"):
            self.assertIn(trecho, r9, trecho)

    def test_veracidade_do_resultado_com_limite_declarado(self):
        r10 = req(10)
        for trecho in ("valida a forma, não a verdade", "classe de origem", "confirmação do proprietário", "resultado_corrigido",
                       "não há como provar"):
            self.assertIn(trecho, r10, trecho)

    def test_sombra_e_bloqueio_efeito_sempre_bloqueia(self):
        r11 = req(11)
        for trecho in ("sombra", "bloqueio", "efeito externo bloqueia desde o início", "fail-closed", "falso positivo"):
            self.assertIn(trecho, r11, trecho)

    def test_avaliacao_offline_sem_juiz_llm_como_portao(self):
        r12 = req(12)
        for trecho in ("rubrica humana", "juiz-llm", "nunca decide entrega nem homologação", "determinístico", "rm-06", "rm-07",
                       "nenhum portão chama modelo"):
            self.assertIn(trecho, r12, trecho)

    def test_registro_sem_dado_pessoal_e_auditoria_com_pausa(self):
        r13, r14 = req(13), req(14)
        for trecho in ("nunca o conteúdo pessoal", "repositório privado", "ausência de registro"):
            self.assertIn(trecho, r13, trecho)
        for trecho in ("amostra", "rubrica", "pausa", "duas amostras seguidas", "não é cronograma de estudo", "ajustável"):
            self.assertIn(trecho, r14, trecho)

    def test_rotinas_operacionais_completas(self):
        r15 = req(15)
        for trecho in ("diária do coach", "no máximo uma mensagem por dia", "auditoria por amostra", "vencimentos de revisão",
                       "pré-voo antes de janela", "renovação de tokens", "14 dias antes", "04/12/2026", "monitor do edital",
                       "deriva do contrato", "parada", "autorizo", "não envia nada"):
            self.assertIn(trecho, r15, trecho)

    def test_parada_fail_closed_e_controle_de_mudanca(self):
        r16, r17, r18 = req(16), req(17), req(18)
        for trecho in ("flags voltam a false", "token revogado", "rotinas desligadas", "exercida na janela do piloto"):
            self.assertIn(trecho, r16, trecho)
        for trecho in ("recusa", "aviso", "falhar aberto", "orientação pedagógica segura"):
            self.assertIn(trecho, r17, trecho)
        for trecho in ("identidade própria", "codeowners", "require_code_owner_reviews", "check de ci", "autoria é indistinguível",
                       "sem controle de mudança"):
            self.assertIn(trecho, r18, trecho)

    def test_honestidade_termina_com_nao_garantido(self):
        r19 = req(19)
        for trecho in ("não garante", "leu e entendeu os contratos", "veracidade", "não está homologada", "não garantido:"):
            self.assertIn(trecho, r19, trecho)
        limites = DOC.split("## Limites", 1)[1].lower().replace("**", "").replace("`", "")
        for trecho in ("não implanta", "não liga flag", "agents.md", "product.md", "settings.json", "nenhum gate avalia a qualidade da cognição",
                       "não garantido:"):
            self.assertIn(trecho, limites, trecho)

    def test_tarefas_derivadas_estao_na_fila_na_ordem(self):
        derivadas = DOC.split("## Tarefas derivadas", 1)[1].split("## Aceite", 1)[0]
        self.assertEqual(re.findall(r"^\d+\. \*\*(\w+)\*\*", derivadas, re.M), ["GE", "RS", "AE", "AM"])
        ordem = [i for i in FILA if i in ("GE", "RS", "AE", "AM")]
        self.assertEqual(ordem, ["GE", "RS", "AE", "AM"])
        self.assertEqual(FILA["GE"]["deliverable"], "scripts/delivery_gate.py")
        self.assertEqual(FILA["RS"]["deliverable"], "scripts/start_receipt.py")
        for i in ("S14", "GE", "RS", "AE", "AM"):
            self.assertEqual(FILA[i]["roadmap_task"], "RM-07", i)
        self.assertIn("S14", FILA["GE"]["depends_on"])
        self.assertIn("PF", FILA["GE"]["depends_on"])  # uma tarefa por vez: o PF vem antes

    def test_nao_ha_recibo_de_producao_indefinido(self):
        self.assertNotIn("recibo de produção", TEXTO)  # a produção liga e desliga pelo SHA fixado (R2), não por recibo sem definição
        self.assertIn("desfixam o sha de produção", req(14))
        self.assertIn("sem sha de produção fixado", req(16))

    def test_nenhum_portao_depende_de_modelo(self):
        for proibido in ("juiz-llm decide", "o modelo aprova", "o llm aprova"):
            self.assertNotIn(proibido, TEXTO, proibido)


if __name__ == "__main__":
    unittest.main()
