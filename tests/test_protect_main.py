"""Contraprovas offline da configuração administrativa."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from protect_main import protection_policy, verify_protection


def response(approvals=0):
    p = protection_policy(approvals)
    p["enforce_admins"] = {"enabled": True}
    p["allow_force_pushes"] = {"enabled": False}
    p["allow_deletions"] = {"enabled": False}
    p["required_conversation_resolution"] = {"enabled": True}
    return p


class ProtectionContractTests(unittest.TestCase):
    def test_policy_estrita_com_pr_e_ci(self):
        policy = protection_policy()
        self.assertTrue(policy["required_status_checks"]["strict"])
        self.assertEqual(policy["required_status_checks"]["contexts"], ["validate"])
        self.assertEqual(policy["required_pull_request_reviews"]["required_approving_review_count"], 0)

    def test_readback_valido(self):
        self.assertTrue(verify_protection(response()))

    def test_aceita_revisor_externo_quando_configurado(self):
        self.assertTrue(verify_protection(response(1), 1))

    def test_rejeita_falsas_aprovacoes(self):
        for value in (-1, 2, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    protection_policy(value)

    def test_rejeita_ci_nao_estrita_ou_ausente(self):
        a = response()
        a["required_status_checks"]["strict"] = False
        with self.assertRaisesRegex(ValueError, "estrito"):
            verify_protection(a)
        a = response()
        a["required_status_checks"]["contexts"] = []
        with self.assertRaisesRegex(ValueError, "validate"):
            verify_protection(a)

    def test_rejeita_pr_ausente(self):
        a = response()
        a["required_pull_request_reviews"] = None
        with self.assertRaisesRegex(ValueError, "PR"):
            verify_protection(a)

    def test_rejeita_bypass_admin(self):
        a = response()
        a["enforce_admins"]["enabled"] = False
        with self.assertRaisesRegex(ValueError, "Administradores"):
            verify_protection(a)

    def test_rejeita_force_push_delete_e_conversas_abertas(self):
        for key, value in (
            ("allow_force_pushes", True),
            ("allow_deletions", True),
            ("required_conversation_resolution", False),
        ):
            with self.subTest(key=key):
                a = response()
                a[key]["enabled"] = value
                with self.assertRaises(ValueError):
                    verify_protection(a)

    def test_rejeita_readback_sem_confirmacao(self):
        with self.assertRaises(ValueError):
            verify_protection({})
        with self.assertRaisesRegex(ValueError, "revisões"):
            verify_protection(response(), 1)


if __name__ == "__main__":
    unittest.main()
