"""Contrato do hook Stop de ENTREGA FINAL (até 18/12/2026, prorrogado em 20/11): .claude/settings.json + .claude/hooks/entrega_final.py. Offline, com executor falso."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".claude" / "hooks" / "entrega_final.py"
SETTINGS = ROOT / ".claude" / "settings.json"
spec = importlib.util.spec_from_file_location("entrega_final", SCRIPT)
ef = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ef)

HOJE = date(2026, 12, 16)  # dois dias antes do prazo prorrogado (18/12)


def usuario(t="faça algo"):
    return json.dumps({"type": "user", "message": {"role": "user", "content": t}})


def bash(c):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": c}}]}})


def texto(t="só conversa"):
    return json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}})


class Executor:
    """Executor falso: responde por prefixo do comando; registra o que foi chamado."""

    def __init__(self, respostas=None, padrao=(0, "")):
        self.respostas, self.padrao, self.chamadas = respostas or {}, padrao, []

    def __call__(self, argv, cwd, timeout):
        self.chamadas.append(list(argv))
        for chave, resp in self.respostas.items():
            if chave in " ".join(argv):
                return resp
        return self.padrao


LIMPO = {"status --porcelain": (0, ""), "rev-parse HEAD": (0, "abc\n"), "rev-parse @{u}": (0, "abc\n")}
PRIORIDADES = (0, json.dumps({"desbloqueios_do_proprietario": [{"id": "P1", "ato": "Enviar a Z1 à Zapia"}, {"id": "P2", "ato": "Decidir o risco diário"}]}))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def dados(self, linhas, ativo=False):
        arq = self.dir / "t.jsonl"
        arq.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return {"transcript_path": str(arq), "stop_hook_active": ativo}

    def decidir(self, linhas, executor=None, hoje=HOJE, ativo=False, checagens=None):
        executor = executor or Executor({**LIMPO, "next_task.py": PRIORIDADES})
        return ef.decidir(self.dados(linhas, ativo), hoje, str(ROOT), executar=executor, checagens=checagens or ef.CHECAGENS), executor


ENTREGA = [usuario(), bash("git push origin x")]


class SettingsTest(unittest.TestCase):
    def test_dois_hooks_stop_sincronos_o_de_entrega_final_com_prazo_para_a_suite(self):
        cfg = json.loads(SETTINGS.read_text(encoding="utf-8"))
        hooks = cfg["hooks"]["Stop"][0]["hooks"]
        self.assertEqual(len(hooks), 2)
        h = hooks[1]
        self.assertEqual(h["type"], "command")
        self.assertIn('"$CLAUDE_PROJECT_DIR/.claude/hooks/entrega_final.py"', h["command"])
        self.assertNotIn("async", h)
        self.assertGreaterEqual(h["timeout"], ef.ORCAMENTO_S + 10)  # a conferência cabe no tempo do hook
        self.assertLessEqual(h["timeout"], 300)
        self.assertTrue(SCRIPT.is_file())

    def test_script_sem_rede_credencial_escrita_nem_merge(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("urllib", "requests", "socket", "http://", "https://", "write_text", "write_bytes", "open(", "GITHUB_TOKEN",
                         "merge_pull_request", "gh pr", "git merge", '"git", "push"', '"git", "commit"', '"git", "add"', '"git", "reset"',
                         '"git", "checkout"', "os.environ[\"GH"):
            self.assertNotIn(proibido, fonte, proibido)
        for git in (a for a in ("status", "rev-parse")):  # só leitura do git
            self.assertIn('"git", "%s"' % git, fonte)

    def test_prazo_e_18_de_dezembro_de_2026_prorrogado_em_20_de_novembro(self):
        # E10: o proprietário prorrogou até o fim do piloto; o piloto não passa do vencimento dos tokens (18/12/2026)
        self.assertEqual(ef.PRAZO, date(2026, 12, 18))


class PrazoTest(Base):
    def test_depois_de_18_12_nao_faz_nada_nem_roda_nada(self):
        saida, ex = self.decidir(ENTREGA, hoje=date(2026, 12, 19))
        self.assertEqual(saida, {})
        self.assertEqual(ex.chamadas, [])

    def test_a_prorrogacao_mantem_o_hook_ativo_depois_do_prazo_antigo(self):
        for dia in (date(2026, 11, 21), date(2026, 12, 1), date(2026, 12, 17)):
            saida, ex = self.decidir(ENTREGA, hoje=dia)
            self.assertIn("systemMessage", saida, dia)
            self.assertTrue(ex.chamadas, dia)

    def test_no_dia_18_12_ainda_confere(self):
        saida, ex = self.decidir(ENTREGA, hoje=date(2026, 12, 18))
        self.assertIn("systemMessage", saida)
        self.assertIn("hoje é 18/12", saida["systemMessage"])

    def test_contagem_regressiva(self):
        self.assertEqual(ef.contagem(date(2026, 12, 16)), "faltam 2 dias para 18/12")
        self.assertEqual(ef.contagem(date(2026, 12, 17)), "falta 1 dia para 18/12")
        self.assertEqual(ef.contagem(date(2026, 12, 18)), "hoje é 18/12, o prazo")


class DisparoTest(Base):
    def test_conversa_comum_e_leitura_nao_disparam(self):
        for linhas in ([usuario(), texto()], [usuario(), bash("git status"), bash("git log --oneline"), texto()],
                       [usuario(), bash('echo "git push" > /dev/null')]):
            saida, ex = self.decidir(linhas)
            self.assertEqual(saida, {}, linhas)
            self.assertEqual(ex.chamadas, [])

    def test_cada_tipo_de_entrega_dispara_a_conferencia(self):
        for comando in ("git commit -m x", "git push -u origin b", "cd /x && git add -A && git commit -q -m y && git push"):
            saida, ex = self.decidir([usuario(), bash(comando)])
            self.assertTrue(ex.chamadas, comando)
            self.assertIn("systemMessage", saida)

    def test_entrega_em_turno_antigo_nao_dispara_agora(self):
        saida, ex = self.decidir([usuario("turno 1"), bash("git push"), usuario("turno 2"), texto()])
        self.assertEqual((saida, ex.chamadas), ({}, []))


class VerdeTest(Base):
    def test_tudo_verde_deixa_encerrar_com_contagem_e_pendencias(self):
        saida, ex = self.decidir(ENTREGA)
        self.assertNotIn("decision", saida)
        m = saida["systemMessage"]
        for trecho in ("faltam 2 dias para 18/12", "git limpo e enviado, gates e testes verdes", "NÃO prova a CI do GitHub",
                       "o merge, que é seu", "P1 Enviar a Z1", "P2 Decidir o risco diário"):
            self.assertIn(trecho, m, trecho)

    def test_roda_todas_as_checagens_na_ordem_com_a_suite_por_ultimo(self):
        _, ex = self.decidir(ENTREGA)
        comandos = [" ".join(c) for c in ex.chamadas]
        suite = [i for i, c in enumerate(comandos) if "unittest discover" in c]
        self.assertEqual(len(suite), 1)
        gates = [i for i, c in enumerate(comandos) if c.startswith("python3 scripts/") and "next_task" not in c]
        self.assertTrue(all(g < suite[0] for g in gates))
        for gate in ("doc_cohesion.py --check", "governance_sync_gate.py", "single_flow_gate.py --check", "roadmap_gate.py --check",
                     "product_gate.py --check", "validate.py"):
            self.assertTrue(any(gate in c for c in comandos), gate)


class VermelhoTest(Base):
    def test_teste_falhando_bloqueia_e_diz_qual(self):
        ex = Executor({**LIMPO, "unittest discover": (1, "FAIL: test_x (tests.test_y)\nAssertionError"), "next_task.py": PRIORIDADES})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertEqual(saida["decision"], "block")
        r = saida["reason"]
        for trecho in ("NÃO está de pé", "suíte de testes falhou", "FAIL: test_x", "faltam 2 dias para 18/12", "P1 Enviar a Z1"):
            self.assertIn(trecho, r, trecho)

    def test_gate_falhando_bloqueia(self):
        for chave, rotulo in (("doc_cohesion", "coesão documental"), ("governance_sync_gate", "sincronia da governança"),
                              ("single_flow_gate", "tarefa única"), ("roadmap_gate", "roadmap"), ("product_gate", "PRODUCT.md"),
                              ("validate.py", "estrutura e dados")):
            ex = Executor({**LIMPO, chave: (2, "erro do gate")})
            saida, _ = self.decidir(ENTREGA, executor=ex)
            self.assertEqual(saida["decision"], "block", chave)
            self.assertIn(rotulo + " falhou", saida["reason"], chave)

    def test_arvore_suja_bloqueia(self):
        ex = Executor({**LIMPO, "status --porcelain": (0, " M a.py\n?? b.py\n")})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertEqual(saida["decision"], "block")
        self.assertIn("2 arquivo(s) com alteração não commitada", saida["reason"])

    def test_head_diferente_do_remoto_bloqueia(self):
        ex = Executor({**LIMPO, "rev-parse @{u}": (0, "def\n")})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertEqual(saida["decision"], "block")
        self.assertIn("HEAD local não é o que está no remoto", saida["reason"])

    def test_sem_remoto_de_acompanhamento_bloqueia(self):
        ex = Executor({**LIMPO, "rev-parse @{u}": (128, "fatal")})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertEqual(saida["decision"], "block")
        self.assertIn("não tem remoto de acompanhamento", saida["reason"])

    def test_varias_falhas_aparecem_juntas(self):
        ex = Executor({**LIMPO, "status --porcelain": (0, " M a\n"), "unittest discover": (1, "x"), "validate.py": (1, "y")})
        r = self.decidir(ENTREGA, executor=ex)[0]["reason"]
        for trecho in ("git:", "suíte de testes falhou", "estrutura e dados falhou"):
            self.assertIn(trecho, r)


class FalhaAbertaELacoTest(Base):
    def test_tempo_esgotado_nao_bloqueia_mas_avisa(self):
        ex = Executor({**LIMPO, "unittest discover": (None, "tempo esgotado"), "next_task.py": PRIORIDADES})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertNotIn("decision", saida)
        self.assertIn("Não consegui concluir: suíte de testes (tempo esgotado)", saida["systemMessage"])
        self.assertIn("Rode à mão", saida["systemMessage"])

    def test_comando_ausente_nao_bloqueia(self):
        ex = Executor({**LIMPO, "roadmap_gate": (None, "não executou: FileNotFoundError")})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertNotIn("decision", saida)
        self.assertIn("roadmap", saida["systemMessage"])

    def test_orcamento_de_tempo_esgotado_pula_o_que_sobra(self):
        relogio = iter([0, 0, 200, 200, 200, 200, 200, 200, 200, 200]).__next__
        falhas, nao = ef.conferir_checagens(str(ROOT), Executor(), relogio=relogio)
        self.assertTrue(nao)
        self.assertTrue(all(x[1] == "sem tempo restante" for x in nao))

    def test_ja_bloqueou_nesta_rodada_avisa_mas_nao_bloqueia_de_novo(self):
        ex = Executor({**LIMPO, "unittest discover": (1, "ainda falha")})
        saida, _ = self.decidir(ENTREGA, executor=ex, ativo=True)
        self.assertNotIn("decision", saida)
        self.assertIn("AINDA vermelha", saida["systemMessage"])

    def test_ja_bloqueou_e_agora_esta_verde_mostra_o_verde(self):
        saida, _ = self.decidir(ENTREGA, ativo=True)
        self.assertIn("git limpo e enviado", saida["systemMessage"])

    def test_sem_pendencias_legiveis_nao_quebra(self):
        ex = Executor({**LIMPO, "next_task.py": (1, "erro")})
        saida, _ = self.decidir(ENTREGA, executor=ex)
        self.assertNotIn("Desbloqueios seus pendentes", saida["systemMessage"])
        ex = Executor({**LIMPO, "next_task.py": (0, "não é json")})
        self.assertNotIn("Desbloqueios", self.decidir(ENTREGA, executor=ex)[0]["systemMessage"])

    def test_entrada_invalida_ou_erro_interno_permite_encerrar_pelo_script(self):
        for bruto in ("", "não é json", "{}", json.dumps({"transcript_path": "/nao/existe.jsonl"})):
            r = subprocess.run([sys.executable, str(SCRIPT)], input=bruto, capture_output=True, text=True, timeout=30,
                               env={**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)})
            self.assertEqual(r.returncode, 0, bruto)
            self.assertEqual(r.stdout.strip(), "", bruto)


class ExecutorRealTest(unittest.TestCase):
    def test_codigo_e_saida(self):
        rc, saida = ef.rodar([sys.executable, "-c", "import sys; print('oi'); sys.exit(3)"], str(ROOT), 10)
        self.assertEqual((rc, saida.strip()), (3, "oi"))

    def test_tempo_esgotado_e_comando_ausente_viram_sem_veredito(self):
        self.assertEqual(ef.rodar([sys.executable, "-c", "import time; time.sleep(5)"], str(ROOT), 1)[0], None)
        self.assertEqual(ef.rodar(["comando-que-nao-existe-xyz"], str(ROOT), 5)[0], None)

    def test_checagens_reais_usam_arquivos_que_existem(self):
        for _, argv in ef.CHECAGENS:
            for parte in argv:
                if parte.startswith("scripts/") or parte.startswith("tests"):
                    self.assertTrue((ROOT / parte).exists(), parte)


if __name__ == "__main__":
    unittest.main()
