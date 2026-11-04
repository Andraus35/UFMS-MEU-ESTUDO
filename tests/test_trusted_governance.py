"""Adversarial tests: base-branch gate and Ed25519 human approval."""
import base64
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from trusted_governance import evaluate, approval_text, get_collection, signature_comment

HEAD = "a" * 40
BASE = "b" * 40
PR = 9


class TrustedGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        folder = Path(cls.tmp.name)
        cls.secret = folder / "private.pem"
        pub = folder / "public.pem"
        subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(cls.secret)], check=True)
        subprocess.run(["openssl", "pkey", "-in", str(cls.secret), "-pubout", "-out", str(pub)], check=True)
        cls.pubkey = base64.b64encode(pub.read_bytes()).decode("ascii")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def signed(self, message=None, actor_id=273433050, login="Andraus35"):
        message = message or approval_text(PR, HEAD, BASE)
        with tempfile.TemporaryDirectory() as folder:
            inp, out = Path(folder) / "msg", Path(folder) / "sig"
            inp.write_text(message)
            subprocess.run(["openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(self.secret),
                            "-in", str(inp), "-out", str(out)], check=True)
            body = signature_comment(message, out.read_bytes())
        return {"body": body, "user": {"login": login, "id": actor_id, "type": "User"}}

    def test_documentacao_comum_sem_assinatura(self):
        self.assertFalse(evaluate(PR, HEAD, BASE, ["docs/suporte.md"], [])["signed_review"])

    def test_caminhos_sensiveis_requerem_chave_humana(self):
        for path in ("ROADMAP.md", "AGENTS.md", "settings.json",
                     ".github/workflows/validate.yml", "scripts/ci_gate_contract.py",
                     "hooks/before_write.py", "rules/CORE.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Ed25519"):
                evaluate(PR, HEAD, BASE, [path], [], self.pubkey)

    def test_assinatura_valida_para_head_base_pr_exatos(self):
        response = evaluate(PR, HEAD, BASE, ["ROADMAP.md"], [self.signed()], self.pubkey)
        self.assertTrue(response["signed_review"])

    def test_assinaturas_de_outro_objeto_rejeitadas(self):
        for msg in (approval_text(PR, "0"*40, BASE), approval_text(PR, HEAD, "1"*40),
                    approval_text(PR+1, HEAD, BASE)):
            with self.subTest(msg=msg), self.assertRaisesRegex(ValueError, "Ed25519"):
                evaluate(PR, HEAD, BASE, ["ROADMAP.md"], [self.signed(msg)], self.pubkey)

    def test_comentario_de_outro_ator_rejeitado(self):
        for person in (self.signed(actor_id=1), self.signed(login="other")):
            with self.assertRaisesRegex(ValueError, "Ed25519"):
                evaluate(PR, HEAD, BASE, ["AGENTS.md"], [person], self.pubkey)

    def test_sem_chave_publica_ou_assinatura_alterada_rejeita(self):
        correct = self.signed()
        wrong = {"body": correct["body"][:-3] + "xxx", "user": correct["user"]}
        for pub, comments in (("", [correct]), (self.pubkey, [wrong])):
            with self.assertRaisesRegex(ValueError, "Ed25519"):
                evaluate(PR, HEAD, BASE, ["ROADMAP.md"], comments, pub)

    def test_ancora_imutavel_mesmo_com_assinatura(self):
        for path in ("scripts/trusted_governance.py",
                     ".github/workflows/trusted-governance.yml",
                     "tests/test_trusted_governance.py"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Immutable"):
                evaluate(PR, HEAD, BASE, [path], [self.signed()], self.pubkey)

    def test_dependencias_indiretas_exigem_assinatura(self):
        for path in ("scripts/core.py", "scripts/rebuild.py",
                     "tests/test_ci_gate_contract.py", "state/CURRENT.json",
                     "edital/manifest.json", "config/topics.csv",
                     "docs/pedagogia/PLANO_GATES.md", "memory/HANDOFF.md",
                     "docs/auditorias/PARECER.md", ".github/copilot-instructions.md",
                     "docs/OPERACAO.md", "docs/API_WRITE_GOVERNANCE.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "Ed25519"):
                evaluate(PR, HEAD, BASE, [path], [], self.pubkey)

    def test_mutacao_coordenada_da_ci_requer_assinatura(self):
        with self.assertRaisesRegex(ValueError, "Ed25519"):
            evaluate(PR, HEAD, BASE, [".github/workflows/validate.yml",
                                      "scripts/ci_gate_contract.py"], [], self.pubkey)

    def test_caminhos_invalidos_e_diff_vazio_falham(self):
        for path in ("", "/tmp/foo", "docs/../bad", "docs//bad", "docs\\bad"):
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                evaluate(PR, HEAD, BASE, [path], [])
        with self.assertRaisesRegex(ValueError, "empty diff"):
            evaluate(PR, HEAD, BASE, [], [])

    def test_limite_de_paginacao_e_falha_fechada(self):
        with mock.patch("trusted_governance.get_json", return_value=[{}]*100):
            with self.assertRaisesRegex(ValueError, "maximum"):
                get_collection("repos/owner/repo/pulls/1/files", "redacted", max_pages=2)
        with mock.patch("trusted_governance.get_json", return_value={}):
            with self.assertRaisesRegex(ValueError, "Unexpected"):
                get_collection("repos/owner/repo/pulls/1/files", "redacted")


if __name__ == "__main__":
    unittest.main()
