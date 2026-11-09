"""S4-R4: o filtro na frente do ToolGateway recusa conteúdo sensível sem alterar o gateway (SHA pinado no GQ-D)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import gateway_filter as gf  # noqa: E402
import test_tool_gateway as base  # noqa: E402


class GatewayFilterTests(unittest.TestCase):
    def run_with(self, parameters, guarded=True):
        req = base.request()
        req["parameters"] = parameters
        calls = []
        kwargs = dict(current_state_revision="rev-12", current_policy_sha="b" * 64, current_authorization_epoch=4,
                      caller_identity="trusted_supervisor", adapter=lambda p: calls.append(p) or {"ok": True},
                      now=base.NOW)
        gw = base.gateway()
        token = base.token_for(req)
        result = gf.guarded_execute(gw, req, token, **kwargs) if guarded else gw.execute(req, token, **kwargs)
        return result, calls

    def test_parametros_sensiveis_sao_recusados_antes_da_chamada(self):
        casos = ({"text": "meu cpf 529.982.247-25"}, {"text": "fulano@example.com"}, {"text": "ghp_" + "a" * 20},
                 {"text": "<html><body>x</body></html>"}, {"token": "x"}, {"a": {"b": [{"password": "x"}]}},
                 {"text": "x" * 3000}, {"enunciado": "texto da questão"})
        for parametros in casos:
            with self.subTest(parametros=str(parametros)[:40]):
                result, calls = self.run_with(parametros)
                self.assertEqual(result["status"], "DENIED")
                self.assertEqual(result["receipt"]["reason_codes"], [gf.SENSITIVE])
                self.assertFalse(result["receipt"]["effect_performed"])
                self.assertEqual(calls, [])

    def test_sem_o_filtro_o_gateway_sozinho_executaria(self):
        result, calls = self.run_with({"text": "meu cpf 529.982.247-25"}, guarded=False)
        self.assertEqual(result["status"], "COMMITTED")  # prova da lacuna que o filtro fecha
        self.assertEqual(len(calls), 1)

    def test_parametros_normais_passam_ao_gateway(self):
        result, calls = self.run_with({"text": "Revisar GER-LEG com 10 questões."})
        self.assertEqual(result["status"], "COMMITTED")
        self.assertEqual(len(calls), 1)

    def test_forma_invalida_fica_com_o_gateway(self):
        self.assertIsNone(gf.check_request({"parameters": "texto"}))
        self.assertIsNone(gf.check_request("x"))


if __name__ == "__main__":
    unittest.main()
