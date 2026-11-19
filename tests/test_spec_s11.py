"""Contrato da S11: ciclo ponta a ponta e piloto curto. Um caderno, janela curta, semáforo fixado antes, relatório sem dado pessoal."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S11_CICLO_PILOTO.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Plano", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}


def req(n):
    return REQUISITOS.split(f"S11-R{n} ", 1)[1].split("| S11-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS11Tests(unittest.TestCase):
    def test_secoes_na_ordem_do_modelo(self):
        posicoes = [DOC.index(s) for s in ("## Objetivo", "## Pesquisa", "## Plano", "## Requisitos", "## Tarefas derivadas", "## Aceite", "## Limites")]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_requisitos_r1_a_r13_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S11-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S11-R\d+) ", l).group(1) for l in linhas], [f"S11-R{i}" for i in range(1, 14)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 5)
        self.assertIn("- **Lacunas:**", PESQUISA)
        sem = PESQUISA.replace("**", "").lower()
        for trecho in ("não li o texto original", "só resumos", "benchmarks", "relato", "não é vinculante", "a meta deve ser justificada"):
            self.assertIn(trecho, sem, trecho)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)

    def test_decisoes_do_proprietario_registradas(self):
        for trecho in ("19/11/2026", "um caderno real consentido", "p7", "p8", "só vale com a aprovação expressa", "nunca liga",
                       "começa em e0 em 20/11", "não bloqueia", "recusa", "não depende de leitura automática"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_um_caderno_sem_promessa_de_eficacia(self):
        r1, r13 = req(1), req(13)
        for trecho in ("um caderno real", "sem teste de hipótese de eficácia", "n=1"):
            self.assertIn(trecho, r1, trecho)
        # a palavra proibida só pode aparecer na frase que a proíbe; qualquer promessa de ganho em outro lugar reprova
        self.assertEqual(TEXTO.count("melhorou"), 1)
        self.assertIn("não contém a palavra \"melhorou\"", r1)
        for trecho in ("utilidade pedagógica", "nem homologa", "rm-10", "relato do proprietário não vira prova independente", "não provado:"):
            self.assertIn(trecho, r13, trecho)

    def test_preflight_tudo_ou_nada_com_flags_hash_e_consentimento(self):
        r2 = req(2)
        for trecho in ("somente leitura", "tudo ou nada", "personal_results_writes_enabled=false", "private_flow_promotion_enabled=false",
                       "hash igual", "privados", "sem forks", "consentimento", "v4", "margem de 7 dias", "contraprova", "leituras injetadas",
                       "head da main no momento do pré-voo", "reinstala o fluxo antes", "não tem linha de comando"):
            self.assertIn(trecho, r2, trecho)

    def test_janela_curta_so_a_flag_do_fluxo_e_aprovacao_expressa(self):
        r3 = req(3)
        for trecho in ("só a flag do fluxo", "24 h", "aprovação expressa", "a do público segue false", "não está no agents.md"):
            self.assertIn(trecho, r3, trecho)

    def test_oito_etapas_cada_uma_com_prova_ou_nao_provada(self):
        r4 = req(4)
        for trecho in ("f1", "f8", "relato dele", "leitura de volta", "check_projection", "não provada", "relatada nunca é escrita como provada"):
            self.assertIn(trecho, r4, trecho)

    def test_entrada_manual_e_o_caminho_de_referencia(self):
        r5 = req(5)
        for trecho in ("manual é o caminho de referência", "não é pré-condição", "recusa", "disponibilidade de questões"):
            self.assertIn(trecho, r5, trecho)

    def test_registro_unico_com_readback_e_sem_marca_de_sintetico(self):
        r7 = req(7)
        for trecho in ("não leva sintetico", "sha do commit", "idempotente", "lido de volta", "pendente", "sem colar valores"):
            self.assertIn(trecho, r7, trecho)

    def test_reavaliacao_usa_o_gerador_e_niveis_honestos(self):
        r8 = req(8)
        for trecho in ("gerador", "lista fechada", "e2", "e3", "desconhecido permanece desconhecido", "consentimento v4", "session_read_guard",
                       "attempt_at", "e4", "fora do alcance de um caderno"):
            self.assertIn(trecho, r8, trecho)

    def test_semaforo_fixado_antes_com_gatilhos_vermelhos(self):
        r10 = req(10)
        for trecho in ("vermelho", "âmbar", "verde", "dado pessoal no repositório público", "sem readback", "flag do público", "token ou segredo exposto",
                       "hash do fluxo diferente", "consentimento inválido", "caso de teste", "inclusive no pré-voo", "fora da lista vermelha",
                       "janela aberta há mais de 24 h", "relatadas", "nunca é verde"):
            self.assertIn(trecho, r10, trecho)

    def test_relatorio_sem_dado_pessoal(self):
        r11 = req(11)
        for trecho in ("sem dado pessoal", "shas", "hashes", "nunca valores de desempenho", "e-mail", "token"):
            self.assertIn(trecho, r11, trecho)

    def test_fechamento_volta_as_duas_flags_a_false(self):
        r12 = req(12)
        for trecho in ("flag do fluxo a false", "pr de fechamento", "duas flags false", "nenhum segundo caderno antes do fechamento"):
            self.assertIn(trecho, r12, trecho)

    def test_nao_liga_nada_nem_altera_contratos(self):
        limites = DOC.split("## Limites", 1)[1].lower().replace("**", "").replace("`", "")
        for trecho in ("não liga flag", "não grava resultado", "agents.md", "product.md", "settings.json", "continuam relato"):
            self.assertIn(trecho, limites, trecho)

    def test_tarefas_derivadas_estao_na_fila_na_ordem(self):
        for item in ("PF", "PJ", "PREL", "RT"):
            self.assertIn(item, FILA, item)
        ordem = [i for i in FILA if i in ("PF", "PREL", "PJ", "RT")]
        self.assertEqual(ordem, ["PF", "PREL", "PJ", "RT"])  # a ordem da fila é a do texto e a das dependências
        derivadas = DOC.split("## Tarefas derivadas", 1)[1].split("## Aceite", 1)[0]
        self.assertEqual(re.findall(r"^\d+\. \*\*(\w+)\*\*", derivadas, re.M), ["PF", "PREL", "PJ", "RT"])
        self.assertEqual(FILA["PF"]["depends_on"], ["S11"])
        self.assertIn("PF", FILA["PJ"]["depends_on"])
        self.assertTrue(FILA["PJ"]["blocking_inputs"])
        self.assertIn("aprovação expressa", " ".join(FILA["PJ"]["blocking_inputs"]))
        self.assertTrue(all(FILA[i]["roadmap_task"] == "RM-08" for i in ("PF", "PJ", "PREL", "RT")))
        self.assertEqual(FILA["PF"]["deliverable"], "scripts/piloto_preflight.py")
        self.assertEqual(FILA["PJ"]["deliverable"], "docs/governanca/E8_JANELA_PILOTO.md")
        self.assertEqual(FILA["RT"]["deliverable"], "scripts/termux/piloto.sh")


if __name__ == "__main__":
    unittest.main()
