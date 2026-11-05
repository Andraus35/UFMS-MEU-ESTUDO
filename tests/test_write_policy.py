"""Contraprovas do bloqueio de resultados pessoais, sem dados reais."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from write_policy import verify_write_policy


class WritePolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "state/events").mkdir(parents=True)
        self.settings = {
            "storage": {
                "repository_must_be_private_for_personal_results": True,
                "personal_results_writes_enabled": False,
            }
        }
        self.save()

    def save(self, events=None):
        (self.root / "settings.json").write_text(
            json.dumps(self.settings), encoding="utf-8")
        (self.root / "state/events/2026-11.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in (events or [])),
            encoding="utf-8")

    def test_bloqueio_inicial_ativo(self):
        self.assertTrue(verify_write_policy(self.root))

    def test_alteracao_da_flag_nao_autoriza_resultados(self):
        self.settings["storage"]["personal_results_writes_enabled"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "permanece bloqueada"):
            verify_write_policy(self.root)

    def test_flag_string_false_nao_satisfaz_politica(self):
        self.settings["storage"]["personal_results_writes_enabled"] = "false"
        self.save()
        with self.assertRaisesRegex(ValueError, "permanece bloqueada"):
            verify_write_policy(self.root)

    def test_ausencia_da_flag_falha_fechada(self):
        del self.settings["storage"]["personal_results_writes_enabled"]
        self.save()
        with self.assertRaisesRegex(ValueError, "permanece bloqueada"):
            verify_write_policy(self.root)

    def test_remover_exigencia_de_privacidade_e_proibido(self):
        self.settings["storage"]["repository_must_be_private_for_personal_results"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "privado"):
            verify_write_policy(self.root)

    def test_evento_de_resultado_injetado_falha(self):
        self.save([{"event_id": "fixture-1", "type": "resultado_recebido"}])
        with self.assertRaisesRegex(ValueError, "Resultado individual encontrado"):
            verify_write_policy(self.root)

    def test_correcao_de_resultado_injetada_falha(self):
        self.save([{"event_id": "fixture-2", "type": "resultado_corrigido"}])
        with self.assertRaisesRegex(ValueError, "Resultado individual encontrado"):
            verify_write_policy(self.root)

    def test_metadado_nao_pessoal_nao_e_bloqueado_pela_politica(self):
        self.save([{"event_id": "fixture-3", "type": "decisao"}])
        self.assertTrue(verify_write_policy(self.root))


    def test_estado_derivado_com_resultado_bloqueado(self):
        path = self.root / "state/CURRENT.json"
        path.write_text(json.dumps({
            "results_count": 1, "last_result_caderno_id": "fake-1"
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "resultado pessoal"):
            verify_write_policy(self.root)

    def test_estado_derivado_nao_admite_contagem_boolean(self):
        path = self.root / "state/CURRENT.json"
        path.write_text(json.dumps({"results_count": False,
                                    "last_result_caderno_id": None}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "resultado pessoal"):
            verify_write_policy(self.root)

    def test_projecao_de_progresso_nao_admite_tentativas(self):
        path = self.root / "state/PROGRESS.csv"
        path.write_text("topic_id,attempted,correct,accuracy,revision_due_at\n"
                        "GER-PORT,2,1,0.5,\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Progresso individual"):
            verify_write_policy(self.root)

    def test_projecao_de_progresso_nao_admite_revisao_pessoal(self):
        path = self.root / "state/PROGRESS.csv"
        path.write_text("topic_id,attempted,correct,accuracy,revision_due_at\n"
                        "GER-PORT,0,0,,2026-11-08T12:00:00Z\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Progresso individual"):
            verify_write_policy(self.root)

    def test_projecoes_vazias_sao_validas(self):
        (self.root / "state/CURRENT.json").write_text(
            json.dumps({"results_count": 0, "last_result_caderno_id": None}),
            encoding="utf-8")
        (self.root / "state/PROGRESS.csv").write_text(
            "topic_id,attempted,correct,accuracy,revision_due_at\n"
            "GER-PORT,0,0,,\n", encoding="utf-8")
        self.assertTrue(verify_write_policy(self.root))

    def test_projecao_invalida_nao_abre_bypass(self):
        (self.root / "state/PROGRESS.csv").write_text(
            "topic_id,attempted\nGER-PORT,0\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Projeção de progresso inválida"):
            verify_write_policy(self.root)

if __name__ == "__main__":
    unittest.main()
