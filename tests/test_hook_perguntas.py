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

    def rodar(self, linhas, ativo=False, projeto=ROOT, bruto=None, sessao=None):
        arquivo = self.dir / "t.jsonl"
        arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        dados = {"transcript_path": str(arquivo), "stop_hook_active": ativo}
        if sessao:
            dados["session_id"] = sessao
        entrada = bruto if bruto is not None else json.dumps(dados)
        r = subprocess.run([sys.executable, str(SCRIPT)], input=entrada, capture_output=True, text=True, timeout=30,
                           env={**os.environ, "CLAUDE_PROJECT_DIR": str(projeto), "CONTEXT_GUARD_HOME": str(self.dir / "home")})
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

    # E13: o hook de passagem entre sessões prevalece sobre as perguntas de continuidade
    def estado_do_guard(self, sessao="sx", **campos):
        d = self.dir / "home" / ".claude" / "context-guard" / "state"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sessao}.json").write_text(json.dumps(campos), encoding="utf-8")

    def test_passou_do_limite_com_lote_finalizado_nao_propoe_continuidade(self):
        self.estado_do_guard(armed_at=1.0, sealed=True, lote_pendente=False)
        self.assertIsNone(self.rodar([usuario(), bash("git push origin x")], sessao="sx"))

    def test_passou_do_limite_mas_sem_selo_tambem_cede_ao_guard(self):
        self.estado_do_guard(armed_at=1.0, lote_pendente=False)  # o guard bloqueia por conta própria; as perguntas não competem
        self.assertIsNone(self.rodar([usuario(), bash("git push")], sessao="sx"))

    def test_lote_pendente_tambem_cede_pois_o_guard_obriga_a_persistir_sem_perguntas(self):
        self.estado_do_guard(armed_at=1.0, sealed=True, lote_pendente=True)
        self.assertIsNone(self.rodar([usuario(), bash("git push")], sessao="sx"))

    def test_sem_limite_ultrapassado_ou_sem_estado_ou_ilegivel_pergunta_como_antes(self):
        self.estado_do_guard(sessao="a", pct=0.2)  # não armado
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], sessao="a"))
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], sessao="inexistente"))
        self.assertBloqueia(self.rodar([usuario(), bash("git push")]))  # sem session_id
        d = self.dir / "home" / ".claude" / "context-guard" / "state"
        (d / "ruim.json").write_text("{quebrado")
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], sessao="ruim"))

    def test_lote_finalizado_sem_o_limite_ter_sido_ultrapassado_nao_cede(self):
        self.estado_do_guard(lote_pendente=False, pct=0.3)  # sem armed_at: o contexto não passou do limite
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], sessao="sx"))

    def test_estado_de_outra_sessao_nao_vale(self):
        self.estado_do_guard(sessao="outra", armed_at=1.0, sealed=True, lote_pendente=False)
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], sessao="sx"))

    def test_estado_antigo_sem_lote_pendente_mas_armado_cede(self):
        self.estado_do_guard(armed_at=1.0, sealed=True)
        self.assertIsNone(self.rodar([usuario(), bash("git push")], sessao="sx"))

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


class PersistenciaEntreSessoesTest(ScriptTest):
    """E53 (opção B): o estado perguntado e as respostas vivem no repositório e atravessam sessões."""

    def projeto_com(self, estado, entradas=True):
        proj = self.dir / "proj"
        (proj / "scripts").mkdir(parents=True, exist_ok=True)
        (proj / "scripts" / "next_task.py").write_text(
            "import json\nprint(json.dumps({'ciclo':{'tarefa':'RM-09','pr':1,'estado':'e'},'fila':{'proximo':{'id':'X','titulo':'t'}}}))\n",
            encoding="utf-8")
        if entradas is not None:
            (proj / "memory").mkdir(exist_ok=True)
            (proj / "memory" / "PERGUNTAS.json").write_text(
                json.dumps({"versao": 1, "entradas": [{"estado": estado, "respostas": ["a: b"]}] if entradas else []}), encoding="utf-8")
        return proj

    ATUAL = "Estado lido agora: ciclo da tarefa RM-09 (PR #1) em 'e'; próximo item da fila: X — t."

    def test_sessao_nova_com_mesmo_estado_registrado_nao_repete(self):
        self.assertIsNone(self.rodar([usuario(), bash("git push")], projeto=self.projeto_com(self.ATUAL)))

    def test_estado_registrado_diferente_bloqueia_e_mostra_o_que_mudou(self):
        antigo = "Estado lido agora: ciclo da tarefa RM-00 (PR #9) em 'x'; próximo item da fila: Z — velho."
        motivo = self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=self.projeto_com(antigo)))
        self.assertIn("O que mudou desde a última pergunta:", motivo)
        self.assertIn("RM-00 (PR #9)", motivo)

    def test_arquivo_ausente_vazio_ou_corrompido_pergunta_como_antes(self):
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=self.projeto_com(self.ATUAL, entradas=None)))
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=self.projeto_com(self.ATUAL, entradas=False)))
        proj = self.projeto_com(self.ATUAL)
        (proj / "memory" / "PERGUNTAS.json").write_text("{nao e json", encoding="utf-8")
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=proj))

    def test_estado_registrado_sem_o_prefixo_nao_vale(self):
        self.assertBloqueia(self.rodar([usuario(), bash("git push")], projeto=self.projeto_com("qualquer coisa")))

    def test_motivo_manda_registrar_as_respostas_no_repositorio(self):
        motivo = self.assertBloqueia(self.rodar([usuario(), bash("git push")]))
        self.assertIn("scripts/registrar_perguntas.py", motivo)
        self.assertIn("memory/PERGUNTAS.json", motivo)


class RegistrarPerguntasTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        sys.path.insert(0, str(ROOT / "scripts"))
        self.addCleanup(sys.path.remove, str(ROOT / "scripts"))
        import registrar_perguntas as rp
        self.rp = rp
        self.estado = PersistenciaEntreSessoesTest.ATUAL

    def lido(self):
        return json.loads((self.raiz / "memory" / "PERGUNTAS.json").read_text(encoding="utf-8"))

    def test_grava_estado_e_respostas_e_o_hook_o_le(self):
        self.rp.registrar(self.raiz, ["Próximo: N1 (Recomendado)"], estado=self.estado, agora="2026-11-28T00:00:00Z")
        self.assertEqual(self.lido()["entradas"][-1]["estado"], self.estado)

    def test_guarda_so_as_ultimas_dez(self):
        for i in range(13):
            self.rp.registrar(self.raiz, ["r%d" % i], estado=self.estado)
        e = self.lido()["entradas"]
        self.assertEqual((len(e), e[-1]["respostas"], e[0]["respostas"]), (10, ["r12"], ["r3"]))

    def test_recusa_dado_pessoal_credencial_e_formas_invalidas(self):
        for ruim in ("a@b.com", "cpf 12345678901", "ghp_abcdef", "x" * 301, "  "):
            with self.assertRaises(ValueError, msg=ruim):
                self.rp.registrar(self.raiz, [ruim], estado=self.estado)
        with self.assertRaises(ValueError):
            self.rp.registrar(self.raiz, ["ok"], estado="sem prefixo")
        with self.assertRaises(ValueError):
            self.rp.registrar(self.raiz, [], estado=self.estado)
        self.assertFalse((self.raiz / "memory" / "PERGUNTAS.json").exists())

    def test_cli_recusa_com_codigo_1(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "registrar_perguntas.py"), "--root", str(self.raiz),
                            "--estado", self.estado, "--resposta", "a@b.com"], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("recusado", r.stderr)


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
