"""Contraprovas do guard offline de persistência privada (ADR-013)."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from private_persistence_guard import (PersistenceBlocked, PUBLIC_REPOSITORY, authorize_private_write,  # noqa: E402
                                       check_consent, check_destination, check_expected_head,
                                       check_new_event, check_visibility, confirm_readback)

PRIV = "Andraus35/ufms-dados-privados-teste"
NOW = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
CONSENT = {"version": "v1", "scope": "resultados_estudo",
           "granted_at": "2026-11-07T10:00:00+00:00", "revoked_at": None}
A, B = "a" * 40, "b" * 40


def reader(private=True, name=PRIV, **extra):
    return lambda target: {"private": private, "full_name": name, **extra}


def run(**over):
    args = dict(target=PRIV, configured=PRIV, consent=CONSENT, visibility_reader=reader(),
                writes_enabled=True, now=NOW)
    args.update(over)
    return authorize_private_write(**args)


class GuardTests(unittest.TestCase):
    def test_caminho_feliz_sintetico(self):
        self.assertTrue(run()["authorized"])

    def test_flag_desabilitada_bloqueia_mesmo_com_tudo_valido(self):
        for flag in (False, None, "true", 1):
            with self.subTest(flag=flag), self.assertRaisesRegex(PersistenceBlocked, "desabilitada"):
                run(writes_enabled=flag)

    def test_p2_repositorio_publico_nunca_e_destino(self):
        for t in (PUBLIC_REPOSITORY, PUBLIC_REPOSITORY.upper()):
            with self.subTest(t=t), self.assertRaisesRegex(PersistenceBlocked, "público"):
                run(target=t, configured=t)
        with self.assertRaisesRegex(PersistenceBlocked, "público"):
            run(configured=PUBLIC_REPOSITORY)

    def test_p2_destino_diferente_ou_invalido(self):
        with self.assertRaisesRegex(PersistenceBlocked, "diferente"):
            run(target="Andraus35/outro")
        for bad in ("", None, "sem-barra", "a/b/c", "x y/z"):
            with self.subTest(bad=bad), self.assertRaisesRegex(PersistenceBlocked, "inválido"):
                check_destination(bad, PRIV)

    def test_p3_consentimento(self):
        casos = {
            "ausente": None,
            "sem versão": {**CONSENT, "version": ""},
            "escopo": {**CONSENT, "scope": "outro"},
            "revogado": {**CONSENT, "revoked_at": "2026-11-07T11:00:00+00:00"},
            "sem fuso": {**CONSENT, "granted_at": "2026-11-07T10:00:00"},
            "data inválida": {**CONSENT, "granted_at": "ontem"},
            "futuro": {**CONSENT, "granted_at": (NOW + timedelta(days=1)).isoformat()},
        }
        for nome, consent in casos.items():
            with self.subTest(nome), self.assertRaisesRegex(PersistenceBlocked, "P3"):
                check_consent(consent, NOW)

    def test_p1_visibilidade_falha_fechada(self):
        def boom(_):
            raise TimeoutError("sem resposta")
        casos = {
            "público": reader(private=False),
            "private ausente": lambda t: {"full_name": PRIV},
            "string true": reader(private="true"),
            "visibility public": reader(visibility="public"),
            "identidade": reader(name="Andraus35/outro"),
            "malformada": lambda t: "ok",
            "nulo": lambda t: None,
            "timeout": boom,
        }
        for nome, leitor in casos.items():
            with self.subTest(nome), self.assertRaisesRegex(PersistenceBlocked, "P1"):
                check_visibility(PRIV, leitor)
        with self.assertRaises(PersistenceBlocked):
            run(visibility_reader=boom)

    def test_p5_idempotencia_e_cas(self):
        self.assertTrue(check_new_event("ev-2", ["ev-1"]))
        for bad in ("ev-1", "", None):
            with self.subTest(bad=bad), self.assertRaises(PersistenceBlocked):
                check_new_event(bad, ["ev-1"])
        self.assertTrue(check_expected_head(A, A))
        for exp, obs in ((A, B), ("curto", A), (A, None)):
            with self.subTest(exp=exp, obs=obs), self.assertRaises(PersistenceBlocked):
                check_expected_head(exp, obs)

    def test_p6_readback_nunca_confirma_sem_prova(self):
        self.assertEqual(confirm_readback(A, A, B, B), "confirmed")
        for args in ((A, B, B, B), (A, A, A, B), (A, None, B, B), ("x", A, B, B), (A, A, B, "")):
            with self.subTest(args=args):
                self.assertEqual(confirm_readback(*args), "pending")

    def test_modulo_nao_faz_rede_nem_escreve(self):
        src = (ROOT / "scripts/private_persistence_guard.py").read_text(encoding="utf-8")
        for proibido in ("urllib", "requests", "socket", "subprocess", "open(", "write_text", "os.environ"):
            self.assertNotIn(proibido, src)


if __name__ == "__main__":
    unittest.main()
