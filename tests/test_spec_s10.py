"""Contrato da S10: Notebook como ferramenta do Tutor. Ponte pela Zapia, rascunho, verificação, falha que fecha o efeito."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S10_NOTEBOOK_TUTOR.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "").replace("`", "")
PESQUISA = DOC.split("## Pesquisa", 1)[1].split("## Requisitos", 1)[0]
REQUISITOS = DOC.split("## Requisitos", 1)[1].split("## Tarefas derivadas", 1)[0]
FILA = json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]
SCHEMA = json.loads((ROOT / "config" / "agent_command_schema.json").read_text(encoding="utf-8"))


def req(n):
    return REQUISITOS.split(f"S10-R{n} ", 1)[1].split("| S10-R", 1)[0].lower().replace("**", "").replace("`", "")


class SpecS10Tests(unittest.TestCase):
    def test_requisitos_r1_a_r12_cada_um_com_criterio(self):
        linhas = [l for l in REQUISITOS.splitlines() if re.match(r"\| S10-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S10-R\d+) ", l).group(1) for l in linhas], [f"S10-R{i}" for i in range(1, 13)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        self.assertGreaterEqual(len(re.findall(r"https?://", PESQUISA)), 5)
        self.assertIn("- **Lacunas:**", PESQUISA)
        sem = PESQUISA.replace("**", "").lower()
        for trecho in ("não testei", "retenção", "não li", "nenhum deles trata de direito administrativo", "autorrelato",
                       "só pelo resumo", "open-05"):
            self.assertIn(trecho, sem, trecho)
        for nivel in ("**A**", "**B**", "**C**"):
            self.assertIn(nivel, PESQUISA)

    def test_fonte_oficial_citada_com_trechos_literais(self):
        for trecho in ("not used to train gemini notebook unless you provide feedback", "the full context of that interaction",
                       "in-line citations"):
            self.assertIn(trecho, PESQUISA.lower().replace("**", ""), trecho)

    def test_decisoes_do_proprietario_e_inversao_do_d12_registradas(self):
        for trecho in ("só pela zapia, como ponte", "lacunas declaradas", "inverte a prioridade do d-12", "e1", "18/11/2026"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_ponte_pela_zapia_sem_mcp_cookie_nem_credencial(self):
        r1 = req(1)
        for trecho in ("caminho único: ponte pela zapia", "mcp", "cookie", "credencial do google", "enviar_prompt_notebook", "notebook_estudo", "só executa o que está em validados"):
            self.assertIn(trecho, r1, trecho)
        for exato in ("nunca recebe credencial do google", "os conectores não oficiais não entram"):
            self.assertIn(exato, r1, exato)
        self.assertIn("enviar_prompt_notebook", SCHEMA["destinations"])
        self.assertEqual(SCHEMA["destinations"]["enviar_prompt_notebook"], "notebook_estudo")

    def test_papeis_do_d23(self):
        r2 = req(2)
        for trecho in ("tutor", "escreve o prompt e verifica", "só rascunho", "só transporta", "não gera nem edita", "rascunho fora do harness"):
            self.assertIn(trecho, r2, trecho)

    def test_prompt_minimo_com_proibicoes_e_limite_do_esquema(self):
        r3 = req(3)
        for trecho in ("tópico", "lacuna", "método", "exigência de fonte", "dado pessoal", "cpf", "credencial", "exportação bruta",
                       "captura de tela", "texto integral de questão", "2000 caracteres", "n2", "lacuna", "notebook_prompt_validator.py", "heurístico", "prompt_sha256", "caixa de comandos", "46 prompts adversariais"):
            self.assertIn(trecho, r3, trecho)
        self.assertEqual(SCHEMA["limits"]["max_param_string_chars"], 2000)

    def test_fontes_so_publicas_e_notebook_privado(self):
        for trecho in ("só texto público e oficial", "nunca entram como fonte", "exportação do tec", "insumo ainda ausente",
                       "o tutor não pede prompt"):
            self.assertIn(trecho, req(4), trecho)
        for trecho in ("privado", "sem compartilhamento por link", "autorizo g-share-off", "somente leitura"):
            self.assertIn(trecho, req(5), trecho)

    def test_resposta_e_dado_nao_confiavel_e_instrucao_embutida_so_relatada(self):
        r6 = req(6)
        for trecho in ("dado não confiável", "literal", "nunca é executada", "relatada", "não vai direto ao estudante"):
            self.assertIn(trecho, r6, trecho)

    def test_verificacao_por_citacao_aberta_antes_de_entregar(self):
        r7 = req(7)
        for trecho in ("abre ao menos uma citação", "confere", "página ou artigo", "excesso de confiança interpretativa", "verificado",
                       "entregue", "fica rascunho"):
            self.assertIn(trecho, r7, trecho)

    def test_privacidade_sem_feedback_e_sem_garantia_de_retencao(self):
        r8 = req(8)
        for trecho in ("não envia feedback", "revisar a interação inteira", "open-05", "não estão verificadas"):
            self.assertIn(trecho, r8, trecho)

    def test_falha_fecha_o_efeito_e_nao_a_orientacao(self):
        r9 = req(9)
        for trecho in ("não repete em laço", "avisa o proprietário", "10 prompts por dia", "primeiro aviso", "proposta", "não alterar"):
            self.assertIn(trecho, r9, trecho)

    def test_nada_provado_e_n1_exige_frases_e_contraprova_de_fidelidade(self):
        r11 = req(11)
        for trecho in ("não foram testados", "n1", "autorizo g-chat-1", "autorizo g-fonte-1", "prompt exato", "não consta nas fontes",
                       "nenhuma integração é declarada"):
            self.assertIn(trecho, r11, trecho)

    def test_cronograma_e_o_da_prova_a_confirmar(self):
        for trecho in ("o da prova no edital", "interpretação a confirmar", "não impõe cronograma"):
            self.assertIn(trecho, req(10), trecho)

    def test_honestidade_sobre_fidelidade(self):
        r12 = req(12)
        for trecho in ("reduz, não elimina", "13%", "direito administrativo", "obrigatória", "ci verde"):
            self.assertIn(trecho, r12, trecho)

    def test_nenhum_teste_real_nem_flag_nem_dado_pessoal_nem_credencial(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        self.assertNotRegex(DOC, r"ghp_|github_pat_|sk-[A-Za-z0-9]{20}|Bearer\s")
        self.assertIn("nenhum teste em conta real, na zapia ou no google", TEXTO)
        cfg = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(cfg["storage"]["personal_results_writes_enabled"], False)

    def test_derivadas_n1_n2_e1_e_nenhuma_criada_na_fila(self):
        derivadas = DOC.split("## Tarefas derivadas", 1)[1].split("## Aceite", 1)[0]
        for item in ("| N1 |", "| N2 |", "| E1 |"):
            self.assertIn(item, derivadas)
        ids = {i["id"] for i in FILA}
        self.assertNotIn("N1", ids)  # N1 é ato do proprietário (frases AUTORIZO); a N2 entrou na fila por decisão posterior dele
        # a N2 (validador offline do prompt) entrou na fila por decisão do proprietário e está entregue em scripts/
        self.assertTrue((ROOT / "scripts" / "notebook_prompt_validator.py").is_file())

    def test_aponta_para_a_rodada_6_e_o_arquivo_existe(self):
        self.assertIn("RESPOSTA_RODADA6_ZAPIA_20261117.md", DOC)
        self.assertTrue((ROOT / "docs" / "governanca" / "RESPOSTA_RODADA6_ZAPIA_20261117.md").is_file())


if __name__ == "__main__":
    unittest.main()
