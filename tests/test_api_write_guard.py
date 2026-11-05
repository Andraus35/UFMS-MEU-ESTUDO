"""Contraprovas do adaptador de propostas de escrita API (sem chamadas de rede)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from api_write_guard import check_proposal, check_readback, git_blob_sha


OLD = "1" * 40
NEW = "2" * 40
BLOB = "3" * 40


def proposed(path="docs/OPERACAO.md", operation="update"):
    return {
        "repository": "Andraus35/UFMS-MEU-ESTUDO",
        "branch": "setup/harness-memory-v0-2",
        "base_branch": "main",
        "pr_number": 1,
        "draft": True,
        "merged": False,
        "state": "open",
        "expected_head_sha": OLD,
        "observed_head_sha": OLD,
        "files": [{"path": path, "operation": operation,
                   "expected_blob_sha": BLOB if operation == "update" else None,
                   "expected_new_blob_sha": "4" * 40}],
    }


class ApiWriteGuardTests(unittest.TestCase):
    def test_plano_documental_valido(self):
        result = check_proposal(proposed())
        self.assertEqual(result["expected_head_sha"], OLD)
        self.assertFalse(result["server_side_enforcement"])

    def test_git_blob_digest_uses_exact_bytes(self):
        import hashlib
        for payload in ("abc", "á", b"raw\\x00bytes"):
            binary = payload.encode("utf-8") if isinstance(payload, str) else payload
            expected = hashlib.sha1(
                b"blob " + str(len(binary)).encode("ascii") + b"\\x00" + binary
            ).hexdigest()
            self.assertEqual(git_blob_sha(payload), expected)

    def test_rejeita_digest_final_ausente_ou_invalido(self):
        for value in (None, "", "short", "g" * 40):
            p = proposed()
            p["files"][0]["expected_new_blob_sha"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "expected_new_blob_sha"):
                check_proposal(p)

    def test_rejeita_update_sem_mudanca_de_blob(self):
        p = proposed()
        p["files"][0]["expected_new_blob_sha"] = BLOB
        with self.assertRaisesRegex(ValueError, "Final blob must differ"):
            check_proposal(p)

    def test_rejeita_escrita_na_main(self):
        p = proposed()
        p["branch"] = "main"
        with self.assertRaisesRegex(ValueError, "branch de trabalho"):
            check_proposal(p)

    def test_rejeita_pr_nao_draft(self):
        p = proposed()
        p["draft"] = False
        with self.assertRaisesRegex(ValueError, "draft"):
            check_proposal(p)

    def test_rejeita_pr_mesclado(self):
        p = proposed()
        p["merged"] = True
        with self.assertRaisesRegex(ValueError, "encerrado"):
            check_proposal(p)

    def test_rejeita_head_concorrente(self):
        p = proposed()
        p["observed_head_sha"] = NEW
        with self.assertRaisesRegex(ValueError, "HEAD mudou"):
            check_proposal(p)

    def test_rejeita_sha_curto(self):
        p = proposed()
        p["expected_head_sha"] = OLD[:7]
        with self.assertRaisesRegex(ValueError, "SHA-1"):
            check_proposal(p)

    def test_rejeita_outro_repositorio(self):
        p = proposed()
        p["repository"] = "outro/outro"
        with self.assertRaisesRegex(ValueError, "Repositório"):
            check_proposal(p)

    def test_rejeita_eventos_pessoais_por_api(self):
        for path in ("state/events/2026-11.jsonl", "state/CURRENT.json",
                     "state/PROGRESS.csv", "private/perfil.json"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "sensível"):
                    check_proposal(proposed(path))

    def test_rejeita_modificacao_dos_proprios_gates(self):
        for path in ("settings.json", "AGENTS.md",
                     "scripts/api_write_guard.py", "scripts/write_policy.py",
                     ".github/workflows/validate.yml", "guardrails/CORE.md"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "sensível"):
                    check_proposal(proposed(path))

    def test_rejeita_path_traversal(self):
        for path in ("docs/../settings.json", "/docs/foo.md",
                     "docs//file.md", "docs\\foo.md"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    check_proposal(proposed(path))

    def test_rejeita_arquivo_secreto(self):
        with self.assertRaisesRegex(ValueError, "secreto"):
            check_proposal(proposed("docs/private.key"))

    def test_rejeita_create_com_blob_preexistente(self):
        p = proposed(operation="create")
        p["files"][0]["expected_blob_sha"] = BLOB
        with self.assertRaisesRegex(ValueError, "Criação"):
            check_proposal(p)

    def test_create_sem_blob_e_admitido_em_docs(self):
        self.assertTrue(check_proposal(proposed(operation="create")))

    def test_rejeita_sem_readback(self):
        with self.assertRaisesRegex(ValueError, "Readback"):
            check_readback(proposed(), NEW, OLD, NEW, "success")

    def test_rejeita_ci_de_outro_sha(self):
        with self.assertRaisesRegex(ValueError, "CI"):
            check_readback(proposed(), NEW, NEW, OLD, "success")

    def test_rejeita_ci_pendente(self):
        with self.assertRaisesRegex(ValueError, "CI"):
            check_readback(proposed(), NEW, NEW, NEW, "queued")

    def test_readback_correspondente_nao_autoriza_merge(self):
        result = check_readback(proposed(), NEW, NEW, NEW, "success")
        self.assertFalse(result["merge_authorized"])
        self.assertEqual(result["claimed_ci"], "success_unverified")
        self.assertEqual(result["readback"], "caller_asserted_only")
        self.assertFalse(result["ci_verified"])
        self.assertFalse(result["authenticated_remote_read"])


if __name__ == "__main__":
    unittest.main()
