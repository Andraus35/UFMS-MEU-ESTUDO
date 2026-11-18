"""Contraprovas de scripts/termux/ufms.sh (gh e curl falsos, remoto git local; sem rede, sem token)."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_termux_cria_repo_privado import FAKE_GH  # noqa: E402
from test_termux_verifica_token_privado import CODIGOS_PRIVADO, FAKE_CURL, PRIVADO, TOKEN  # noqa: E402

SCRIPT = ROOT / "scripts" / "termux" / "ufms.sh"


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                          env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid"))


class UfmsTermuxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        for nome, texto in (("gh", FAKE_GH), ("curl", FAKE_CURL)):
            arquivo = self.bin / nome
            arquivo.write_text(texto, encoding="utf-8")
            arquivo.chmod(arquivo.stat().st_mode | stat.S_IXUSR)
        self.estado = self.dir / "estado"
        self.estado.mkdir()
        self.plano_dir = self.dir / "planos"

    def tearDown(self):
        self.tmp.cleanup()

    def rodar(self, *args, entrada="", clone=None, **env):
        ambiente = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_DIR=str(self.estado),
                        UFMS_DIR=str(clone or ROOT), UFMS_SEM_PKG="1", UFMS_SEM_REDE="1",
                        UFMS_PLANO_DIR=str(self.plano_dir), TMPDIR=str(self.dir))
        ambiente.update(env)
        return subprocess.run(["bash", str(SCRIPT), *args], input=entrada, env=ambiente, capture_output=True, text=True,
                              timeout=120)

    def remoto_local(self):
        """Cria um remoto bare com um commit em main e devolve seu caminho."""
        bare, semente = self.dir / "remoto.git", self.dir / "semente"
        git("init", "-q", "--bare", "-b", "main", str(bare))
        git("init", "-q", "-b", "main", str(semente))
        (semente / "AGENTS.md").write_text("x", encoding="utf-8")
        (semente / "scripts").mkdir()
        (semente / "scripts" / "study_plan.py").write_text("x", encoding="utf-8")
        git("add", "-A", cwd=semente)
        git("commit", "-q", "-m", "um", cwd=semente)
        git("remote", "add", "origin", str(bare), cwd=semente)
        git("push", "-q", "origin", "main", cwd=semente)
        return bare, semente

    # estáticos -----------------------------------------------------------------------------------------------
    def test_sintaxe_executavel_e_sem_segredos_nem_escrita_remota(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
        self.assertTrue(SCRIPT.stat().st_mode & stat.S_IXUSR)
        texto = SCRIPT.read_text(encoding="utf-8")
        for proibido in ("GH_TOKEN", "github_pat_", "git push", "--force", "-X POST", "-X PATCH", "-X DELETE",
                         "gh repo create", "personal_results_writes_enabled=true", "read -rs"):
            self.assertNotIn(proibido, texto)
        # só três gravações remotas existem (consentimentos v3 e v4 e o plano), todas no repositório PRIVADO, por ato do proprietário
        gravacoes = [l for l in texto.splitlines() if "-X PUT" in l and not l.lstrip().startswith("#")]
        self.assertEqual(len(gravacoes), 3, gravacoes)
        for linha in gravacoes:
            self.assertIn('repos/$PRIVADO/contents/', linha)
        self.assertNotIn("UFMS-MEU-ESTUDO/contents", texto)

    def test_ajuda_lista_os_subcomandos_e_comando_desconhecido_falha(self):
        r = self.rodar("ajuda")
        self.assertEqual(r.returncode, 0)
        for comando in ("preparar", "atualizar", "diagnostico", "token", "plano"):
            self.assertIn(comando, r.stdout)
        r = self.rodar("destruir")
        self.assertEqual(r.returncode, 2)
        self.assertIn("desconhecido", r.stderr)

    # preparar e atualizar ------------------------------------------------------------------------------------
    def test_preparar_clona_e_depois_atualiza_sem_mexer_em_alteracao_local(self):
        bare, semente = self.remoto_local()
        clone = self.dir / "clone"
        r = self.rodar("preparar", clone=clone, UFMS_TESTE="1", UFMS_REMOTE=str(bare))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((clone / "AGENTS.md").exists())
        self.assertIn("clone criado", r.stdout)
        (semente / "novo.txt").write_text("1", encoding="utf-8")
        git("add", "-A", cwd=semente)
        git("commit", "-q", "-m", "dois", cwd=semente)
        git("push", "-q", "origin", "main", cwd=semente)
        r = self.rodar("preparar", clone=clone, UFMS_TESTE="1", UFMS_REMOTE=str(bare))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((clone / "novo.txt").exists())
        (clone / "AGENTS.md").write_text("alterado pelo dono", encoding="utf-8")
        r = self.rodar("atualizar", clone=clone, UFMS_TESTE="1", UFMS_REMOTE=str(bare))
        self.assertEqual(r.returncode, 1)
        self.assertIn("alterações locais", r.stderr)
        self.assertEqual((clone / "AGENTS.md").read_text(encoding="utf-8"), "alterado pelo dono")

    def test_preparar_nao_sobrescreve_pasta_que_nao_e_clone(self):
        bare, _ = self.remoto_local()
        clone = self.dir / "existente"
        clone.mkdir()
        (clone / "meu.txt").write_text("importante", encoding="utf-8")
        r = self.rodar("preparar", clone=clone, UFMS_TESTE="1", UFMS_REMOTE=str(bare))
        self.assertEqual(r.returncode, 1)
        self.assertIn("não vou sobrescrever", r.stderr)
        self.assertEqual((clone / "meu.txt").read_text(encoding="utf-8"), "importante")

    def test_remoto_so_pode_ser_trocado_em_modo_de_teste(self):
        bare, _ = self.remoto_local()
        oficial = "https://github.com/Andraus35/UFMS-MEU-ESTUDO.git"
        # o git reescreve a URL oficial para o remoto local (sem rede); o que se confere é a URL gravada no clone
        reescrita = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": f"url.{bare}.insteadOf", "GIT_CONFIG_VALUE_0": oficial}
        sem_teste, com_teste = self.dir / "clone_sem", self.dir / "clone_com"
        r = self.rodar("preparar", clone=sem_teste, UFMS_REMOTE="https://exemplo.invalid/outro.git", **reescrita)
        self.assertEqual(r.returncode, 0, r.stderr)
        url = git("config", "--get", "remote.origin.url", cwd=sem_teste).stdout.strip()
        self.assertEqual(url, oficial)  # sem UFMS_TESTE=1 o remoto trocado é ignorado
        r = self.rodar("preparar", clone=com_teste, UFMS_TESTE="1", UFMS_REMOTE=str(bare))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(git("config", "--get", "remote.origin.url", cwd=com_teste).stdout.strip(), str(bare))

    def test_comandos_exigem_o_clone(self):
        for comando in ("atualizar", "diagnostico", "plano", "token"):
            r = self.rodar(comando, clone=self.dir / "vazio")
            self.assertEqual(r.returncode, 1, comando)
            self.assertIn("Não achei o clone", r.stderr)

    # diagnóstico ---------------------------------------------------------------------------------------------
    def test_diagnostico_com_repositorio_privado_e_consentimento(self):
        (self.estado / "exists").touch()
        (self.estado / "private").write_text("true", encoding="utf-8")
        (self.estado / "consent.b64").write_text("QUJD", encoding="utf-8")
        r = self.rodar("diagnostico", GH_TOKEN="github_pat_SENTINELA0123456789abcdef")
        self.assertEqual(r.returncode, 0, r.stderr)
        for trecho in ("START de estudo (bootstrap): OK", "AGENTS.md", "escrita de resultados pessoais: DESABILITADA",
                       "gh: logado", "repositório privado de dados: existe, private=true", "consent.json): presente"):
            self.assertIn(trecho, r.stdout)
        self.assertNotIn("SENTINELA", r.stdout + r.stderr)
        self.assertNotIn("@", r.stdout)

    def test_diagnostico_sinaliza_repositorio_publico_consentimento_ausente_e_sem_login(self):
        (self.estado / "exists").touch()
        (self.estado / "private").write_text("false", encoding="utf-8")
        r = self.rodar("diagnostico")
        self.assertIn("ATENÇÃO: o repositório de dados existe e NÃO é privado", r.stdout)
        (self.estado / "private").write_text("true", encoding="utf-8")
        r = self.rodar("diagnostico")
        self.assertIn("consent.json): AUSENTE", r.stdout)
        (self.estado / "noauth").touch()
        r = self.rodar("diagnostico")
        self.assertIn("gh: NÃO logado", r.stdout)
        self.assertNotIn("repositório privado de dados", r.stdout)

    def test_diagnostico_nao_escreve_nada_no_github(self):
        (self.estado / "exists").touch()
        (self.estado / "private").write_text("true", encoding="utf-8")
        self.rodar("diagnostico")
        chamadas = (self.estado / "calls.log").read_text(encoding="utf-8")
        self.assertNotIn("-X", chamadas)
        self.assertNotIn("repo create", chamadas)

    # token ---------------------------------------------------------------------------------------------------
    def test_token_delega_ao_verificador_no_perfil_privado(self):
        r = self.rodar("token", entrada=TOKEN + "\n", FAKE_LOG=str(self.dir / "curl.log"),
                       FAKE_CODES=json.dumps(CODIGOS_PRIVADO), FAKE_REPOS=PRIVADO, FAKE_PRIVADOS=PRIVADO,
                       FAKE_EXPIRY="2026-12-15 12:00:00 -0400")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULTADO: CONFERE com o perfil privado", r.stdout)
        self.assertNotIn("SENTINELA", r.stdout + r.stderr)
        r = self.rodar("token", "qualquer", entrada=TOKEN + "\n")
        self.assertEqual(r.returncode, 1)

    # plano ---------------------------------------------------------------------------------------------------
    def test_plano_gera_arquivo_local_0600_fora_do_repositorio(self):
        r = self.rodar("plano", entrada="2026-11-16\n240\ndomingo\nambos\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        arquivos = list(self.plano_dir.glob("plano-*.json"))
        self.assertEqual(len(arquivos), 1)
        self.assertEqual(stat.S_IMODE(arquivos[0].stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.plano_dir.stat().st_mode), 0o700)
        plano = json.loads(arquivos[0].read_text(encoding="utf-8"))
        self.assertEqual(plano["parameters"]["rest_weekday"], 6)
        self.assertEqual(plano["parameters"]["daily_minutes"], 240)
        self.assertEqual(plano["parameters"]["exam_date"], "2027-01-17")
        self.assertTrue(all(d["weekday"] != 6 or d["kind"] != "teoria" for d in plano["days"]))
        self.assertIn("FORA do repositório", r.stdout)
        self.assertIn("Tutor", r.stdout)
        self.assertFalse(list(ROOT.glob("plano-*.json")))

    def test_plano_cargo_unico_e_nao_sobrescreve(self):
        self.rodar("plano", entrada="2026-11-16\n240\n6\n523\n")
        self.rodar("plano", entrada="2026-11-16\n240\n6\n523\n")
        self.assertEqual(len(list(self.plano_dir.glob("plano-2026-11-16-523*.json"))), 2)

    def test_plano_recusa_entradas_invalidas_sem_criar_arquivo(self):
        for entrada in ("2026-11-16\nabc\ndomingo\nambos\n", "2026-11-16\n5\ndomingo\nambos\n",
                        "2026-11-16\n240\nfunday\nambos\n", "2026-11-16\n240\ndomingo\n999\n",
                        "16/11/2026\n240\ndomingo\nambos\n", "2027-02-01\n240\ndomingo\nambos\n"):
            r = self.rodar("plano", entrada=entrada)
            self.assertEqual(r.returncode, 1, entrada)
            self.assertFalse(self.plano_dir.exists() and list(self.plano_dir.glob("plano-*")), entrada)

    def test_plano_recusa_pasta_dentro_do_repositorio(self):
        self.addCleanup(shutil.rmtree, ROOT / "plano_tmp", True)  # se o script falhar, não deixa lixo no repositório
        r = self.rodar("plano", entrada="2026-11-16\n240\ndomingo\nambos\n", UFMS_PLANO_DIR=str(ROOT / "plano_tmp"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("dentro do repositório", r.stderr)
        self.assertFalse((ROOT / "plano_tmp").exists())

    def test_documentos_apontam_para_a_ferramenta(self):
        for caminho in ("memory/HANDOFF.md", "docs/governanca/PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md"):
            self.assertIn("scripts/termux/ufms.sh", (ROOT / caminho).read_text(encoding="utf-8"), caminho)


if __name__ == "__main__":
    unittest.main()
