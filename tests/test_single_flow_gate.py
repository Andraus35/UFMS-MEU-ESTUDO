"""Contraprovas adversariais da regra de uma branch/PR por tarefa."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from single_flow_gate import fetch_pr, validate_local, validate_remote

class SingleFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live = validate_local(ROOT)

    def temp_root(self, mutation=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name in ("ROADMAP.md", "AGENTS.md", "memory/HANDOFF.md"):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / name).read_text(encoding="utf-8"), encoding="utf-8")
        data = copy.deepcopy(self.live)
        if mutation:
            mutation(data)
        state = root / "state/WORKFLOW.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return temp, root

    def test_estado_unico_valido(self):
        self.assertGreaterEqual(validate_local(ROOT)["active"]["pr_number"], 1)
        self.assertRegex(validate_local(ROOT)["active"]["task_id"], r"^(?:SIM-\d{2}|RM-\d{2}(?:-PREP)?)$")

    def test_preparacao_rm08_e_uma_unica_subtarefa_serial(self):
        state = validate_local(ROOT)
        self.assertEqual(state["active"]["task_id"], "RM-08-PREP")
        self.assertEqual(state["next_task_after_merge"], "RM-08")

    def test_rejeita_subtarefa_nao_autorizada(self):
        tmp, root = self.temp_root(lambda d: d["active"].__setitem__("task_id", "RM-08-REAL"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "Tarefa ativa inválida"):
                validate_local(root)

    def test_rejeita_varias_frentes_habilitadas(self):
        for key, mutation in (
            ("max_open_pull_requests", 2),
            ("max_active_work_branches", 2),
            ("allow_parallel_work", True),
            ("allow_concurrent_prs", True),
            ("require_previous_merge_before_next", False),
            ("require_head_ci", False),
            ("require_negative_tests_for_high_medium", False),
        ):
            with self.subTest(key=key):
                tmp, root = self.temp_root(lambda d: d["rules"].__setitem__(key, mutation))
                with tmp:
                    with self.assertRaisesRegex(ValueError, "enfraquecida"):
                        validate_local(root)

    def test_rejeita_pr_legado_sem_sha_ou_duplicado(self):
        for mutate in (
            lambda d: d["deferred_pull_requests"][0].__setitem__("sha", ""),
            lambda d: d["deferred_pull_requests"][0].__setitem__("number", d["active"]["pr_number"]),
            lambda d: d["deferred_pull_requests"][0].__setitem__("branch", d["active"]["branch"]),
            lambda d: d["deferred_pull_requests"][0].__setitem__("archived_without_merge", False),
        ):
            tmp, root = self.temp_root(mutate)
            with tmp:
                with self.assertRaises(ValueError):
                    validate_local(root)

    def test_rejeita_branch_main_ativa(self):
        tmp, root = self.temp_root(lambda d: d["active"].__setitem__("branch", "main"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "Branch principal"):
                validate_local(root)

    def test_rejeita_tarefa_fora_do_roadmap(self):
        tmp, root = self.temp_root(lambda d: d["active"].__setitem__("task_id", "SIM-99"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "ausente no roadmap"):
                validate_local(root)

    def test_rejeita_ausencia_de_fonte_unica_no_handoff(self):
        tmp, root = self.temp_root()
        with tmp:
            path = root / "memory/HANDOFF.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "state/WORKFLOW.json", "estado_vago"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sem estado único"):
                validate_local(root)

    def test_handoff_repete_tarefa_pr_branch_e_proxima_tarefa(self):
        state = validate_local(ROOT)
        checkpoint = (ROOT / "memory/HANDOFF.md").read_text(encoding="utf-8").split("\\n---\\n", 1)[0]
        self.assertIn(f"**{state['active']['task_id']} / PR #{state['active']['pr_number']}**", checkpoint)
        self.assertIn(state["active"]["branch"], checkpoint)
        self.assertIn(f"**Próxima tarefa: {state['next_task_after_merge']}**", checkpoint)

    def test_rejeita_handoff_com_pr_ativo_divergente(self):
        tmp, root = self.temp_root()
        with tmp:
            path = root / "memory/HANDOFF.md"
            content = path.read_text(encoding="utf-8")
            active = self.live["active"]
            marker = f"**{active['task_id']} / PR #{active['pr_number']}**"
            path.write_text(content.replace(marker, marker.replace(
                f"#{active['pr_number']}", f"#{active['pr_number'] + 1}"), 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HANDOFF diverge"):
                validate_local(root)

    def test_rejeita_handoff_com_branch_ativa_divergente(self):
        tmp, root = self.temp_root()
        with tmp:
            path = root / "memory/HANDOFF.md"
            content = path.read_text(encoding="utf-8")
            path.write_text(content.replace(
                self.live["active"]["branch"], "wrong/branch", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HANDOFF diverge"):
                validate_local(root)

    def test_rejeita_handoff_com_proxima_tarefa_divergente(self):
        tmp, root = self.temp_root()
        with tmp:
            path = root / "memory/HANDOFF.md"
            content = path.read_text(encoding="utf-8")
            marker = f"**Próxima tarefa: {self.live['next_task_after_merge']}**"
            path.write_text(content.replace(marker, "**Próxima tarefa: RM-99**", 1),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Próxima tarefa do HANDOFF"):
                validate_local(root)

    def pr(self, n=None, branch=None, sha="a" * 40, base="main"):
        return {"number": self.live["active"]["pr_number"] if n is None else n,
                "head": {"ref": branch or self.live["active"]["branch"], "sha": sha},
                "base": {"ref": base}}

    def merged_pr(self):
        return {"number": self.live["active"]["pr_number"], "state": "closed",
                "merged_at": "2026-11-05T15:00:00Z",
                "head": {"ref": self.live["active"]["branch"]},
                "base": {"ref": "main"}}

    def check_remote(self, prs, event="pull_request", ref="unused/merge", head=None, prior=None):
        return validate_remote(self.live, prs, event, ref,
                               self.live["active"]["branch"] if head is None else head,
                               prior, "a" * 40)

    def test_aceita_um_unico_pr(self):
        self.assertTrue(self.check_remote([self.pr()]))
        self.assertTrue(self.check_remote([self.pr()], event="push",
                                          ref=self.live["active"]["branch"], head=""))

    def test_rejeita_dois_prs_simultaneos(self):
        with self.assertRaisesRegex(ValueError, "Múltiplos PRs"):
            self.check_remote([self.pr(), self.pr(self.live["active"]["pr_number"] + 1, "fix/other")])

    def test_rejeita_pr_diferente(self):
        with self.assertRaisesRegex(ValueError, "PR remoto diferente"):
            self.check_remote([self.pr(self.live["active"]["pr_number"] + 1, "fix/other")])

    def test_rejeita_branch_de_pr_diferente(self):
        with self.assertRaisesRegex(ValueError, "Branch remota diferente"):
            self.check_remote([self.pr(branch="other/branch")])

    def test_rejeita_sha_do_pr_diferente_do_evento(self):
        with self.assertRaisesRegex(ValueError, "SHA do evento diverge"):
            self.check_remote([self.pr(sha="b" * 40)])

    def test_rejeita_base_de_pr_diferente_de_main(self):
        with self.assertRaisesRegex(ValueError, "main como base"):
            self.check_remote([self.pr(base="develop")])

    def test_rejeita_sha_de_evento_ausente_ou_invalido(self):
        with self.assertRaisesRegex(ValueError, "SHA do evento ausente"):
            validate_remote(self.live, [self.pr()], "pull_request", "unused",
                            self.live["active"]["branch"], None, "")

    def test_rejeita_push_em_branch_legada(self):
        with self.assertRaisesRegex(ValueError, "fora da única frente"):
            self.check_remote([self.pr()], event="push", ref="fix/other", head="")

    def test_rejeita_pr_evento_de_outra_branch(self):
        with self.assertRaisesRegex(ValueError, "PR concorrente"):
            self.check_remote([self.pr()], head="other/branch")

    def test_rejeita_branch_sem_pr(self):
        with self.assertRaisesRegex(ValueError, "sem PR aberto"):
            self.check_remote([], event="push", ref=self.live["active"]["branch"], head="")

    def test_permite_main_sem_pr_apos_merge_comprovado(self):
        state = copy.deepcopy(self.live)
        state["active"]["phase"] = "review"
        result = validate_remote(state, [], "push", "main", "", self.merged_pr())
        self.assertEqual(result["phase"], "awaiting_next_task")
        self.assertEqual(result["next_task"], self.live["next_task_after_merge"])
        self.assertEqual(result["last_merged_pr"], self.live["active"]["pr_number"])

    def test_rejeita_lista_invalida(self):
        with self.assertRaisesRegex(ValueError, "inválido"):
            self.check_remote(None)

    def test_rejeita_main_sem_prova_de_merge(self):
        with self.assertRaisesRegex(ValueError, "Sem comprovação"):
            self.check_remote([], event="push", ref="main", head="")

    def test_rejeita_pr_fechado_sem_merge(self):
        prior = self.merged_pr()
        prior["merged_at"] = None
        with self.assertRaisesRegex(ValueError, "não comprovadamente mesclado"):
            self.check_remote([], event="push", ref="main", head="", prior=prior)

    def test_rejeita_pr_mesclado_em_base_ou_branch_errada(self):
        for mutation in (
            lambda d: d["base"].__setitem__("ref", "other"),
            lambda d: d["head"].__setitem__("ref", "other"),
            lambda d: d.__setitem__("number", self.live["active"]["pr_number"] + 1),
            lambda d: d.__setitem__("state", "open"),
        ):
            prior = self.merged_pr()
            mutation(prior)
            with self.subTest(prior=prior), self.assertRaisesRegex(
                    ValueError, "não comprovadamente mesclado"):
                self.check_remote([], event="push", ref="main", head="", prior=prior)

    def test_rejeita_main_com_pr_em_aberto(self):
        with self.assertRaisesRegex(ValueError, "fora da única frente"):
            self.check_remote([self.pr()], event="push", ref="main", head="")

    def test_rejeita_evento_indefinido(self):
        with self.assertRaisesRegex(ValueError, "Evento GitHub"):
            self.check_remote([self.pr()], event="", ref="main", head="")

    def test_rejeita_main_pos_merge_sem_revisao(self):
        from copy import deepcopy
        state = deepcopy(self.live)
        state["active"]["phase"] = "work"
        with self.assertRaisesRegex(ValueError, "sem checkpoint"):
            validate_remote(state, [], "push", "main", "", self.merged_pr())

    def test_rejeita_remocao_do_contrato_pos_merge(self):
        tmp, root = self.temp_root(
            lambda d: d.__setitem__("post_merge_resolution", "assume_closed"))
        with tmp:
            with self.assertRaisesRegex(ValueError, "transição pós-merge"):
                validate_local(root)

    def test_aceita_estado_terminal_da_fila(self):
        tmp, root = self.temp_root()
        with tmp:
            self.assertEqual(validate_local(root)["next_task_after_merge"], "RM-08")

    def test_fila_sim_terminal_pode_avancar_para_rm(self):
        tmp, root = self.temp_root(lambda d: d.__setitem__("next_task_after_merge", "DONE"))
        with tmp:
            self.assertEqual(validate_local(root)["next_task_after_merge"], "DONE")

    def test_rejeita_estado_terminal_sem_marcador_no_roadmap(self):
        tmp, root = self.temp_root(lambda d: d.__setitem__("next_task_after_merge", "DONE"))
        with tmp:
            roadmap = root / "ROADMAP.md"
            current = roadmap.read_text(encoding="utf-8")
            current = current.replace(
                "**Fila de simplificação concluída**", "**Próxima tarefa: SIM-99**", 1)
            roadmap.write_text(current, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Marcador de encerramento"):
                validate_local(root)

    def test_rejeita_roadmap_com_proxima_tarefa_divergente(self):
        tmp, root = self.temp_root()
        with tmp:
            roadmap = root / "ROADMAP.md"
            current = roadmap.read_text(encoding="utf-8")
            if self.live["next_task_after_merge"] == "DONE":
                current = current.replace(
                    "**Fila de simplificação concluída**", "**Próxima tarefa: SIM-99**", 1)
                message = "Marcador de encerramento"
            else:
                current = current.replace(
                    "**Próxima tarefa: " + self.live["next_task_after_merge"] + "**",
                    "**Próxima tarefa: SIM-99**", 1)
                message = "diverge"
            roadmap.write_text(current, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, message):
                validate_local(root)

    def test_api_de_merge_indisponivel_bloqueia(self):
        with patch("single_flow_gate.urlopen", side_effect=URLError("simulated outage")):
            with self.assertRaisesRegex(ValueError, "indisponível"):
                fetch_pr("Andraus35/UFMS-MEU-ESTUDO",
                         self.live["active"]["pr_number"], token="teste")

    def test_pr_remoto_invalido_nao_aceita_comprovacao(self):
        with self.assertRaisesRegex(ValueError, "Número do PR"):
            fetch_pr("Andraus35/UFMS-MEU-ESTUDO", True, token=None)
        with self.assertRaisesRegex(ValueError, "GITHUB_REPOSITORY"):
            fetch_pr("repo/invalido/extra", 9, token=None)

if __name__ == "__main__":
    unittest.main()
