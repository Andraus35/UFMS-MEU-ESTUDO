"""Testes adversariais offline do contrato de CI."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ci_gate_contract import verify_composite_validation, verify_security_contract, verify_workflow

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

    def test_remocao_do_sha_exato_do_evento(self):
        bad = WORKFLOW.replace(
            "          GITHUB_HEAD_SHA: ${{ github.event.pull_request.head.sha || github.sha }}\n", "")
        with self.assertRaisesRegex(ValueError, "SHA exato do evento"):
            verify_workflow(bad)

    def test_duplicacao_do_sha_exato_do_evento(self):
        line = "          GITHUB_HEAD_SHA: ${{ github.event.pull_request.head.sha || github.sha }}\n"
        bad = WORKFLOW.replace(line, line + line)
        with self.assertRaisesRegex(ValueError, "SHA exato do evento"):
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


    def test_validacoes_edital_estao_consolidadas_em_validate(self):
        self.assertTrue(verify_composite_validation(ROOT))

    def test_remocao_de_validacao_consolidada_falha(self):
        source = (ROOT / "scripts/validate.py").read_text(encoding="utf-8")
        tokens = (
            "chunks = check_edital(root)",
            "indexed_vagas = check_vagas(root)",
            "indexed_atribuicoes = check_atribuicoes(root)",
            "official_observations,verified_amendments,open_alerts = check_sources(root)",
        )
        for token in tokens:
            with self.subTest(token=token):
                with self.assertRaisesRegex(ValueError, "Validação consolidada"):
                    verify_composite_validation(ROOT, source.replace(token, "", 1))

    def test_ci_rejeita_repetir_validacao_ja_consolidada(self):
        duplicate = (
            "      - name: Validar integridade do edital\\n"
            "        run: python scripts/chunk_edital.py --check\\n"
        )
        with self.assertRaisesRegex(ValueError, "já executada"):
            verify_workflow(WORKFLOW + duplicate)


if __name__ == "__main__":
    unittest.main()
