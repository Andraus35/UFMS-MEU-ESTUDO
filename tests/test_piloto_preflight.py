"""PF: pré-voo do piloto (S11-R2, R10). Leituras injetadas sintéticas; uma contraprova por item VERMELHO e por item ÂMBAR."""
import ast
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import piloto_preflight as pf  # noqa: E402

DOC = (ROOT / "docs/governanca/E5_CONSENTIMENTO_V4_PROPOSTA_20261118.md").read_text(encoding="utf-8")
TEXTO = next(l[2:].strip() for l in DOC.splitlines() if l.startswith("> "))
AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
MAIN = "f654cc28c823960655d90888ae4d177dc4d339a0"
H = "b092dd9ba636" + "0" * 52


def consent(**mud):
    c = {"version": "v4", "scope": "resultados_estudo", "inclui": ["resultados_estudo", "plano_estudo", "leitura_projecoes_sessoes_app_claude"],
         "granted_at": "2026-11-19T12:00:00+00:00", "revoked_at": None, "text": TEXTO, "text_sha256": hashlib.sha256(TEXTO.encode("utf-8")).hexdigest()}
    c.update(mud)
    return c


def repo(**mud):
    r = {"private": True, "fork": False, "forks_count": 0, "colaboradores": 1, "convites": 0}
    r.update(mud)
    return r


def leituras(**mud):
    base = {
        "flags": {"personal_results_writes_enabled": False, "private_flow_promotion_enabled_no_sha_fixado": False},
        "fluxo": {"sha_fixado": MAIN, "hash_instalado": H, "hash_esperado": H, "hash_esperado_sha": MAIN},
        "main_sha": MAIN,
        "repositorios": {"entrada": repo(), "dados": repo()},
        "consentimento": consent(),
        "tokens": [{"nome": "zapia_dados", "expira_em": "2026-12-18T00:00:00+00:00"}, {"nome": "zapia token", "expira_em": "2026-12-18T00:00:00+00:00"}],
        "ci": {"head_sha": MAIN, "conclusoes": ["success", "success"]},
    }
    base.update(mud)
    return base


def roda(l, modo="abertura", agora=AGORA):
    return pf.executar(l, modo, agora)


def item(saida, ident):
    return next(i for i in saida["itens"] if i["id"] == ident)


class CaminhoFelizTests(unittest.TestCase):
    def test_abertura_toda_verde(self):
        s = roda(leituras())
        self.assertEqual(s["resultado"], "VERDE", [i for i in s["itens"] if i["resultado"] != "VERDE"])
        self.assertEqual({i["id"] for i in s["itens"]},
                         {"flags", "fluxo_hash", "sha_fixado", "repo_entrada", "repo_dados", "consentimento_v4", "tokens", "ci", "contraprova_gerador"})

    def test_repouso_toda_verde(self):
        self.assertEqual(roda(leituras(), "repouso")["resultado"], "VERDE")

    def test_pos_janela_verde_com_flag_do_fluxo_ligada_no_sha_fixado(self):
        l = leituras(janela_aberta_em="2026-11-20T08:00:00+00:00")
        l["flags"]["private_flow_promotion_enabled_no_sha_fixado"] = True
        s = roda(l, "pos_janela")
        self.assertEqual(s["resultado"], "VERDE", [i for i in s["itens"] if i["resultado"] != "VERDE"])
        self.assertIn("janela", {i["id"] for i in s["itens"]})


class ContraprovasVermelhasTests(unittest.TestCase):
    """Cada gatilho vermelho de S11-R10 classifica VERMELHO já no pré-voo, antes de qualquer escrita."""

    def vermelho(self, l, ident, modo="abertura"):
        s = roda(l, modo)
        self.assertEqual(s["resultado"], "VERMELHO", ident)
        self.assertEqual(item(s, ident)["resultado"], "VERMELHO", ident)

    def test_flag_do_publico_ligada(self):
        l = leituras()
        l["flags"]["personal_results_writes_enabled"] = True
        for modo in ("abertura", "repouso"):
            self.vermelho(copy.deepcopy(l), "flags", modo)
        l2 = leituras(janela_aberta_em="2026-11-20T08:00:00+00:00")
        l2["flags"].update(personal_results_writes_enabled=True, private_flow_promotion_enabled_no_sha_fixado=True)
        self.vermelho(l2, "flags", "pos_janela")

    def test_flag_do_fluxo_errada_para_o_modo(self):
        l = leituras()
        l["flags"]["private_flow_promotion_enabled_no_sha_fixado"] = True
        self.vermelho(l, "flags", "abertura")  # ligada fora da janela
        self.vermelho(copy.deepcopy(l), "flags", "repouso")  # fechamento sem reinstalar: o fluxo continua ligado no SHA fixado
        self.vermelho(leituras(janela_aberta_em="2026-11-20T08:00:00+00:00"), "flags", "pos_janela")  # janela sem a flag ligada

    def test_flags_ausentes_ou_nao_booleanas(self):
        for flags in (None, {}, {"personal_results_writes_enabled": "false", "private_flow_promotion_enabled_no_sha_fixado": False},
                      {"personal_results_writes_enabled": False, "private_flow_promotion_enabled_no_sha_fixado": 0}):
            l = leituras()
            l["flags"] = flags
            self.vermelho(l, "flags")

    def test_hash_do_fluxo_diferente_ou_malformado(self):
        for mud in ({"hash_instalado": "d2cad256cbd9" + "0" * 52}, {"hash_instalado": "xyz"}, {"hash_instalado": None}):
            l = leituras()
            l["fluxo"].update(mud)
            self.vermelho(l, "fluxo_hash")
        l = leituras()
        l["fluxo"] = None
        self.vermelho(l, "fluxo_hash")

    def test_sha_fixado_diferente_da_main_pede_reinstalar(self):
        l = leituras()
        l["fluxo"]["sha_fixado"] = "f3f756b6f52215c023dd466a8e88547c9cded45a"
        s = roda(l)
        self.assertEqual(item(s, "sha_fixado")["resultado"], "VERMELHO")
        self.assertIn("ATUALIZAR", item(s, "sha_fixado")["motivo"])
        for ruim in (None, "curto", "G" * 40):
            l = leituras()
            l["fluxo"]["sha_fixado"] = ruim
            self.vermelho(l, "sha_fixado")
        self.vermelho(leituras(main_sha="abc"), "sha_fixado")

    def test_repositorio_nao_privado(self):
        for nome in pf.REPOS:
            l = leituras()
            l["repositorios"][nome] = repo(private=False)
            self.vermelho(l, f"repo_{nome}")

    def test_repositorio_com_campos_ausentes_ou_leitura_indisponivel(self):
        l = leituras()
        l["repositorios"]["dados"] = {"private": True}
        self.vermelho(l, "repo_dados")
        l = leituras()
        l["repositorios"]["entrada"] = None
        self.vermelho(l, "repo_entrada")
        l = leituras()
        l["repositorios"] = None
        self.assertEqual(roda(l)["resultado"], "VERMELHO")
        l = leituras()
        l["repositorios"]["dados"] = repo(forks_count=-1)
        self.vermelho(l, "repo_dados")

    def test_consentimento_invalido_ou_revogado(self):
        for c in (None, consent(version="v3"), consent(revoked_at="2026-11-19T13:00:00+00:00"), consent(inclui=["resultados_estudo"]),
                  consent(text_sha256="0" * 64), consent(granted_at="2026-12-01T00:00:00+00:00"), "texto"):
            self.vermelho(leituras(consentimento=c), "consentimento_v4")

    def test_ci_ausente_ou_malformada_fecha(self):
        for ci in (None, {}, {"head_sha": MAIN, "conclusoes": []}, {"head_sha": "x", "conclusoes": ["success"]}, {"head_sha": MAIN, "conclusoes": [1]}):
            self.vermelho(leituras(ci=ci), "ci")

    def test_tokens_ausentes_ou_sem_expiracao_fecham(self):
        for tokens in (None, [], [{"nome": "zapia_dados"}], [{"nome": "zapia_dados", "expira_em": "2026-12-18T00:00:00"}],
                       [{"nome": "Token Real 123!", "expira_em": "2026-12-18T00:00:00+00:00"}], ["texto"]):
            self.vermelho(leituras(tokens=tokens), "tokens")

    def test_janela_aberta_ha_mais_de_24_h_ou_sem_hora(self):
        base = leituras()
        base["flags"]["private_flow_promotion_enabled_no_sha_fixado"] = True
        for aberta in (None, "2026-11-19T11:00:00+00:00", "ontem", "2026-11-20T08:00:00", "2026-11-21T08:00:00+00:00"):
            l = copy.deepcopy(base)
            l["janela_aberta_em"] = aberta
            self.vermelho(l, "janela", "pos_janela")

    def test_hash_esperado_de_outro_sha_ou_sem_sha_fecha(self):
        for mud in ({"hash_esperado_sha": "1" * 40}, {"hash_esperado_sha": None}, {"hash_esperado_sha": "curto"}):
            l = leituras()
            l["fluxo"].update(mud)
            self.vermelho(l, "fluxo_hash")
        l = leituras()
        del l["fluxo"]["hash_esperado_sha"]
        self.vermelho(l, "fluxo_hash")

    def test_nome_de_token_com_digito_ou_hifen_nao_e_erro(self):
        for nome in ("zapia_dados2", "Zapia-dados", "token 2"):
            l = leituras(tokens=[{"nome": nome, "expira_em": "2026-12-18T00:00:00+00:00"}])
            self.assertEqual(item(roda(l), "tokens")["resultado"], "VERDE", nome)

    def test_token_ja_expirado_e_vermelho(self):
        for expira in ("2026-11-19T00:00:00+00:00", "2026-11-20T12:00:00+00:00"):
            self.vermelho(leituras(tokens=[{"nome": "zapia_dados", "expira_em": expira}]), "tokens")

    def test_leitura_que_quebra_a_conferencia_vira_item_vermelho_sem_derrubar(self):
        for texto in ("\ud800", "\x00", "a" * 10_000_000):
            c = consent()
            c["text"] = texto
            s = roda(leituras(consentimento=c))  # não levanta
            self.assertEqual(s["resultado"], "VERMELHO")
            self.assertEqual(item(s, "consentimento_v4")["resultado"], "VERMELHO")
        for ruim in ({"flags": object()}, {"tokens": [{"nome": object(), "expira_em": 3}]}, {"ci": {"head_sha": MAIN, "conclusoes": [[]]}}):
            self.assertEqual(roda(leituras(**ruim))["resultado"], "VERMELHO")

    def test_entrada_que_nao_e_objeto_fecha_tudo(self):
        for entrada in (None, [], "texto", 3):
            s = roda(entrada)
            self.assertEqual(s["resultado"], "VERMELHO")
            self.assertTrue(all(i["resultado"] != "VERDE" or i["id"] == "contraprova_gerador" for i in s["itens"]))


class ContraprovasAmbarTests(unittest.TestCase):
    """Itens fora da lista vermelha: ÂMBAR (corrige e repete uma vez), nunca VERDE."""

    def ambar(self, l, ident):
        s = roda(l)
        self.assertEqual(s["resultado"], "AMBAR", ident)
        self.assertEqual(item(s, ident)["resultado"], "AMBAR", ident)

    def test_forks_colaborador_extra_ou_convite(self):
        for mud in ({"fork": True}, {"forks_count": 1}, {"colaboradores": 2}, {"convites": 1}):
            l = leituras()
            l["repositorios"]["entrada"] = repo(**mud)
            self.ambar(l, "repo_entrada")

    def test_token_com_validade_menor_que_janela_mais_7_dias(self):
        for expira in ("2026-11-27T11:59:59+00:00", "2026-11-20T13:00:00+00:00"):
            l = leituras(tokens=[{"nome": "zapia_dados", "expira_em": expira}])
            self.ambar(l, "tokens")
        # exatamente 8 dias (janela de 24 h mais margem de 7 dias) NÃO basta: a validade precisa ser MAIOR que isso
        self.ambar(leituras(tokens=[{"nome": "zapia_dados", "expira_em": "2026-11-28T12:00:00+00:00"}]), "tokens")
        self.assertEqual(item(roda(leituras(tokens=[{"nome": "zapia_dados", "expira_em": "2026-11-28T12:00:01+00:00"}])), "tokens")["resultado"], "VERDE")

    def test_job_pulado_ou_neutro_nao_torna_a_ci_vermelha(self):
        self.assertEqual(item(roda(leituras(ci={"head_sha": MAIN, "conclusoes": ["success", "skipped", "neutral"]})), "ci")["resultado"], "VERDE")
        for ruim in ("cancelled", "timed_out", "action_required", "failure"):
            self.ambar(leituras(ci={"head_sha": MAIN, "conclusoes": ["success", ruim]}), "ci")

    def test_nome_de_token_com_cara_de_segredo_nao_apaga_o_relatorio(self):
        for nome in ("github_pat_entrada", "ghp_zapia"):
            l = leituras(tokens=[{"nome": nome, "expira_em": "2026-11-23T00:00:00+00:00"}])
            s = roda(l)
            self.assertEqual(s["resultado"], "AMBAR", nome)  # o item de token continua âmbar; nada virou "saida"
            self.assertNotIn("saida", {i["id"] for i in s["itens"]})
            self.assertNotIn(nome, json.dumps(s))
        l = leituras(tokens=[{"nome": "ghp_zapia", "expira_em": "2026-11-19T00:00:00+00:00"}])
        s = roda(l)
        self.assertEqual(item(s, "tokens")["resultado"], "VERMELHO")
        self.assertNotIn("ghp_zapia", json.dumps(s))

    def test_ci_nao_verde_ou_em_outro_sha(self):
        self.ambar(leituras(ci={"head_sha": MAIN, "conclusoes": ["success", "failure"]}), "ci")
        self.ambar(leituras(ci={"head_sha": "1" * 40, "conclusoes": ["success"]}), "ci")

    def test_vermelho_vence_ambar(self):
        l = leituras(ci={"head_sha": MAIN, "conclusoes": ["failure"]}, consentimento=None)
        self.assertEqual(roda(l)["resultado"], "VERMELHO")


class TudoOuNadaESaidaTests(unittest.TestCase):
    def test_um_unico_item_nao_verde_impede_o_verde(self):
        for ident, mud in (("tokens", {"tokens": [{"nome": "x", "expira_em": "2026-11-21T00:00:00+00:00"}]}),
                           ("ci", {"ci": {"head_sha": MAIN, "conclusoes": ["failure"]}})):
            s = roda(leituras(**mud))
            self.assertNotEqual(s["resultado"], "VERDE", ident)

    def test_modo_invalido_e_horario_sem_fuso_levantam(self):
        with self.assertRaises(ValueError):
            pf.executar(leituras(), "producao", AGORA)
        with self.assertRaises(ValueError):
            pf.executar(leituras(), "abertura", datetime(2026, 11, 20, 12, 0))

    def test_saida_so_tem_prefixos_de_hash_e_nenhum_segredo(self):
        s = roda(leituras(consentimento=consent(version="v3")))
        texto = json.dumps(s, ensure_ascii=False)
        self.assertNotIn(H, texto)  # hash inteiro nunca sai: só 12 caracteres
        self.assertNotIn(MAIN, texto)
        self.assertNotRegex(texto, r"github_pat_|ghp_|gho_|https?://")

    def test_saida_com_padrao_de_segredo_e_descartada(self):
        l = leituras()
        l["tokens"] = [{"nome": "zapia_dados", "expira_em": "2026-12-18T00:00:00+00:00"}]
        original = pf._item
        try:
            pf._item = lambda i, r, m: original(i, r, m + " github_pat_ABCDEFGH12345678")
            s = pf.executar(l, "abertura", AGORA)
        finally:
            pf._item = original
        self.assertEqual(s["resultado"], "VERMELHO")
        self.assertEqual(s["itens"][0]["id"], "saida")
        self.assertNotIn("github_pat_", json.dumps(s))

    def test_contraprova_do_gerador_detecta_guarda_quebrado(self):
        original = pf.gerar_projecao
        try:
            pf.gerar_projecao = lambda *a, **k: {"schema": 1}
            s = roda(leituras())
        finally:
            pf.gerar_projecao = original
        self.assertEqual(item(s, "contraprova_gerador")["resultado"], "VERMELHO")
        self.assertEqual(s["resultado"], "VERMELHO")


class LinhaDeComandoTests(unittest.TestCase):
    def cli(self, conteudo, modo="abertura"):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "leituras.json"
            if conteudo is not None:
                arq.write_text(conteudo, encoding="utf-8")
            p = subprocess.run([sys.executable, str(ROOT / "scripts/piloto_preflight.py"), "--modo", modo, "--leituras", str(arq)],
                               capture_output=True, text=True, timeout=60, cwd=d, env={"PATH": "/usr/bin:/bin"})
        return p

    def test_verde_vermelho_e_arquivo_ausente(self):
        verde = self.cli(json.dumps(leituras()))
        self.assertEqual(verde.returncode, 0, verde.stderr[-300:])
        self.assertEqual(json.loads(verde.stdout)["resultado"], "VERDE")
        ruim = leituras(consentimento=None)
        self.assertEqual(self.cli(json.dumps(ruim)).returncode, 1)
        ambar = leituras(ci={"head_sha": MAIN, "conclusoes": ["failure"]})
        self.assertEqual(self.cli(json.dumps(ambar)).returncode, 3)  # 2 é o código de uso incorreto do argparse
        self.assertEqual(subprocess.run([sys.executable, str(ROOT / "scripts/piloto_preflight.py"), "--modo", "abertura"], capture_output=True,
                                        text=True, timeout=60, env={"PATH": "/usr/bin:/bin"}).returncode, 2)
        self.assertEqual(self.cli("{não é json").returncode, 1)
        self.assertEqual(self.cli(None).returncode, 1)


class SomenteLeituraTests(unittest.TestCase):
    def test_importa_so_modulos_offline_e_so_abre_arquivo_na_linha_de_comando(self):
        arvore = ast.parse((ROOT / "scripts/piloto_preflight.py").read_text(encoding="utf-8"))
        usados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                usados |= {a.name.split(".")[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom):
                usados.add((no.module or "").split(".")[0])
        self.assertEqual(usados, {"argparse", "json", "re", "sys", "datetime", "private_persistence_guard", "projection_generator", "session_read_guard"})
        chamadas = {n.func.id for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(chamadas & {"exec", "eval", "__import__", "compile"})
        escrita = [n for n in ast.walk(arvore) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in ("write", "write_text", "mkdir", "unlink")]
        self.assertEqual(escrita, [])
        # `open` só aparece em `main`, e lá só em leitura (nenhum modo de escrita); `executar` e os itens nunca abrem arquivo
        for funcao in (f for f in ast.walk(arvore) if isinstance(f, ast.FunctionDef)):
            aberturas = [n for n in ast.walk(funcao) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open"]
            if funcao.name != "main":
                self.assertEqual(aberturas, [], funcao.name)
            for a in aberturas:
                modo = a.args[1].value if len(a.args) > 1 and isinstance(a.args[1], ast.Constant) else "r"
                self.assertNotRegex(str(modo), r"[wax+]")

    def test_nenhuma_flag_e_alterada_pelo_modulo(self):
        antes = (ROOT / "settings.json").read_bytes()
        roda(leituras())
        self.assertEqual((ROOT / "settings.json").read_bytes(), antes)
        settings = json.loads(antes)
        self.assertIs(settings["storage"]["personal_results_writes_enabled"], False)
        self.assertIs(settings["storage"]["private_flow_promotion_enabled"], False)


if __name__ == "__main__":
    unittest.main()
