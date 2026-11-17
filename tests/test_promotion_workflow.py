"""Contraprovas do teste estático do modelo do fluxo de promoção (C2; S6-R4, R5, R6). Offline, sem rede."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import promotion_workflow_check as chk  # noqa: E402

MODELO = (ROOT / chk.MODELO).read_text(encoding="utf-8")
SHA = "a" * 40
HASH = "b" * 64
INSTANCIADO = MODELO.replace(chk.PLACEHOLDER_SHA, SHA).replace(chk.PLACEHOLDER_GATE, HASH)


def muta(antigo, novo, base=MODELO):
    assert base.count(antigo) == 1, antigo
    return base.replace(antigo, novo)


PASSO_PROMOCAO = "      - name: Promover com o portão"
PASSO_CAIXA = "      - name: Promover comandos da caixa"


def muta_passo(marcador, antigo, novo, base=MODELO):
    """Muta SÓ dentro de um passo (os passos de promoção e da caixa têm linhas parecidas)."""
    inicio = base.index(marcador)
    fim = base.find("\n      - name:", inicio + 1)
    fim = len(base) if fim == -1 else fim
    segmento = base[inicio:fim]
    assert segmento.count(antigo) == 1, antigo
    return base[:inicio] + segmento.replace(antigo, novo) + base[fim:]


class ModeloTest(unittest.TestCase):
    def test_modelo_cumpre_o_contrato(self):
        self.assertEqual(chk.verificar(MODELO), [])

    def test_modelo_nao_esta_onde_o_github_o_executaria(self):
        self.assertFalse((ROOT / ".github/workflows/promover.yml").exists())
        self.assertTrue(chk.MODELO.startswith("config/"))

    def test_modelo_traz_marcadores_e_nao_valores_inventados(self):
        self.assertIn(chk.PLACEHOLDER_SHA, MODELO)
        self.assertIn(chk.PLACEHOLDER_GATE, MODELO)
        self.assertNotRegex(MODELO, r"VALIDADOR_SHA:\s*[0-9a-f]{40}")

    def test_modelo_instanciado_so_passa_com_valores_reais(self):
        self.assertEqual(chk.verificar(INSTANCIADO, instanciado=True), [])
        self.assertIn("VALIDADOR_SHA_INVALIDO", chk.verificar(MODELO, instanciado=True))
        self.assertIn("VALIDADOR_HASH_INVALIDO", chk.verificar(MODELO, instanciado=True))
        curto = INSTANCIADO.replace(SHA, "abc123", 1)
        self.assertIn("VALIDADOR_SHA_INVALIDO", chk.verificar(curto, instanciado=True))

    def test_cli_check_passa_no_modelo(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/promotion_workflow_check.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class ContraprovasTest(unittest.TestCase):
    def assertViola(self, texto, codigo, instanciado=False):
        achados = chk.verificar(texto, instanciado=instanciado)
        self.assertTrue(any(a == codigo or a.startswith(codigo + ":") for a in achados), (codigo, achados))

    # S6-R5: gatilhos e permissões
    def test_pull_request_target_recusado(self):
        self.assertViola(muta("  workflow_dispatch:\n", "  workflow_dispatch:\n  pull_request_target:\n"), "GATILHO_PROIBIDO")

    def test_gatilhos_de_terceiros_recusados(self):
        for g in ("pull_request", "issue_comment", "issues", "workflow_run", "schedule"):
            self.assertViola(muta("  workflow_dispatch:\n", "  workflow_dispatch:\n  %s:\n" % g), "GATILHO_PROIBIDO")

    def test_permissao_padrao_nao_vazia_recusada(self):
        self.assertViola(muta("permissions: {}\n", "permissions:\n  contents: write\n"), "PERMISSOES_PADRAO_NAO_VAZIAS")
        self.assertViola(muta("permissions: {}\n", "permissions: write-all\n"), "PERMISSOES_PADRAO_NAO_VAZIAS")

    def test_permissao_sem_o_bloco_padrao_recusada(self):
        self.assertViola(muta("permissions: {}\n", ""), "PERMISSOES_PADRAO_NAO_VAZIAS")

    def test_permissao_extra_no_job_recusada(self):
        for extra in ("actions: write", "workflows: write", "pull-requests: write", "issues: write", "id-token: write"):
            t = muta("      contents: write\n", "      contents: write\n      %s\n" % extra)
            self.assertTrue(chk.verificar(t), extra)

    # S6-R5: expressão não confiável
    def test_interpolacao_em_run_recusada(self):
        t = muta('test "$(git rev-parse HEAD)" = "$EVENTO_SHA"', 'test "$(git rev-parse HEAD)" = "${{ github.sha }}"')
        self.assertViola(t, "EXPRESSAO_EM_RUN")

    def test_entrada_controlada_por_terceiros_recusada(self):
        for expr in ("github.event.head_commit.message", "github.head_ref", "github.event.pull_request.title",
                     "github.event.issue.body", "github.event.comment.body", "github.actor", "inputs.qualquer"):
            t = muta("EVENTO_SHA: ${{ github.sha }}", "EVENTO_SHA: ${{ %s }}" % expr)
            self.assertViola(t, "EXPRESSAO_NAO_PERMITIDA")

    def test_expressao_no_env_global_recusada(self):
        t = muta("  VALIDADOR_REPO: Andraus35/UFMS-MEU-ESTUDO\n", "  VALIDADOR_REPO: Andraus35/UFMS-MEU-ESTUDO\n  X: ${{ secrets.DADOS_TOKEN }}\n")
        self.assertTrue(chk.verificar(t))

    def test_segredo_so_no_env_da_etapa_de_promocao(self):
        self.assertViola(muta("          DADOS_TOKEN: ${{ secrets.DADOS_TOKEN }}\n", ""), "SEGREDO_FORA_DO_ENV_DA_ETAPA")
        dobrado = muta_passo(PASSO_PROMOCAO, "          EXECUCAO: ${{ github.run_id }}\n",
                             "          EXECUCAO: ${{ github.run_id }}\n          OUTRO: ${{ secrets.DADOS_TOKEN }}\n")
        self.assertViola(dobrado, "SEGREDO_FORA_DO_ENV_DA_ETAPA")

    def test_segredo_impresso_recusado(self):
        t = muta_passo(PASSO_PROMOCAO, 'set -euo pipefail\n          python "$RUNNER_TEMP', 'set -euo pipefail\n          echo "$DADOS_TOKEN"\n          python "$RUNNER_TEMP')
        self.assertViola(t, "SEGREDO_IMPRESSO_OU_GRAVADO")

    # S6-R5: ações e validador fixados
    def test_acao_por_tag_recusada_e_por_sha_aceita(self):
        base = muta("    steps:\n", "    steps:\n      - uses: actions/checkout@v4\n")
        self.assertViola(base, "ACAO_NAO_FIXADA_POR_SHA")
        ok = muta("    steps:\n", "    steps:\n      - uses: actions/checkout@" + "c" * 40 + "\n")
        self.assertEqual(chk.verificar(ok), [])

    def test_validador_por_ramo_recusado(self):
        t = muta("VALIDADOR_SHA: __VALIDADOR_SHA__", "VALIDADOR_SHA: main")
        self.assertViola(t, "VALIDADOR_SHA_INVALIDO")
        self.assertViola(muta('fetch -q --depth 1 "https://github.com/$VALIDADOR_REPO.git" "$VALIDADOR_SHA"',
                              'fetch -q --depth 1 "https://github.com/$VALIDADOR_REPO.git" main'), "VALIDADOR_POR_RAMO")

    def test_repositorio_do_validador_alterado_recusado(self):
        self.assertViola(muta("VALIDADOR_REPO: Andraus35/UFMS-MEU-ESTUDO", "VALIDADOR_REPO: outro/repositorio"),
                         "VALIDADOR_REPO_DIVERGENTE")

    def test_sem_sha_do_validador_recusado(self):
        self.assertViola(muta("  VALIDADOR_SHA: __VALIDADOR_SHA__\n", ""), "VALIDADOR_SHA_INVALIDO")

    def test_sem_conferencia_do_hash_do_portao_recusada(self):
        t = muta('          test "$atual" = "$VALIDADOR_GATE_SHA256"\n', "")
        self.assertViola(t, "SEM_CONFERENCIA_DO_VALIDADOR")

    def test_sem_conferencia_do_sha_obtido_recusada(self):
        t = muta('          test "$(git rev-parse HEAD)" = "$VALIDADOR_SHA"\n', "")
        self.assertViola(t, "SEM_CONFERENCIA_DO_VALIDADOR")

    def test_sem_conferencia_do_hash_do_proprio_fluxo_recusada(self):
        self.assertViola(muta('          test -n "$FLUXO_SHA256_ESPERADO"\n', ""), "SEM_CONFERENCIA_DO_HASH_DO_FLUXO")
        self.assertViola(muta("sha256sum fila_repo", "cat fila_repo"), "SEM_CONFERENCIA_DO_HASH_DO_FLUXO")

    def test_sem_conferencia_do_sha_do_evento_recusada(self):
        t = muta('          test "$(git rev-parse HEAD)" = "$EVENTO_SHA"\n', "")
        self.assertViola(t, "SEM_CONFERENCIA_DO_SHA_DO_EVENTO")

    def test_etapa_removida_ou_reordenada_recusada(self):
        t = re.sub(r"      - name: Conferir o hash do próprio fluxo\n.*?(?=      - name: Obter o validador)", "", MODELO, flags=re.S)
        self.assertViola(t, "ETAPAS_FORA_DE_ORDEM_OU_AUSENTES")
        a, b = "      - name: Obter a fila no SHA do evento\n", "      - name: Conferir o hash do próprio fluxo\n"
        trocado = MODELO.replace(a, "@@A@@").replace(b, a).replace("@@A@@", b)
        self.assertViola(trocado, "ETAPAS_FORA_DE_ORDEM_OU_AUSENTES")

    def test_promocao_sem_o_sha_fixado_recusada(self):
        t = muta_passo(PASSO_PROMOCAO, ' --validador-sha "$VALIDADOR_SHA"', "")
        self.assertViola(t, "PROMOCAO_SEM_SHA_FIXADO")

    # a caixa de comandos: SHA fixado e sem o segredo do histórico
    def test_caixa_sem_o_sha_fixado_recusada(self):
        self.assertViola(muta_passo(PASSO_CAIXA, ' --validador-sha "$VALIDADOR_SHA"', ""), "CAIXA_SEM_SHA_FIXADO")
        self.assertViola(muta_passo(PASSO_CAIXA, "command_box_runner.py", "outro_script.py"), "CAIXA_SEM_SHA_FIXADO")

    def test_caixa_com_o_segredo_do_historico_recusada(self):
        t = muta_passo(PASSO_CAIXA, "          EXECUCAO: ${{ github.run_id }}\n",
                       "          EXECUCAO: ${{ github.run_id }}\n          DADOS_TOKEN: ${{ secrets.DADOS_TOKEN }}\n")
        achados = chk.verificar(t)
        self.assertIn("CAIXA_COM_SEGREDO_DO_HISTORICO", achados)
        self.assertIn("SEGREDO_FORA_DO_ENV_DA_ETAPA", achados)  # e o segredo aparece mais de uma vez

    def test_passo_da_caixa_removido_ou_fora_de_ordem_recusado(self):
        sem = MODELO[:MODELO.index(PASSO_CAIXA)]
        self.assertViola(sem, "ETAPAS_FORA_DE_ORDEM_OU_AUSENTES")

    # execução serial e sem bypass
    def test_concorrencia_e_timeout_exigidos(self):
        self.assertViola(muta("cancel-in-progress: false", "cancel-in-progress: true"), "CONCORRENCIA_NAO_SERIAL")
        self.assertViola(muta("    timeout-minutes: 10\n", ""), "SEM_TIMEOUT")

    def test_bypass_e_acoes_perigosas_recusados(self):
        casos = {
            "continue-on-error: true": "BYPASS_CONTINUE_ON_ERROR",
            "set +e": "ERRO_IGNORADO",
            "curl -s https://exemplo.invalido": "REDE_LIVRE",
            "pip install pacote": "INSTALACAO_EXTERNA",
            "git push origin main": "PUSH_FORA_DO_PORTAO",
            "set -x": "DEPURACAO_QUE_VAZA_SEGREDO",
            "printenv": "DESPEJO_DE_AMBIENTE",
        }
        for linha, codigo in casos.items():
            t = muta_passo(PASSO_PROMOCAO, '          set -euo pipefail\n          python "$RUNNER_TEMP',
                           '          set -euo pipefail\n          %s\n          python "$RUNNER_TEMP' % linha)
            self.assertViola(t, codigo)

    def test_texto_vazio_ou_invalido_falha_fechado(self):
        for ruim in ("", "   \n", None, 42):
            self.assertEqual(chk.verificar(ruim), ["TEXTO_VAZIO"])

    def test_fronteiras_do_verificador(self):
        fonte = (ROOT / "scripts/promotion_workflow_check.py").read_text(encoding="utf-8")
        for proibido in ("import requests", "urllib", "socket", "subprocess", "os.environ", "open(", ".write_text("):
            self.assertNotIn(proibido, fonte)


if __name__ == "__main__":
    unittest.main()
