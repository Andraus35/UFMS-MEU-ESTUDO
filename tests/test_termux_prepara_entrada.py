"""C3: contraprovas de scripts/termux/prepara_entrada.sh com `gh` e `curl` FALSOS e com estado (sem rede, sem credencial)."""
import base64
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_REL = Path("scripts/termux/prepara_entrada.sh")
PUBLIC = "Andraus35/UFMS-MEU-ESTUDO"
ENTRADA = "Andraus35/ufms-meu-estudo-entrada"
DADOS = "Andraus35/ufms-meu-estudo-dados"
WF = ".github/workflows/promover.yml"
TOKEN = "github_pat_ficticio_0123456789abcdef"
TOKEN2 = "github_pat_ficticio_trocado_9876543210"

FAKE_GH = r'''#!/usr/bin/env python3
import base64, hashlib, json, os, sys
D = os.environ["FAKE_DIR"]
S = json.load(open(D + "/state.json"))
args = sys.argv[1:]
open(D + "/calls.log", "a").write(" ".join(args) + "\n")

def save():
    json.dump(S, open(D + "/state.json", "w"))

def erro(msg, code=1):
    sys.stderr.write(msg + "\n"); sys.exit(code)

if any(f in " ".join(args) for f in S.get("fail", [])):
    erro("gh: Server Error (HTTP 500)")
if args[0] == "auth":
    sys.exit(1 if S.get("noauth") else 0)
if args[:2] == ["repo", "create"]:
    S["repos"][args[2]] = {"private": "--private" in args, "fork": False, "forks_count": 0, "allow_forking": True,
                           "collaborators": 1, "invitations": 0}
    save(); sys.exit(0)

def repo_arg():
    return args[args.index("--repo") + 1]

if args[0] == "secret":
    if args[1] == "list":
        erro("unknown flag: --jq")  # gh antigo do Termux: `secret list` sem --jq; o script usa a API
    if args[1] == "set":
        S["secrets"].setdefault(repo_arg(), {})[args[2]] = sys.stdin.read(); save(); sys.exit(0)
if args[0] == "variable":
    v = S["variables"].setdefault(repo_arg(), {})
    if args[1] == "set":
        v[args[2]] = args[args.index("--body") + 1]; save(); sys.exit(0)
    if args[1] == "get":
        if args[2] not in v: erro("gh: Not Found (HTTP 404)")
        print(v[args[2]]); sys.exit(0)
if args[0] != "api":
    sys.exit(0)

rest = args[1:]
metodo, campos, jq, path, i = "GET", {}, None, None, 0
while i < len(rest):
    a = rest[i]
    if a == "-X": metodo = rest[i + 1]; i += 2
    elif a in ("-f", "-F"): k, _, v = rest[i + 1].partition("="); campos[k] = v; i += 2
    elif a == "--jq": jq = rest[i + 1]; i += 2
    else: path = a; i += 1

def saida(obj):
    if jq is None: print(json.dumps(obj)); sys.exit(0)
    if jq == "length": print(len(obj)); sys.exit(0)
    if jq == ".[].name": print("\n".join(obj)); sys.exit(0)
    v = obj[jq[1:]]
    print(("true" if v else "false") if isinstance(v, bool) else v); sys.exit(0)

def nao_achou():
    erro("gh: Not Found (HTTP 404)")

parts = path.split("/")
if parts[0] != "repos": nao_achou()
nome = parts[1] + "/" + parts[2]
tail = "/".join(parts[3:])
if nome == "Andraus35/UFMS-MEU-ESTUDO" and tail == "commits/main":
    saida({"sha": S["main_sha"]})
r = S["repos"].get(nome)
if r is None: nao_achou()
if tail == "":
    if metodo == "PATCH":
        if S.get("patch_fork_falha"): erro("gh: Validation Failed (HTTP 422)")
        r["allow_forking"] = False; save(); sys.exit(0)
    saida({"private": r["private"], "fork": r["fork"], "forks_count": r["forks_count"], "allow_forking": r["allow_forking"],
           "full_name": nome})
if tail == "actions/secrets":
    saida({"secrets": [{"name": n} for n in S["secrets"].get(nome, {})]}) if jq is None else (print("\n".join(S["secrets"].get(nome, {}).keys())), sys.exit(0))
if tail == "collaborators": saida([0] * r["collaborators"])
if tail == "invitations": saida([0] * r["invitations"])
ac = S["actions"].setdefault(nome, {"allowed_actions": "all", "default_workflow_permissions": "write"})
if tail == "actions/permissions":
    if metodo == "PUT": ac["allowed_actions"] = campos["allowed_actions"]; save(); sys.exit(0)
    saida(ac)
if tail == "actions/permissions/selected-actions":
    if metodo == "PUT" and campos.get("github_owned_allowed") == "false" and campos.get("verified_allowed") == "false":
        erro("gh: You cannot have 'verified_allowed', 'github_owned_allowed', and 'patterns_allowed' all disabled at the same time. (Conflict)")
    if metodo == "PUT": save(); sys.exit(0)
    saida({})
if tail == "actions/permissions/workflow":
    if metodo == "PUT": ac["default_workflow_permissions"] = campos["default_workflow_permissions"]; save(); sys.exit(0)
    saida(ac)
if tail.startswith("contents/"):
    chave = nome + "|" + tail[len("contents/"):]
    arqs = S["files"]
    if metodo == "PUT":
        if chave in arqs and campos.get("sha") != arqs[chave]["sha"]: erro("gh: Invalid request (HTTP 422)")
        bruto = base64.b64decode(campos["content"])
        if S.get("corromper_readback"): bruto += b"# adulterado\n"
        arqs[chave] = {"bytes": base64.b64encode(bruto).decode(), "sha": hashlib.sha1(bruto).hexdigest()}
        save(); sys.exit(0)
    if chave not in arqs: nao_achou()
    b = arqs[chave]["bytes"]
    wrapped = "\n".join(b[j:j + 60] for j in range(0, len(b), 60))  # como a API do GitHub
    saida({"sha": arqs[chave]["sha"], "content": wrapped})
nao_achou()
'''

FAKE_CURL = r'''#!/usr/bin/env python3
import json, os, sys
D = os.environ["FAKE_DIR"]
open(D + "/curl.log", "a").write(" ".join(sys.argv[1:]) + "\n")
sys.stdin.read()  # o cabeçalho com o token chega por stdin (-K -), nunca por argumento
url = sys.argv[-1]
codes = json.load(open(D + "/curl.json"))
for trecho, code in codes.items():
    if trecho in url:
        sys.stdout.write(str(code)); sys.exit(0)
sys.stdout.write("000")
'''


def sha256(dados):
    return hashlib.sha256(dados).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # clone de teste LIMPO e com git: o roteiro conta com HEAD == main pública e árvore sem alterações
        self.clone = self.tmp / "clone"
        for pasta in ("scripts", "config/modelos_fluxo"):
            shutil.copytree(ROOT / pasta, self.clone / pasta, ignore=shutil.ignore_patterns("__pycache__"))
        git = lambda *a: subprocess.run(["git", "-C", str(self.clone), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                        check=True, capture_output=True, text=True)
        git("init", "-q")
        git("add", "-A")
        git("commit", "-q", "-m", "clone de teste")
        self.head = git("rev-parse", "HEAD").stdout.strip()
        self.script = self.clone / SCRIPT_REL
        self.fake = self.tmp / "fake"
        self.fake.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for nome, codigo in (("gh", FAKE_GH), ("curl", FAKE_CURL)):
            (self.bin / nome).write_text(codigo, encoding="utf-8")
            (self.bin / nome).chmod((self.bin / nome).stat().st_mode | stat.S_IXUSR)
        self.estado = {
            "repos": {DADOS: self.repo(), PUBLIC: self.repo()}, "actions": {}, "secrets": {}, "variables": {}, "files": {},
            "main_sha": self.head, "fail": [],
        }
        self.salvar()
        (self.fake / "curl.json").write_text("{}")

    @staticmethod
    def repo(**mudar):
        r = {"private": True, "fork": False, "forks_count": 0, "allow_forking": True, "collaborators": 1, "invitations": 0}
        r.update(mudar)
        return r

    def salvar(self):
        (self.fake / "state.json").write_text(json.dumps(self.estado))

    def ler_estado(self):
        return json.loads((self.fake / "state.json").read_text())

    def rodar(self, entradas, *args, env=None):
        ambiente = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake)}
        ambiente.update(env or {})
        r = subprocess.run(["bash", str(self.script), *args], input="".join(l + "\n" for l in entradas), capture_output=True,
                           text=True, env=ambiente, timeout=120)
        return r

    def chamadas(self):
        p = self.fake / "calls.log"
        return p.read_text().splitlines() if p.exists() else []

    def escritas(self):
        return [c for c in self.chamadas() if re.search(r"-X (PUT|PATCH|DELETE)|repo create|secret set|variable set", c)]

    def com_entrada(self, **mudar):
        self.estado["repos"][ENTRADA] = self.repo(**mudar)
        self.salvar()

    def completo(self, r):
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULTADO: tudo conferido", r.stdout)


class CaminhoFelizTest(Base):
    def test_do_zero_cria_configura_guarda_segredo_instala_e_confere(self):
        r = self.rodar(["CRIAR", "CONFIGURAR", TOKEN, "INSTALAR"])
        self.completo(r)
        e = self.ler_estado()
        self.assertTrue(e["repos"][ENTRADA]["private"])
        self.assertEqual(e["actions"][ENTRADA], {"allowed_actions": "local_only", "default_workflow_permissions": "read"})
        self.assertEqual(e["secrets"][ENTRADA]["DADOS_TOKEN"], TOKEN)  # entrou por stdin
        instalado = base64.b64decode(e["files"][f"{ENTRADA}|{WF}"]["bytes"])
        self.assertNotIn(b"__VALIDADOR", instalado)
        self.assertIn(f"VALIDADOR_SHA: {self.head}".encode(), instalado)  # o SHA fixado é o da main pública
        self.assertIn(("VALIDADOR_GATE_SHA256: " + sha256((self.clone / "scripts/promotion_gate.py").read_bytes())).encode(), instalado)
        self.assertIn(("VALIDADOR_EMISSOR_SHA256: " + sha256((self.clone / "scripts/sinal_emissor.py").read_bytes())).encode(), instalado)
        self.assertEqual(e["variables"][ENTRADA]["FLUXO_SHA256"], sha256(instalado))
        self.assertIn("DESABILITADA", r.stdout)

    def test_reexecucao_com_tudo_pronto_nao_escreve_nem_pergunta(self):
        self.completo(self.rodar(["CRIAR", "CONFIGURAR", TOKEN, "INSTALAR"]))
        (self.fake / "calls.log").unlink()
        r = self.rodar([])
        self.completo(r)
        self.assertEqual(self.escritas(), [])
        self.assertIn("já instalado e idêntico", r.stdout)
        self.assertIn("DADOS_TOKEN já existe; mantido", r.stdout)

    def test_nada_do_que_o_roteiro_faz_toca_na_flag_nem_no_repositorio_publico(self):
        self.completo(self.rodar(["CRIAR", "CONFIGURAR", TOKEN, "INSTALAR"]))
        for c in self.escritas():
            self.assertNotIn(PUBLIC, c)
            self.assertNotIn(DADOS, c.replace(f"repos/{DADOS}", "") if "PATCH" not in c else "")  # só o PATCH de forks toca em dados
        fonte = self.script.read_text(encoding="utf-8")
        self.assertNotIn("personal_results_writes_enabled=true", fonte)
        self.assertNotIn("settings.json", fonte)


class P1EConfiguracaoTest(Base):
    def test_dados_ausente_ou_publico_bloqueia_sem_escrever(self):
        for repos in ({PUBLIC: self.repo()}, {PUBLIC: self.repo(), DADOS: self.repo(private=False)}):
            self.estado["repos"] = repos
            self.salvar()
            r = self.rodar(["CRIAR", "CONFIGURAR"])
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("BLOQUEADO", r.stderr)
            self.assertEqual(self.escritas(), [])

    def test_entrada_existente_e_publica_bloqueia_sem_escrever(self):
        self.com_entrada(private=False)
        r = self.rodar(["CRIAR", "CONFIGURAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("P1", r.stderr)
        self.assertEqual(self.escritas(), [])

    def test_sem_a_frase_criar_nada_e_criado(self):
        for resposta in ("", "criar", "SIM"):
            r = self.rodar([resposta])
            self.assertEqual(r.returncode, 1)
            self.assertNotIn(ENTRADA, self.ler_estado()["repos"])

    def test_criada_como_publica_por_engano_nao_segue(self):
        # o gh falso cria com --private; simulamos um repositório que aparece público após a criação
        self.estado["fail"] = []
        self.salvar()
        shutil.copy(self.bin / "gh", self.tmp / "gh_ok")
        codigo = (self.bin / "gh").read_text().replace('"private": "--private" in args', '"private": False')
        (self.bin / "gh").write_text(codigo)
        r = self.rodar(["CRIAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("P1", r.stderr)
        self.assertEqual([c for c in self.escritas() if "secret" in c or "contents" in c], [])

    def test_colaboradores_convites_e_forks_bloqueiam(self):
        casos = {"colaboradores": {"collaborators": 2}, "convites": {"invitations": 1}, "fork": {"fork": True},
                 "com forks": {"forks_count": 1}}
        for nome, mudanca in casos.items():
            self.com_entrada(**mudanca)
            r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
            self.assertEqual(r.returncode, 1, nome + r.stdout)
            self.assertEqual([c for c in self.chamadas() if "secret set" in c or "contents" in c and "PUT" in c], [], nome)
            (self.fake / "calls.log").unlink(missing_ok=True)

    def test_dados_com_colaborador_tambem_bloqueia(self):
        self.estado["repos"][DADOS]["collaborators"] = 2
        self.com_entrada()
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn(DADOS, r.stderr)

    def test_leitura_indisponivel_bloqueia_em_vez_de_assumir(self):
        self.com_entrada()
        self.estado["fail"] = ["collaborators"]
        self.salvar()
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.assertEqual(r.returncode, 1)

    def test_github_que_nao_desabilita_forks_nao_impede_se_nao_ha_colaborador_nem_forks(self):
        self.com_entrada()
        self.estado["patch_fork_falha"] = True
        self.salvar()
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.completo(r)
        self.assertIn("não aceitou desabilitar forks", r.stdout)

    def test_acoes_local_only_sem_chamar_selected_actions_e_retomada_de_execucao_parcial(self):
        # rodada real de 18/11/2026: o GitHub recusou `selected` com tudo desligado e a etapa 2 parou, com `entrada` já criada
        self.com_entrada()
        self.estado["actions"][ENTRADA] = {"allowed_actions": "selected", "default_workflow_permissions": "write"}
        self.salvar()
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.completo(r)
        self.assertEqual(self.ler_estado()["actions"][ENTRADA], {"allowed_actions": "local_only", "default_workflow_permissions": "read"})
        chamadas = (self.fake / "calls.log").read_text()
        self.assertNotIn("selected-actions", chamadas)
        self.assertIn("allowed_actions=local_only", chamadas)
        self.assertNotIn("secret list", chamadas)  # gh antigo do Termux não aceita --jq nele: a listagem vai pela API

    def test_sem_a_frase_configurar_fica_pendente_e_nao_aplica(self):
        self.com_entrada()
        r = self.rodar(["", TOKEN, "INSTALAR"])
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("configuração (forks e ações) NÃO aplicada", r.stderr)
        self.assertEqual(self.ler_estado()["actions"].get(ENTRADA, {}).get("allowed_actions", "all"), "all")


class SegredoTest(Base):
    def setUp(self):
        super().setUp()
        self.com_entrada()

    def test_token_com_formato_errado_bloqueia_e_nao_grava(self):
        for ruim in ("ghp_classico_0123456789abcdef", "qualquercoisa"):
            r = self.rodar(["CONFIGURAR", ruim, "INSTALAR"])
            self.assertEqual(r.returncode, 1, ruim)
            self.assertIn("fine-grained", r.stderr)
            self.assertEqual(self.ler_estado()["secrets"], {})

    def test_token_com_caractere_invisivel_cr_ou_espaco_no_meio_bloqueia_e_nao_grava(self):
        # prova real de 18/11/2026: o fluxo falhou com TOKEN_INVALIDO; o roteiro agora recusa o token malformado antes de guardá-lo
        for ruim in (TOKEN + "\r", TOKEN + "\u200b", "github_pat_com espaco_no_meio_0123456789"):
            self.setUp()  # estado novo a cada volta: a etapa 2 só pergunta CONFIGURAR enquanto não foi aplicada
            r = self.rodar(["CONFIGURAR", ruim, "INSTALAR"])
            self.assertEqual(r.returncode, 1, repr(ruim))
            self.assertIn("caractere fora do padrão", r.stderr, repr(ruim))
            self.assertEqual(self.ler_estado()["secrets"], {})
            self.assertNotIn("secret set", " ".join(self.chamadas()))
        self.setUp()
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.ler_estado()["secrets"][ENTRADA]["DADOS_TOKEN"], TOKEN)

    def test_token_vazio_vira_pendencia_e_nada_e_gravado(self):
        r = self.rodar(["CONFIGURAR", "", "INSTALAR"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("segredo DADOS_TOKEN NÃO guardado", r.stderr)
        self.assertEqual(self.ler_estado()["secrets"], {})

    def test_segredo_existente_nao_e_sobrescrito_sem_pedido(self):
        self.estado["secrets"][ENTRADA] = {"DADOS_TOKEN": "antigo-valor-ficticio"}
        self.salvar()
        self.completo(self.rodar(["CONFIGURAR", "INSTALAR"]))
        self.assertEqual(self.ler_estado()["secrets"][ENTRADA]["DADOS_TOKEN"], "antigo-valor-ficticio")

    def test_substituicao_so_com_a_variavel_explicita(self):
        self.estado["secrets"][ENTRADA] = {"DADOS_TOKEN": "antigo-valor-ficticio"}
        self.salvar()
        self.completo(self.rodar(["CONFIGURAR", TOKEN2, "INSTALAR"], env={"SUBSTITUIR_SEGREDO": "1"}))
        self.assertEqual(self.ler_estado()["secrets"][ENTRADA]["DADOS_TOKEN"], TOKEN2)

    def test_token_nunca_aparece_em_argumento_saida_ou_log(self):
        r = self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"])
        self.completo(r)
        self.assertNotIn(TOKEN, r.stdout + r.stderr)
        self.assertNotIn(TOKEN, "\n".join(self.chamadas()))
        self.assertNotIn(TOKEN, (self.fake / "calls.log").read_text())
        set_chamada = [c for c in self.chamadas() if c.startswith("secret set")]
        self.assertEqual(set_chamada, [f"secret set DADOS_TOKEN --repo {ENTRADA}"])  # sem --body: o valor veio por stdin

    def test_falha_ao_listar_segredos_bloqueia(self):
        self.estado["fail"] = ["actions/secrets"]
        self.salvar()
        self.assertEqual(self.rodar(["CONFIGURAR", TOKEN, "INSTALAR"]).returncode, 1)


class FluxoTest(Base):
    def setUp(self):
        super().setUp()
        self.com_entrada()
        self.estado["actions"][ENTRADA] = {"allowed_actions": "local_only", "default_workflow_permissions": "read"}
        self.estado["secrets"][ENTRADA] = {"DADOS_TOKEN": "x"}
        self.salvar()

    def test_clone_sujo_ou_diferente_da_main_publica_bloqueia(self):
        (self.clone / "scripts/promotion_gate.py").write_text("# adulterado\n")  # arquivo RASTREADO alterado
        r = self.rodar(["INSTALAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("rastreados alterados", r.stderr)
        subprocess.run(["git", "-C", str(self.clone), "checkout", "--", "scripts/promotion_gate.py"], check=True)
        self.estado["main_sha"] = "f" * 40
        self.salvar()
        r = self.rodar(["INSTALAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("git pull", r.stderr)
        self.assertNotIn(f"{ENTRADA}|{WF}", self.ler_estado()["files"])

    def test_arquivo_novo_nao_rastreado_nao_bloqueia_e_o_python_nao_suja_a_arvore(self):
        (self.clone / "anotacao-minha.txt").write_text("nota")
        self.completo(self.rodar(["INSTALAR"]))
        limpo = subprocess.run(["git", "-C", str(self.clone), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True).stdout
        self.assertEqual(limpo, "")
        self.assertFalse(list(self.clone.rglob("__pycache__")))  # nenhum bytecode deixado pelo roteiro

    def test_modelo_que_nao_passa_no_teste_estatico_nao_e_instalado(self):
        modelo = self.clone / "config/modelos_fluxo/promover.yml"
        modelo.write_text(modelo.read_text().replace("  workflow_dispatch:\n", "  workflow_dispatch:\n  pull_request_target:\n"))
        subprocess.run(["git", "-C", str(self.clone), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "adultera"], check=True)
        self.estado["main_sha"] = subprocess.run(["git", "-C", str(self.clone), "rev-parse", "HEAD"], capture_output=True,
                                                  text=True).stdout.strip()
        self.salvar()
        r = self.rodar(["INSTALAR"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("teste estático", r.stderr)
        self.assertNotIn(f"{ENTRADA}|{WF}", self.ler_estado()["files"])

    def test_modelo_sem_marcador_bloqueia(self):
        modelo = self.clone / "config/modelos_fluxo/promover.yml"
        modelo.write_text(modelo.read_text().replace("__VALIDADOR_SHA__", "fixo"))
        subprocess.run(["git", "-C", str(self.clone), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "sem marcador"], check=True)
        self.estado["main_sha"] = subprocess.run(["git", "-C", str(self.clone), "rev-parse", "HEAD"], capture_output=True,
                                                  text=True).stdout.strip()
        self.salvar()
        self.assertEqual(self.rodar(["INSTALAR"]).returncode, 1)

    def test_sem_a_frase_instalar_o_fluxo_fica_pendente(self):
        r = self.rodar([""])
        self.assertEqual(r.returncode, 2)
        self.assertIn("fluxo NÃO instalado", r.stderr)
        self.assertNotIn(f"{ENTRADA}|{WF}", self.ler_estado()["files"])

    def test_fluxo_existente_diferente_nao_e_sobrescrito_sem_atualizar(self):
        self.estado["files"][f"{ENTRADA}|{WF}"] = {"bytes": base64.b64encode(b"antigo\n").decode(), "sha": "1" * 40}
        self.salvar()
        r = self.rodar([""])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(base64.b64decode(self.ler_estado()["files"][f"{ENTRADA}|{WF}"]["bytes"]), b"antigo\n")
        self.assertEqual(self.ler_estado()["variables"], {})  # variável de hash só acompanha fluxo conferido
        r = self.rodar(["ATUALIZAR"])
        self.completo(r)
        novo = base64.b64decode(self.ler_estado()["files"][f"{ENTRADA}|{WF}"]["bytes"])
        self.assertIn(self.head.encode(), novo)
        self.assertEqual(self.ler_estado()["variables"][ENTRADA]["FLUXO_SHA256"], sha256(novo))

    def test_leitura_de_volta_divergente_nao_grava_a_variavel(self):
        self.estado["corromper_readback"] = True
        self.salvar()
        r = self.rodar(["INSTALAR"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("NÃO confere", r.stderr)
        self.assertEqual(self.ler_estado()["variables"], {})

    def test_o_fluxo_instalado_passa_no_verificador_com_valores_reais(self):
        self.completo(self.rodar(["INSTALAR"]))
        instalado = base64.b64decode(self.ler_estado()["files"][f"{ENTRADA}|{WF}"]["bytes"])
        gerado = self.tmp / "instalado.yml"
        gerado.write_bytes(instalado)
        r = subprocess.run([sys.executable, str(self.clone / "scripts/promotion_workflow_check.py"), "--check", "--instanciado",
                            "--arquivo", str(gerado)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


class SondaTest(Base):
    def codigos(self, **mudar):
        base = {f"/repos/{ENTRADA}/contents/zz-sonda.txt": 422, f"/repos/{DADOS}/contents/zz-sonda.txt": 403,
                f"/repos/{ENTRADA}/contents/.github/workflows/zz-sonda.yml": 404, f"/repos/{PUBLIC}/contents/zz-sonda.txt": 403}
        base.update(mudar)
        (self.fake / "curl.json").write_text(json.dumps(base))

    def test_token_com_o_alcance_esperado_passa(self):
        self.codigos()
        r = self.rodar([TOKEN2], "sondar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("RESULTADO: o token tem só o alcance esperado", r.stdout)

    def test_token_que_grava_no_historico_no_fluxo_ou_no_publico_diverge(self):
        for url in (f"/repos/{DADOS}/contents/zz-sonda.txt", f"/repos/{ENTRADA}/contents/.github/workflows/zz-sonda.yml",
                    f"/repos/{PUBLIC}/contents/zz-sonda.txt"):
            self.codigos(**{url: 422})
            r = self.rodar([TOKEN2], "sondar")
            self.assertEqual(r.returncode, 2, url)
            self.assertIn("DIVERGE", r.stdout)

    def test_token_sem_acesso_a_fila_diverge(self):
        self.codigos(**{f"/repos/{ENTRADA}/contents/zz-sonda.txt": 403})
        self.assertEqual(self.rodar([TOKEN2], "sondar").returncode, 2)

    def test_resposta_estranha_nao_conta_como_ok(self):
        self.codigos(**{f"/repos/{DADOS}/contents/zz-sonda.txt": 201})  # a sonda foi ACEITA: nunca é o esperado
        r = self.rodar([TOKEN2], "sondar")
        self.assertEqual(r.returncode, 2)

    def test_token_vazio_bloqueia_e_o_token_nunca_vai_em_argumento(self):
        self.codigos()
        self.assertEqual(self.rodar([""], "sondar").returncode, 1)
        r = self.rodar([TOKEN2], "sondar")
        self.assertNotIn(TOKEN2, (self.fake / "curl.log").read_text())
        self.assertNotIn(TOKEN2, r.stdout + r.stderr)

    def test_sonda_usa_corpo_vazio_e_so_metodo_put_em_caminhos_de_sonda(self):
        self.codigos()
        self.rodar([TOKEN2], "sondar")
        for linha in (self.fake / "curl.log").read_text().splitlines():
            self.assertIn("-X PUT", linha)
            self.assertIn("--data {}", linha)
            self.assertIn("zz-sonda", linha)


class ContratoDoScriptTest(unittest.TestCase):
    def setUp(self):
        self.fonte = (ROOT / SCRIPT_REL).read_text(encoding="utf-8")

    def test_sintaxe_do_bash(self):
        r = subprocess.run(["bash", "-n", str(ROOT / SCRIPT_REL)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_destinos_fixos_e_nunca_o_publico(self):
        self.assertIn(f'ENTRADA="{ENTRADA}"', self.fonte)
        self.assertIn(f'DADOS="{DADOS}"', self.fonte)
        self.assertIn("P2:", self.fonte)

    def test_cada_escrita_tem_frase_e_nao_ha_atalho_que_pule(self):
        for frase in ("CRIAR", "CONFIGURAR", "INSTALAR", "ATUALIZAR"):
            self.assertIn(f"pergunta {frase}", self.fonte)
        for proibido in ("--yes", "--force", "-f force", "set -x", "echo \"$TOKEN\"", "printf '%s' \"$TOKEN\" |  tee", "--body \"$TOKEN\"",
                         "--body $TOKEN", "> \"$TMP/token", "curl -u"):
            self.assertNotIn(proibido, self.fonte)

    def test_segredo_so_por_stdin_e_entrada_oculta(self):
        self.assertIn("read -rs TOKEN", self.fonte)
        self.assertIn("gh secret set DADOS_TOKEN --repo", self.fonte)
        self.assertIsNone(re.search(r"gh secret set[^\n]*--body", self.fonte))
        self.assertIn('unset TOKEN', self.fonte)

    def test_nao_habilita_a_flag_e_nao_cria_fila_que_dispararia_o_fluxo(self):
        self.assertIsNone(re.search(r"personal_results_writes_enabled\s*[:=]\s*true", self.fonte))
        self.assertNotIn("fila/entradas", self.fonte)
        self.assertNotIn("comandos/", self.fonte.replace("comandos", ""))

    def test_declara_os_limites(self):
        for trecho in ("NÃO habilita a escrita de resultados", "NÃO prova o fluxo de ponta a ponta", "C5", "ato seu"):
            self.assertIn(trecho, self.fonte)


    def test_prompts_nomeiam_cada_token_e_proibem_a_troca(self):
        # o proprietário regenera dois tokens; o prompt precisa dizer qual colar em cada etapa
        etapa3 = next(l for l in self.fonte.splitlines() if "Cole o token" in l and "zapia_dados" in l and "SÓ" not in l)
        self.assertIn('"zapia_dados"', etapa3)
        self.assertIn("NÃO o zapia token", etapa3)
        sonda = next(l for l in self.fonte.splitlines() if "Cole o token" in l and "SÓ para `entrada`" in l)
        self.assertIn('"zapia token"', sonda)
        self.assertIn("NÃO o zapia_dados", sonda)


if __name__ == "__main__":
    unittest.main()
