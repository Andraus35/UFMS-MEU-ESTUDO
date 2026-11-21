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

    def test_ativacao_no_projeto_preserva_os_hooks_existentes_e_nada_mais_muda(self):
        h = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]
        stop = [x["command"] for g in h["Stop"] for x in g["hooks"]]
        self.assertTrue(any("perguntas_boas_praticas.py" in c for c in stop))  # os dois hooks Stop existentes continuam
        self.assertTrue(any("entrega_final.py" in c for c in stop))
        self.assertEqual(sum("claude_context_guard.py" in c for c in stop), 1)
        for ev in ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "PreCompact", "SessionEnd"):
            cmds = [x["command"] for g in h[ev] for x in g["hooks"]]
            ours = [c for c in cmds if "claude_context_guard.py" in c]
            self.assertEqual(len(ours), 1, ev)
            self.assertEqual(ours[0], f'python3 "$CLAUDE_PROJECT_DIR/scripts/claude_context_guard.py" {ev}')
            self.assertTrue(all(x.get("timeout") == 30 for g in h[ev] for x in g["hooks"] if "claude_context_guard.py" in x["command"]), ev)
        self.assertEqual(h["SessionStart"][0]["matcher"], "startup|resume|clear|compact")
        self.assertEqual(set(h), {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "PreCompact", "SessionEnd"})
        for caminho in ("AGENTS.md", "PRODUCT.md", "agents/TUTOR.md", "agents/COACH.md", "agents/ZAPIA.md", "settings.json"):
            self.assertNotIn("claude_context_guard", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        self.assertIn("e12-b (este lote, pr #158)", T)
        self.assertIn("aprovação expressa do texto e do merge", T)
        self.assertIn("nada vale na main", T)

    def test_config_do_projeto_e_segura_e_aponta_para_o_handoff(self):
        c = json.loads((ROOT / ".claude" / "context-guard.json").read_text(encoding="utf-8"))
        self.assertEqual(set(c), {"extra_instruction"})  # sem repo_copy, sem mudar limite
        e = c["extra_instruction"]
        for trecho in ("memory/HANDOFF.md", "bootstrap.py --mode engineering", "next_task.py", "nunca merge", "nunca push forçado",
                       "aprovação expressa", "confirmar no GitHub", "sem pedir permissão", "nunca na `main`"):
            self.assertIn(trecho, e, trecho)

    def test_doc_declara_riscos_da_ativacao(self):
        for trecho in ("três hooks stop no mesmo evento", "não foi testada em claude code real", "não há repo_copy no projeto",
                       "como desfazer", "falha aberto"):
            self.assertIn(trecho, T, trecho)

    def test_limites_honestos_declarados(self):
        for trecho in ("nenhum teste em claude code real", "percentual é estimativa", "conteúdo do prompt é redigido pelo modelo",
                       "commit e push não são feitos pelo hook", "hooks de usuário não existem em sessões na nuvem",
                       "falha do script é aberta", "conferir na prática antes de confiar"):
            self.assertIn(trecho, T, trecho)

    def test_codigo_sem_rede_e_sem_escrita_fora_do_esperado(self):
        for proibido in ("urllib", "requests", "socket", "http.client", "os.system", "shell=True", "git\", \"push", "git\", \"commit"):
            self.assertNotIn(proibido, CODE, proibido)
        usados = set(re.findall(r'git\((?:cwd|root|[a-z_]+), "([a-z-]+)"', CODE)) | set(re.findall(r'git\(cwd, "([a-z-]+)"', CODE))
        self.assertTrue(usados <= {"rev-parse", "status", "log", "symbolic-ref"}, usados)  # só leitura: nunca commit, push, reset ou checkout
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
