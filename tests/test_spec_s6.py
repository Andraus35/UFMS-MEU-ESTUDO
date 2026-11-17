"""Contrato da S6: execução na nuvem, três fronteiras, portão em código, origem não provada e consentimento v4."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "especificacoes" / "S6_EXECUCAO_CANAL.md").read_text(encoding="utf-8")
TEXTO = DOC.lower().replace("**", "")


class SpecS6Tests(unittest.TestCase):
    def test_requisitos_r1_a_r13_cada_um_com_criterio(self):
        linhas = [l for l in DOC.splitlines() if re.match(r"\| S6-R\d+ \|", l)]
        self.assertEqual([re.match(r"\| (S6-R\d+) ", l).group(1) for l in linhas], [f"S6-R{i}" for i in range(1, 14)])
        for l in linhas:
            self.assertGreaterEqual(len([c for c in l.split("|") if c.strip()]), 3, l[:30])

    def test_decisoes_do_proprietario_e_emendas_registradas(self):
        for trecho in ("não quero nada manual e local", "sessões do app claude na nuvem", "fila no repositório privado e validação por github actions",
                       "a zapia entrega o dado na fila", "esperar a automação", "emendam o d-18", "d-02", "tarefa e1"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_tres_fronteiras_e_so_o_fluxo_escreve_no_historico(self):
        for trecho in ("ufms-meu-estudo-entrada", "ufms-meu-estudo-dados", "só o fluxo", "só acrescentando", "preventiva", "forks desabilitados"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_portao_em_ordem_e_flag_falsa_nao_promove_nada(self):
        portao = TEXTO.split("s6-r4", 1)[1].split("s6-r5", 1)[0]
        ordem = ["forma e tamanho", "esquema do evento", "filtro de dado pessoal", "p2", "p1", "p3", "a flag", "idempotência", "p6"]
        pos = [portao.index(o) for o in ordem]
        self.assertEqual(pos, sorted(pos))
        self.assertIn("falsa ⇒ nada é promovido", portao)

    def test_origem_nao_e_provada_e_nao_ha_chave_no_modelo(self):
        for trecho in ("a origem tutor ou coach não é provada criptograficamente", "limita o dano", "informativo", "s4-r2",
                       "nenhuma chave ou token chega ao modelo"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_credenciais_separadas_e_token_zapia_dados_vira_credencial_do_fluxo(self):
        for trecho in ("só `entrada`", "só `dados`", "30 dias", "zapia_dados", "credencial do fluxo", "workflows", "segredo do repositório"):
            self.assertIn(trecho, TEXTO.replace("`", "`"), trecho)
        self.assertNotRegex(DOC, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")

    def test_consentimento_v4_para_o_app_claude_e_revogacao_com_data(self):
        for trecho in ("consentimento v4", "o app claude processa dado pessoal", "somente leitura", "16/02/2027", "os dois privados guardam dado pessoal"):
            self.assertIn(trecho, TEXTO, trecho)

    def test_pesquisa_com_links_confianca_e_lacunas_honestas(self):
        pesquisa = DOC.split("## Pesquisa", 1)[1].split("## Plano", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"https?://", pesquisa)), 8)
        self.assertIn("- **Lacunas:**", pesquisa)
        for trecho in ("nenhum desenho foi testado", "não confirmei", "sessões agendadas", "não consultei jurista"):
            self.assertIn(trecho, pesquisa.replace("**", ""))

    def test_nao_altera_contrato_nem_habilita_escrita_e_item_da_fila(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertIn("rodam no computador do proprietário", (ROOT / "PRODUCT.md").read_text(encoding="utf-8"))  # D-18 segue até a E1
        for caminho in ("agents/TUTOR.md", "agents/COACH.md", "AGENTS.md"):
            self.assertNotIn("S6_EXECUCAO", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", DOC))
        item = next(i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"] if i["id"] == "S6")
        self.assertTrue((ROOT / item["deliverable"]).exists())


if __name__ == "__main__":
    unittest.main()
