"""Contrato da E2: emenda aditiva da S4, S5 e S9. O texto antigo permanece, a emenda vale, nada de PRODUCT.md, agents/ ou flag."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESP = ROOT / "docs" / "especificacoes"
S4 = (ESP / "S4_OPERACAO.md").read_text(encoding="utf-8")
S5 = (ESP / "S5_ZAPIA.md").read_text(encoding="utf-8")
S9 = (ESP / "S9_LEITURA_PLATAFORMAS.md").read_text(encoding="utf-8")
REG = (ROOT / "docs" / "governanca" / "E2_EMENDA_S5_S4R2_20261118.md").read_text(encoding="utf-8")


def emenda(texto):
    return texto.split("## Emenda E2 (18/11/2026)", 1)[1].lower().replace("**", "").replace("`", "")


class EmendaTests(unittest.TestCase):
    def test_cada_especificacao_tem_a_secao_no_fim_e_o_aviso_no_topo(self):
        for nome, t in (("S4", S4), ("S5", S5), ("S9", S9)):
            self.assertEqual(t.count("## Emenda E2 (18/11/2026)"), 1, nome)
            self.assertTrue(t.rstrip().split("## Emenda E2", 1)[1].count("\n## ") == 0, nome)  # é a última seção
            self.assertIn('há a seção "Emenda E2"', t.split("## ", 1)[0] + t[:900], nome)

    def test_o_texto_antigo_permanece(self):
        for trecho in ("o proprietário exporta (ou captura) o desempenho na plataforma (opção f)", "origem verificável",
                       "a assinatura recomendada é **ed25519**", "o ambiente dos agentes está em d-18"):
            self.assertIn(trecho, (S4 + S5).lower(), trecho)
        self.assertIn("linha de base e o primeiro caminho", S9.lower().replace("**", ""))

    def test_s4_desempenho_pela_zapia_pedido_por_tutor_ou_coach_com_limite(self):
        e = emenda(S4)
        for t in ("pela zapia, pedido pelo tutor ou pelo coach", "no lugar da exportação manual", "no máximo 1 por dia e só com atividade concluída",
                  "tabela estruturada", "relato do procedimento", "análise de conteúdo não entra", "fila", "a zapia não grava resultado por comando",
                  "e3", "exportação manual continua sendo a alternativa", "qconcursos segue só por entrada manual"):
            self.assertIn(t, e, t)

    def test_s4_r2_continua_nao_atendida_na_nuvem(self):
        e = emenda(S4)
        for t in ("não há assinatura que o modelo não possa forjar", "não traz assinatura", "informativo", "continua não atendida",
                  "validação da caixa de comandos", "escopo mínimo dos tokens"):
            self.assertIn(t, e, t)

    def test_s5_r3_r8_r13(self):
        e = emenda(S5)
        for t in ("não é assinado", "comandos/validados/", "recibo de mesmo hash", "token só do repositório entrada", "zapia_dados",
                  "credencial do fluxo", "nunca vão ao modelo", "s5-r13", "não interpreta o conteúdo", "relato do procedimento",
                  "autorrelato", "não guarda o arquivo", "só pela fila entrada", "para ao primeiro aviso", "não foi testada"):
            self.assertIn(t, e, t)
        self.assertIn("1 por dia e só com atividade concluída", e)

    def test_s9_r1_emendada_sem_aprovar_a_ordem_e_com_zapia_liberada(self):
        e = emenda(S9)
        for t in ("pela zapia, pedido pelo tutor ou pelo coach", "continua como alternativa", "não aprovou a ordem proposta",
                  "a zapia também está liberada", "s9-r5", "s9-r6", "s9-r8", "liberada pelo proprietário", "pontuação", "bloco procedimento",
                  "não aceita análise de conteúdo", "repositório privado", "(z1) não foi executado", "habilita as plataformas por padrão"):
            self.assertIn(t, e, t)

    def test_registro_diz_proposta_e_o_que_fica_de_fora(self):
        t = REG.lower().replace("**", "").replace("`", "")
        for trecho in ("proposta aguardando a revisão do proprietário", "pedido explícito dele", "não altera", "agents/", "e3",
                       "compartilhada por tutor e coach", "liberada", "não impõe condição prévia",
                       "não foi testada", "aditiva", "autorrelato"):
            self.assertIn(trecho, t, trecho)
        self.assertNotRegex(REG, r"\bPR\s*#\d+")
        self.assertNotRegex(REG, r"\b[0-9a-f]{40}\b")

    def test_nao_toca_product_agents_settings_nem_a_flag(self):
        product = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(product.encode("utf-8")), 38 * 1024)
        for nome in ("TUTOR.md", "COACH.md", "ZAPIA.md"):
            txt = (ROOT / "agents" / nome).read_text(encoding="utf-8")
            self.assertNotIn("pedir_relatorio", txt)  # a operação nova é a E3, com aprovação
        cfg = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(cfg["storage"]["personal_results_writes_enabled"], False)

    def test_sem_dado_pessoal_nem_numero_de_desempenho_nem_credencial(self):
        todo = S4 + S5 + S9 + REG
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", REG))
        self.assertNotRegex(emenda(S4) + emenda(S5) + emenda(S9), r"\b\d{1,3}\.\d{3}\b")  # nenhum total de questões, acertos ou erros
        self.assertNotRegex(todo, r"ghp_|github_pat_[A-Za-z0-9_]{10}|Bearer\s")

    def test_fila_tem_a_e2_com_escopo_e_a_entrega_existe(self):
        fila = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}
        self.assertEqual(fila["E2"]["deliverable"], "docs/governanca/E2_EMENDA_S5_S4R2_20261118.md")
        self.assertTrue((ROOT / fila["E2"]["deliverable"]).is_file())


if __name__ == "__main__":
    unittest.main()
