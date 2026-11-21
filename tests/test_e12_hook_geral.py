"""Contrato do registro E12 (hook geral): código fora de contrato, ativação no projeto só como proposta, limites honestos."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs" / "governanca" / "E12_HOOK_GERAL_PASSAGEM_ENTRE_SESSOES.md").read_text(encoding="utf-8")
T = DOC.lower().replace("**", "").replace("`", "")
CODE = (ROOT / "scripts" / "claude_context_guard.py").read_text(encoding="utf-8")


class E12Tests(unittest.TestCase):
    def test_arquivos_citados_existem(self):
        for caminho in set(re.findall(r"`((?:scripts|tests)/[\w./-]+)`", DOC)):
            self.assertTrue((ROOT / caminho).is_file(), caminho)

    def test_nao_ativa_nada_no_projeto(self):
        for caminho in (".claude/settings.json", "AGENTS.md", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md", "settings.json"):
            self.assertNotIn("claude_context_guard", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertIn("este pr não ativa nada no projeto", T)
        self.assertIn("não aplicada neste pr", T)
        self.assertIn("aprovação expressa do texto e do merge", T)

    def test_limites_honestos_declarados(self):
        for trecho in ("nenhum teste em claude code real", "percentual é estimativa", "conteúdo do prompt é redigido pelo modelo",
                       "commit e push não são feitos pelo hook", "hooks de usuário não existem em sessões na nuvem",
                       "falha do script é aberta", "conferir na prática antes de confiar"):
            self.assertIn(trecho, T, trecho)

    def test_exemplo_de_ativacao_e_json_valido(self):
        bloco = re.search(r"```json\n(.*?)```", DOC, re.S).group(1)
        h = json.loads(bloco)["hooks"]["UserPromptSubmit"][0]["hooks"][0]
        self.assertEqual(h["type"], "command")
        self.assertIn("scripts/claude_context_guard.py", h["command"])

    def test_codigo_sem_rede_e_sem_escrita_fora_do_esperado(self):
        for proibido in ("urllib", "requests", "socket", "http.client", "os.system", "shell=True", "git\", \"push", "git\", \"commit"):
            self.assertNotIn(proibido, CODE, proibido)
        usados = set(re.findall(r'git\((?:cwd|root|[a-z_]+), "([a-z-]+)"', CODE)) | set(re.findall(r'git\(cwd, "([a-z-]+)"', CODE))
        self.assertTrue(usados <= {"rev-parse", "status", "log"}, usados)  # só leitura: nunca commit, push, reset ou checkout
        self.assertTrue(usados, "o teste não achou nenhuma chamada git")

    def test_valores_padrao_do_enunciado(self):
        self.assertIn('"threshold": 0.5', CODE)
        for secao in ("## Primeiro passo", "## Estado", "## Pendências"):
            self.assertIn(secao, CODE)

    def test_item_da_fila_aponta_para_este_registro(self):
        fila = {i["id"]: i for i in json.loads((ROOT / "state" / "WORKFLOW.json").read_text(encoding="utf-8"))["work_queue"]}
        self.assertEqual(fila["HOOKG"]["deliverable"], "docs/governanca/E12_HOOK_GERAL_PASSAGEM_ENTRE_SESSOES.md")


if __name__ == "__main__":
    unittest.main()
