"""GAP-A (GA-1 e GA-2): reprodução e correção dos achados ALTOS do Tutor e do Coach de 21/11/2026.

GA-1: o validador aceitava `registrar_resultado` com params arbitrários (o esquema não fechava campos por operação).
GA-2: o `delivery_gate` aceitava COMANDO `enviar_mensagem` com texto de percentual e disponibilidade em `params` (os filtros só rodavam no corpo).
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import agent_commands as ac  # noqa: E402
import command_params_schema as cps  # noqa: E402
import test_agent_commands as tac  # noqa: E402
import test_delivery_gate as tdg  # noqa: E402


class Ga1EsquemaDeParamsTests(unittest.TestCase):
    def test_enviar_mensagem_so_aceita_o_campo_texto(self):
        self.assertEqual(tac.run(tac.make())["decision"], ac.ACCEPTED)
        r = tac.run(tac.make(params={"texto": "Revisão pendente.", "extra": "x"}, nonce="n-0000000000000002", key="k-00000002"))
        self.assertEqual((r["decision"], r["code"]), (ac.DENIED, "PARAMS_CAMPO_DESCONHECIDO"))

    def test_enviar_mensagem_sem_texto_ou_com_tipo_errado_e_recusada(self):
        for params, n in (({}, 3), ({"texto": 5}, 4)):
            r = tac.run(tac.make(params=params, nonce=f"n-00000000000000{n:02d}", key=f"k-000000{n:02d}"))
            self.assertEqual(r["decision"], ac.DENIED, params)

    def test_registrar_resultado_com_params_arbitrarios_e_recusado_com_flag_falsa(self):
        cmd = tac.make("tutor", "registrar_resultado", params={"qualquer": "coisa", "acertos": 31}, nonce="n-0000000000000005", key="k-00000005")
        r = ac.validate_command(cmd, keys=tac.KEYS, now=tac.NOW, ledger=ac.CommandLedger(), schema=tac.SCHEMA, flags={"personal_results_writes_enabled": False})
        self.assertEqual((r["decision"], r["code"]), (ac.DENIED, "REGISTRO_PESSOAL_BLOQUEADO_PELA_FLAG"))

    def test_registrar_resultado_sem_a_flag_legivel_tambem_e_recusado_fail_closed(self):
        cmd = tac.make("tutor", "registrar_exportacao_desempenho", params={"a": 1}, nonce="n-0000000000000006", key="k-00000006")
        r = ac.validate_command(cmd, keys=tac.KEYS, now=tac.NOW, ledger=ac.CommandLedger(), schema=tac.SCHEMA, flags={})
        self.assertEqual(r["code"], "REGISTRO_PESSOAL_BLOQUEADO_PELA_FLAG")

    def test_o_padrao_le_a_flag_do_settings_e_ela_esta_falsa(self):
        self.assertIs(cps.flag_resultados_pessoais(), False)
        cmd = tac.make("coach", "registrar_acompanhamento", params={"a": 1}, nonce="n-0000000000000007", key="k-00000007")
        r = ac.validate_command(cmd, keys=tac.KEYS, now=tac.NOW, ledger=ac.CommandLedger(), schema=tac.SCHEMA)  # sem flags: lê o settings.json real
        self.assertEqual(r["code"], "REGISTRO_PESSOAL_BLOQUEADO_PELA_FLAG")

    def test_prompt_do_notebook_so_tem_prompt_e_hash(self):
        ok = {"prompt": "texto do prompt", "prompt_sha256": "a" * 64}
        self.assertIsNone(cps.validar_params("enviar_prompt_notebook", ok))
        self.assertEqual(cps.validar_params("enviar_prompt_notebook", {**ok, "x": 1}), "PARAMS_CAMPO_DESCONHECIDO")
        self.assertEqual(cps.validar_params("enviar_prompt_notebook", {"prompt": "t"}), "PARAMS_CAMPO_OBRIGATORIO_AUSENTE")

    def test_operacoes_sem_esquema_fechado_estao_declaradas_como_pendencia(self):
        self.assertEqual(set(cps.SEM_ESQUEMA_FECHADO), {"ler_arquivo_repositorio", "criar_lembrete", "consultar_agenda_minima", "registrar_plano"})
        for op in cps.SEM_ESQUEMA_FECHADO:
            self.assertIsNone(cps.validar_params(op, {"qualquer": 1}))  # pendência declarada, ainda sem esquema


class Ga2FiltroNoTextoDoComandoTests(unittest.TestCase):
    def motivos(self, texto):
        return tdg.vai(tdg.comando(params={"texto": texto}))["motivos"]

    def test_percentual_e_disponibilidade_no_texto_do_comando_sao_recusados(self):
        r = tdg.vai(tdg.comando(params={"texto": "acertou 80% e há 300 questões disponíveis"}))
        self.assertEqual(r["decisao"], "RECUSADA")
        self.assertIn("dado_de_desempenho_nao_verificavel", r["motivos"])
        self.assertIn("disponibilidade_de_questoes_afirmada", r["motivos"])

    def test_segredo_url_e_enunciado_no_texto_do_comando_sao_recusados(self):
        self.assertIn("url_fora_da_lista", self.motivos("veja https://exemplo.com/x"))
        self.assertIn("enunciado_de_questao", self.motivos("Enunciado: assinale a alternativa correta entre as opções."))

    def test_texto_limpo_do_comando_continua_aceito(self):
        r = tdg.vai(tdg.comando(params={"texto": "Revisão pendente."}))
        self.assertEqual(r["motivos"], [])

    def test_prompt_do_notebook_nao_recebe_o_filtro_de_pagina(self):
        r = tdg.vai(tdg.comando(op="enviar_prompt_notebook", papel="tutor", params={"prompt": "Tópico: Lei 8.112/1990, edital p. 29", "prompt_sha256": "a" * 64}))
        self.assertNotIn("pagina_citada_sem_alegacao", r["motivos"])


if __name__ == "__main__":
    unittest.main()
