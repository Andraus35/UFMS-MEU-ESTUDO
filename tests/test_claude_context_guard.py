"""Testes do context-guard com transcrições SINTÉTICAS e HOME temporário. Nada toca o ~/.claude real."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = DIR / "claude_context_guard.py"
INSTALL = DIR / "claude_context_guard_install.py"
PROMPT = ("## Primeiro passo\nRode `git status` e continue a tarefa X pelo arquivo Y; depois rode os testes do módulo Z e abra o PR.\n"
          "## Estado\nBranch feature/x no SHA abc123, testes verdes, falta a documentação e a revisão do dono do projeto.\n"
          "## Pendências\nO usuário decide o nome da API; não mexer nos arquivos de contrato sem aprovação expressa dele; CI ainda não rodou. Releia o handoff do projeto antes de qualquer escrita e confirme o SHA remoto.\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()
        self.proj = Path(self.tmp.name) / "proj"
        self.proj.mkdir()
        subprocess.run(["git", "-C", str(self.proj), "init", "-q"], check=True)
        self.env = {**os.environ, "CONTEXT_GUARD_HOME": str(self.home), "HOME": str(self.home), "CONTEXT_GUARD_WINDOW": "200000"}  # janela pequena só para os testes de mecanismo; o padrão real (1M) tem testes próprios
        self.tr = Path(self.tmp.name) / "t.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, tokens, sidechain_tokens=None, users=("faça a tarefa X", "agora o teste Y")):
        rows = [{"type": "user", "message": {"content": u}} for u in users]
        rows.append({"type": "assistant", "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": tokens - 10, "cache_creation_input_tokens": 0}}})
        if sidechain_tokens:
            rows.append({"type": "assistant", "isSidechain": True, "message": {"usage": {"input_tokens": sidechain_tokens}}})
        self.tr.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    def run_hook(self, event, sid="s1", extra=None, env=None):
        payload = {"session_id": sid, "cwd": str(self.proj), "transcript_path": str(self.tr), **(extra or {})}
        r = subprocess.run([sys.executable, str(SCRIPT), event], input=json.dumps(payload), capture_output=True, text=True,
                           env={**self.env, **(env or {})})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def seal(self, sid="s1", body=PROMPT):
        return subprocess.run([sys.executable, str(SCRIPT), "seal", "--session", sid, "--cwd", str(self.proj)], input=body,
                              capture_output=True, text=True, env=self.env)

    def prompt_files(self):
        return list((self.home / ".claude" / "handoffs").glob("*/NEXT_SESSION_PROMPT.md"))


class MedirTests(Base):
    def test_abaixo_do_limite_nao_faz_nada(self):
        self.transcript(99_000)  # 49,5% de 200k
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.assertIsNone(self.run_hook("PostToolUse"))

    def test_no_limite_injeta_a_ordem_com_comando_de_selo(self):
        self.transcript(100_000)  # exatamente 50%
        for ev in ("UserPromptSubmit", "PostToolUse"):
            o = self.run_hook(ev)["hookSpecificOutput"]
            self.assertEqual(o["hookEventName"], ev)
            self.assertIn("COMECE AGORA", o["additionalContext"])
            self.assertIn("seal --session s1", o["additionalContext"])
            self.assertIn("## Primeiro passo", o["additionalContext"])

    def test_subagente_e_sidechain_nao_contam(self):
        self.transcript(10_000, sidechain_tokens=190_000)
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.transcript(150_000)
        self.assertIsNone(self.run_hook("PostToolUse", extra={"agent_id": "sub1"}))

    def test_janela_configuravel_e_deduzida_de_uso_acima_de_200k(self):
        self.transcript(120_000)
        self.assertIsNone(self.run_hook("UserPromptSubmit", env={"CONTEXT_GUARD_WINDOW": "1000000"}))  # 12% de 1M
        self.transcript(400_000)  # acima de 200k: a janela é 1M, logo 40%: ainda abaixo
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.transcript(600_000)
        self.assertIsNotNone(self.run_hook("UserPromptSubmit"))

    def test_limite_configuravel(self):
        self.transcript(60_000)
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.assertIsNotNone(self.run_hook("UserPromptSubmit", env={"CONTEXT_GUARD_THRESHOLD": "0.25"}))

    def test_transcript_ausente_ou_corrompido_nao_quebra(self):
        self.tr.write_text("lixo\n{", encoding="utf-8")
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.tr.unlink()
        self.assertIsNone(self.run_hook("Stop"))


class JanelaPadraoTests(Base):
    def hook(self, event="UserPromptSubmit", sid="s1"):
        env = {k: v for k, v in self.env.items() if k != "CONTEXT_GUARD_WINDOW"}
        payload = {"session_id": sid, "cwd": str(self.proj), "transcript_path": str(self.tr)}
        r = subprocess.run([sys.executable, str(SCRIPT), event], input=json.dumps(payload), capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def test_padrao_e_1m_187k_nao_dispara_e_500k_dispara(self):
        self.transcript(187_100)  # a tela do proprietário mostrava 19% de 1M; com 200k seria 94% (falso alarme)
        self.assertIsNone(self.hook())
        self.transcript(499_999)
        self.assertIsNone(self.hook())
        self.transcript(500_000)
        self.assertIn("COMECE AGORA", self.hook()["hookSpecificOutput"]["additionalContext"])

    def test_config_do_projeto_versionada_fixa_1m(self):
        cfg = json.loads((Path(__file__).resolve().parents[1] / ".claude" / "context-guard.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["window_tokens"], 1_000_000)
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"window_tokens": 1_000_000', src)

    def test_depois_do_selo_o_aviso_nao_repete_a_cada_ferramenta(self):
        self.transcript(600_000)
        self.assertIn("COMECE AGORA", self.hook("PostToolUse")["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(self.seal().returncode, 0)
        primeiro = self.hook("PostToolUse")
        self.assertIn("JÁ SELADO", primeiro["hookSpecificOutput"]["additionalContext"])
        for _ in range(3):
            self.assertIsNone(self.hook("PostToolUse"))  # mesmo estado do lote: silêncio


class DesarmeTests(Base):
    """HOOKR: sessão armada por engano (falso alarme) volta ao normal quando a medição cai abaixo do limite."""

    def estado(self, sid="s1"):
        return json.loads((self.home / ".claude" / "context-guard" / "state" / f"{sid}.json").read_text())

    def test_armada_por_engano_desarma_quando_a_medicao_cai_abaixo_do_limite(self):
        self.transcript(150_000)  # 75% de 200k: arma e sela
        self.assertIsNotNone(self.run_hook("UserPromptSubmit"))
        self.assertEqual(self.seal().returncode, 0)
        self.assertTrue(self.estado()["armed_at"])
        self.transcript(40_000, users=("faça a tarefa X",))  # 20% de 200k: abaixo do limite
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        st = self.estado()
        for k in ("armed_at", "sealed", "sealed_at", "stop_blocks", "aviso_chave"):
            self.assertNotIn(k, st, k)
        self.assertEqual(st["desarmes"], 1)

    def test_desarmada_o_stop_nao_trava_mais(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.transcript(40_000)
        self.run_hook("UserPromptSubmit")
        self.assertIsNone(self.run_hook("Stop"))

    def test_acima_do_limite_continua_armada_e_selada(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.assertEqual(self.seal().returncode, 0)
        self.transcript(160_000)
        self.run_hook("PostToolUse")
        st = self.estado()
        self.assertTrue(st["armed_at"])
        self.assertTrue(st["sealed"])
        self.assertNotIn("desarmes", st)

    def test_sem_medida_nao_desarma(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.tr.write_text(json.dumps({"type": "user", "message": {"content": "oi"}}) + "\n", encoding="utf-8")  # sem usage
        self.run_hook("UserPromptSubmit")
        self.assertTrue(self.estado()["armed_at"])

    def test_o_hook_de_perguntas_so_le_e_deixa_de_ceder_depois_do_desarme(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("perguntas", Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "perguntas_boas_praticas.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        os.environ["CONTEXT_GUARD_HOME"] = str(self.home)
        try:
            self.transcript(150_000)
            self.run_hook("UserPromptSubmit")
            self.assertTrue(mod.cede_ao_hook_de_passagem({"session_id": "s1"}))
            self.transcript(40_000)
            self.run_hook("UserPromptSubmit")
            self.assertFalse(mod.cede_ao_hook_de_passagem({"session_id": "s1"}))
        finally:
            os.environ.pop("CONTEXT_GUARD_HOME", None)

    def test_modulo_de_estado_existe_e_o_instalador_o_copia(self):
        raiz = Path(__file__).resolve().parents[1] / "scripts"
        self.assertTrue((raiz / "context_guard_state.py").is_file())
        self.assertIn("context_guard_state.py", (raiz / "claude_context_guard_install.py").read_text(encoding="utf-8"))


class BranchProtegidaComMergePendenteTests(Base):
    """HOOKR2: na branch protegida/destacada com merge sem recibo, o hook orienta a preparar o repositório (e não manda só encerrar)."""

    def repo(self, pr_ativo, assunto_do_merge="feat: algo (#7)"):
        g = ["git", "-C", str(self.proj), "-c", "user.email=a@b.c", "-c", "user.name=t"]
        subprocess.run([*g, "checkout", "-q", "-B", "main"], check=True)
        (self.proj / "state").mkdir(exist_ok=True)
        (self.proj / "state" / "WORKFLOW.json").write_text(json.dumps({"active": {"pr_number": pr_ativo, "task_id": "RM-00"}}), encoding="utf-8")
        subprocess.run([*g, "add", "-A"], check=True)
        subprocess.run([*g, "commit", "-q", "-m", assunto_do_merge], check=True)
        remoto = Path(self.tmp.name) / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remoto)], check=True)
        subprocess.run([*g, "remote", "add", "origin", str(remoto)], check=True)
        subprocess.run([*g, "push", "-q", "-u", "origin", "main"], check=True)

    def armado_e_selado(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.assertEqual(self.seal().returncode, 0)

    def texto(self):
        o = self.run_hook("PostToolUse")
        return o["hookSpecificOutput"]["additionalContext"] if o else ""

    def test_merge_pendente_de_recibo_em_branch_protegida_orienta_a_preparar_o_repo(self):
        self.repo(pr_ativo=7)  # o PR registrado (#7) aparece mesclado no histórico da main
        self.armado_e_selado()
        t = self.texto()
        for trecho in ("record_merge_receipt.py", "branch do próximo lote", "origin/main", "HANDOFF", "#7"):
            self.assertIn(trecho, t, trecho)
        self.assertNotIn("encerre", t)

    def test_sem_merge_pendente_em_branch_protegida_continua_a_mandar_encerrar(self):
        self.repo(pr_ativo=99)  # #99 não está mesclado: não há recibo pendente
        self.armado_e_selado()
        t = self.texto()
        self.assertIn("Lote finalizado e persistido", t)
        self.assertNotIn("record_merge_receipt.py", t)

    def test_sem_workflow_ou_sem_git_nao_quebra_e_cai_no_comportamento_anterior(self):
        self.armado_e_selado()  # repo sem commits e sem state/WORKFLOW.json
        t = self.texto()
        self.assertNotIn("record_merge_receipt.py", t)

    def test_o_aviso_orientado_sai_uma_vez_por_estado(self):
        self.repo(pr_ativo=7)
        self.armado_e_selado()
        self.assertIn("record_merge_receipt.py", self.texto())
        self.assertEqual(self.texto(), "")

    def test_modulo_existe_e_o_instalador_o_copia(self):
        raiz = Path(__file__).resolve().parents[1] / "scripts"
        self.assertTrue((raiz / "context_guard_branch.py").is_file())
        self.assertIn("context_guard_branch.py", (raiz / "claude_context_guard_install.py").read_text(encoding="utf-8"))


class SeloETravaTests(Base):
    def test_selo_recusa_prompt_incompleto_e_curto(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        r = self.seal(body="## Primeiro passo\nfaça algo")
        self.assertEqual(r.returncode, 2)
        self.assertIn("RECUSADO", r.stderr)
        self.assertEqual(self.prompt_files(), [])
        for falta in ("## Primeiro passo", "## Estado", "## Pendências"):
            self.assertEqual(self.seal(body=PROMPT.replace(falta, "## Outro")).returncode, 2, falta)

    def test_selo_recusa_prompt_com_as_secoes_mas_curto_demais(self):
        r = self.seal(body="## Primeiro passo\na\n## Estado\nb\n## Pendências\nc\n")
        self.assertEqual(r.returncode, 2)
        self.assertIn("mínimo de 400", r.stderr)

    def test_stop_bloqueia_enquanto_nao_selado_e_libera_depois(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        o = self.run_hook("Stop")
        self.assertEqual(o["decision"], "block")
        self.assertIn("bloqueio 1 de 3", o["reason"])
        self.assertEqual(self.seal().returncode, 0)
        self.assertIsNone(self.run_hook("Stop"))
        aviso = self.run_hook("UserPromptSubmit")["hookSpecificOutput"]["additionalContext"]  # selado: a ordem de preparar para de repetir
        self.assertIn("JÁ SELADO", aviso)
        self.assertNotIn("COMECE AGORA", aviso)

    def test_stop_nao_bloqueia_sem_ter_atingido_o_limite(self):
        self.transcript(50_000)
        self.run_hook("UserPromptSubmit")
        self.assertIsNone(self.run_hook("Stop"))

    def test_stop_nunca_prende_a_sessao(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        for i in range(3):
            self.assertEqual(self.run_hook("Stop", extra={"stop_hook_active": i > 0})["decision"], "block")
        self.assertIsNone(self.run_hook("Stop"))  # quarto: libera

    def test_selo_grava_prompt_com_fatos_e_arquiva_o_anterior(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.assertEqual(self.seal().returncode, 0)
        (p,) = self.prompt_files()
        txt = p.read_text(encoding="utf-8")
        self.assertIn("origin=seal", txt)
        self.assertIn("Fatos verificados pelo hook", txt)
        self.assertIn("contexto medido: 75%", txt)
        self.assertIn(str(self.proj), txt)
        self.run_hook("UserPromptSubmit", sid="s2")  # outra sessão
        self.assertEqual(self.seal(sid="s2", body=PROMPT + "\nSegunda sessão.").returncode, 0)
        self.assertEqual(len(list((p.parent / "history").glob("*.md"))), 1)

    def test_copia_no_repositorio_quando_configurada(self):
        (self.home / ".claude").mkdir(parents=True)
        (self.home / ".claude" / "context-guard.json").write_text(json.dumps({"repo_copy": ".claude/handoff/NEXT.md"}))
        self.assertEqual(self.seal().returncode, 0)
        self.assertTrue((self.proj / ".claude" / "handoff" / "NEXT.md").is_file())


class FallbackEPassagemTests(Base):
    def test_session_end_gera_fallback_se_nao_selou_e_houve_trabalho(self):
        self.transcript(30_000)
        self.run_hook("SessionEnd")
        (p,) = self.prompt_files()
        txt = p.read_text(encoding="utf-8")
        self.assertIn("origin=fallback", txt)
        self.assertIn("agora o teste Y", txt)
        self.assertIn("GERADO AUTOMATICAMENTE" if False else "AUTOMATICAMENTE", txt)
        for h in ("## Primeiro passo", "## Estado", "## Pendências"):
            self.assertIn(h, txt)

    def test_nao_sobrescreve_prompt_selado_da_mesma_sessao(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.seal()
        self.run_hook("PreCompact")
        self.run_hook("SessionEnd")
        self.assertIn("origin=seal", self.prompt_files()[0].read_text(encoding="utf-8"))

    def test_sessao_vazia_nao_gera_fallback(self):
        self.transcript(1_000, users=())
        self.run_hook("SessionEnd")
        self.assertEqual(self.prompt_files(), [])

    def test_session_start_entrega_o_prompt_da_sessao_anterior(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.seal()
        for src in ("startup", "clear", "compact"):
            o = self.run_hook("SessionStart", sid="nova", extra={"source": src})["hookSpecificOutput"]
            self.assertEqual(o["hookEventName"], "SessionStart")
            self.assertIn("redigido e selado pela sessão anterior", o["additionalContext"])
            self.assertIn("## Primeiro passo", o["additionalContext"])
            self.assertIn("CONFIRA o estado real", o["additionalContext"])
        self.assertIsNone(self.run_hook("SessionStart", sid="nova", extra={"source": "resume"}))

    def test_session_start_marca_fallback_como_pista(self):
        self.transcript(30_000)
        self.run_hook("SessionEnd")
        o = self.run_hook("SessionStart", sid="nova", extra={"source": "startup"})["hookSpecificOutput"]
        self.assertIn("GERADO AUTOMATICAMENTE (pista, não fato)", o["additionalContext"])

    def test_session_start_sem_prompt_nao_diz_nada(self):
        self.assertIsNone(self.run_hook("SessionStart", sid="nova", extra={"source": "startup"}))

    def test_projetos_diferentes_nao_misturam_prompts(self):
        self.transcript(30_000)
        self.run_hook("SessionEnd")
        outro = Path(self.tmp.name) / "outro"
        outro.mkdir()
        subprocess.run(["git", "-C", str(outro), "init", "-q"], check=True)
        r = subprocess.run([sys.executable, str(SCRIPT), "SessionStart"], capture_output=True, text=True, env=self.env,
                           input=json.dumps({"session_id": "n", "cwd": str(outro), "source": "startup"}))
        self.assertEqual(r.stdout.strip(), "")

    def test_pastas_com_o_mesmo_nome_em_caminhos_diferentes_nao_misturam(self):
        self.transcript(30_000)
        self.run_hook("SessionEnd")
        gemeo = Path(self.tmp.name) / "x" / "proj"
        gemeo.mkdir(parents=True)
        subprocess.run(["git", "-C", str(gemeo), "init", "-q"], check=True)
        r = subprocess.run([sys.executable, str(SCRIPT), "SessionStart"], capture_output=True, text=True, env=self.env,
                           input=json.dumps({"session_id": "n", "cwd": str(gemeo), "source": "startup"}))
        self.assertEqual(r.stdout.strip(), "")

    def test_subdiretorio_do_mesmo_repo_usa_o_mesmo_prompt(self):
        self.transcript(30_000)
        self.run_hook("SessionEnd")
        sub = self.proj / "a" / "b"
        sub.mkdir(parents=True)
        r = subprocess.run([sys.executable, str(SCRIPT), "SessionStart"], capture_output=True, text=True, env=self.env,
                           input=json.dumps({"session_id": "n", "cwd": str(sub), "source": "startup"}))
        self.assertIn("Prompt de start", r.stdout)

    def test_falha_do_script_e_aberta(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "UserPromptSubmit"], input="{não é json", capture_output=True, text=True, env=self.env)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, ""))
        self.assertIn("UserPromptSubmit", (self.home / ".claude" / "context-guard" / "errors.log").read_text())


class AvisoPosSeloTests(Base):
    def armado_e_selado(self):
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.assertEqual(self.seal().returncode, 0)

    def estado(self):
        return json.loads((self.home / ".claude" / "context-guard" / "state" / "s1.json").read_text())

    def test_lote_finalizado_manda_nao_propor_novo_lote_e_encerrar(self):
        self.armado_e_selado()
        t = self.run_hook("UserPromptSubmit")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Lote finalizado e persistido", t)
        self.assertIn("NÃO proponha novo lote", t)
        self.assertIn("encerre", t)
        self.assertIsNone(self.run_hook("PostToolUse"))  # o aviso sai uma vez por estado do lote
        self.assertIs(self.estado()["lote_pendente"], False)

    def test_lote_pendente_manda_finalizar_antes_de_encerrar(self):
        self.armado_e_selado()
        (self.proj / "alteracao.txt").write_text("x")  # árvore suja
        t = self.run_hook("UserPromptSubmit")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("AINDA NÃO está persistido", t)
        self.assertIn("NÃO abra outro lote", t)
        self.assertNotIn("Lote finalizado", t)
        self.assertIs(self.estado()["lote_pendente"], True)

    def test_commit_local_nao_enviado_conta_como_pendente(self):
        remoto = Path(self.tmp.name) / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", str(remoto)], check=True)
        g = ["git", "-C", str(self.proj), "-c", "user.email=a@b.c", "-c", "user.name=t"]
        subprocess.run([*g, "commit", "-q", "--allow-empty", "-m", "a"], check=True)
        subprocess.run([*g, "remote", "add", "origin", str(remoto)], check=True)
        subprocess.run([*g, "push", "-q", "-u", "origin", "HEAD"], check=True, capture_output=True)
        self.armado_e_selado()
        self.assertIn("Lote finalizado", self.run_hook("PostToolUse")["hookSpecificOutput"]["additionalContext"])
        subprocess.run([*g, "commit", "-q", "--allow-empty", "-m", "b"], check=True)
        self.assertIn("AINDA NÃO está persistido", self.run_hook("PostToolUse")["hookSpecificOutput"]["additionalContext"])

    def test_abaixo_do_limite_nao_avisa(self):
        self.transcript(50_000)
        self.assertIsNone(self.run_hook("UserPromptSubmit"))
        self.assertNotIn("lote_pendente", self.estado())


class FimDeLoteEPersistenciaTests(Base):
    def ramo_de_trabalho(self, nome="feat"):
        subprocess.run(["git", "-C", str(self.proj), "symbolic-ref", "HEAD", f"refs/heads/{nome}"], check=True)

    def ordem(self):
        self.transcript(150_000)
        return self.run_hook("UserPromptSubmit")["hookSpecificOutput"]["additionalContext"]

    def test_ordem_manda_verificar_o_fim_do_lote_antes_de_persistir_e_selar_sem_pedir_permissao(self):
        t = self.ordem()
        posicoes = [t.index(x) for x in ("1. VERIFICAR O FIM DO LOTE", "2. PERSISTIR O REPOSITÓRIO", "3. SELAR")]
        self.assertEqual(posicoes, sorted(posicoes))
        for trecho in ("para não cortar ao meio", "NÃO inicie outra", "ponto de corte consistente", "`WIP:`", "NÃO peça permissão ao usuário",
                       "NÃO use AskUserQuestion", "faça commit e push na branch de trabalho atual", "nunca force push", "nunca merge",
                       "nunca commit na branch principal", "selar só depois de persistir"):
            self.assertIn(trecho, t, trecho)

    def test_fatos_do_lote_aparecem_com_o_nome_correto_dos_arquivos(self):
        self.ramo_de_trabalho()
        (self.proj / "alteracao.txt").write_text("x")
        (self.proj / "outro.txt").write_text("y")
        t = self.ordem()
        self.assertIn("branch `feat`", t)
        self.assertIn("2 alteração(ões) não commitada(s)", t)
        self.assertIn("alteracao.txt", t)  # o strip do git não pode comer o começo do nome
        self.assertNotIn("PROTEGIDA", t)

    def test_arquivo_rastreado_modificado_mantem_o_nome_inteiro(self):
        self.ramo_de_trabalho()
        (self.proj / "rastreado.txt").write_text("a")
        g = ["git", "-C", str(self.proj), "-c", "user.email=a@b.c", "-c", "user.name=t"]
        subprocess.run([*g, "add", "-A"], check=True)
        subprocess.run([*g, "commit", "-q", "-m", "a"], check=True)
        (self.proj / "rastreado.txt").write_text("b")  # " M rastreado.txt": o strip do git come o espaço inicial
        self.assertIn("rastreado.txt", self.ordem())
        self.assertNotIn("astreado.txt,", self.ordem().replace("rastreado.txt", ""))

    def test_branch_principal_e_marcada_como_protegida(self):
        self.ramo_de_trabalho("main")
        self.assertIn("PROTEGIDA: não comite nela", self.ordem())

    def test_stop_bloqueia_selado_mas_nao_persistido(self):
        self.ramo_de_trabalho()
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.assertEqual(self.seal().returncode, 0)
        self.assertIsNone(self.run_hook("Stop"))  # selado e limpo: libera
        (self.proj / "pendente.txt").write_text("x")
        o = self.run_hook("Stop")
        self.assertEqual(o["decision"], "block")
        self.assertIn("ainda NÃO está persistido", o["reason"])
        self.assertIn("persista agora (commit e push", o["reason"])
        self.assertIn("pendente.txt", o["reason"])

    def test_stop_nao_prende_em_branch_protegida(self):
        self.ramo_de_trabalho("main")
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.seal()
        (self.proj / "pendente.txt").write_text("x")
        self.assertIsNone(self.run_hook("Stop"))  # não há como persistir na principal: não bloqueia

    def test_stop_persistir_tem_teto_de_bloqueios(self):
        self.ramo_de_trabalho()
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.seal()
        (self.proj / "pendente.txt").write_text("x")
        for _ in range(3):
            self.assertEqual(self.run_hook("Stop")["decision"], "block")
        self.assertIsNone(self.run_hook("Stop"))

    def test_aviso_pos_selo_com_lote_pendente_manda_persistir_sem_pedir_permissao(self):
        self.ramo_de_trabalho()
        self.transcript(150_000)
        self.run_hook("UserPromptSubmit")
        self.seal()
        (self.proj / "pendente.txt").write_text("x")
        t = self.run_hook("PostToolUse")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("sem pedir permissão", t)
        self.assertIn("pendente.txt", t)
        self.assertIn("sele o prompt de novo", t)

    def test_repositorio_sem_commits_nao_e_confundido_com_sem_git(self):
        self.assertNotIn("não é um repositório git", self.ordem())


class ConfigDoProjetoTests(Base):
    def projeto_cfg(self, obj):
        (self.proj / ".claude").mkdir(exist_ok=True)
        (self.proj / ".claude" / "context-guard.json").write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")

    def texto(self, **kw):
        o = self.run_hook("UserPromptSubmit", **kw)
        return o["hookSpecificOutput"]["additionalContext"] if o else None

    def test_limite_do_projeto_vale_para_aquele_projeto(self):
        self.transcript(60_000)  # 30%
        self.assertIsNone(self.texto())
        self.projeto_cfg({"threshold": 0.25})
        self.assertIn("COMECE AGORA", self.texto())

    def test_instrucao_extra_do_projeto_entra_na_ordem(self):
        self.transcript(150_000)
        self.assertNotIn("Instrução específica deste projeto", self.texto())
        self.projeto_cfg({"extra_instruction": "Atualize memory/HANDOFF.md e rode os gates do projeto."})
        t = self.texto()
        self.assertIn("Instrução específica deste projeto: Atualize memory/HANDOFF.md", t)

    def test_projeto_nao_muda_chaves_fora_da_lista(self):
        self.transcript(150_000)
        self.projeto_cfg({"repo_copy": ".claude/handoff/X.md", "threshold": 0.9})
        self.assertIsNone(self.texto())  # threshold do projeto vale (0,9)
        self.transcript(190_000)
        self.assertIsNotNone(self.texto())
        self.assertEqual(self.seal().returncode, 0)
        self.assertFalse((self.proj / ".claude" / "handoff").exists())  # repo_copy do projeto é ignorado

    def test_config_do_projeto_invalida_e_ignorada(self):
        self.transcript(150_000)
        self.projeto_cfg("{quebrado")
        self.assertIn("COMECE AGORA", self.texto())

    def test_comando_de_selo_aponta_para_este_script(self):
        self.transcript(150_000)
        self.assertIn(f'python3 "{SCRIPT.resolve()}" seal --session s1', self.texto())

    def test_comando_de_selo_usa_home_quando_o_script_esta_sob_o_home(self):
        subprocess.run([sys.executable, str(INSTALL), "--home", str(self.home)], check=True, capture_output=True)
        instalado = self.home / ".claude" / "hooks" / "claude_context_guard.py"
        self.transcript(150_000)
        r = subprocess.run([sys.executable, str(instalado), "UserPromptSubmit"], capture_output=True, text=True, env=self.env,
                           input=json.dumps({"session_id": "s1", "cwd": str(self.proj), "transcript_path": str(self.tr)}))
        self.assertIn('python3 "$HOME/.claude/hooks/claude_context_guard.py" seal --session s1',
                      json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"])


class InstaladorTests(Base):
    def run_install(self, *a):
        return subprocess.run([sys.executable, str(INSTALL), *a, "--home", str(self.home)], capture_output=True, text=True)

    def settings(self):
        return json.loads((self.home / ".claude" / "settings.json").read_text())

    def test_instala_preservando_o_que_existe_e_e_idempotente(self):
        (self.home / ".claude").mkdir(parents=True)
        (self.home / ".claude" / "settings.json").write_text(json.dumps({
            "model": "opus", "permissions": {"allow": ["Bash(git *)"]},
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo meu-hook"}]}]}}))
        self.assertEqual(self.run_install().returncode, 0)
        self.assertEqual(self.run_install().returncode, 0)
        s = self.settings()
        self.assertEqual(s["model"], "opus")
        self.assertIn("Bash(git *)", s["permissions"]["allow"])
        self.assertEqual(sum("claude_context_guard.py" in a for a in s["permissions"]["allow"]), 1)
        stops = s["hooks"]["Stop"]
        self.assertEqual(len(stops), 2)  # o hook do usuário + o nosso, sem duplicar
        self.assertTrue(any("meu-hook" in h["command"] for g in stops for h in g["hooks"]))
        for ev in ("SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "PreCompact", "SessionEnd"):
            self.assertEqual(sum("claude_context_guard.py" in h["command"] for g in s["hooks"][ev] for h in g["hooks"]), 1, ev)
        self.assertEqual(s["hooks"]["SessionStart"][0]["matcher"], "startup|resume|clear|compact")
        self.assertTrue((self.home / ".claude" / "hooks" / "claude_context_guard.py").is_file())
        self.assertEqual(self.run_install("--check").stdout.strip(), "INSTALADO")
        self.assertTrue(list((self.home / ".claude").glob("settings.json.bak-*")))

    def test_remove_so_o_que_instalou(self):
        (self.home / ".claude").mkdir(parents=True)
        (self.home / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo meu-hook"}]}]}}))
        self.run_install()
        self.run_install("--uninstall")
        s = self.settings()
        self.assertEqual(list(s["hooks"]), ["Stop"])
        self.assertEqual(s["hooks"]["Stop"][0]["hooks"][0]["command"], "echo meu-hook")
        self.assertEqual(self.run_install("--check").stdout.strip(), "NÃO INSTALADO")

    def test_settings_invalido_nao_e_sobrescrito(self):
        (self.home / ".claude").mkdir(parents=True)
        p = self.home / ".claude" / "settings.json"
        p.write_text("{quebrado")
        self.assertNotEqual(self.run_install().returncode, 0)
        self.assertEqual(p.read_text(), "{quebrado")


if __name__ == "__main__":
    unittest.main()
