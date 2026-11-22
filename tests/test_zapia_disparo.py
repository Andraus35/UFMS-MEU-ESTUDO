"""S20-R6/R9: conferência offline do disparo único da rotina de teste da Zapia. NÃO prova a Zapia real nem a pontualidade em 3 dias."""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import zapia_disparo as zd  # noqa: E402
import zapia_entrega as ze  # noqa: E402

AG = datetime(2026, 11, 23, 12, 0, 0, tzinfo=timezone.utc)
H = "a" * 64
NOME = "f1-rotina.json"


def entrega(quando="2026-11-23T12:03:10Z", h=H, nome=NOME, **extra):
    e = {"entrada_id": nome, "hash_corpo": h, "status": "ENTREGUE", "entregue_em": quando, "origem_declarada": "coach"}
    e.update(extra)
    return ze._canonico(e)


class Pura(unittest.TestCase):
    def conferir(self, **kw):
        return zd.conferir_disparo(kw.pop("bruto", entrega()), kw.pop("recibos", {NOME: H}), NOME, kw.pop("ag", AG), **kw)

    def test_dentro_da_tolerancia_confere(self):
        self.assertIsNone(self.conferir())

    def test_no_instante_exato_e_no_limite_conferem(self):
        self.assertIsNone(self.conferir(bruto=entrega("2026-11-23T12:00:00Z")))
        self.assertIsNone(self.conferir(bruto=entrega("2026-11-23T12:15:00Z")))

    def test_antes_do_agendado_nao_e_disparo(self):
        self.assertEqual(self.conferir(bruto=entrega("2026-11-23T11:59:59Z")), "ENTREGA_ANTES_DO_AGENDADO")

    def test_depois_da_tolerancia_falha(self):
        self.assertEqual(self.conferir(bruto=entrega("2026-11-23T12:15:01Z")), "ENTREGA_FORA_DA_TOLERANCIA")

    def test_carimbo_mal_formado_falha(self):
        for q in ("2026-11-23 12:03:10", "2026-11-23T12:03:10+00:00", "ontem", "2026-13-40T99:99:99Z", "2026-11-3T12:3:10Z", ""):
            self.assertEqual(self.conferir(bruto=entrega(q)), "CARIMBO_INVALIDO", q)

    def test_herda_as_recusas_do_f1(self):
        self.assertEqual(self.conferir(bruto=entrega(h="b" * 64)), "ENTREGA_COM_HASH_DIFERENTE_DO_RECIBO")
        self.assertEqual(self.conferir(bruto=entrega(texto="x")), "ENTREGA_FORA_DO_FORMATO")
        self.assertEqual(self.conferir(bruto=b"nao json"), "ENTREGA_ILEGIVEL")
        self.assertEqual(self.conferir(bruto=entrega(nome="outro.json")), "ENTREGA_INCONSISTENTE")

    def test_agendamento_invalido(self):
        self.assertEqual(self.conferir(ag=datetime(2026, 11, 23, 12, 0, 0)), "AGENDAMENTO_INVALIDO")
        self.assertEqual(self.conferir(ag="2026-11-23T12:00:00Z"), "AGENDAMENTO_INVALIDO")
        self.assertEqual(self.conferir(tolerancia=timedelta(0)), "AGENDAMENTO_INVALIDO")
        self.assertEqual(self.conferir(tolerancia=900), "AGENDAMENTO_INVALIDO")

    def test_fuso_do_agendamento_e_convertido(self):
        ag = datetime(2026, 11, 23, 8, 0, 0, tzinfo=timezone(timedelta(hours=-4)))  # 12:00 UTC
        self.assertIsNone(self.conferir(ag=ag))


class Pasta(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "comandos" / "recibos").mkdir(parents=True)
        (self.tmp / "comandos" / "entregas").mkdir(parents=True)

    def recibo(self, nome=NOME, h=H):
        (self.tmp / "comandos" / "recibos" / nome).write_bytes(ze._canonico({"entrada_id": nome, "hash_corpo": h, "status": "PROMOVER"}))

    def entrega(self, nome=NOME, **kw):
        (self.tmp / "comandos" / "entregas" / nome).write_bytes(entrega(nome=nome, **kw))

    def run_(self):
        return zd.conferir_pasta_unica(self.tmp, NOME, AG)

    def test_caminho_feliz(self):
        self.recibo(); self.entrega()
        self.assertEqual(self.run_()["ok"], True)

    def test_sem_entrega_falha(self):
        self.recibo()
        self.assertEqual(self.run_()["codigo"], "SEM_ENTREGA")

    def test_reenvio_do_mesmo_hash_em_outro_arquivo_falha(self):
        self.recibo(); self.recibo("f1-rotina-2.json")
        self.entrega(); self.entrega("f1-rotina-2.json", quando="2026-11-23T12:10:00Z")
        self.assertEqual(self.run_()["codigo"], "MAIS_DE_UMA_ENTREGA_DO_MESMO_HASH")

    def test_teto_diario_excedido_falha(self):
        self.recibo()
        self.entrega()
        for i in (1, 2):
            n = f"outro{i}.json"
            self.recibo(n, h=str(i) * 64); self.entrega(n, h=str(i) * 64, quando="2026-11-23T13:00:00Z")
        self.assertEqual(self.run_()["codigo"], "TETO_DIARIO_EXCEDIDO")

    def test_duas_entregas_em_hashes_diferentes_no_dia_passam(self):
        self.recibo(); self.entrega()
        self.recibo("outro.json", h="c" * 64); self.entrega("outro.json", h="c" * 64, quando="2026-11-23T13:00:00Z")
        self.assertTrue(self.run_()["ok"])

    def test_entrega_ilegivel_de_outro_arquivo_falha_fechado(self):
        self.recibo(); self.entrega()
        (self.tmp / "comandos" / "entregas" / "lixo.json").write_bytes(b"\xff\xfe")
        self.assertEqual(self.run_()["codigo"], "ENTREGA_ILEGIVEL")

    def test_manual_antes_do_agendado_falha(self):
        self.recibo(); self.entrega(quando="2026-11-23T11:00:00Z")
        self.assertEqual(self.run_()["codigo"], "ENTREGA_ANTES_DO_AGENDADO")

    def test_cli(self):
        self.recibo(); self.entrega()
        self.assertEqual(zd.main(["--raiz", str(self.tmp), "--agendado", "2026-11-23T12:00:00Z"]), 0)
        self.assertEqual(zd.main(["--raiz", str(self.tmp), "--agendado", "2026-11-23T10:00:00Z"]), 1)
        self.assertEqual(zd.main(["--raiz", str(self.tmp), "--agendado", "amanha"]), 2)


class Preparo(unittest.TestCase):
    def test_preparar_aceita_o_nome_da_rotina_e_o_recibo_leva_o_mesmo_nome(self):
        import zapia_f1_prep as prep
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        self.assertEqual(prep.main(["preparar", "--saida", str(tmp), "--nome", "f1-rotina.json"]), 0)
        recibo = json.loads((tmp / "recibos" / "f1-rotina.json").read_text(encoding="utf-8"))
        self.assertEqual(recibo["entrada_id"], "f1-rotina.json")
        self.assertTrue((tmp / "validados" / "f1-rotina.json").exists())
        self.assertEqual(prep.main(["preparar", "--saida", str(tmp / "b")]), 0)
        self.assertTrue((tmp / "b" / "validados" / "f1-teste.json").exists())


if __name__ == "__main__":
    unittest.main()
