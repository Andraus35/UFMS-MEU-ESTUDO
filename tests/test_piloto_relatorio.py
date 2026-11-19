"""PREL: relatório do ciclo e semáforo (S11-R4, R10, R11, R13). Entradas sintéticas; uma contraprova por gatilho."""
import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import piloto_relatorio as pr  # noqa: E402

AGORA = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
SHA = "f654cc28c823960655d90888ae4d177dc4d339a0"
H = "b092dd9ba636" + "0" * 52


def etapa(estado="PROVADA", quem="gerador", prova="projecao_check", desconhecido="nenhum"):
    return {"estado": estado, "quem": quem, "prova": prova, "desconhecido": desconhecido}


def ciclo():
    return {
        "preflights": {"abertura": "VERDE", "pos_janela": "VERDE", "repouso": "VERDE"},
        "janela": {"aberta_em": "2026-11-20T10:00:00+00:00", "fechada_em": "2026-11-20T16:00:00+00:00"},
        "evento": {"id": "evt-001", "commit_sha": SHA, "hash_corpo": H, "readback": True},
        "contagens": {"eventos_gravados": 1, "eventos_recusados": 0},
        "niveis": {"E2": 3},
        "etapas": {
            "F1": etapa(quem="tutor", prova="readback"), "F2": etapa(quem="tutor", prova="projecao_check"),
            "F3": etapa("RELATADA", "proprietario", "relato_com_captura", "veracidade_do_resultado"),
            "F4": etapa("RELATADA", "proprietario", "relato_com_captura", "veracidade_do_resultado"),
            "F5": etapa(quem="tutor", prova="validacao_f5"), "F6": etapa(quem="fluxo", prova="readback"),
            "F7": etapa(quem="gerador", prova="projecao_check"),
            "F8": etapa("NAO_EXERCIDA", "tutor", "justificativa", "utilidade"),
        },
        "gatilhos": {g: False for g in pr.GATILHOS_VERMELHOS + pr.GATILHOS_AMBAR},
        "lacunas": ["o relatório de captura não foi lido pelo repositório"],
    }


def gera(c):
    return pr.gerar_relatorio(c, AGORA)


class CaminhoFelizTests(unittest.TestCase):
    def test_verde_com_oito_etapas_e_n_igual_a_1(self):
        r = gera(ciclo())
        self.assertEqual(r["semaforo"], "VERDE", r["motivos"])
        self.assertEqual(r["n"], 1)
        self.assertEqual([e["etapa"] for e in r["etapas"]], list(pr.ETAPAS))
        self.assertEqual(r["janela"]["duracao_horas"], 6.0)
        self.assertEqual(r["nao_provado"], list(pr.NAO_PROVADO))
        self.assertEqual(set(r), set(pr.TOPO))

    def test_hashes_saem_so_como_prefixo_de_12(self):
        r = gera(ciclo())
        self.assertEqual(r["evento"]["commit_sha"], SHA[:12])
        self.assertEqual(r["evento"]["hash_corpo"], H[:12])
        self.assertNotIn(SHA, json.dumps(r))
        self.assertNotIn(H, json.dumps(r))

    def test_relato_e_marcado_como_relatada_e_nao_como_provada(self):
        r = gera(ciclo())
        estados = {e["etapa"]: e["estado"] for e in r["etapas"]}
        self.assertEqual((estados["F3"], estados["F4"]), ("RELATADA", "RELATADA"))
        self.assertEqual(estados["F8"], "NAO_EXERCIDA")

    def test_markdown_deriva_do_json_e_termina_com_nao_provado(self):
        md = pr.para_markdown(gera(ciclo()))
        self.assertTrue(md.rstrip().splitlines()[-len(pr.NAO_PROVADO) - 1] == "Não provado:")
        for item in pr.NAO_PROVADO:
            self.assertIn(f"- {item}", md)
        self.assertIn("Semáforo: VERDE", md)
        for e in pr.ETAPAS:
            self.assertIn(f"| {e} |", md)
        self.assertNotRegex(md, r"melhorou|%|https?://")


class VermelhoTests(unittest.TestCase):
    def vermelho(self, c, trecho=None):
        r = gera(c)
        self.assertEqual(r["semaforo"], "VERMELHO", r["motivos"])
        if trecho:
            self.assertTrue(any(trecho in m for m in r["motivos"]), (trecho, r["motivos"]))
        return r

    def test_cada_gatilho_vermelho_classifica_vermelho(self):
        for g in pr.GATILHOS_VERMELHOS:
            c = ciclo()
            c["gatilhos"][g] = True
            self.vermelho(c, g)

    def test_preflight_vermelho_vale_mesmo_sem_escrita(self):
        for m in pr.PREVOOS:
            c = ciclo()
            c["preflights"][m] = "VERMELHO"
            self.vermelho(c, f"preflight_{m}_vermelho")

    def test_janela_aberta_ha_mais_de_24_h_nunca_e_verde(self):
        c = ciclo()
        c["janela"] = {"aberta_em": "2026-11-20T10:00:00+00:00", "fechada_em": "2026-11-21T11:00:00+00:00"}
        self.vermelho(c, "janela_aberta_ha_mais_de_24_h")
        c["janela"] = {"aberta_em": "2026-11-19T10:00:00+00:00", "fechada_em": None}
        self.vermelho(c, "janela_aberta_ha_mais_de_24_h")

    def test_janela_ainda_aberta_no_relatorio_e_vermelho(self):
        c = ciclo()
        c["janela"] = {"aberta_em": "2026-11-21T10:00:00+00:00", "fechada_em": None}
        self.vermelho(c, "janela_ainda_aberta")

    def test_janela_invalida(self):
        for janela in (None, {}, {"aberta_em": "ontem", "fechada_em": None}, {"aberta_em": "2026-11-20T10:00:00", "fechada_em": None},
                       {"aberta_em": "2026-11-20T10:00:00+00:00", "fechada_em": "2026-11-20T09:00:00+00:00"},
                       {"aberta_em": "2026-11-20T10:00:00+00:00", "fechada_em": "lixo"}):
            c = ciclo()
            c["janela"] = janela
            self.vermelho(c)

    def test_evento_sem_readback_ou_malformado(self):
        c = ciclo()
        c["evento"]["readback"] = False
        self.vermelho(c, "evento_sem_readback")
        for mud in ({"commit_sha": "curto"}, {"hash_corpo": "x"}, {"id": "com espaço"}, {"readback": "sim"}):
            c = ciclo()
            c["evento"].update(mud)
            self.vermelho(c, "evento_ausente_ou_malformado")
        c = ciclo()
        c["evento"] = None
        self.vermelho(c)

    def test_f3_ou_f4_escritas_como_provada_sao_vermelho(self):
        for e in ("F3", "F4"):
            c = ciclo()
            c["etapas"][e] = etapa("PROVADA", "proprietario", "relato")
            self.vermelho(c, f"{e}_escrita_como_provada")

    def test_estado_inesperado_cai_no_padrao_fechado(self):
        c = ciclo()
        c["etapas"]["F6"] = etapa("NAO_EXERCIDA")
        self.vermelho(c, "F6_estado_inesperado")
        c = ciclo()
        c["etapas"]["F8"] = etapa("RELATADA", "tutor", "relato")
        self.vermelho(c, "F8_estado_inesperado")
        c = ciclo()
        c["etapas"]["F3"] = etapa("NAO_EXERCIDA", "proprietario", "relato")
        self.vermelho(c, "F3_estado_inesperado")

    def test_entradas_ausentes_ou_malformadas_fecham_sem_repetir_o_conteudo(self):
        for ruim in (None, [], "texto", 3, {}):
            r = gera(ruim)
            self.assertEqual(r["semaforo"], "VERMELHO")
            self.assertEqual(set(r), {"schema", "gerado_em", "n", "semaforo", "motivos"})
        for chave in ("preflights", "gatilhos", "etapas", "contagens", "niveis", "janela", "evento"):
            c = ciclo()
            c[chave] = "xyz"
            self.assertEqual(gera(c)["semaforo"], "VERMELHO", chave)
            c = ciclo()
            del c[chave]
            self.assertEqual(gera(c)["semaforo"], "VERMELHO", chave)

    def test_gatilho_nao_booleano_ou_faltando(self):
        c = ciclo()
        c["gatilhos"]["segredo_exposto"] = "nao"
        self.vermelho(c, "segredo_exposto")
        c = ciclo()
        del c["gatilhos"]["readback_atrasou"]
        self.vermelho(c, "readback_atrasou")

    def test_preflight_com_valor_desconhecido(self):
        c = ciclo()
        c["preflights"]["abertura"] = "OK"
        self.vermelho(c, "preflights_ausentes")

    def test_vermelho_vence_ambar(self):
        c = ciclo()
        c["gatilhos"]["readback_atrasou"] = True
        c["gatilhos"]["segredo_exposto"] = True
        self.assertEqual(gera(c)["semaforo"], "VERMELHO")


class AmbarTests(unittest.TestCase):
    def ambar(self, c, trecho):
        r = gera(c)
        self.assertEqual(r["semaforo"], "AMBAR", r["motivos"])
        self.assertTrue(any(trecho in m for m in r["motivos"]), (trecho, r["motivos"]))

    def test_gatilhos_ambar(self):
        for g in pr.GATILHOS_AMBAR:
            c = ciclo()
            c["gatilhos"][g] = True
            self.ambar(c, g)

    def test_preflight_ambar(self):
        for m in pr.PREVOOS:
            c = ciclo()
            c["preflights"][m] = "AMBAR"
            self.ambar(c, f"preflight_{m}_ambar")

    def test_etapa_f1_a_f7_nao_provada_por_falta_de_registro(self):
        for e in ("F1", "F2", "F3", "F4", "F5", "F6", "F7"):
            c = ciclo()
            c["etapas"][e] = etapa("NAO_PROVADA", "proprietario", "nenhuma")
            self.ambar(c, f"{e}_nao_provada")
        c = ciclo()
        del c["etapas"]["F5"]  # etapa sem linha aparece como NAO_PROVADA, nunca em branco
        self.ambar(c, "F5_nao_provada")
        self.assertEqual({e["etapa"]: e["estado"] for e in gera(c)["etapas"]}["F5"], "NAO_PROVADA")

    def test_f8_nao_provada_e_ambar_e_exercida_ou_nao_exercida_e_verde(self):
        c = ciclo()
        c["etapas"]["F8"] = etapa("NAO_PROVADA", "tutor", "nenhuma")
        self.ambar(c, "F8_nao_provada")
        c["etapas"]["F8"] = etapa("PROVADA", "tutor", "validacao_f5")
        self.assertEqual(gera(c)["semaforo"], "VERDE")

    def test_verde_nunca_sai_com_etapa_nao_provada(self):
        for e in pr.ETAPAS:
            c = ciclo()
            c["etapas"][e] = etapa("NAO_PROVADA", "proprietario", "nenhuma")
            self.assertNotEqual(gera(c)["semaforo"], "VERDE", e)


class CamposFechadosETextoTests(unittest.TestCase):
    def test_enumeracoes_fechadas_recusam_texto_livre_na_etapa(self):
        for mud in ({"quem": "Fulano da Silva"}, {"prova": "acertei 12 de 20"}, {"desconhecido": "nota 85%"}, {"estado": "OK"}):
            c = ciclo()
            c["etapas"]["F1"] = {**etapa(), **mud}
            r = gera(c)
            self.assertEqual(r["semaforo"], "VERMELHO")
            self.assertNotIn("Fulano", json.dumps(r))
            self.assertNotIn("85%", json.dumps(r))

    def test_lacunas_so_com_padrao_restrito(self):
        for lacuna in ("nota 85%", "veja https://x.y/conta", "fulano@x.com", "token github_pat_ABCDEF", "x", "a" * 200, "acertos: 12"):
            c = ciclo()
            c["lacunas"] = [lacuna]
            r = gera(c)
            self.assertEqual(r["semaforo"], "VERMELHO", lacuna)
            self.assertNotIn(lacuna, json.dumps(r))
        c = ciclo()
        c["lacunas"] = ["x"] * 11
        self.assertEqual(gera(c)["semaforo"], "VERMELHO")

    def test_lacunas_padrao_sempre_presentes(self):
        r = gera(ciclo())
        for l in pr.LACUNAS_PADRAO:
            self.assertIn(l, r["lacunas"])

    def test_contagens_e_niveis_so_inteiros_e_niveis_conhecidos(self):
        for chave, valor in (("contagens", {"eventos_gravados": -1, "eventos_recusados": 0}), ("contagens", {"eventos_gravados": 1.5, "eventos_recusados": 0}),
                             ("contagens", {"eventos_gravados": True, "eventos_recusados": 0}), ("contagens", {"eventos_gravados": 1}),
                             ("niveis", {"E9": 1}), ("niveis", {"E2": "3"}), ("niveis", {"Tópico X": 80})):
            c = ciclo()
            c[chave] = valor
            self.assertEqual(gera(c)["semaforo"], "VERMELHO", (chave, valor))

    def test_validador_recusa_campo_extra_promessa_de_ganho_e_etapa_faltando(self):
        r = gera(ciclo())
        extra = {**r, "nome_do_estudante": "x"}
        with self.assertRaises(ValueError):
            pr.validar_relatorio(extra)
        with self.assertRaises(ValueError):
            pr.validar_relatorio({**r, "motivos": ["o aluno melhorou muito"]})
        with self.assertRaises(ValueError):
            pr.validar_relatorio({**r, "motivos": ["ganho de 12%"]})
        with self.assertRaises(ValueError):
            pr.validar_relatorio({**r, "etapas": r["etapas"][:-1]})
        with self.assertRaises(ValueError):
            pr.validar_relatorio({**r, "nao_provado": []})
        with self.assertRaises(ValueError):
            pr.validar_relatorio({**r, "n": 2})

    def test_relatorio_verde_nao_contem_promessa_de_eficacia(self):
        texto = json.dumps(gera(ciclo()), ensure_ascii=False).lower()
        for proibido in ("melhorou", "ganhou", "%", "https://", "enunciado", "gabarito", "github_pat_"):
            self.assertNotIn(proibido, texto)
        self.assertIn("utilidade pedagógica", texto)  # a lista "Não provado" está presente

    def test_horario_sem_fuso_levanta(self):
        with self.assertRaises(ValueError):
            pr.gerar_relatorio(ciclo(), datetime(2026, 11, 21, 12, 0))

    def test_nao_muda_a_entrada(self):
        c = ciclo()
        antes = copy.deepcopy(c)
        gera(c)
        self.assertEqual(c, antes)


class LinhaDeComandoTests(unittest.TestCase):
    def cli(self, conteudo, extra=()):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "ciclo.json"
            if conteudo is not None:
                arq.write_text(conteudo, encoding="utf-8")
            return subprocess.run([sys.executable, str(ROOT / "scripts/piloto_relatorio.py"), "--ciclo", str(arq), *extra],
                                  capture_output=True, text=True, timeout=60, cwd=d, env={"PATH": "/usr/bin:/bin"})

    def test_codigos_de_saida_e_markdown(self):
        c = ciclo()
        # a linha de comando usa o relógio real: o ciclo sintético de 20/11 com janela fechada continua VERDE
        verde = self.cli(json.dumps(c))
        self.assertEqual(verde.returncode, 0, verde.stderr[-300:])
        self.assertEqual(json.loads(verde.stdout)["semaforo"], "VERDE")
        md = self.cli(json.dumps(c), ("--markdown",))
        self.assertEqual(md.returncode, 0)
        self.assertIn("Não provado:", md.stdout)
        c["gatilhos"]["readback_atrasou"] = True
        self.assertEqual(self.cli(json.dumps(c)).returncode, 3)
        c["gatilhos"]["segredo_exposto"] = True
        self.assertEqual(self.cli(json.dumps(c)).returncode, 1)
        self.assertEqual(self.cli("{não é json").returncode, 1)
        self.assertEqual(self.cli(None).returncode, 1)
        self.assertEqual(subprocess.run([sys.executable, str(ROOT / "scripts/piloto_relatorio.py")], capture_output=True, text=True,
                                        timeout=60, env={"PATH": "/usr/bin:/bin"}).returncode, 2)


class SomenteLeituraTests(unittest.TestCase):
    def test_importa_so_modulos_offline_e_so_abre_arquivo_na_linha_de_comando(self):
        arvore = ast.parse((ROOT / "scripts/piloto_relatorio.py").read_text(encoding="utf-8"))
        usados = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                usados |= {a.name.split(".")[0] for a in no.names}
            elif isinstance(no, ast.ImportFrom):
                usados.add((no.module or "").split(".")[0])
        self.assertEqual(usados, {"argparse", "json", "re", "sys", "datetime"})
        chamadas = {n.func.id for n in ast.walk(arvore) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(chamadas & {"exec", "eval", "__import__", "compile"})
        self.assertEqual([n for n in ast.walk(arvore) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in ("write", "write_text", "mkdir", "unlink")], [])
        for funcao in (f for f in ast.walk(arvore) if isinstance(f, ast.FunctionDef)):
            aberturas = [n for n in ast.walk(funcao) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open"]
            if funcao.name != "main":
                self.assertEqual(aberturas, [], funcao.name)
            for a in aberturas:
                modo = a.args[1].value if len(a.args) > 1 and isinstance(a.args[1], ast.Constant) else "r"
                self.assertNotRegex(str(modo), r"[wax+]")


if __name__ == "__main__":
    unittest.main()
