"""Contraprovas dos contratos locais de abertura e fechamento."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from agent_gates import BOOTSTRAP_FILES, HOOK_FILES, check_bootstrap, check_hook_contract, validate_roadmap_text, validate_simplification_queue
from hooks import before_write, after_write, checkpoint
from interaction_policy import (ALLOWED, CONFIRMED, DENIED, NOT_IMPLEMENTED, NOT_SENT, PENDING_READBACK, ORIENTATION, ROUTINE_AUTHORIZED, SENSITIVE, decide_action, delivery_status)


class AgentGateTests(unittest.TestCase):
    def test_bootstrap_do_repositorio_tem_quatro_identidades(self):
        hashes = check_bootstrap(ROOT)
        self.assertEqual(len(hashes), 4)
        self.assertEqual(BOOTSTRAP_FILES[1], 'ROADMAP.md')
        self.assertEqual(list(hashes), list(BOOTSTRAP_FILES))
        self.assertTrue(all(len(x) == 64 for x in hashes.values()))

    def test_edital_integral_nao_e_bootstrap(self):
        self.assertEqual(BOOTSTRAP_FILES, ("AGENTS.md", "ROADMAP.md", "memory/HANDOFF.md", "state/CURRENT.json"))
        self.assertNotIn("EDITAL_UFMS_152_2026.md", BOOTSTRAP_FILES)
        self.assertNotIn("edital/INDEX.md", BOOTSTRAP_FILES)

    def test_hooks_do_repositorio_tem_interfaces(self):
        self.assertEqual(set(check_hook_contract(ROOT)), set(HOOK_FILES))

    def test_hooks_efetivamente_executam_validacao(self):
        self.assertTrue(before_write.run(ROOT))
        self.assertTrue(after_write.run(ROOT))
        marker = checkpoint.run(ROOT)
        self.assertFalse(marker["persistencia_remota_confirmada"])
        self.assertEqual(marker["event_count"], 0)

    def test_hook_nao_aprova_raiz_ausente(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError, OSError, KeyError)):
                before_write.run(Path(tmp))

    def test_bootstrap_rejeita_arquivo_vazio(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {
                "bootstrap": {"mandatory": list(BOOTSTRAP_FILES)},
                "hooks": {"native_registration_required": True, **HOOK_FILES},
            }
            for name in BOOTSTRAP_FILES:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("fixture", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            (root / "AGENTS.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                check_bootstrap(root)

    def test_roadmap_ausente_vazio_placeholder_falham(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in BOOTSTRAP_FILES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            (root / "settings.json").write_text(json.dumps({"bootstrap": {"mandatory": list(BOOTSTRAP_FILES)}}), encoding="utf-8")
            (root / "ROADMAP.md").unlink()
            with self.assertRaisesRegex(ValueError, "ausente"):
                check_bootstrap(root)
            (root / "ROADMAP.md").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "vazio"):
                check_bootstrap(root)
            (root / "ROADMAP.md").write_text("placeholder", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "truncado/placeholder"):
                check_bootstrap(root)

    def test_roadmap_omitido_ou_fora_de_ordem_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ordered = list(BOOTSTRAP_FILES)
            for variant in ([x for x in ordered if x != "ROADMAP.md"],
                            [ordered[0], ordered[2], ordered[1], *ordered[3:]]):
                (root / "settings.json").write_text(json.dumps({"bootstrap": {"mandatory": variant}}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "ordem"):
                    check_bootstrap(root)

    def test_roadmap_fila_real_integra_e_e_valida(self):
        contents = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertTrue(validate_roadmap_text(contents))

    def test_mutantes_de_fila_nao_podem_passar(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        mutants = (
            original.replace("| RM-10 |", "| RM-09 |"),
            original.replace("| RM-04 |", "| RM-99 |"),
            original.replace("| RM-03 | P1 |", "| RM-03 | P9 |"),
            original.replace("| RM-03 | P1 |", "| RM-03 | P1 |", 1).replace(
                "| planejado |", "| ESTADO_FALSO |", 1),
            original.split("## Fila de execução")[0],
        )
        for mutation in mutants:
            with self.subTest(length=len(mutation)):
                with self.assertRaises(ValueError):
                    validate_roadmap_text(mutation)

    def test_rm03_permanece_nao_homologado_sem_evidencia_real(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-03 |"))
        self.assertIn("| implementado_nao_homologado |", line)
        self.assertIn("sem evidência real", line)

    def test_rm04_permanece_nao_homologado_sem_calibracao(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-04 |"))
        self.assertIn("| implementado_nao_homologado |", line)
        self.assertIn("sem calibração em dados reais", line)

    def test_rm07_reauditoria_nao_homologada(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-07 |"))
        self.assertIn("| implementado_nao_homologado |", line)
        self.assertIn("0/27 end-to-end PASS", line)

    def test_rm06_nao_homologado_com_sessenta_casos_sem_teste(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-06 |"))
        self.assertIn("| implementado_nao_homologado |", line)
        self.assertIn("60 sem teste canônico", line)

    def test_rm05_nao_homologado_sem_validacao_de_plataforma(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-05 |"))
        self.assertIn("| implementado_nao_homologado |", line)
        self.assertIn("plataforma real não homologada", line)

    def test_alteracao_estrategica_sem_baseline_rejeitada(self):
        original = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        line = next(line for line in original.splitlines() if line.startswith("| RM-02 |"))
        fields = line.split("|")
        self.assertEqual(fields[4].strip(), "implementado_nao_homologado")
        variants = []
        for index, value in (
            (2, "P2"),
            (4, "homologado"),
            (5, "Critério aprovado sem resultados, provas ou testes suficientes"),
        ):
            changed = fields.copy()
            changed[index] = " " + value + " "
            variants.append(original.replace(line, "|".join(changed), 1))
        for variant in variants:
            with self.subTest(changed=variant != original):
                with self.assertRaisesRegex(ValueError, "baseline auditada"):
                    validate_roadmap_text(variant)


    def test_fila_pessoal_presente_e_verificavel(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        self.assertTrue(validate_simplification_queue(roadmap))

    def test_fila_terminal_aceita_somente_itens_concluidos(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        terminal = roadmap  # marcador terminal já está no snapshot da fila concluída
        self.assertTrue(validate_simplification_queue(terminal))

    def test_fila_terminal_rejeita_item_ainda_em_andamento(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        terminal = roadmap.replace(
            "**Próxima tarefa: SIM-10**", "**Fila de simplificação concluída**", 1)
        line = next(line for line in terminal.splitlines() if line.startswith("| SIM-11 |"))
        terminal = terminal.replace(line, line.rsplit("|", 2)[0] + "| em_andamento |", 1)
        with self.assertRaisesRegex(ValueError, "itens pendentes"):
            validate_simplification_queue(terminal)

    def test_fila_pessoal_rejeita_mutantes_criticos(self):
        roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
        mutations = (
            roadmap.replace("| SIM-02 | ALTA |", "| SIM-02 | BAIXA |", 1),
            roadmap.replace("| SIM-05 | MEDIA |", "| SIM-05 | BAIXA |", 1),
            re.sub(r"\*\*Próxima tarefa: SIM-\d{2}\*\*|\*\*Fila de simplificação concluída\*\*", "**Próxima tarefa: indefinida**", roadmap, count=1),
            roadmap.replace("`tests/test_write_policy.py`", "sem_testes", 1).replace("`tests/test_ci_gate_contract.py`; teste: habilitação", "sem_testes; teste: habilitação", 1),
            roadmap.replace("| SIM-10 | BAIXA |", "| SIM-04 | BAIXA |", 1),
            roadmap.replace("registro: `docs/pedagogia/README.md`", "sem_registro", 1),
        )
        for version in mutations:
            with self.subTest(changed=version != roadmap):
                self.assertNotEqual(version, roadmap)
                with self.assertRaises(ValueError):
                    validate_simplification_queue(version)

    def test_hook_sem_interface_run_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {"hooks": {"native_registration_required": True, **HOOK_FILES}}
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            for name in HOOK_FILES.values():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("print('sem run')\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sem interface run"):
                check_hook_contract(root)

    def test_configuracao_de_hook_divergente_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings = {"hooks": {"native_registration_required": True,
                                   **HOOK_FILES, "checkpoint": "hooks/other.py"}}
            (root / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
            for name in HOOK_FILES.values():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("def run(): pass\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergente"):
                check_hook_contract(root)


class InteractionPolicyTests(unittest.TestCase):
    def test_orientacao_e_autonoma_sem_integracao_ou_aprovacao(self):
        result = decide_action(ORIENTATION)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["decision"], ALLOWED)
        self.assertEqual(result["effect"], "NONE")
        self.assertFalse(result["approval_required"])

    def test_rotina_exige_consentimento_de_escopo_nao_aprovacao_por_mensagem(self):
        denied = decide_action(
            ROUTINE_AUTHORIZED,
            integration_available=True,
            integration_verified=True,
        )
        self.assertFalse(denied["allowed"])
        self.assertEqual(denied["decision"], DENIED)
        allowed = decide_action(
            ROUTINE_AUTHORIZED,
            integration_available=True,
            integration_verified=True,
            scope_authorized=True,
            explicit_approval=False,
        )
        self.assertTrue(allowed["allowed"])
        self.assertFalse(allowed["approval_required"])

    def test_integracao_ausente_ou_nao_verificada_falha_fechado(self):
        for available, verified in ((False, False), (True, False)):
            with self.subTest(available=available, verified=verified):
                result = decide_action(
                    ROUTINE_AUTHORIZED,
                    integration_available=available,
                    integration_verified=verified,
                    scope_authorized=True,
                )
                self.assertFalse(result["allowed"])
                self.assertEqual(result["decision"], NOT_IMPLEMENTED)

    def test_acao_sensivel_exige_aprovacao_humana_explicita(self):
        args = {
            "integration_available": True,
            "integration_verified": True,
        }
        denied = decide_action(SENSITIVE, **args)
        self.assertFalse(denied["allowed"])
        self.assertEqual(denied["decision"], DENIED)
        self.assertTrue(denied["approval_required"])
        allowed = decide_action(SENSITIVE, explicit_approval=True, **args)
        self.assertTrue(allowed["allowed"])
        self.assertEqual(allowed["decision"], ALLOWED)

    def test_acao_desconhecida_e_bloqueada(self):
        result = decide_action("send_anything", integration_available=True,
                               integration_verified=True, scope_authorized=True)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["decision"], DENIED)

    def test_nao_alega_entrega_sem_acao_e_readback(self):
        self.assertEqual(delivery_status(), NOT_IMPLEMENTED)
        self.assertEqual(
            delivery_status(integration_available=True, integration_verified=True),
            NOT_SENT,
        )
        self.assertEqual(
            delivery_status(integration_available=True, integration_verified=True,
                            action_performed=True),
            PENDING_READBACK,
        )
        self.assertEqual(
            delivery_status(integration_available=True, integration_verified=True,
                            action_performed=True, readback_confirmed=True),
            CONFIRMED,
        )


if __name__ == "__main__":
    unittest.main()
