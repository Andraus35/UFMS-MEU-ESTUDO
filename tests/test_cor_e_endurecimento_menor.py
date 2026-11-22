"""COR-E (AT-8, AC-9): lista de permissão de caminhos de leitura, citação por palavra inteira, hash por página e idade da projeção só com data.

Cada achado tem teste que falhava antes da correção e contraprova (sem falso positivo). Offline, dados fictícios."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import command_params_schema as cps  # noqa: E402
import manual_pages as mp  # noqa: E402
import session_read_guard as srg  # noqa: E402

TEXTO = "O prazo de posse é de trinta dias contados da publicação do ato de provimento, conforme a regra geral do estatuto aplicável ao caso."


def ler(caminho):
    return cps.validar_params("ler_arquivo_repositorio", {"caminho": caminho})


class At8ListaDePermissaoTeste(unittest.TestCase):
    def test_arquivos_internos_e_de_codigo_ficam_fora(self):
        for ruim in ("state/CURRENT.json", "state/WORKFLOW.json", "scripts/zapia_entrega.py", ".github/CODEOWNERS", "tests/test_x.py",
                     "settings.json", "comandos/validados/a.json", "outro/arquivo.md"):
            self.assertIn(ler(ruim), ("PARAMS_CAMINHO_FORA_DA_LISTA", "PARAMS_CAMINHO_INVALIDO"), ruim)
        self.assertEqual(ler("state/CURRENT.json"), "PARAMS_CAMINHO_FORA_DA_LISTA")

    def test_contraprova_o_que_o_agente_precisa_ler_continua_permitido(self):
        for bom in ("edital/INDEX.md", "edital/chunks/p001-c01.md", "docs/PLATFORMS.md", "config/topics.csv", "rules/STUDY.md", "agents/COACH.md",
                    "AGENTS.md", "ROADMAP.md", "PRODUCT.md", "memory/HANDOFF.md"):
            self.assertIsNone(ler(bom), bom)

    def test_prefixo_parecido_nao_vale(self):
        for ruim in ("docs_internos/x.md", "editalx/y.md", "memory/outro.md", "docs"):
            self.assertEqual(ler(ruim), "PARAMS_CAMINHO_FORA_DA_LISTA", ruim)

    def test_travessia_e_oculto_seguem_recusados_antes_da_lista(self):
        for ruim in ("docs/../state/CURRENT.json", "docs/.env", "/etc/passwd"):
            self.assertEqual(ler(ruim), "PARAMS_CAMINHO_INVALIDO", ruim)


class Ac9ManualTeste(unittest.TestCase):
    def manifesto(self):
        return mp.montar_manifesto({1: TEXTO, 2: TEXTO}, "fonte fictícia", "1ª ed.")

    def test_citacao_no_meio_de_palavra_e_recusada(self):
        m = mp.montar_manifesto({1: TEXTO}, "fonte fictícia", "1ª ed.")
        for frag in ("prazo de pos", "azo de posse", "dias contados da publica"):
            self.assertEqual(mp.conferir_citacao(m, 1, TEXTO, frag)["codigo"], "CITACAO_FORA_DA_PAGINA", frag)

    def test_contraprova_citacao_literal_por_palavras_inteiras_passa(self):
        m = mp.montar_manifesto({1: TEXTO}, "fonte fictícia", "1ª ed.")
        for bom in ("O prazo de posse é de trinta dias", "contados da publicação do ato de provimento,", "posse é de trinta"):
            self.assertTrue(mp.conferir_citacao(m, 1, TEXTO, bom)["ok"], bom)
        self.assertEqual(mp.conferir_citacao(m, 1, TEXTO, "trinta de posse prazo")["codigo"], "CITACAO_FORA_DA_PAGINA")  # ordem importa

    def test_paginas_de_texto_identico_nao_compartilham_hash(self):
        m = self.manifesto()
        self.assertNotEqual(m["paginas"][0]["sha256"], m["paginas"][1]["sha256"])
        # a página 2 aberta com o texto da 1 não vale pela 2 se o texto diferir; com o mesmo texto cada uma vale só pelo próprio número
        self.assertEqual(mp.hash_pagina(TEXTO, 1), m["paginas"][0]["sha256"])
        self.assertNotEqual(mp.hash_pagina(TEXTO, 1), mp.hash_pagina(TEXTO, 2))

    def test_prova_de_leitura_continua_exigindo_cada_pagina(self):
        m = self.manifesto()
        self.assertTrue(mp.prova_de_leitura(m, {1: TEXTO, 2: TEXTO}, [1, 2])["ok"])
        self.assertEqual(mp.prova_de_leitura(m, {1: TEXTO}, [1, 2])["faltando"], [2])
        self.assertEqual(mp.prova_de_leitura(m, {1: TEXTO, 2: TEXTO + " x"}, [1, 2])["divergentes"], [2])


class Ac9IdadePorDataTeste(unittest.TestCase):
    def test_data_sem_hora_em_orientacao_usa_a_idade_maxima(self):
        agora = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)  # 2026-11-18 00:00 até agora: 84 h
        r = srg.conferir_idade({"gerado_em": "2026-11-18"}, agora, "orientacao")
        self.assertEqual(r["decisao"], "AVISO")
        self.assertGreater(r["horas"], 72)

    def test_contraprova_data_recente_segue_ok_e_prazo_segue_recusando_data(self):
        agora = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(srg.conferir_idade({"gerado_em": "2026-11-20"}, agora, "orientacao")["decisao"], "OK")  # 36 h
        self.assertEqual(srg.conferir_idade({"gerado_em": "2026-11-21"}, agora, "orientacao")["decisao"], "OK")
        self.assertEqual(srg.conferir_idade({"gerado_em": "2026-11-21"}, agora, "prazo")["codigo"], "PROJECAO_SEM_INSTANTE")
        self.assertEqual(srg.conferir_idade({"gerado_em": "2026-11-22"}, agora, "orientacao")["codigo"], "PROJECAO_NO_FUTURO")


if __name__ == "__main__":
    unittest.main()
