"""Os prompts persistidos para a conta nova da Zapia não podem divergir dos arquivos que citam."""
import hashlib
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governanca"
PROMPTS = (GOV / "PROMPTS_PRONTOS_ZAPIA_CONTA_NOVA_20261109.md").read_text(encoding="utf-8")
ROTEIRO = GOV / "ROTEIRO_VALIDACAO_ZAPIA_RODADA4_20261109.md"
SCRIPT = ROOT / "scripts" / "termux" / "verifica_token.sh"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ZapiaPromptsTests(unittest.TestCase):
    def test_hash_do_roteiro_citado_confere(self):
        citados = set(re.findall(r"\b[0-9a-f]{64}\b", PROMPTS))
        self.assertIn(sha(ROTEIRO), citados)
        self.assertGreaterEqual(PROMPTS.count(sha(ROTEIRO)), 4)  # valores de referência e três prompts

    def test_hashes_dos_textos_v11_conferem(self):
        for nome, tamanho in (("V11_3000.txt", 3000), ("V11_6000.txt", 6000)):
            arquivo = GOV / nome
            self.assertIn(sha(arquivo), PROMPTS, nome)
            texto = arquivo.read_text(encoding="utf-8")
            self.assertEqual(len(texto), tamanho, nome)
            self.assertIn("acentuação: ação, coração, órgão", texto)

    def test_todo_prompt_fixa_o_mesmo_ref_de_commit(self):
        refs = set(re.findall(r"ref\s+([0-9a-f]{40})", PROMPTS)) | set(re.findall(r"ref `([0-9a-f]{40})`", PROMPTS))
        self.assertEqual(len(refs), 1, refs)

    def test_o_ref_citado_contem_o_roteiro_quando_ha_historico_git(self):
        ref = re.search(r"ref `([0-9a-f]{40})`", PROMPTS).group(1)
        existe = subprocess.run(["git", "cat-file", "-e", ref], cwd=ROOT, capture_output=True).returncode == 0
        if not existe:
            self.skipTest("histórico Git raso: o commit citado não está disponível neste checkout")
        saida = subprocess.run(["git", "show", f"{ref}:docs/governanca/{ROTEIRO.name}"], cwd=ROOT,
                               capture_output=True)
        self.assertEqual(hashlib.sha256(saida.stdout).hexdigest(), sha(ROTEIRO))

    def test_autorizacoes_dos_prompts_sao_limitadas(self):
        frases = re.findall(r"AUTORIZO (V\d+[ab]?(?:, V\d+[ab]?)*)", PROMPTS)
        self.assertEqual(sorted(frases), sorted(["V1, V2, V7", "V11", "V4, V6"]))
        self.assertNotIn("AUTORIZO V10", PROMPTS)  # TEC só depois da resposta do suporte
        self.assertNotIn("AUTORIZO V3", PROMPTS)   # WhatsApp fora (D-20)
        self.assertNotIn("AUTORIZO V5", PROMPTS)

    def test_passos_trazem_as_permissoes_do_token_e_proibem_valor_no_chat(self):
        for trecho in ("Contents: Read-only", "Issues: Read and write", "30 dias", "formulário seguro", "nunca vai no chat",
                       "somente o app"):
            self.assertIn(trecho, PROMPTS)
        self.assertNotRegex(PROMPTS, r"github_pat_[A-Za-z0-9_]{10,}|ghp_[A-Za-z0-9]{10,}")

    def test_script_termux_sintaxe_e_nao_imprime_o_token(self):
        self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)]).returncode, 0)
        texto = SCRIPT.read_text(encoding="utf-8")
        permitido = (re.escape("read -rs TOKEN"), re.escape('[ -n "$TOKEN" ]'), re.escape('case "$TOKEN" in'),
                     re.escape("${TOKEN:0:4}"), re.escape("unset TOKEN"),
                     re.escape("printf 'header = \"Authorization: Bearer %s\"\\n' \"$TOKEN\" | curl"))
        for numero, linha in enumerate(texto.splitlines(), 1):
            if "TOKEN" in linha and not linha.lstrip().startswith("#") and "TOKEN=" not in linha.replace("$TOKEN", ""):
                self.assertTrue(any(re.search(p, linha) for p in permitido), (numero, linha))
        self.assertIn("curl -sS -K -", texto)  # o token vai por stdin, nunca na linha de comando
        self.assertNotIn("-H \"Authorization", texto)
        self.assertIn("chmod 700", texto)
        self.assertIn("rm -rf", texto)

    def test_sondas_do_script_nao_enviam_dados_reais(self):
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(texto.count("'{}'"), 4)  # as quatro sondas de escrita usam corpo vazio


if __name__ == "__main__":
    unittest.main()
