"""Contraprovas do Ed25519 em Python puro: vetores do RFC 8032 e cruzamento com a biblioteca, se houver."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ed25519_pure as ed  # noqa: E402

VECTORS = (  # RFC 8032, seção 7.1 (testes 1 e 2)
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
     "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
     "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
)


class Ed25519PureTests(unittest.TestCase):
    def test_vetores_do_rfc_8032(self):
        for secret, public, message, signature in VECTORS:
            secret, public, message, signature = map(bytes.fromhex, (secret, public, message, signature))
            self.assertEqual(ed.public_key(secret), public)
            self.assertEqual(ed.sign(secret, message), signature)
            self.assertTrue(ed.verify(public, message, signature))

    def test_mensagem_ou_assinatura_adulterada_e_recusada(self):
        secret, public, message, signature = map(bytes.fromhex, VECTORS[1])
        self.assertFalse(ed.verify(public, message + b"x", signature))
        self.assertFalse(ed.verify(public, b"", signature))
        for i in (0, 31, 32, 63):
            alterada = bytearray(signature)
            alterada[i] ^= 1
            self.assertFalse(ed.verify(public, message, bytes(alterada)), i)

    def test_entradas_malformadas_nao_levantam_excecao(self):
        secret, public, message, signature = map(bytes.fromhex, VECTORS[1])
        for pub, sig in ((public[:31], signature), (public, signature[:63]), (b"", b""), (public, signature + b"\0"),
                         ("texto", signature), (public, "texto"), (b"\xff" * 32, signature)):
            self.assertFalse(ed.verify(pub, message, sig))

    def test_s_fora_do_intervalo_e_recusado(self):
        secret, public, message, signature = map(bytes.fromhex, VECTORS[1])
        s = int.from_bytes(signature[32:], "little") + ed.Q  # mesma classe de resíduo, fora do intervalo canônico
        maleavel = signature[:32] + s.to_bytes(32, "little")
        self.assertFalse(ed.verify(public, message, maleavel))

    def test_chave_privada_com_tamanho_errado(self):
        with self.assertRaises(ValueError):
            ed.sign(b"curta", b"m")

    def test_cruzamento_com_biblioteca_quando_disponivel(self):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError:
            self.skipTest("biblioteca cryptography ausente; os vetores do RFC já provam a implementação")
        for _ in range(10):
            secret, message = os.urandom(32), os.urandom(37)
            key = Ed25519PrivateKey.from_private_bytes(secret)
            public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            self.assertEqual(ed.public_key(secret), public)
            self.assertEqual(ed.sign(secret, message), key.sign(message))
            self.assertTrue(ed.verify(public, message, key.sign(message)))

    def test_modulo_sem_rede_nem_arquivo(self):
        source = (ROOT / "scripts/ed25519_pure.py").read_text(encoding="utf-8")
        for forbidden in ("import socket", "urllib", "requests", "open(", "write_text", "subprocess"):
            self.assertNotIn(forbidden, source, forbidden)


if __name__ == "__main__":
    unittest.main()
