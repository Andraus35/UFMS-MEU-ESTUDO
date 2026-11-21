"""Contrato do hook Stop de perguntas de fim de rodada (.claude/settings.json + script). Offline, sem rede."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / ".claude" / "settings.json"
SCRIPT = ROOT / ".claude" / "hooks" / "perguntas_boas_praticas.py"


def usuario(texto="faça algo"):
    return json.dumps({"type": "user", "message": {"role": "user", "content": texto}})


def resultado_de_ferramenta():
    return json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}})


def uso(nome, entrada=None):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": nome, "input": entrada or {}}]}})


def bash(comando):
    return uso("Bash", {"command": comando})


def texto(t="só conversa"):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}})


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))

    def test_so_o_hook_stop_e_nada_mais(self):
        self.assertEqual(set(self.cfg), {"hooks"})  # sem permissions, env, plugins, modelo etc. (decisão do proprietário)
        # E12-B: o hook geral de passagem entre sessões (claude_context_guard) acrescenta eventos; o conjunto é fechado e testado em test_e12_hook_geral
        self.assertEqual(set(self.cfg["hooks"]), {"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "PreCompact", "SessionEnd"})

    def test_um_unico_hook_de_comando_que_chama_o_script_versionado(self):
        grupos = self.cfg["hooks"]["Stop"]
        self.assertEqual(len(grupos), 2)  # o grupo original (perguntas e entrega final) e o do hook geral (E12-B)
        self.assertIn("claude_context_guard.py", grupos[1]["hooks"][0]["command"])
        hooks = grupos[0]["hooks"]
        self.assertEqual(len(hooks), 2)  # o de perguntas e o de entrega final (até 20/11/2026)
        h = hooks[0]
        self.assertEqual(h["type"], "command")
        self.assertIn('"$CLAUDE_PROJECT_DIR/.claude/hooks/perguntas_boas_praticas.py"', h["command"])
        self.assertTrue(SCRIPT.is_file())
        self.assertLessEqual(h["timeout"], 30)
        self.assertNotIn("async", h)  # precisa ser síncrono para poder bloquear

    def test_sem_segredo_nem_rede_no_registro(self):
        bruto = SETTINGS.read_text(encoding="utf-8")
        for proibido in ("http://", "https://", "curl", "wget", "token", "secret", "senha", "ghp_", "github_pat_", "||", ">/dev/null"):
            self.assertNotIn(proibido, bruto)

    def test_hook_nao_foi_removido_ou_desativado_por_arquivo_irmao(self):
        self.assertNotIn("disableAllHooks", SETTINGS.read_text(encoding="utf-8"))


class ScriptTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def rodar(self, linhas, ativo=False, projeto=ROOT, bruto=None):
        arquivo = self.dir / "t.jsonl"
        arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        entrada = bruto if bruto is not None else json.dumps({"transcript_path": str(arquivo), "stop_hook_active": ativo})
        r = subprocess.run([sys.executable, str(SCRIPT)], input=entrada, capture_output=True, text=True, timeout=30,
                           env={**os.environ, "CLAUDE_PROJECT_DIR": str(projeto)})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def assertBloqueia(self, saida):
        self.assertIsNotNone(saida)
        self.assertEqual(saida["decision"], "block")
        return saida["reason"]

    def test_entrega_sem_pergunta_bloqueia_com_a_sequencia_e_o_estado(self):
        motivo = self.assertBloqueia(self.rodar([usuario(), bash("git push origin x")]))
        self.assertIn("AskUserQuestion", motivo)
        self.assertIn("PRÓXIMA", motivo)
        ordem = [motivo.index(t) for t in ("PENDÊNCIAS", "ROADMAP", "FILA")]
        self.assertEqual(ordem, sorted(ordem))  # pendências, depois roadmap, depois fila
        self.assertIn("(Recomendado)", motivo)
        self.assertIn("Estado lido agora:", motivo)  # veio de scripts/next_task.py do projeto

    def test_cada_tipo_de_entrega_dispara(self):
        casos = [bash("git commit -m x"), bash("git push -u origin b"), bash("cd /x && git add -A && git commit -q -m y && git push"),
                 bash("(git commit -m z)"), uso("mcp__github__create_pull_request"), uso("mcp__github__merge_pull_request"),
                 uso("mcp__github__push_files"), uso("mcp__github__create_or_update_file"), uso("mcp__github__update_pull_request"),
                 uso("mcp__github__delete_file")]
        for caso in casos:
            self.assertBloqueia(self.rodar([usuario(), caso]))

    def test_conversa_comum_e_leitura_nao_bloqueiam(self):
        self.assertIsNone(self.rodar([usuario(), texto()]))
        self.assertIsNone(self.rodar([usuario(), uso("Read", {"file_path": "/x"}), bash("git status"), bash("git log --oneline"),
                                      bash("git diff"), uso("mcp__github__pull_request_read"), texto()]))

    def test_texto_que_apenas_cita_git_push_nao_e_entrega(self):
        self.assertIsNone(self.rodar([usuario(), bash('echo "teste git push origin x" > /dev/null'), texto("vou fazer git push depois")]))
        self.assertIsNone(self.rodar([usuario(), bash("grep -n 'git commit' arquivo.txt")]))

    def test_pergunta_neste_turno_libera(self):
        self.assertIsNone(self.rodar([usuario(), bash("git push"), uso("AskUserQuestion"), resultado_de_ferramenta(), texto()]))

    def test_pergunta_em_turno_antigo_nao_libera_a_entrega_nova(self):
        self.assertBloqueia(self.rodar([usuario("turno 1"), uso("AskUserQuestion"), usuario("turno 2"), bash("git push")]))

    def test_entrega_em_turno_antigo_nao_dispara_no_turno_de_conversa(self):
        self.assertIsNone(self.rodar([usuario("turno 1"), bash("git push"), usuario("turno 2"), texto("resposta")]))

    def test_resultado_de_ferramenta_nao_conta_como_novo_pedido_do_usuario(self):
        self.assertBloqueia(self.rodar([usuario(), bash("git commit -m a"), resultado_de_ferramenta(), texto()]))

    def test_mensagem_de_subagente_nao_reinicia_o_turno(self):
        subagente = json.dumps({"type": "user", "isSidechain": True, "message": {"role": "user", "content": "prompt do subagente"}})
        self.assertBloqueia(self.rodar([usuario(), bash("git push"), subagente, texto()]))

    def test_trava_contra_laco(self):
        self.assertIsNone(self.rodar([usuario(), bash("git push")], ativo=True))

    def test_falha_aberta_em_entrada_ruim(self):
        for bruto in ("lixo", "", "{}", '{"transcript_path": "/nao/existe.jsonl"}', '{"transcript_path": 5}', "[]", "null"):
            self.assertIsNone(self.rodar([usuario()], bruto=bruto), bruto)

    def test_linhas_invalidas_no_transcript_nao_derrubam(self):
        self.assertBloqueia(self.rodar([usuario(), "nao e json", bash("git push"), "{"]))

    # E13: só o que mudou
    def feedback(self):
        motivo = self.assertBloqueia(self.rodar([usuario(), bash("git push")]))
        return "Stop hook feedback:\n" + motivo, motivo

    def test_mesmo_estado_ja_perguntado_nao_bloqueia_de_novo(self):
        feedback, _ = self.feedback()
        self.assertIsNone(self.rodar([usuario(feedback), uso("AskUserQuestion"), usuario("outro pedido"), bash("git push")]))

    def test_mesmo_estado_sem_pergunta_depois_bloqueia(self):
        feedback, _ = self.feedback()
        self.assertBloqueia(self.rodar([usuario(feedback), usuario("outro pedido"), bash("git push")]))

    def test_pergunta_ANTES_do_aviso_nao_conta(self):
        feedback, _ = self.feedback()
        self.assertBloqueia(self.rodar([uso("AskUserQuestion"), usuario(feedback), usuario("outro pedido"), bash("git push")]))
        self.assertBloqueia(self.rodar([usuario("a"), texto(), uso("AskUserQuestion"), usuario(feedback), usuario("outro pedido"), bash("git push")]))

    def test_estado_mudou_bloqueia_e_mostra_o_que_mudou(self):
        antigo = "Estado lido agora: ciclo da tarefa RM-00 (PR #1) em 'em_andamento'; próximo item da fila: X — antigo."
        motivo = self.assertBloqueia(self.rodar([usuario("Stop hook feedback:\nFim de rodada. " + antigo), uso("AskUserQuestion"),
                                                  usuario("outro pedido"), bash("git push")]))
        self.assertIn("O que mudou desde a última pergunta:", motivo)
        self.assertIn("ciclo da tarefa RM-00 (PR #1)", motivo)  # o antes
        self.assertIn("Estado lido agora:", motivo)  # e o agora (estado real do projeto)

    def test_aviso_em_bloco_de_texto_tambem_e_lido(self):
        feedback, _ = self.feedback()
        linha = json.dumps({"type": "user", "message": {"content": [{"type": "text", "text": feedback}]}})
        self.assertIsNone(self.rodar([linha, uso("AskUserQuestion"), usuario("outro pedido"), bash("git push")]))

    def test_sem_historico_ou_sem_estado_legivel_pergunta_como_antes(self):
        self.assertBloqueia(self.rodar([usuario(), bash("git push")]))
        feedback, _ = self.feedback()
        # projeto sem scripts/next_task.py: não há como comparar, então pergunta
        self.assertBloqueia(self.rodar([usuario(feedback), uso("AskUserQuestion"), usuario("x"), bash("git push")], projeto=self.dir))

    def test_o_hook_continua_so_lendo(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        for proibido in (".write_text(", "write_bytes(", ".mkdir(", "os.remove", "shutil"):
            self.assertNotIn(proibido, fonte, proibido)

    def test_estado_indisponivel_nao_impede_o_bloqueio(self):
        motivo = self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=self.dir))  # sem scripts/next_task.py
        self.assertNotIn("Estado lido agora:", motivo)
        self.assertIn("AskUserQuestion", motivo)

    def test_saida_e_so_json_de_bloqueio(self):
        arquivo = self.dir / "t.jsonl"
        arquivo.write_text(usuario() + "\n" + bash("git push") + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps({"transcript_path": str(arquivo)}),
                           capture_output=True, text=True, timeout=30, env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)})
        self.assertEqual(set(json.loads(r.stdout)), {"decision", "reason"})
        self.assertEqual(r.stderr, "")


class FronteirasTest(unittest.TestCase):
    def test_script_nao_usa_rede_nem_grava_nem_le_segredo(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("import requests", "urllib", "socket", "http.client", ".write_text(", "write_bytes(", "os.environ[",
                         "GH_TOKEN", "DADOS_TOKEN", "shell=True", "eval(", "exec("):
            self.assertNotIn(proibido, fonte)
        self.assertIsNone(re.search(r"open\([^)]*['\"][wax]", fonte))  # nenhuma abertura para escrita
        self.assertEqual(fonte.count("subprocess.run("), 1)  # só scripts/next_task.py, com tempo limite
        self.assertIn("timeout=10", fonte)

    def test_ordem_da_sequencia_esta_no_texto_do_bloqueio(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        ordem = [fonte.index(t) for t in ("(1) PENDÊNCIAS", "(2) ROADMAP", "(3) FILA")]
        self.assertEqual(ordem, sorted(ordem))

    def test_texto_do_bloqueio_segue_a_regra_de_lote_do_agents(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        compacta = re.sub(r"\"\s*\n\s*\"", "", fonte)
        for trecho in ("Um lote por vez", "micro tarefas coesas da mesma frente no mesmo PR", "outra frente, o merge vem antes"):
            self.assertIn(trecho, compacta)
        self.assertNotIn("Uma tarefa por vez", fonte)  # a regra antiga foi substituída pela de lote (AGENTS.md, 21/11/2026)


if __name__ == "__main__":
    unittest.main()
