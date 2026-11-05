"""Testes adversariais offline do contrato de CI."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ci_gate_contract import verify_security_contract, verify_workflow

WORKFLOW = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")


class CIGateContractTests(unittest.TestCase):
    def test_workflow_atual_cumpre_gates(self):
        self.assertTrue(verify_security_contract(ROOT))

    def test_remocao_do_gate_roadmap(self):
        bad = WORKFLOW.replace(
            "      - name: Validar roadmap e bootstrap\n"
            "        run: python scripts/roadmap_gate.py --check\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_remocao_do_gate_de_trabalho_unico(self):
        bad = WORKFLOW.replace(
            "      - name: Garantir trabalho serial e PR unico\n"
            "        run: python scripts/single_flow_gate.py --remote\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_remocao_de_permissao_de_leitura_dos_prs(self):
        bad = WORKFLOW.replace("  pull-requests: read\n", "")
        with self.assertRaisesRegex(ValueError, "gatilho/permissão"):
            verify_workflow(bad)

    def test_remocao_de_start_engenharia(self):
        bad = WORKFLOW.replace(
            "      - name: Validar START controlado de engenharia\n"
            "        run: python scripts/bootstrap.py --mode engineering\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_remocao_de_broker_de_agente(self):
        bad = WORKFLOW.replace(
            "      - name: Validar broker read-only com SHA de checkout\n"
            "        run: python scripts/agent_entrypoint.py --role engineer --check\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_remocao_do_gate_privacidade(self):
        bad = WORKFLOW.replace(
            "      - name: Verificar bloqueio de resultados pessoais\n"
            "        run: python scripts/write_policy.py --check\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_desativar_checagem_de_ci(self):
        bad = WORKFLOW.replace(
            "      - name: Validar contrato de segurança da CI\n"
            "        run: python scripts/ci_gate_contract.py --check\n", "")
        with self.assertRaisesRegex(ValueError, "Etapa de CI obrigatória"):
            verify_workflow(bad)

    def test_remocao_de_trigger_pull_request(self):
        bad = WORKFLOW.replace("  pull_request:\n", "")
        with self.assertRaisesRegex(ValueError, "gatilho/permissão"):
            verify_workflow(bad)

    def test_alterar_permissao_de_acesso(self):
        bad = WORKFLOW.replace("  contents: read", "  contents: write")
        with self.assertRaisesRegex(ValueError, "gatilho/permissão|Permissão"):
            verify_workflow(bad)

    def test_forcar_continue_on_error(self):
        bad = WORKFLOW.replace("        run: python scripts/validate.py\n",
                               "        run: python scripts/validate.py\n        continue-on-error: true\n")
        with self.assertRaisesRegex(ValueError, "Bypass"):
            verify_workflow(bad)

    def test_duplicacao_de_gate_e_rejeitada(self):
        row = ("      - name: Verificar bloqueio de resultados pessoais\n"
               "        run: python scripts/write_policy.py --check\n")
        bad = WORKFLOW.replace(row, row + row)
        with self.assertRaisesRegex(ValueError, "duplicada"):
            verify_workflow(bad)


if __name__ == "__main__":
    unittest.main()
