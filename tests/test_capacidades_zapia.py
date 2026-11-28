"""Leitura obrigatória das capacidades da Zapia (decisão do proprietário de 22/11/2026): o START imprime o resumo e o hash, falha fechado se o registro
sumir, e o HANDOFF aponta para ele. Protege o registro contra remoção e contra afirmação além da prova (sem conector de GitHub; F1 e rotina NÃO provados)."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import bootstrap  # noqa: E402

DOC = ROOT / bootstrap.CAPACIDADES_ZAPIA


class RegistroTeste(unittest.TestCase):
    def test_o_registro_existe_e_diz_o_que_esta_provado_e_o_que_nao_esta(self):
        t = DOC.read_text(encoding="utf-8")
        for trecho in ("PROVADO (22/11/2026", "NÃO precisa de conector de GitHub", "HTTP com token", "-X`, `-H` e `-d`", "NÃO PROVADO",
                       "rotina agendada", "notificação espontânea", "F1", "NÃO executa o Python do repositório", "Requested, not filled in by the user",
                       "AUTORIZO rotina automática agora"):
            self.assertIn(trecho, t, trecho)

    def test_o_resumo_traz_a_prova_da_rotina_as_licoes_e_o_que_nao_esta_provado(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("PROVADO (23/11/2026, E23", "dispararam sozinhas", "traduziu `comandos` para `commands`", "github_ufms_repo_token", "em inglês",
                       "relato de cada chamada", "de hora em hora, das 06h às 22h", "uma rotina crie outra", "ZAPIA-F3", "sem a frase `AUTORIZO`"):
            self.assertIn(trecho, r, trecho)
        self.assertNotIn("a **rotina agendada** da Zapia;", r)  # a versão antiga do NÃO PROVADO, superada pelo E23

    def test_o_resumo_guarda_o_limite_de_4000_caracteres_da_tarefa_do_hook(self):
        import agendar_rotina
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("LIMITE OBSERVADO (25/11/2026", "no máximo 4000 caracteres", "String should have at most 4000 characters", "LIMITE_TAREFA_HOOK = 4000",
                       "não foi medido"):
            self.assertIn(trecho, r, trecho)
        self.assertEqual(agendar_rotina.LIMITE_TAREFA_HOOK, 4000)  # o registro e o código dizem o mesmo número
        self.assertEqual(agendar_rotina.LIMITE_TAREFA_HOOK, int(__import__("re").search(r"LIMITE_TAREFA_HOOK = (\d+)", r).group(1)))

    def test_o_resumo_guarda_a_recusa_de_hook_identico(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("RESTRIÇÃO OBSERVADA (25/11/2026", "An identical subscription already exists: 2bef6d04-e272-4b25-b9b9-4d44958cfd73",
                       "the user decides", "atualize", "não foi testada", "a escolha é do proprietário"):
            self.assertIn(trecho, r, trecho)

    def test_o_resumo_guarda_a_parada_do_hook_na_conferencia_do_hash(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("issue #8", "PAROU na conferência do SHA-256", "O arquivo do `entrada` está íntegro", "a32afe90", "ensure_ascii=False",
                       "não manda mais a Zapia calcular hash", "pula", "consome o disparo"):
            self.assertIn(trecho, r, trecho)

    def test_o_resumo_guarda_as_duas_contas_da_zapia_na_engenharia_e_o_gmail_em_outra_conta(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("DECISÃO DO PROPRIETÁRIO (27/11/2026", "autorizadas e são intercambiáveis na fase de engenharia", "andraus.dev@gmail.com",
                       "um hook ENG ativo por vez", "estende nenhuma prova",
                       "OBSERVADO (27/11/2026, E49", "recebidos por outra conta Zapia", "não dispararia", "Não testado"):
            self.assertIn(trecho, r, trecho)

    def test_o_resumo_guarda_a_primeira_ativacao_do_hook_eng_e_a_licao_do_assunto(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("9f622bbf", "assunto fora do padrao", "(Issue #N)", "começa com", "idêntico", "Não provado:** recorrência"):
            self.assertIn(trecho, r, trecho)

    def test_o_resumo_guarda_a_primeira_rodada_completa_do_canal_e_o_erro_de_copia_do_hash(self):
        r = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"])
        for trecho in ("OBSERVADO (28/11/2026, E49", "sem o proprietário colar prompt", "errou **1 caractere**", "HASH_NAO_CONFERE", "16 caracteres", "notebook_renomear", "eng-0002", "conferiu", "eng-0003", "eng-0004", "646 caracteres", "eng-0005", "primeira resposta com conteúdo ACEITA", "4 acertos em 4", "eng-0006", "item `motivo`"):
            self.assertIn(trecho, r, trecho)

    def test_o_registro_nao_promove_o_que_nao_foi_provado(self):
        resumo = "\n".join(bootstrap.capacidades_zapia(ROOT)["resumo"]).lower()
        self.assertNotIn("rotina agendada provada", resumo)
        self.assertNotIn("notificação espontânea provada", resumo)
        self.assertIn("não provado", resumo)

    def test_o_hand_off_aponta_para_o_registro(self):
        h = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("LEITURA OBRIGATÓRIA: capacidades da Zapia", h)
        self.assertIn("docs/governanca/CAPACIDADES_ZAPIA_VERIFICADAS.md", h)


class StartTeste(unittest.TestCase):
    def test_start_de_estudo_e_de_engenharia_trazem_resumo_e_hash(self):
        for modo in ("study", "engineering"):
            r = bootstrap.run(ROOT, modo)["capacidades_zapia"]
            self.assertEqual(r["sha256"], hashlib.sha256(DOC.read_bytes()).hexdigest(), modo)
            self.assertEqual(r["leitura"], "OBRIGATORIA em toda sessao")
            self.assertTrue(any("PROVADO" in linha for linha in r["resumo"]), modo)

    def test_sem_o_registro_ou_sem_as_marcas_o_start_falha_fechado(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)
        (tmp / "docs" / "governanca").mkdir(parents=True)
        (tmp / bootstrap.CAPACIDADES_ZAPIA).write_text("sem marcas", encoding="utf-8")
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)
        (tmp / bootstrap.CAPACIDADES_ZAPIA).write_text("<!-- RESUMO-START -->\n\n<!-- RESUMO-END -->", encoding="utf-8")
        with self.assertRaises(ValueError):
            bootstrap.capacidades_zapia(tmp)

    def test_o_hash_muda_se_o_registro_mudar(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "docs" / "governanca").mkdir(parents=True)
        p = tmp / bootstrap.CAPACIDADES_ZAPIA
        p.write_text("<!-- RESUMO-START -->\nA\n<!-- RESUMO-END -->", encoding="utf-8")
        h1 = bootstrap.capacidades_zapia(tmp)["sha256"]
        p.write_text("<!-- RESUMO-START -->\nB\n<!-- RESUMO-END -->", encoding="utf-8")
        self.assertNotEqual(h1, bootstrap.capacidades_zapia(tmp)["sha256"])


if __name__ == "__main__":
    unittest.main()
