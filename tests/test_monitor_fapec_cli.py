"""Provas CLI ponta a ponta do monitor FAPEC usando fixtures offline.

Confere a tradução dos estados para exit codes e protege os arquivos canônicos
contra mutação durante a execução do modo fixture.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "monitor_fapec.py"
CONTEST = (
    "CONCURSO PÚBLICO PARA INGRESSO NA CARREIRA DE TÉCNICO-ADMINISTRATIVOS "
    "EM EDUCAÇÃO DA FUNDAÇÃO UNIVERSIDADE FEDERAL DE MATO GROSSO DO SUL"
)
OPENING = "EDITAL PROGEP/UFMS N. º 001/2026 - Edital de Abertura"
CANONICAL_FILES = (
    ROOT / "EDITAL_UFMS_152_2026.md",
    ROOT / "edital" / "manifest.json",
    ROOT / "edital" / "fontes_oficiais.json",
)


def page(extra="", contest=CONTEST):
    return (
        "<html><body><p>" + contest + "</p><p>30/10/2026</p><p>"
        + OPENING + "</p><a>DOWNLOAD</a>" + extra + "</body></html>"
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FapecMonitorCliTests(unittest.TestCase):
    def run_fixture(self, html):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "page.html"
            fixture.write_text(html, encoding="utf-8")
            fixture_before = fixture.read_bytes()
            canonical_before = {path: digest(path) for path in CANONICAL_FILES}

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--fixture", str(fixture)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            self.assertEqual(fixture.read_bytes(), fixture_before)
            self.assertEqual(
                {path: digest(path) for path in CANONICAL_FILES},
                canonical_before,
                "modo fixture não pode alterar fonte, manifesto ou registro canônico",
            )
            self.assertEqual(completed.stderr, "")
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["writes"])
            self.assertFalse(payload["normative_revision_verified"])
            self.assertEqual(payload["scope"], "single_fapec_contest_page_only")
            self.assertEqual(
                payload["checked_url"],
                "https://portal.concurso.fundacaofapec.org.br/edital/ver/22",
            )
            return completed.returncode, payload

    def test_page_without_detected_change_exits_zero_but_is_not_exhaustive(self):
        code, payload = self.run_fixture(page())
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "no_change_observed_on_single_page")
        self.assertFalse(payload["publication_candidate"])
        self.assertIn("outras fontes", payload["reason"])

    def test_publication_candidate_exits_two_for_manual_review(self):
        code, payload = self.run_fixture(page("<p>ERRATA publicada</p>"))
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "needs_manual_review")
        self.assertTrue(payload["publication_candidate"])

    def test_unverifiable_page_exits_three_not_zero(self):
        code, payload = self.run_fixture(
            page(contest="CONCURSO MUNICIPAL DE OUTRA CIDADE")
        )
        self.assertEqual(code, 3)
        self.assertEqual(payload["status"], "unverifiable")
        self.assertFalse(payload["publication_candidate"])


if len(CANONICAL_FILES) != 3:
    raise RuntimeError("Conjunto de arquivos canônicos do teste foi alterado")


if __name__ == "__main__":
    unittest.main()
