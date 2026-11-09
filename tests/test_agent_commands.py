"""Contraprovas do validador offline de comandos Tutor/Coach -> Zapia (PR-013; S4-R1 a S4-R4)."""
import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_commands as ac  # noqa: E402
from agents_gate import COACH_ONLY, SHARED, TUTOR_ONLY  # noqa: E402

NOW = datetime(2026, 11, 8, 15, 0, 0, tzinfo=timezone.utc)
KEYS = {"tutor": b"chave-sintetica-tutor-0001", "coach": b"chave-sintetica-coach-0002"}
SCHEMA = ac.load_schema()
VALID_CPF = "52998224725"


def make(origin="tutor", operation="enviar_mensagem", destination=None, params=None, nonce="n-0000000000000001",
         key="k-00000001", issued=NOW, signer=None, **over):
    command = {
        "schema_version": "1.0", "origin": origin, "operation": operation,
        "destination": destination or SCHEMA["destinations"][operation],
        "params": params if params is not None else {"texto": "Revisar GER-LEG com 10 questões."},
        "idempotency_key": key, "nonce": nonce,
        "issued_at": issued.strftime("%Y-%m-%dT%H:%M:%SZ"), "signature": "",
    }
    command.update(over)
    command["signature"] = ac.sign(command, (signer or KEYS[origin]))
    return command


def run(command, ledger=None, now=NOW):
    return ac.validate_command(command, keys=KEYS, now=now, ledger=ledger or ac.CommandLedger(), schema=SCHEMA)


class CommandSchemaTests(unittest.TestCase):
    def test_comando_valido_e_aceito_para_cada_perfil(self):
        self.assertEqual(run(make())["decision"], ac.ACCEPTED)
        self.assertEqual(run(make("coach", "criar_lembrete", params={"atividade": "revisao-GER-PORT"}))["decision"], ac.ACCEPTED)

    def test_cpf_valido_de_teste_realmente_valido(self):
        self.assertTrue(ac._cpf_valid(VALID_CPF))
        self.assertFalse(ac._cpf_valid("11111111111"))

    def test_origem_desconhecida_ou_sem_chave_e_recusada(self):
        self.assertEqual(run(make(origin="tutor", **{}) | {"origin": "zapia"})["code"], "ORIGEM_DESCONHECIDA")
        r = ac.validate_command(make(), keys={"coach": KEYS["coach"]}, now=NOW, ledger=ac.CommandLedger(), schema=SCHEMA)
        self.assertEqual(r["code"], "ORIGEM_DESCONHECIDA")

    def test_assinatura_adulterada_ou_com_chave_errada(self):
        adulterado = make()
        adulterado["params"]["texto"] = "outro texto"
        self.assertEqual(run(adulterado)["code"], "ASSINATURA_INVALIDA")
        self.assertEqual(run(make(signer=b"chave-do-modelo"))["code"], "ASSINATURA_INVALIDA")
        vazio = make()
        vazio["signature"] = ""
        self.assertEqual(run(vazio)["code"], "ASSINATURA_INVALIDA")
        self.assertEqual(run(make(signature=None) | {"signature": None})["code"], "ASSINATURA_INVALIDA")

    def test_operacao_fora_do_perfil(self):
        for op in COACH_ONLY:
            self.assertEqual(run(make("tutor", op))["code"], "OPERACAO_FORA_DO_PERFIL", op)
        for op in TUTOR_ONLY:
            self.assertEqual(run(make("coach", op))["code"], "OPERACAO_FORA_DO_PERFIL", op)
        self.assertEqual(run(make(operation="apagar_repositorio", destination="x"))["code"], "OPERACAO_FORA_DO_PERFIL")

    def test_operacoes_compartilhadas_servem_aos_dois(self):
        for op in SHARED:
            for origin in ("tutor", "coach"):
                self.assertEqual(run(make(origin, op, params={"a": "b"}))["decision"], ac.ACCEPTED, (origin, op))

    def test_destino_nao_designado(self):
        self.assertEqual(run(make(destination="qualquer_pessoa"))["code"], "DESTINO_NAO_DESIGNADO")
        self.assertEqual(run(make("tutor", "registrar_resultado", destination="repo_publico_leitura"))["code"],
                         "DESTINO_NAO_DESIGNADO")

    def test_campos_fora_do_esquema_ausentes_ou_extras(self):
        extra = make(); extra["extra"] = 1; extra["signature"] = ac.sign(extra, KEYS["tutor"])
        self.assertEqual(run(extra)["code"], "CAMPOS_FORA_DO_ESQUEMA")
        falta = make(); del falta["nonce"]; falta["signature"] = ac.sign(falta, KEYS["tutor"])
        self.assertEqual(run(falta)["code"], "CAMPOS_FORA_DO_ESQUEMA")
        self.assertEqual(run("comando")["code"], "COMANDO_NAO_OBJETO")
        self.assertEqual(run(make(schema_version="9.9"))["code"], "VERSAO_DESCONHECIDA")

    def test_janela_de_tempo(self):
        velho = make(issued=NOW - timedelta(seconds=SCHEMA["limits"]["time_window_seconds"] + 1))
        futuro = make(issued=NOW + timedelta(seconds=SCHEMA["limits"]["time_window_seconds"] + 1))
        self.assertEqual(run(velho)["code"], "FORA_DA_JANELA")
        self.assertEqual(run(futuro)["code"], "FORA_DA_JANELA")
        self.assertEqual(run(make(issued=NOW - timedelta(seconds=SCHEMA["limits"]["time_window_seconds"])))["decision"],
                         ac.ACCEPTED)
        self.assertEqual(run(make(issued_at="ontem"))["code"], "DATA_INVALIDA")

    def test_nonce_repetido_e_recusado(self):
        ledger = ac.CommandLedger()
        self.assertEqual(run(make(), ledger)["decision"], ac.ACCEPTED)
        r = run(make(key="k-00000002"), ledger)
        self.assertEqual(r["code"], "NONCE_REPETIDO")

    def test_idempotencia_repeticao_nao_executa_de_novo(self):
        ledger = ac.CommandLedger()
        self.assertEqual(run(make(nonce="n-0000000000000001"), ledger)["decision"], ac.ACCEPTED)
        r = run(make(nonce="n-0000000000000002"), ledger)
        self.assertEqual((r["decision"], r["code"]), (ac.DUPLICATE, "IDEMPOTENTE"))

    def test_chave_reutilizada_com_outro_corpo_e_conflito(self):
        ledger = ac.CommandLedger()
        run(make(nonce="n-0000000000000001"), ledger)
        r = run(make(nonce="n-0000000000000002", params={"texto": "corpo diferente"}), ledger)
        self.assertEqual(r["code"], "CHAVE_REUTILIZADA_COM_OUTRO_CORPO")
        r = run(make("coach", "enviar_mensagem", nonce="n-0000000000000003"), ledger)
        self.assertEqual(r["decision"], ac.DUPLICATE)  # mesmo corpo, mesma chave: idempotente

    def test_recusa_nao_altera_o_registro(self):
        ledger = ac.CommandLedger()
        run(make(signer=b"errada"), ledger)
        run(make(params={"cpf": "x"}), ledger)
        self.assertEqual((ledger.nonces, ledger.keys), (set(), {}))
        self.assertEqual(run(make(), ledger)["decision"], ac.ACCEPTED)

    def test_chave_e_nonce_com_formato_invalido(self):
        self.assertEqual(run(make(key="curta"))["code"], "CHAVE_IDEMPOTENCIA_INVALIDA")
        self.assertEqual(run(make(nonce="curto"))["code"], "NONCE_INVALIDO")
        self.assertEqual(run(make(key="a b c d e f g h"))["code"], "CHAVE_IDEMPOTENCIA_INVALIDA")


class PersonalDataFilterTests(unittest.TestCase):
    def deny(self, params, code):
        self.assertEqual(run(make(params=params))["code"], code, params)

    def test_cpf_formatado_e_cpf_valido_sem_pontuacao(self):
        self.deny({"texto": "meu cpf 529.982.247-25"}, "PARAMS_DADO_PESSOAL")
        self.deny({"texto": f"id {VALID_CPF}"}, "PARAMS_DADO_PESSOAL")

    def test_onze_digitos_que_nao_sao_cpf_nao_geram_falso_positivo(self):
        self.assertEqual(run(make(params={"texto": "protocolo 12345678901"}))["decision"], ac.ACCEPTED)

    def test_email(self):
        self.deny({"texto": "contato fulano@example.com"}, "PARAMS_DADO_PESSOAL")

    def test_segredos(self):
        self.deny({"texto": "ghp_" + "a" * 20}, "PARAMS_SEGREDO")
        self.deny({"texto": "github_pat_" + "B" * 20}, "PARAMS_SEGREDO")
        self.deny({"texto": "Authorization: Bearer abcdefghij1234567890"}, "PARAMS_SEGREDO")
        self.deny({"texto": "-----BEGIN PRIVATE KEY-----"}, "PARAMS_SEGREDO")

    def test_html_bruto(self):
        self.deny({"texto": "<html><body>x</body></html>"}, "PARAMS_HTML_BRUTO")
        self.deny({"texto": "<script>alert(1)</script>"}, "PARAMS_HTML_BRUTO")

    def test_campos_proibidos_em_qualquer_nivel(self):
        for key in ("token", "Senha", "cookie", "enunciado", "alternativas", "cpf", "screenshot"):
            self.deny({key: "x"}, "PARAMS_CAMPO_PROIBIDO")
        self.deny({"a": {"b": [{"password": "x"}]}}, "PARAMS_CAMPO_PROIBIDO")

    def test_texto_longo_profundidade_e_tipo(self):
        self.deny({"texto": "a" * (SCHEMA["limits"]["max_param_string_chars"] + 1)}, "PARAMS_TEXTO_LONGO")
        self.deny({"a": {"b": {"c": {"d": {"e": {"f": 1}}}}}}, "PARAMS_PROFUNDOS")
        nao_serializavel = make()
        nao_serializavel["params"] = {"a": {1, 2}}
        self.assertEqual(run(nao_serializavel)["code"], "COMANDO_NAO_SERIALIZAVEL")
        self.assertEqual(run(make(params=["lista"]))["code"], "PARAMS_NAO_OBJETO")

    def test_comando_grande_demais(self):
        big = {f"c{i}": "x" * 1500 for i in range(15)}
        self.assertEqual(run(make(params=big))["code"], "COMANDO_GRANDE")


ED_SECRET = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")  # chave de teste do RFC 8032
ED_PUBLIC = ac.ed25519_pure.public_key(ED_SECRET)
OTHER_SECRET = bytes(range(32))


def make_ed(origin="tutor", secret=ED_SECRET, **over):
    command = make(origin, **over)
    command["signature"] = ac.sign_ed25519(command, secret)
    return command


def run_ed(command, ledger=None, entry=("ed25519", ED_PUBLIC)):
    return ac.validate_command(command, keys={"tutor": entry, "coach": entry}, now=NOW,
                               ledger=ledger or ac.CommandLedger(), schema=SCHEMA)


class Ed25519SignatureTests(unittest.TestCase):
    def test_assinatura_ed25519_valida_e_aceita(self):
        self.assertEqual(run_ed(make_ed())["decision"], ac.ACCEPTED)

    def test_comando_adulterado_ou_chave_privada_errada_e_recusado(self):
        adulterado = make_ed()
        adulterado["params"]["texto"] = "outro texto"
        self.assertEqual(run_ed(adulterado)["code"], "ASSINATURA_INVALIDA")
        self.assertEqual(run_ed(make_ed(secret=OTHER_SECRET))["code"], "ASSINATURA_INVALIDA")

    def test_sem_rebaixamento_hmac_nao_vale_para_origem_ed25519(self):
        comando = make()  # assinado com HMAC
        self.assertEqual(run_ed(comando)["code"], "ASSINATURA_INVALIDA")

    def test_sem_rebaixamento_ed25519_nao_vale_para_origem_hmac(self):
        self.assertEqual(run_ed(make_ed(), entry=("hmac", b"segredo-de-teste"))["code"], "ASSINATURA_INVALIDA")

    def test_assinatura_malformada(self):
        for ruim in ("", "zz" * 64, "ab" * 63, "ab" * 65, None, 123):
            comando = make_ed()
            comando["signature"] = ruim
            self.assertEqual(run_ed(comando)["code"], "ASSINATURA_INVALIDA", ruim)

    def test_configuracao_de_chave_invalida_falha_fechado(self):
        for entry in (("ed25519", b"curta"), ("ed25519", "texto"), ("rsa", ED_PUBLIC), ("hmac", b""), (), "x", None,
                      ("ed25519",)):
            self.assertEqual(run_ed(make_ed(), entry=entry)["code"], "ASSINATURA_INVALIDA", entry)

    def test_demais_regras_continuam_valendo_com_ed25519(self):
        self.assertEqual(run_ed(make_ed(params={"cpf": "x"}))["code"], "PARAMS_CAMPO_PROIBIDO")
        ledger = ac.CommandLedger()
        self.assertEqual(run_ed(make_ed(), ledger)["decision"], ac.ACCEPTED)
        self.assertEqual(run_ed(make_ed(key="k-00000002"), ledger)["code"], "NONCE_REPETIDO")
        self.assertEqual(run_ed(make_ed(issued=NOW - timedelta(seconds=300)))["code"], "FORA_DA_JANELA")

    def test_esquema_recomenda_ed25519(self):
        self.assertEqual(SCHEMA["signature"]["recommended"], "ed25519")


class SchemaConsistencyTests(unittest.TestCase):
    def test_esquema_coerente_com_os_perfis(self):
        self.assertEqual(ac.check(), [])

    def test_mutantes_do_esquema_sao_detectados(self):
        import json
        import shutil
        import tempfile
        for mutate in (
            lambda s: s["destinations"].pop("enviar_mensagem"),
            lambda s: s["destinations"].update({"operacao_nova": "x"}),
            lambda s: s["required_fields"].remove("signature"),
            lambda s: s["required_fields"].remove("nonce"),
            lambda s: s["origins"].append("zapia"),
        ):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "config").mkdir()
                data = copy.deepcopy(SCHEMA)
                mutate(data)
                (root / "config/agent_command_schema.json").write_text(json.dumps(data), encoding="utf-8")
                self.assertTrue(ac.check(root))

    def test_validador_nao_escreve_nem_usa_rede(self):
        source = (ROOT / "scripts/agent_commands.py").read_text(encoding="utf-8")
        for forbidden in ("import socket", "import requests", "urllib", "open(", "write_text", "subprocess"):
            self.assertNotIn(forbidden, source, forbidden)


if __name__ == "__main__":
    unittest.main()
