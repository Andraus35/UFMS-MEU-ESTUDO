"""C6A: guarda offline da leitura de projeções por sessões (v4 obrigatório, projeção em lista fechada, sem histórico bruto)."""
import copy
import hashlib
import json
import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import session_read_guard as g  # noqa: E402
from private_persistence_guard import PersistenceBlocked  # noqa: E402

DOC = (ROOT / "docs/governanca/E5_CONSENTIMENTO_V4_PROPOSTA_20261118.md").read_text(encoding="utf-8")
TEXTO = next(l[2:].strip() for l in DOC.splitlines() if l.startswith("> "))
AGORA = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


def consent(**mud):
    c = {"version": "v4", "scope": "resultados_estudo", "inclui": ["resultados_estudo", "plano_estudo", "leitura_projecoes_sessoes_app_claude"],
         "granted_at": "2026-11-19T12:00:00+00:00", "revoked_at": None, "text": TEXTO,
         "text_sha256": hashlib.sha256(TEXTO.encode("utf-8")).hexdigest()}
    c.update(mud)
    return c


PROJ = {"schema": 1, "gerado_em": "2026-11-20",
        "niveis": [{"topico": "Lei 8.112/1990: regime disciplinar", "nivel": "E1"}],
        "pendencias": [{"atividade_id": "caderno-001", "tipo": "caderno"}],
        "revisoes": [{"topico": "Lei 8.112/1990: regime disciplinar", "vence_em": "2026-11-27"}]}


def bloqueia(teste, fn, trecho):
    with teste.assertRaises(PersistenceBlocked) as cm:
        fn()
    teste.assertIn(trecho, str(cm.exception))


class ConsentimentoV4Tests(unittest.TestCase):
    def test_caminho_feliz_com_o_texto_real_aprovado(self):
        self.assertEqual(g.check_consent_v4(consent(), AGORA), "v4")
        r = g.authorize_session_read(consent(), "projecao", PROJ, AGORA)
        self.assertEqual(r, {"authorized": True, "consent_version": "v4", "kind": "projecao"})

    def test_exige_v4_e_recusa_versoes_antigas(self):
        for versao in ("v2", "v3", "v5", None, 4):
            bloqueia(self, lambda: g.check_consent_v4(consent(version=versao), AGORA), "V4")

    def test_recusa_consentimento_invalido(self):
        casos = [(None, "ausente"), (consent(scope="outro"), "escopo"), (consent(revoked_at="2026-11-19T13:00:00+00:00"), "revogado"),
                 (consent(granted_at="2026-12-01T00:00:00+00:00"), "futura"), (consent(granted_at="2026-11-19T12:00:00"), "sem fuso"),
                 (consent(granted_at="ontem"), "inválida"), (consent(inclui=["resultados_estudo", "plano_estudo"]), "não cobre"),
                 (consent(inclui="leitura_projecoes_sessoes_app_claude"), "não cobre"),
                 (consent(text_sha256="0" * 64), "hash"), (consent(text=TEXTO + " extra"), "hash")]
        for c, trecho in casos:
            bloqueia(self, lambda: g.check_consent_v4(c, AGORA), trecho)

    def test_recusa_texto_que_nao_e_o_do_v4_mesmo_com_hash_certa(self):
        for texto in (TEXTO.replace("app Claude", "sistema"), TEXTO.replace("somente leitura", "leitura"),
                      TEXTO.replace("nunca o histórico bruto", "o histórico"), TEXTO.replace("Versão: v4.", "Versão: v3.")):
            bloqueia(self, lambda: g.check_consent_v4(consent(text=texto, text_sha256=hashlib.sha256(texto.encode()).hexdigest()), AGORA), "V4")


class ProjecaoTests(unittest.TestCase):
    def mut(self, fn):
        p = copy.deepcopy(PROJ)
        fn(p)
        return p

    def test_recusa_campos_fora_da_lista_fechada(self):
        ruins = [self.mut(lambda p: p.update(texto_questao="Qual é o prazo?")), self.mut(lambda p: p.update(conta="fulano")),
                 self.mut(lambda p: p["niveis"][0].update(enunciado="x")), self.mut(lambda p: p["niveis"][0].pop("nivel")),
                 self.mut(lambda p: p["pendencias"][0].update(url="https://x")), self.mut(lambda p: p.update(historico=[])),
                 self.mut(lambda p: p.update(schema=2)), self.mut(lambda p: p.update(gerado_em="hoje"))]
        for p in ruins:
            with self.assertRaises(PersistenceBlocked):
                g.check_projection(p)
        for nao_objeto in (None, [], "x", 1):
            with self.assertRaises(PersistenceBlocked):
                g.check_projection(nao_objeto)

    def test_recusa_conteudo_proibido_nos_valores(self):
        proibidos = ["fulano@example.com", "https://tecconcursos.com.br/caderno", "www.qconcursos.com", "github_pat_ficticio123", "token de acesso",
                     "cookie da sessão", "enunciado da questão 3", "gabarito: C", "cpf 000", "linha1\nlinha2"]
        for v in proibidos:
            with self.assertRaises(PersistenceBlocked, msg=v):
                g.check_projection(self.mut(lambda p: p["niveis"][0].update(topico=v)))

    def test_recusa_valores_invalidos(self):
        for fn in (lambda p: p["niveis"][0].update(nivel="E9"), lambda p: p["pendencias"][0].update(tipo="outro"),
                   lambda p: p["pendencias"][0].update(atividade_id="com espaço"), lambda p: p["revisoes"][0].update(vence_em="amanhã"),
                   lambda p: p["niveis"][0].update(topico="x" * 200), lambda p: p.update(niveis=[PROJ["niveis"][0]] * 501),
                   lambda p: p.update(niveis={"a": 1}), lambda p: p["niveis"].append("texto solto")):
            with self.assertRaises(PersistenceBlocked):
                g.check_projection(self.mut(fn))

    def test_projecao_vazia_valida_e_topico_com_acentos_passa(self):
        g.check_projection({"schema": 1, "gerado_em": "2026-11-20"})
        g.check_projection(self.mut(lambda p: p["niveis"][0].update(topico="Desconsideração da Personalidade Jurídica")))


class AutorizacaoTests(unittest.TestCase):
    def test_recusa_historico_bruto_fila_e_exportacao(self):
        for kind in ("historico", "historico_bruto", "fila", "exportacao", "", None):
            bloqueia(self, lambda: g.authorize_session_read(consent(), kind, PROJ, AGORA), "projeções")

    def test_ordem_fail_closed_tipo_depois_consentimento_depois_projecao(self):
        bloqueia(self, lambda: g.authorize_session_read(consent(version="v3"), "projecao", PROJ, AGORA), "exige o consentimento v4")
        ruim = copy.deepcopy(PROJ); ruim["conta"] = "x"
        bloqueia(self, lambda: g.authorize_session_read(consent(), "projecao", ruim, AGORA), "PROJECAO")
        bloqueia(self, lambda: g.authorize_session_read(consent(revoked_at="2026-11-19T13:00:00+00:00"), "projecao", PROJ, AGORA), "revogado")


class LimitesDoModuloTests(unittest.TestCase):
    def test_modulo_e_offline_e_nao_grava_nem_le_segredo(self):
        fonte = (ROOT / "scripts/session_read_guard.py").read_text(encoding="utf-8")
        for proibido in ("import socket", "urllib", "requests", "subprocess", "open(", "os.environ", "write_text", "http.client"):
            self.assertNotIn(proibido, fonte)

    def test_a_flag_de_escrita_continua_falsa_e_o_modulo_nao_a_altera(self):
        s = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertIs(s["storage"]["personal_results_writes_enabled"], False)

    def test_o_consentimento_gerado_pelo_consentir_v4_passa_neste_guarda(self):
        ufms = (ROOT / "scripts/termux/ufms.sh").read_text(encoding="utf-8")
        self.assertIn('"leitura_projecoes_sessoes_app_claude"', ufms)
        self.assertIn('"version": "v4"', ufms)
        m = re.search(r'"inclui": \[([^\]]*)\]', ufms[ufms.index("cmd_consentir_v4"):])
        self.assertTrue(g.INCLUI_OBRIGATORIO.issubset(set(re.findall(r'"([^"]+)"', m.group(1)))))


if __name__ == "__main__":
    unittest.main()
