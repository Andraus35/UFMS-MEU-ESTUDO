"""Contraprovas das chaves Ed25519 e da assinatura local dos comandos (sem rede; chaves só em diretório temporário)."""
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_commands as ac  # noqa: E402
import agent_keys as ak  # noqa: E402

BASE = {"schema_version": "1.0", "origin": "tutor", "operation": "enviar_mensagem", "destination": "proprietario",
        "params": {"texto": "Revisar GER-LEG com 10 questões."}, "idempotency_key": "k-00000001",
        "nonce": "n-0000000000000001", "issued_at": "2026-11-09T12:00:00Z", "signature": ""}


def run_cli(args, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = ak.main(args, **kwargs)
    return code, out.getvalue(), err.getvalue()


class AgentKeysTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.key = self.dir / "tutor.key"

    def tearDown(self):
        self.tmp.cleanup()

    def pub(self):
        return ak.generate(self.key, repo_root=ROOT)

    def test_gera_par_com_privada_0600_e_so_imprime_a_publica(self):
        code, out, err = run_cli(["generate", "--private-out", str(self.key)])
        self.assertEqual(code, 0, err)
        public = json.loads(out)["public_key"]
        secret_hex = self.key.read_text(encoding="utf-8").strip()
        self.assertEqual(stat.S_IMODE(self.key.stat().st_mode), 0o600)
        self.assertEqual(len(bytes.fromhex(public)), 32)
        self.assertNotIn(secret_hex, out + err)
        self.assertEqual(ac.ed25519_pure.public_key(bytes.fromhex(secret_hex)).hex(), public)

    def test_nao_sobrescreve_nem_grava_dentro_do_repositorio(self):
        self.pub()
        with self.assertRaises(FileExistsError):
            ak.generate(self.key, repo_root=ROOT)
        with self.assertRaises(ValueError):
            ak.generate(ROOT / "tutor.key", repo_root=ROOT)
        with self.assertRaises(ValueError):
            ak.generate(ROOT / "config" / "tutor.key", repo_root=ROOT)
        self.assertFalse((ROOT / "tutor.key").exists())
        code, _, err = run_cli(["generate", "--private-out", str(ROOT / "tutor.key")])
        self.assertEqual(code, 1)
        self.assertIn("repositório", err)

    def test_comando_assinado_localmente_e_aceito_pela_chave_publica(self):
        public = bytes.fromhex(self.pub())
        assinado = ak.sign_command(BASE, self.key)
        r = ac.validate_command(assinado, keys={"tutor": ("ed25519", public)}, now=datetime(2026, 11, 9, 12, 0, 30, tzinfo=timezone.utc),
                                ledger=ac.CommandLedger())
        self.assertEqual(r["decision"], ac.ACCEPTED, r)

    def test_chave_diferente_ou_comando_adulterado_e_recusado(self):
        self.pub()
        outra = self.dir / "outra.key"
        public_outra = bytes.fromhex(ak.generate(outra, repo_root=ROOT))
        now = datetime(2026, 11, 9, 12, 0, 30, tzinfo=timezone.utc)
        assinado = ak.sign_command(BASE, self.key)
        r = ac.validate_command(assinado, keys={"tutor": ("ed25519", public_outra)}, now=now, ledger=ac.CommandLedger())
        self.assertEqual(r["code"], "ASSINATURA_INVALIDA")
        assinado["params"]["texto"] = "adulterado"
        r = ac.validate_command(assinado, keys={"tutor": ("ed25519", bytes.fromhex(self.pub_of(self.key)))}, now=now,
                                ledger=ac.CommandLedger())
        self.assertEqual(r["code"], "ASSINATURA_INVALIDA")

    def pub_of(self, path):
        return ac.ed25519_pure.public_key(bytes.fromhex(Path(path).read_text(encoding="utf-8").strip())).hex()

    def test_auto_preenche_hora_e_nonce_unicos(self):
        self.pub()
        a, b = ak.sign_command(BASE, self.key, auto=True), ak.sign_command(BASE, self.key, auto=True)
        self.assertNotEqual(a["nonce"], b["nonce"])
        self.assertRegex(a["nonce"], r"^n-[0-9a-f]{24}$")
        agora = datetime.now(timezone.utc)
        emitido = datetime.fromisoformat(a["issued_at"][:-1] + "+00:00")
        self.assertLess(abs((agora - emitido).total_seconds()), 5)

    def test_chave_privada_com_permissao_aberta_ou_malformada(self):
        self.pub()
        os.chmod(self.key, 0o644)
        with self.assertRaises(ValueError):
            ak.sign_command(BASE, self.key)
        os.chmod(self.key, 0o600)
        self.key.write_text("zz\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            ak.sign_command(BASE, self.key)
        self.key.write_text("ab" * 31 + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            ak.sign_command(BASE, self.key)

    def test_cli_sign_e_check_ponta_a_ponta(self):
        public = self.pub()
        registro = self.dir / "chaves.json"
        registro.write_text(json.dumps({"keys": {"tutor": public, "coach": None}}), encoding="utf-8")
        arq = self.dir / "cmd.json"
        arq.write_text(json.dumps(BASE), encoding="utf-8")
        code, out, err = run_cli(["sign", "--key", str(self.key), "--command-file", str(arq), "--auto"])
        self.assertEqual(code, 0, err)
        signed = self.dir / "signed.json"
        signed.write_text(out, encoding="utf-8")
        code, out, _ = run_cli(["check", "--command-file", str(signed)], public_keys_path=registro)
        self.assertEqual((code, json.loads(out)["decision"]), (0, ac.ACCEPTED))
        coach = json.loads(signed.read_text(encoding="utf-8"))
        coach["origin"] = "coach"
        coach["signature"] = ""
        coach["signature"] = ac.sign_ed25519(coach, bytes.fromhex(self.key.read_text(encoding="utf-8").strip()))
        signed.write_text(json.dumps(coach), encoding="utf-8")
        code, out, _ = run_cli(["check", "--command-file", str(signed)], public_keys_path=registro)
        self.assertEqual((code, json.loads(out)["code"]), (1, "ORIGEM_DESCONHECIDA"))  # coach sem chave registrada

    def test_registro_de_chaves_publicas_do_repositorio_e_fail_closed(self):
        self.assertEqual(ak.load_public_keys(), {})  # sem chave real registrada, nada é aceito
        for ruim in ('{"keys": []}', '{"keys": {"zapia": "ab"}}', '{"keys": {"tutor": "zz"}}',
                     '{"keys": {"tutor": "' + "ab" * 31 + '"}}', "não é json"):
            arq = self.dir / "r.json"
            arq.write_text(ruim, encoding="utf-8")
            with self.assertRaises(ValueError, msg=ruim):
                ak.load_public_keys(arq)

    def test_nenhuma_chave_privada_no_repositorio(self):
        for caminho in list(ROOT.glob("config/*.json")) + [ROOT / "scripts/agent_keys.py"]:
            texto = caminho.read_text(encoding="utf-8")
            self.assertNotIn("BEGIN PRIVATE KEY", texto)
        dados = json.loads((ROOT / "config/agent_public_keys.json").read_text(encoding="utf-8"))
        self.assertEqual(set(dados["keys"]), {"tutor", "coach"})


if __name__ == "__main__":
    unittest.main()
