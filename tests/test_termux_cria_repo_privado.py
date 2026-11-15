"""Contraprovas de scripts/termux/cria_repo_privado.sh com um `gh` falso (sem rede, sem credencial)."""
import base64
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import private_persistence_guard as guard  # noqa: E402

SCRIPT = ROOT / "scripts" / "termux" / "cria_repo_privado.sh"
ADR = ROOT / "docs" / "governanca" / "ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md"
REPO = "Andraus35/ufms-meu-estudo-dados"

FAKE_GH = r'''#!/usr/bin/env bash
D="$FAKE_DIR"
echo "$*" >> "$D/calls.log"
case "$1" in
  auth) [ -f "$D/noauth" ] && exit 1; exit 0;;
  repo) touch "$D/exists"; printf '%s' "${FAKE_CREATE_PRIVATE:-true}" > "$D/private"; exit 0;;
  api)
    shift
    if [ "$1" = "-X" ]; then
      for a in "$@"; do case "$a" in content=*) printf '%s' "${a#content=}" > "$D/consent.b64";; esac; done
      exit 0
    fi
    path="$1"; shift
    case "$path" in
      repos/*/contents/consent.json)
        if [ -f "$D/consent.b64" ]; then
          case "$*" in
            *.sha*) echo "abc123";;
            *) if [ -n "${FAKE_READBACK_BAD:-}" ]; then echo "AAAA"; else cat "$D/consent.b64"; fi;;
          esac
        else echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi;;
      repos/*)
        if [ -f "$D/error500" ]; then echo "gh: Server Error (HTTP 500)" >&2; exit 1; fi
        if [ -f "$D/exists" ]; then cat "$D/private"; else echo "gh: Not Found (HTTP 404)" >&2; exit 1; fi;;
    esac;;
esac
exit 0
'''


class CriaRepoPrivadoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
        self.state = self.dir / "state"
        self.state.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def existe(self, privado=True):
        (self.state / "exists").touch()
        (self.state / "private").write_text("true" if privado else "false", encoding="utf-8")

    def rodar(self, entrada="", **env):
        ambiente = dict(os.environ, FAKE_DIR=str(self.state), PATH=f"{self.bin}:{os.environ['PATH']}", **env)
        return subprocess.run(["bash", str(SCRIPT)], input=entrada, env=ambiente, capture_output=True, text=True,
                              timeout=60)

    def chamadas(self):
        arquivo = self.state / "calls.log"
        return arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""

    def consentimento(self):
        bruto = (self.state / "consent.b64").read_text(encoding="utf-8")
        return json.loads(base64.b64decode(bruto).decode("utf-8"))

    def test_sintaxe_executavel_e_destino_fixo_nunca_o_publico(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(f'REPO="{REPO}"', texto)
        self.assertEqual(guard.check_destination(REPO, REPO), REPO)
        with self.assertRaises(guard.PersistenceBlocked):
            guard.check_destination(guard.PUBLIC_REPOSITORY, guard.PUBLIC_REPOSITORY)
        self.assertIn("--private", texto)
        for proibido in ("--public", "curl", "GH_TOKEN", "github_pat_", "git push", "--force", "personal_results_writes_enabled=true"):
            self.assertNotIn(proibido, texto)

    def test_repositorio_privado_existente_registra_consentimento_valido_pelo_guard(self):
        self.existe(True)
        r = self.rodar("CONSINTO v2\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("repo create", self.chamadas())
        consentimento = self.consentimento()
        self.assertEqual(guard.check_consent(consentimento), "v2")
        self.assertEqual(consentimento["scope"], guard.CONSENT_SCOPE)
        self.assertIsNone(consentimento["revoked_at"])
        self.assertEqual(consentimento["text_sha256"], hashlib.sha256(consentimento["text"].encode("utf-8")).hexdigest())
        self.assertIn("Versão: v2.", consentimento["text"])
        self.assertIn(consentimento["text"], ADR.read_text(encoding="utf-8"))
        self.assertIn("readback", r.stdout)
        self.assertIn("DESABILITADA", r.stdout)

    def test_repositorio_publico_bloqueia_sem_gravar_nada(self):
        self.existe(False)
        r = self.rodar("CONSINTO v2\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("NÃO é privado", r.stderr)
        self.assertNotIn("-X PUT", self.chamadas())
        self.assertFalse((self.state / "consent.b64").exists())

    def test_inexistente_cria_privado_e_exige_a_frase(self):
        r = self.rodar("nao\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("repo create", self.chamadas())
        r = self.rodar("CRIAR\nCONSINTO v2\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        criacao = [l for l in self.chamadas().splitlines() if l.startswith("repo create")]
        self.assertEqual(len(criacao), 1)
        self.assertIn(REPO, criacao[0])
        self.assertIn("--private", criacao[0])
        self.assertEqual(guard.check_consent(self.consentimento()), "v2")

    def test_criado_mas_nao_confirmado_como_privado_bloqueia(self):
        r = self.rodar("CRIAR\nCONSINTO v2\n", FAKE_CREATE_PRIVATE="false")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("BLOQUEADO (P1)", r.stderr)
        self.assertFalse((self.state / "consent.b64").exists())

    def test_erro_que_nao_e_404_nao_cria_nem_grava(self):
        (self.state / "error500").touch()
        r = self.rodar("CRIAR\nCONSINTO v2\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("repo create", self.chamadas())
        self.assertFalse((self.state / "consent.b64").exists())

    def test_sem_a_frase_do_consentimento_nada_e_gravado(self):
        self.existe(True)
        for resposta in ("\n", "sim\n", "consinto v2\n", "CONSINTO v1\n", ""):
            r = self.rodar(resposta)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("NÃO registrado", r.stdout)
            self.assertFalse((self.state / "consent.b64").exists(), resposta)
            self.assertNotIn("-X PUT", self.chamadas())

    def test_consentimento_existente_nao_e_sobrescrito(self):
        self.existe(True)
        (self.state / "consent.b64").write_text("ORIGINAL", encoding="utf-8")
        r = self.rodar("CONSINTO v2\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("mantido", r.stdout)
        self.assertEqual((self.state / "consent.b64").read_text(encoding="utf-8"), "ORIGINAL")
        self.assertNotIn("-X PUT", self.chamadas())

    def test_readback_divergente_fica_pendente(self):
        self.existe(True)
        r = self.rodar("CONSINTO v2\n", FAKE_READBACK_BAD="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("PENDENTE (P6)", r.stderr)

    def test_sem_login_do_gh_para_antes_de_qualquer_coisa(self):
        (self.state / "noauth").touch()
        r = self.rodar("CRIAR\nCONSINTO v2\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("gh auth login", r.stderr)
        self.assertNotIn("repo create", self.chamadas())

    def test_nada_vaza_credencial_na_saida(self):
        self.existe(True)
        r = self.rodar("CONSINTO v2\n", GH_TOKEN="github_pat_SEGREDO0123456789")
        self.assertNotRegex(r.stdout + r.stderr, r"github_pat_|ghp_[A-Za-z0-9]{10,}")
        self.assertNotIn("SEGREDO", self.chamadas())


    def test_documentos_apontam_para_o_script_e_a_flag_continua_falsa(self):
        for caminho in ("docs/governanca/ADR013_PERSISTENCIA_PRIVADA_DESENHO_20261107.md", "memory/HANDOFF.md",
                        "docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md"):
            self.assertIn("cria_repo_privado.sh", (ROOT / caminho).read_text(encoding="utf-8"), caminho)
        configuracao = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(re.search(r'"personal_results_writes_enabled":\s*false', json.dumps(configuracao, indent=2)) is not None, True)


if __name__ == "__main__":
    unittest.main()
