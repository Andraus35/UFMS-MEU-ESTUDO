"""Contrato dos roteiros do proprietário (lote C): P9, PJ, CM e reconciliação do 523. Só documentação; nada é executado."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governanca"
ROTEIROS = {
    "P9": GOV / "ROTEIRO_P9_RENOVAR_TOKENS_20261121.md",
    "PJ": GOV / "ROTEIRO_PJ_JANELA_PILOTO_20261121.md",
    "CM": GOV / "ROTEIRO_CM_CONTROLE_DE_MUDANCA_20261121.md",
    "523": GOV / "ROTEIRO_RECONCILIACAO_523_20261121.md",
}
TEXTO = {k: p.read_text(encoding="utf-8") for k, p in ROTEIROS.items()}


def t(k):
    return TEXTO[k].lower().replace("**", "").replace("`", "")


class RoteirosTests(unittest.TestCase):
    def test_existem_e_declaram_que_a_sessao_nao_executa(self):
        for k, p in ROTEIROS.items():
            self.assertTrue(p.is_file(), k)
        for k in ("P9", "PJ", "CM", "523"):
            self.assertRegex(t(k), r"a sessão não [^.]*(executa|consulta)", k)
            self.assertIn("## limites", t(k), k)

    def test_sem_segredo_email_ou_token_real(self):
        for k, s in TEXTO.items():
            self.assertNotRegex(s, r"ghp_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9]", k)
            self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", s), k)

    def test_scripts_citados_existem_exceto_o_rt_declarado_ausente(self):
        for k, s in TEXTO.items():
            for caminho in set(re.findall(r"`((?:scripts|docs|tests|config)/[\w./-]+)`", s)):
                if caminho == "scripts/termux/piloto.sh":
                    self.assertIn("ainda não existe", t(k))  # o RT depende da PJ e é declarado ausente
                    continue
                self.assertTrue((ROOT / caminho).exists(), f"{k}: {caminho}")

    def test_p9_tokens_escopo_validade_e_sem_valor_no_chat(self):
        s = t("P9")
        for trecho in ("zapia_dados", "zapia token", "ufms-meu-estudo-dados", "ufms-meu-estudo-entrada", "contents: read and write",
                       "mais de 8 dias", "04/12/2026", "18/12/2026", "substituir_segredo=1", "revogar os tokens antigos",
                       "nunca vai ao chat", "formulário seguro", "p9 feita:"):
            self.assertIn(trecho, s, trecho)
        self.assertLess(s.index("gerar o novo `zapia_dados`".replace("`", "")), s.index("revogar os tokens antigos"))  # revoga depois de conferir

    def test_pj_sequencia_frases_e_o_que_nao_vale(self):
        s = t("PJ")
        for trecho in ("--modo abertura", "--modo pos_janela", "--modo repouso", "atualizar", "24 h", "citando pr e head",
                       "o atalho \"mesclar\" não vale", "mesclar sem reinstalar não desliga", "personal_results_writes_enabled",
                       "private_flow_promotion_enabled", "ciclo funciona uma vez", "não prova utilidade pedagógica",
                       "aprovo a janela do piloto", "ainda não existe", "04/12/2026"):
            self.assertIn(trecho, s, trecho)
        self.assertIn("a flag `personal_results_writes_enabled` fica `false`".replace("`", ""), s)
        pos = [s.index(p) for p in ("pré-voo de abertura", "aprovação expressa", "pr de janela", "reinstalar o fluxo no sha do merge da janela",
                                    "pré-voo pós-janela", "pr de fechamento", "pré-voo de repouso")]
        self.assertEqual(pos, sorted(pos))

    def test_cm_identidade_impasse_e_limites(self):
        s = t("CM")
        for trecho in ("require review from code owners", "indistinguível", "não pode aprovar o próprio pr", "usuário-máquina", "github app",
                       "0 aprovações gerais", "protect_main.py --plan", "relato seu", "não sei", "e9", "aprovo o texto e o merge"):
            self.assertIn(trecho, s, trecho)

    def test_523_nao_estima_nao_versiona_e_nao_escolhe_numero(self):
        s = t("523")
        for trecho in ("137", "187", "não definitivo", "pendencia_aberta", "sem alterar nenhum caderno", "só leitura", "mesmos filtros",
                       "outro dia", "não use média nem escolha o maior", "não escolha", "versiona número", "autorrelato", "retificações do edital continuam não conferidas",
                       "declaro definitivo"):
            self.assertIn(trecho, s, trecho)
        self.assertNotRegex(TEXTO["523"], r"\d{1,3}(?:[.,]\d+)?\s?%")  # nenhum percentual
        # a Zapia está liberada (D-27): nenhuma restrição reintroduzida; a regressão geral está em test_sem_restricoes_de_acesso
        self.assertNotIn("autorizo tec", s)
        self.assertNotRegex(s, r"\bcota\b")

    def test_flags_continuam_falsas_e_roteiros_nao_mudam_contrato(self):
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"personal_results_writes_enabled":\s*false')
        self.assertRegex((ROOT / "settings.json").read_text(encoding="utf-8"), r'"private_flow_promotion_enabled":\s*false')
        for caminho in ("AGENTS.md", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md"):
            self.assertNotIn("ROTEIRO_", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
