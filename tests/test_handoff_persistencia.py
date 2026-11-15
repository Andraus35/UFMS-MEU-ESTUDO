"""O HANDOFF precisa deixar a retomada da persistência explícita e sem autorizar escrita pessoal."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = (ROOT / "memory" / "HANDOFF.md").read_text(encoding="utf-8")


class RetomadaPersistenciaTests(unittest.TestCase):
    def bloco(self):
        inicio = HANDOFF.index("### Retomada da persistência")
        return HANDOFF[inicio:HANDOFF.index("**Cuidados desta fase:**", inicio)]

    def test_ponto_de_partida_e_ordem_de_passos(self):
        bloco = self.bloco()
        for trecho in ("cria_repo_privado.sh", "next_task.py", "PR-010", "P4", "OPEN-01", "OPEN-02", "P7", "P8", "P9",
                       "personal_results_writes_enabled=false"):
            self.assertIn(trecho, bloco)
        posicoes = [bloco.index(f"{n}. **") for n in range(1, 7)]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_nao_autoriza_gravacao_nem_pede_token_no_chat(self):
        bloco = self.bloco()
        for trecho in ("sem escrever", "PR próprio, com aprovação humana expressa", "Nunca antes",
                       "não** vão ao repositório público", "Não pedir token ao proprietário no chat"):
            self.assertIn(trecho, bloco)
        self.assertNotIn("personal_results_writes_enabled=true", bloco)

    def test_o_bloco_fica_depois_do_aviso_de_defasagem(self):
        self.assertLess(HANDOFF.index("Aviso de defasagem do checkpoint"), HANDOFF.index("### Retomada da persistência"))


if __name__ == "__main__":
    unittest.main()
