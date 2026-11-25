"""Aprovação destacada do proprietário sobre o hash do comando (limite 3, lote VOLTA-N1). Chaves SINTÉTICAS em diretório temporário; sem rede."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import agent_keys  # noqa: E402
import aprovacao_comando as ap  # noqa: E402
import volta_n1 as vn  # noqa: E402
import zapia_n1_prep as prep  # noqa: E402

H = "a1" * 32
M = prep.montar(datetime(2026, 11, 25, 15, 0, 0, tzinfo=timezone.utc))
FONTE = M["fonte_bytes"].decode("utf-8")
META = {"fonte_nome": M["fonte_nome"], "itens": {i["nome"]: {"hash_corpo": i["hash_corpo"], "contraprova": i["contraprova"], "ancora_gabarito": i["ancora_gabarito"]}
                                                  for i in M["itens"]}}


def pasta_privada():
    d = Path(tempfile.mkdtemp())
    os.chmod(d, 0o700)
    return d


class ChaveTest(unittest.TestCase):
    def setUp(self):
        self.d = pasta_privada()
        self.priv = self.d / "chave"
        self.pub = agent_keys.generate(self.priv)

    def test_aprova_e_verifica(self):
        a = ap.aprovar(H, self.priv)
        self.assertEqual(set(a), ap.CAMPOS)
        self.assertIsNone(ap.verificar(a, H, self.pub))

    def test_recusas(self):
        a = ap.aprovar(H, self.priv)
        outra = agent_keys.generate(self.d / "outra")
        casos = [
            (a, "b2" * 32, self.pub, "APROVACAO_DE_OUTRO_COMANDO"),
            ({**a, "assinatura": "0" * 128}, H, self.pub, "ASSINATURA_NAO_CONFERE"),
            (a, H, outra, "ASSINATURA_NAO_CONFERE"),
            ({**a, "aprovado_por": "tutor"}, H, self.pub, "APROVACAO_DE_OUTRO_COMANDO"),
            ({**a, "extra": 1}, H, self.pub, "APROVACAO_FORA_DO_FORMATO"),
            ({"hash_corpo": H}, H, self.pub, "APROVACAO_FORA_DO_FORMATO"),
            ({**a, "assinatura": "xyz"}, H, self.pub, "ASSINATURA_MALFORMADA"),
            (a, H, "zz", "CHAVE_PUBLICA_INVALIDA"),
            (a, H, None, "CHAVE_PUBLICA_INVALIDA"),
            ("texto", H, self.pub, "APROVACAO_FORA_DO_FORMATO"),
            (None, H, self.pub, "APROVACAO_FORA_DO_FORMATO"),
        ]
        for aprov, h, chave, codigo in casos:
            self.assertEqual(ap.verificar(aprov, h, chave), codigo, str((aprov, h, chave)))

    def test_hash_do_corpo_invalido_nao_assina(self):
        for ruim in ("", "abc", "G" * 64, None, 5, "A" * 64):
            with self.assertRaises(ValueError, msg=str(ruim)):
                ap.aprovar(ruim, self.priv)

    def test_guarda_da_chave_privada(self):
        aberta = self.d / "aberta"
        agent_keys.generate(aberta)
        os.chmod(aberta, 0o644)
        with self.assertRaises(ValueError):
            ap.aprovar(H, aberta)
        with self.assertRaises(ValueError):
            ap.aprovar(H, self.d / "nao-existe")
        dentro = ROOT / "chave_dentro_do_repo_teste"
        dentro.write_text("00" * 32, encoding="utf-8")
        os.chmod(dentro, 0o600)
        try:
            with self.assertRaises(ValueError):
                ap.aprovar(H, dentro)
        finally:
            dentro.unlink()

    def test_assinatura_nao_vale_para_outro_dominio(self):
        import ed25519_pure
        secret = bytes.fromhex(self.priv.read_text().strip())
        crua = ed25519_pure.sign(secret, H.encode()).hex()  # assinou o hash sem o domínio: não vale como aprovação
        self.assertEqual(ap.verificar({"hash_corpo": H, "aprovado_por": "proprietario", "assinatura": crua}, H, self.pub), "ASSINATURA_NAO_CONFERE")


class IntegracaoComAVoltaTest(unittest.TestCase):
    def setUp(self):
        self.d = pasta_privada()
        self.priv = self.d / "chave"
        self.pub = agent_keys.generate(self.priv)
        import test_volta_n1 as tv
        self.meta, self.fonte = tv.META, tv.FONTE  # mesmo kit das respostas (cada montagem tem nonce e hash próprios)
        self.aprov = {n: ap.aprovar(i["hash_corpo"], self.priv) for n, i in self.meta["itens"].items()}
        self.boas = tv.boas()

    def test_com_aprovacoes_validas_a_autoria_sobe(self):
        r = vn.processar(self.meta, self.fonte, self.boas, None, self.aprov, self.pub)
        self.assertEqual(r["veredito"], vn.PRONTO)
        self.assertEqual({i["autoria"] for i in r["relatorio_tutor"]}, {"aprovada_pelo_proprietario"})

    def test_sem_aprovacoes_a_autoria_fica_declarada(self):
        r = vn.processar(self.meta, self.fonte, self.boas)
        self.assertEqual({i["autoria"] for i in r["relatorio_tutor"]}, {"declarada"})

    def test_aprovacao_de_outro_comando_ou_ausente_derruba_o_veredito(self):
        for mudar in (lambda a: a.__setitem__("n1-fonte.json", a["n1-questao.json"]), lambda a: a.__setitem__("n1-fonte.json", None)):
            aprov = dict(self.aprov)
            mudar(aprov)
            r = vn.processar(self.meta, self.fonte, self.boas, None, aprov, self.pub)
            self.assertEqual(r["veredito"], vn.NAO_PROVADO)
            self.assertTrue(any(i["autoria"].startswith("APROVACAO_RECUSADA") for i in r["relatorio_tutor"]))

    def test_cli_aprovar_e_verificar_pelo_arquivo(self):
        (self.d / "meta.json").write_text(json.dumps(self.meta, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ap.main(["aprovar", "--privada", str(self.priv), "--meta", str(self.d / "meta.json"), "--saida", str(self.d / "ap")]), 0)
            self.assertEqual(ap.main(["verificar", "--publica", self.pub, "--meta", str(self.d / "meta.json"), "--aprovacoes", str(self.d / "ap")]), 0)
            (self.d / "ap" / "n1-fonte.aprovacao.json").unlink()
            self.assertEqual(ap.main(["verificar", "--publica", self.pub, "--meta", str(self.d / "meta.json"), "--aprovacoes", str(self.d / "ap")]), 2)


if __name__ == "__main__":
    unittest.main()
