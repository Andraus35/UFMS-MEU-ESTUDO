"""Contrato da S15: orquestração do ciclo (fluxo, rotina e fonte de tempo). Especificação; não implanta nem homologa."""
import glob
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMINHO = ROOT / "docs" / "especificacoes" / "S15_ORQUESTRACAO_FLUXO_ROTINA_TEMPO.md"
DOC = CAMINHO.read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Mapa", 1)[0]
MAPA = DOC.split("## Mapa das decisões", 1)[1].split("## Fluxo e rotina", 1)[0]
FLUXO = DOC.split("## Fluxo e rotina", 1)[1].split("## Procedimento da rotina", 1)[0]
PROCEDIMENTO = DOC.split("## Procedimento da rotina", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}
PRODUCT = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")


def req(n):
    return REQUISITOS.split(f"S15-R{n} ", 1)[1].split("| S15-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS15Tests(unittest.TestCase):
    def test_secoes_na_ordem_do_modelo(self):
        posicoes = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Mapa das decisões", "## Fluxo e rotina", "## Procedimento da rotina", "## Requisitos",
                                           "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_requisitos_r1_a_r19_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S15-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S15-R\d+) ", l).group(1) for l in linhas], [f"S15-R{i}" for i in range(1, 20)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_links_confianca_e_lacunas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 6)
        self.assertIn("- **Lacunas:**", PESQUISA)
        self.assertIn("**B**", PESQUISA)
        self.assertIn("**C**", PESQUISA)
        sem = PESQUISA.replace("**", "").lower()
        for trecho in ("nada aqui foi testado", "lida só em parte", "não foi verificada", "propostas", "21/11/2026"):
            self.assertIn(trecho, sem, trecho)

    def test_fonte_de_verdade_do_tempo_relogio_injetado_em_utc_e_modelo_nao_estima(self):
        r1 = req(1)
        for trecho in ("utc", "relógio do ambiente que roda o código determinístico", "injetado", "o modelo nunca estima", "datetime.now()"):
            self.assertIn(trecho, r1, trecho)

    def test_fuso_e_dia_de_estudo_sao_proposta_do_proprietario(self):
        r2 = req(2)
        for trecho in ("america/campo_grande", "utc−4", "00:00 local", "decisão do proprietário", "d-29", "nunca inferido"):
            self.assertIn(trecho, r2, trecho)

    def test_quem_acorda_dois_estagios_e_candidatos_em_ordem(self):
        r3 = req(3)
        for trecho in ("dois estágios", "decidir", "executar", "tarefa agendada do app claude", "schedule", "job da zapia", "900 s",
                       "não decide", "o relógio só **chama**".replace("**", "")):
            self.assertIn(trecho, r3, trecho)
        self.assertLess(r3.index("(a)"), r3.index("(b)"))
        self.assertLess(r3.index("(b)"), r3.index("(c)"))
        self.assertIn("proprietário", r3)

    def test_prova_do_gatilho_sem_efeito_exige_autorizo_e_tres_dias(self):
        r4 = req(4)
        for trecho in ("sem efeito", "carimbo", "três dias", "pontualidade", "autorizo"):
            self.assertIn(trecho, r4, trecho)

    def test_idade_da_projecao_e_janela_e_despertar_perdido(self):
        self.assertIn("24 h", req(5))
        self.assertIn("72 h", req(5))
        for trecho in ("janela de validade", "rotina-aaaa-mm-dd", "data local", "não duplica"):
            self.assertIn(trecho, req(6), trecho)
        for trecho in ("nada é enviado em seu lugar", "ausência do recibo do dia", "em dobro"):
            self.assertIn(trecho, req(7), trecho)

    def test_nenhuma_cognicao_no_relogio_e_zapia_nao_decide(self):
        r8 = req(8)
        for trecho in ("só chamam", "decide", "zapia", "executa", "nenhum gate avalia o raciocínio"):
            self.assertIn(trecho, r8, trecho)
        self.assertNotRegex(TEXTO, r"o relógio (decide|escolhe)")
        self.assertNotIn("restringir a escolha", TEXTO.replace("nenhuma regra desta especificação restringe a escolha", ""))

    def test_estado_de_liberacao_hoje_nao_resolve_atos_do_proprietario(self):
        r9 = req(9)
        for trecho in ("autorizo", "duas flags", "false", "pj", "p9", "04/12/2026", "e0", "consentimento v4", "não as resolve", "21/11/2026", "especificar", "não é** o".replace("**", "")):
            self.assertIn(trecho, r9, trecho)
        self.assertIn("aprovação expressa citando pr e head", r9)

    def test_estudante_sempre_pode_acionar_e_tempo_de_prova_nao_e_rotina(self):
        self.assertIn("sem esperar", req(10))
        self.assertIn("pausada por ele", req(10))
        for trecho in ("240 minutos", "config/concursos.json", "nunca estimados"):
            self.assertIn(trecho, req(11), trecho)

    def test_mapa_cobre_os_temas_unificados_com_origem(self):
        for tema in ("papéis", "onde rodam", "canal", "ciclo", "método e prazos", "rotina diária", "limites da zapia", "entrega e gates",
                     "leitura de resultado", "persistência", "piloto"):
            self.assertIn(tema, MAPA.lower(), tema)
        linhas = [l for l in MAPA.splitlines() if l.startswith("| ") and not l.startswith("| Tema") and not l.startswith("|---")]
        self.assertGreaterEqual(len(linhas), 11)
        for l in linhas:
            self.assertRegex(l.rsplit("|", 2)[-2], r"(D-\d+|S\d+|PRODUCT)", l[:40])

    def test_tabela_de_gatilhos_a_g_com_quem_acorda_decide_executa(self):
        for rotulo in ("A.", "B.", "C.", "D.", "E.", "F.", "G."):
            self.assertIn(f"**{rotulo}", FLUXO, rotulo)
        for coluna in ("Quem acorda", "Quem decide", "Quem executa"):
            self.assertIn(coluna, FLUXO)
        self.assertIn("Tutor prescreve", FLUXO)  # o lembrete é do Coach; a prescrição da revisão é do Tutor
        self.assertIn("Zapia envia", FLUXO)

    def test_rastreabilidade_todo_identificador_citado_existe_na_origem(self):
        for s, r in sorted(set(re.findall(r"\bS(\d+)-R(\d+)\b", DOC))):
            if s == "15":
                continue
            origem = glob.glob(str(ROOT / "docs" / "especificacoes" / f"S{s}_*.md"))
            self.assertEqual(len(origem), 1, f"S{s}")
            self.assertIn(f"| S{s}-R{r} |", Path(origem[0]).read_text(encoding="utf-8"), f"S{s}-R{r}")
        candidatas = {"D-29", "D-30"}  # propostas: ainda não existem no PRODUCT.md
        for d in sorted(set(re.findall(r"\bD-\d+\b", DOC)) - candidatas):
            self.assertRegex(PRODUCT, rf"\*\*{d} \(", d)
        for d in candidatas:
            self.assertNotIn(f"**{d} (", PRODUCT, f"{d} já virou decisão: atualizar a S15")

    def test_nao_implanta_nem_autoriza_nem_homologa(self):
        for trecho in ("não implanta, não autoriza e não homologa", "não implementa, não agenda, não autoriza e não homologa",
                       "implementado_nao_homologado", "bloqueados"):
            self.assertIn(trecho, TEXTO, trecho)
        self.assertNotIn("autorizo recebido", TEXTO)

    def test_skill_spec_lean_negada_declarada_como_lacuna(self):
        self.assertIn("a instalação dela nesta sessão foi negada pelo ambiente", TEXTO)

    def test_termina_com_nao_garantido(self):
        self.assertIn("**Não garantido:**", DOC)
        cauda = DOC.split("**Não garantido:**", 1)[1].lower()
        for trecho in ("gatilho agendado", "zapia entregue", "relógio do ambiente", "persistência de resultados"):
            self.assertIn(trecho.replace("zapia entregue", "zapia entregue"), cauda.replace("a zapia entregue", "zapia entregue"), trecho)

    def test_procedimento_p0_a_p6_e_autorizacao_nao_e_o_autorizo(self):
        for passo in ("P0", "P1", "P2", "P3", "P4", "P5", "P6"):
            self.assertIn(f"| {passo} |", PROCEDIMENTO, passo)
        ordem = [PROCEDIMENTO.index(f"| P{i} |") for i in range(7)]
        self.assertEqual(ordem, sorted(ordem))
        sem = PROCEDIMENTO.replace("**", "").replace("`", "")
        for trecho in ("autorizou especificar a rotina", "não é a frase AUTORIZO de S8-R8", "nenhum job, lembrete ou tarefa é criado",
                       "encerra a execução sem enviar nada", "Zapia executa", "Coach decide o texto", "sem recibo"):
            self.assertIn(trecho, sem, trecho)

    def test_r15_pre_condicoes_em_ordem_e_falha_nao_envia(self):
        r = req(15)
        for trecho in ("em ordem", "relógio injetado", "start", "autorizada e não pausada", "consentimento v4", "idade", "sha do contrato", "não envia nada", "só o código do motivo"):
            self.assertIn(trecho, r, trecho)

    def test_r16_classes_do_dia_e_precedencia(self):
        r = req(16)
        for trecho in ("função pura", "descanso", "sem_plano", "revisao_vencida", "devido_hoje", "sem_atividade", "precedência", "não é reagendada em silêncio", "o texto é do coach"):
            self.assertIn(trecho, r, trecho)
        ordem = [r.index(c) for c in ("descanso (sem", "sem_plano (", "revisao_vencida (", "devido_hoje (", "sem_atividade (")]
        self.assertEqual(ordem, sorted(ordem))

    def test_r17_limites_diarios_e_tres_dias_sem_interacao(self):
        r = req(17)
        for trecho in ("duas** mensagens".replace("**", ""), "dias locais", "um** segundo lembrete".replace("**", ""), "entram no briefing", "sem rajada", "três", "uma única** pergunta".replace("**", ""),
                       "proposta ajustável"):
            self.assertIn(trecho, r, trecho)

    def test_r18_r19_conteudo_pausa_e_sem_cobranca_retroativa(self):
        r18, r19 = req(18), req(19)
        for trecho in ("sem** desempenho".replace("**", ""), "zapia não redige", "verificador de entrega"):
            self.assertIn(trecho, r18, trecho)
        for trecho in ("pausa", "desfixa o sha", "retomar é ato dele", "não gera cobrança dos dias perdidos", "visível"):
            self.assertIn(trecho, r19, trecho)

    def test_tarefas_derivadas_sao_quatro_e_nao_viram_fila_agora(self):
        derivadas = DOC.split("## Tarefas derivadas", 1)[1].split("## Aceite", 1)[0]
        self.assertEqual(len(re.findall(r"^\d+\. \*\*", derivadas, re.M)), 4)
        self.assertEqual(set(FILA) & {"S15-RELOGIO", "S15-PROVA"}, set())

    def test_item_s15_na_fila_com_entrega_dependencias_e_roadmap(self):
        item = FILA["S15"]
        self.assertEqual(item["deliverable"], "docs/especificacoes/S15_ORQUESTRACAO_FLUXO_ROTINA_TEMPO.md")
        self.assertEqual(item["roadmap_task"], "RM-09")
        self.assertEqual(item["depends_on"], ["S8", "S14"])
        self.assertEqual(item["blocking_inputs"], [])
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertIn("**RM-09 — S15:**", roadmap)
        self.assertIn("RM-09 permanece `planejado`", roadmap.split("**RM-09 — S15:**", 1)[1].split("\n", 1)[0])
        readme = (ROOT / "docs" / "especificacoes" / "README.md").read_text(encoding="utf-8")
        self.assertIn("| S15 |", readme)


if __name__ == "__main__":
    unittest.main()
