"""Ed25519 (RFC 8032) em Python puro, só com a biblioteca padrão.

Existe para o repositório continuar sem dependências externas na CI (S4: assinatura de comandos).
Adaptado do código de referência do RFC 8032, seção 6. Verificação usa só dados públicos; a geração de
assinatura (`sign`) serve a testes e ao código local do agente e **não** é resistente a ataques de
temporização: em produção, prefira uma biblioteca auditada (por exemplo `cryptography`) para assinar.
Sem rede, sem arquivo, sem segredo embutido.
"""
import hashlib

P = 2 ** 255 - 19
Q = 2 ** 252 + 27742317777372353535851937790883648493


def _inv(x):
    return pow(x, P - 2, P)


D = -121665 * _inv(121666) % P
SQRT_M1 = pow(2, (P - 1) // 4, P)


def _recover_x(y, sign):
    if y >= P:
        return None
    x2 = (y * y - 1) * _inv(D * y * y + 1) % P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * SQRT_M1 % P
    if (x * x - x2) % P != 0:
        return None
    if (x & 1) != sign:
        x = P - x
    return x


_GY = 4 * _inv(5) % P
_GX = _recover_x(_GY, 0)
G = (_GX, _GY, 1, _GX * _GY % P)


def _add(a, b):
    A, B = (a[1] - a[0]) * (b[1] - b[0]) % P, (a[1] + a[0]) * (b[1] + b[0]) % P
    C, E_ = 2 * a[3] * b[3] * D % P, 2 * a[2] * b[2] % P
    E, F, G_, H = B - A, E_ - C, E_ + C, B + A
    return (E * F % P, G_ * H % P, F * G_ % P, E * H % P)


def _mul(s, point):
    result = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            result = _add(result, point)
        point = _add(point, point)
        s >>= 1
    return result


def _equal(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % P == 0 and (a[1] * b[2] - b[1] * a[2]) % P == 0


def _compress(point):
    zinv = _inv(point[2])
    x, y = point[0] * zinv % P, point[1] * zinv % P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _decompress(data):
    if len(data) != 32:
        return None
    y = int.from_bytes(data, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % P)


def _h(data):
    return int.from_bytes(hashlib.sha512(data).digest(), "little") % Q


def _expand(secret):
    if len(secret) != 32:
        raise ValueError("a chave privada deve ter 32 bytes")
    digest = hashlib.sha512(secret).digest()
    a = int.from_bytes(digest[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, digest[32:]


def public_key(secret):
    a, _ = _expand(secret)
    return _compress(_mul(a, G))


def sign(secret, message):
    a, prefix = _expand(secret)
    pub = _compress(_mul(a, G))
    r = _h(prefix + message)
    rs = _compress(_mul(r, G))
    s = (r + _h(rs + pub + message) * a) % Q
    return rs + int.to_bytes(s, 32, "little")


def verify(public, message, signature):
    """True só se a assinatura for válida; qualquer entrada malformada devolve False."""
    if not isinstance(public, (bytes, bytearray)) or not isinstance(signature, (bytes, bytearray)):
        return False
    if len(public) != 32 or len(signature) != 64:
        return False
    a_point = _decompress(bytes(public))
    r_point = _decompress(bytes(signature[:32]))
    if a_point is None or r_point is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= Q:
        return False
    h = _h(bytes(signature[:32]) + bytes(public) + message)
    return _equal(_mul(s, G), _add(r_point, _mul(h, a_point)))
